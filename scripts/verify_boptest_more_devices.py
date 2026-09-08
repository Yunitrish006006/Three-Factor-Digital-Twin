"""Recompute bank selection and every recorded closed-loop metric."""
import argparse,csv,json
from run_boptest_more_devices import ART,ROOT,CONFIG,source_hashes,sha,make
from run_boptest_cross_plant import metrics
from boptest_native_adapter import encode,decode
from digital_twin.control.delayed_dynamics import identify_bank

def loadrows(path):
    with path.open() as f:return [{k:float(v) for k,v in r.items()} for r in csv.DictReader(f)]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--plant',choices=['heat_pump','apartment','commercial']);args=parser.parse_args()
    names=[args.plant] if args.plant else ['heat_pump','apartment','commercial']
    freeze=json.loads((ART/'freeze.json').read_text());assert freeze['sources']==source_hashes()
    output={'status':'PASS','plants':{},'sources_match':True};total=0
    for name in names:
        p=ART/(name+'.json');r=json.loads(p.read_text());assert r['status']=='COMPLETED'
        assert r['sources']==freeze['sources'] and r['freeze_sha256']==sha(ART/'freeze.json')
        c=r['config'];assert c==json.loads(CONFIG.read_text())[name];cal=loadrows(ROOT/r['calibration_trace'])
        sp=ART/(name+'_selection.json');sel=json.loads(sp.read_text())
        assert sel['sources']==freeze['sources'] and r['selection_sha256']==sha(sp)
        assert sel['adaptation_sha256']==sha(ART/(name+'_adaptation.json'))
        for h in [2,6]:
            stored=r['banks'][str(h)];new=identify_bank(cal[:h*60],c['target_C'],c['step_s'])
            assert new['status']==stored['status'] and new['validation_starts']==stored['validation_starts']
            assert len(stored['candidates'])==10
            for a,b in zip(new['candidates'],stored['candidates']):
                assert a['status']==b['status'] and a['n']==b['n']
                if a['validation_rollout_rmse_C'] is not None:assert abs(a['validation_rollout_rmse_C']-b['validation_rollout_rmse_C'])<1e-5
            if stored['status']=='FITTED':
                a,b=new['selected'],stored['selected'];assert (a['order'],a['delay_steps'])==(b['order'],b['delay_steps'])
                assert max(abs(x-y) for x,y in zip(a['a'],b['a']))<1e-5
                for key in ['b','c','intercept','tau_s','steady_gain_C_per_u']:
                    assert abs(a[key]-b[key])<1e-5
                for method in ['auto_pi','proposed']:
                    trials=[t for t in r['trials'] if t['budget_h']==h and t['method']==method]
                    assert len(trials)==2 and [t['q'] for t in trials]==[.5,1.]
                    best=min(trials,key=lambda t:t['metrics']['mae_C'])
                    choice=next(v for v in sel['selected'] if v['budget_h']==h and v['method']==method)
                    assert choice['q']==best['q'] and choice['trial_sha256']==best['sha256']
            else:assert not any(t['budget_h']==h for t in r['trials']+r['evaluations'])
        successful=sum(b['status']=='FITTED' for b in r['banks'].values())
        assert len(r['trials'])==successful*4 and len(r['evaluations'])==successful*4
        assert all(e['active_adaptation_h']==e['budget_h']+4 for e in r['evaluations'])
        initial={}
        for rec in [r['identification']]+r['trials']+r['evaluations']:
            path=ROOT/rec['trace'];assert sha(path)==rec['sha256'];rows=loadrows(path);total+=1
            assert len(rows)==rec['scored_hours']*60
            assert rec['warmup_hours']==24
            assert abs(rec['initial_u']-decode(c,rows[0]['actuator_native']))<1e-12
            expected_start=(rec['day'] if 'day' in rec else 2 if 'method' in rec else 1)*86400
            assert rows[0]['time_s']==expected_start
            for a,b in zip(rows,rows[1:]):
                assert b['time_s']-a['time_s']==60 and abs(a['next_T']-b['T'])<1e-9
                assert abs(encode(c,a['u'])-b['actuator_native'])<1e-9
            for row in rows:assert 0<=row['u']<=1
            if 'method' in rec:
                ctrl=make(c,r['banks'][str(rec['budget_h'])]['selected'],rec['q'],rec['method'])
                ctrl.prime(rows[0]['T'],rec['initial_u'])
                for i,row in enumerate(rows):
                    assert abs(ctrl.step(row['T'],row['previous_u'],i)-row['u'])<1e-8
            else:
                from digital_twin.control.portable_pi import clamp
                for i,row in enumerate(rows):
                    assert abs(row['u']-clamp(rec['initial_u']+[-.15,.15,0,.25,-.25,.10][(i//15)%6]))<1e-12
            for k,v in metrics(rows,c).items():assert abs(v-rec['metrics'][k])<1e-9
            if 'day' in rec:
                choice=next(v for v in sel['selected'] if v['budget_h']==rec['budget_h'] and v['method']==rec['method']);assert rec['q']==choice['q']
                assert rec['day'] in [20,50] and rows[0]['time_s']==rec['day']*86400
                assert abs(initial.setdefault(rec['day'],rows[0]['T'])-rows[0]['T'])<1e-9
        decisions=[]
        for h in [2,6]:
            pairs=[]
            for day in [20,50]:
                items={e['method']:e for e in r['evaluations'] if e['day']==day and e['budget_h']==h}
                if not items:continue
                a,b=items['proposed']['metrics'],items['auto_pi']['metrics']
                pairs.append({'day':day,'mae_gain_C':b['mae_C']-a['mae_C'],'max_error_delta_C':a['max_abs_error_C']-b['max_abs_error_C'],
                    'nonregression':a['mae_C']<=b['mae_C']+.02 and a['max_abs_error_C']<=b['max_abs_error_C']+.2})
            decisions.append({'budget_h':h,'pairs':pairs,'gate':len(pairs)==2 and all(p['nonregression'] for p in pairs) and sum(p['mae_gain_C'] for p in pairs)>0})
        output['plants'][name]={'model_status':{h:b['status'] for h,b in r['banks'].items()},'decisions':decisions,'result_sha256':sha(p)}
    output['new_traces']=total;output['scope']='THREE_NEW_FMUS_WITH_BOUNDED_ADAPTATION';output['all_six_budgets_pass']=len(names)==3 and all(d['gate'] for p in output['plants'].values() for d in p['decisions'])
    destination=ART/(f'{args.plant}_verification.json' if args.plant else 'verification.json')
    destination.write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output,indent=2))

if __name__=='__main__':main()
