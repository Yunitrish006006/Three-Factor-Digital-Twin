"""Verify frozen sources, old-model reuse, every command/diagnostic and paired gates."""
import argparse,csv,json,math
from run_boptest_consistent import ART,ROOT,CONFIG,source_hashes,old_path,sha
from boptest_consistent_adapter import metrics,encode,decode
from digital_twin.control.consistent_pi import ConsistentPI
from digital_twin.control.portable_pi import PortablePI
from digital_twin.control.delayed_dynamics import tuning

def loadrows(p):
    with p.open() as f:return [{k:float(v) for k,v in r.items()} for r in csv.DictReader(f)]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--plant');args=parser.parse_args()
    configs=json.loads(CONFIG.read_text());names=[args.plant] if args.plant else list(configs)
    freeze=json.loads((ART/'freeze.json').read_text());assert freeze['sources']==source_hashes()
    output=dict(status='PASS',sources_match=True,scope='FIVE_DEVELOPMENT_PLANTS_NEW_DATES',plants={},traces=0)
    for name in names:
        r=json.loads((ART/(name+'.json')).read_text());old=json.loads(old_path(name).read_text());c=configs[name]
        assert r['status']=='COMPLETED' and r['config']==c and r['banks']==old['banks']
        assert r['sources']==freeze['sources'] and r['freeze_sha256']==sha(ART/'freeze.json')
        valid=sum(b['status']=='FITTED' for b in r['banks'].values());assert len(r['evaluations'])==4*valid
        initial={};cases={}
        for e in r['evaluations']:
            assert e['q']==.5 and e['active_adaptation_h']==e['budget_h'] and e['scored_hours']==24 and e['warmup_hours']==24
            path=ROOT/e['trace'];assert sha(path)==e['sha256'];rows=loadrows(path);assert len(rows)==1440
            assert rows[0]['time_s']==e['day']*86400 and e['day'] in (25,60)
            assert abs(initial.setdefault(e['day'],rows[0]['T'])-rows[0]['T'])<1e-9
            m=r['banks'][str(e['budget_h'])]['selected'];ctrl=ConsistentPI(22,60,m,e['method']=='consistent');ctrl.prime(rows[0]['T'],e['initial_u'])
            g=tuning(m,60,.5);base=PortablePI(22,60,g['kp'],g['ti'],g['b'],False);base.prime(rows[0]['T'],e['initial_u'])
            for i,row in enumerate(rows):
                assert 0<=row['u']<=1 and abs(row['previous_u']-decode(c,row['actuator_native']))<1e-9
                got=ctrl.step(row['T'],row['previous_u'],i,row['outdoor']);assert abs(got-row['u'])<1e-9
                if e['method']=='auto_pi':assert abs(base.step(row['T'],row['previous_u'],i)-row['u'])<1e-9
                for k,v in ctrl.diagnostics.items():assert abs(v-row[k])<1e-9
                if i:
                    prev=rows[i-1];assert row['time_s']-prev['time_s']==60 and abs(row['T']-prev['next_T'])<1e-9
                    assert abs(row['actuator_native']-encode(c,prev['u']))<1e-9
                    assert abs(row['correction_u']-prev['correction_u'])<=.01+1e-12
                assert abs(row['correction_u'])<=.1+1e-12
            for k,v in metrics(rows,c).items():assert abs(v-e['metrics'][k])<1e-9
            cases[(e['day'],e['budget_h'],e['method'])]=e
            e['diagnostics_audit']={'correction_nonzero_rows':sum(abs(x['correction_u'])>1e-12 for x in rows),'max_abs_correction_u':max(abs(x['correction_u']) for x in rows)}
            output['traces']+=1
        decisions=[]
        for h in (2,6):
            pairs=[]
            for day in (25,60):
                if (day,h,'consistent') not in cases:continue
                ae,be=cases[(day,h,'auto_pi')],cases[(day,h,'consistent')];a,b=ae['metrics'],be['metrics']
                pairs.append(dict(day=day,mae_gain_C=a['mae_C']-b['mae_C'],nonregression=b['mae_C']<=a['mae_C']+.02 and b['max_abs_error_C']<=a['max_abs_error_C']+.2 and b['requested_TV_u']<=1.25*a['requested_TV_u']+.1,**be['diagnostics_audit']))
            decisions.append(dict(budget_h=h,pairs=pairs,gate=len(pairs)==2 and all(x['nonregression'] for x in pairs) and sum(x['mae_gain_C'] for x in pairs)>0))
        output['plants'][name]=dict(model_status={h:b['status'] for h,b in r['banks'].items()},decisions=decisions,result_sha256=sha(ART/(name+'.json')))
    output['valid_budgets']=sum(s=='FITTED' for p in output['plants'].values() for s in p['model_status'].values())
    output['passed_budgets']=sum(d['gate'] for p in output['plants'].values() for d in p['decisions'])
    output['hypothesis']='SUPPORTED_WITHIN_DEVELOPMENT_ONLY' if len(names)==5 and output['passed_budgets']==9 else 'NOT_SUPPORTED'
    path=ART/(args.plant+'_verification.json' if args.plant else 'verification.json');path.write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output,indent=2))
if __name__=='__main__':main()
