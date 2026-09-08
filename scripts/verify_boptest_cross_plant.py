"""Audit shared adaptation recipe, valid comparisons and rejected fits."""
import csv,json
from run_boptest_cross_plant import ART,ROOT,CONFIG,sha,source_hashes,metrics,encode
from digital_twin.control.portable_pi import fit_dynamics

def main():
    configs=json.loads(CONFIG.read_text());freeze=json.loads((ART/'freeze.json').read_text())
    assert freeze['sources']==source_hashes(configs)
    output={'status':'PASS','plants':{},'source_freeze_matches':True};ntraces=0
    for name,c in configs.items():
        p=ART/(name+'.json');r=json.loads(p.read_text());assert r['status']=='COMPLETED'
        assert r['sources']==freeze['sources'] and r['freeze_sha256']==sha(ART/'freeze.json')
        sp=ART/(name+'_selection.json');selection=json.loads(sp.read_text())
        assert selection['sources']==freeze['sources'] and r['selection_sha256']==sha(sp)
        assert selection['pre_evaluation_result_sha256']==sha(ART/(name+'_adaptation.json'))
        initial={};calibration=None
        for record in [r['identification']]+r['trials']+r['evaluations']:
            path=ROOT/record['trace'];assert sha(path)==record['sha256']
            with path.open() as f:rows=[{k:float(v) for k,v in row.items()} for row in csv.DictReader(f)]
            ntraces+=1;assert len(rows)==record['scored_hours']*3600/c['step_s']
            if record is r['identification']:calibration=rows
            for a,b in zip(rows,rows[1:]):
                assert b['time_s']-a['time_s']==c['step_s']
                assert abs(b['T']-a['next_T'])<1e-9
                assert abs(b['supply_C']-encode(c,a['u']))<1e-9
            for row in rows:
                assert 0<=row['u']<=1 and abs(row['aux']-c['aux_value'])<1e-9
            for k,v in metrics(rows,c).items():assert abs(v-record['metrics'][k])<1e-9
            if 'day' in record:
                assert abs(initial.setdefault(record['day'],rows[0]['T'])-rows[0]['T'])<1e-9
                assert rows[0]['time_s']>3*86400
        for h in [2,6]:
            fit=fit_dynamics(calibration[:h*60],c['target_C'],c['step_s'])
            assert fit['status']==r['fits'][str(h)]['status']
            for a,b in zip(fit['coefficients'],r['fits'][str(h)]['coefficients']):assert abs(a-b)<1e-7
            subset=[x for x in selection['selected'] if x['budget_h']==h]
            if fit['status']!='FITTED':
                assert not subset and not any(x['budget_h']==h for x in r['trials']+r['evaluations'])
            else:
                assert len(subset)==2
                for choice in subset:
                    candidates=[t for t in r['trials'] if t['budget_h']==h and t['method']==choice['method']]
                    assert len(candidates)==2 and [v['q'] for v in candidates]==[.5,1]
                    best=min(candidates,key=lambda x:x['metrics']['mae_C'])
                    assert choice['q']==best['q'] and choice['trial_trace_sha256']==best['sha256']
        comparisons=[]
        for h in [2,6]:
            for day in [10,40]:
                rs={x['method']:x for x in r['evaluations'] if x['budget_h']==h and x['day']==day}
                if not rs:continue
                a,b=rs['proposed']['metrics'],rs['auto_pi']['metrics']
                comparisons.append({'budget_h':h,'day':day,'mae_gain_C':b['mae_C']-a['mae_C'],
                    'nonregression':a['mae_C']<=b['mae_C']+.02 and a['max_abs_error_C']<=b['max_abs_error_C']+.2})
        output['plants'][name]={'fit_statuses':{h:f['status'] for h,f in r['fits'].items()},'evaluated_episodes':len(r['evaluations']),'comparisons':comparisons,'result_sha256':sha(p)}
    output['traces']=ntraces
    output['cross_plant_success']=all(x['evaluated_episodes']==8 and all(c['nonregression'] for c in x['comparisons']) and sum(c['mae_gain_C'] for c in x['comparisons'])>0 for x in output['plants'].values())
    (ART/'verification.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output,indent=2))

if __name__=='__main__':main()
