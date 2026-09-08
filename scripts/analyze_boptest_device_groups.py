"""Post-result descriptive groups; no estimation, selection or control changes."""
import csv,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from run_boptest_cross_plant import sha
from digital_twin.control.consistent_pi import responses
ART=ROOT/'openspec/changes/analyze-boptest-device-groups/artifacts'
CURRENT=ROOT/'openspec/changes/model-consistent-compensation/artifacts'

def rows(path):
    with path.open() as f:return [{k:float(v) for k,v in r.items()} for r in csv.DictReader(f)]

def main():
    ART.mkdir(parents=True,exist_ok=True);source={}
    def consume(p):source[str(p.relative_to(ROOT))]=sha(p);return p
    audit=json.loads(consume(CURRENT/'verification.json').read_text());out=[]
    for name in ['air','hydronic','heat_pump','apartment','commercial']:
        r=json.loads(consume(CURRENT/(name+'.json')).read_text());cal=rows(consume(ROOT/r['calibration_trace']))
        for h in [2,6]:
            b=r['banks'][str(h)];entry=dict(plant=name,budget_h=h,case=r['config']['case'],measurement=r['config']['measurement_kind'],bank_status=b['status'])
            prefix=cal[:h*60];temps=[x[k] for x in prefix for k in ('T','next_T')]
            entry['calibration']=dict(temperature_span_C=max(temps)-min(temps),temperature_min_C=min(temps),temperature_max_C=max(temps),input_min=min(x['u'] for x in prefix),input_max=max(x['u'] for x in prefix))
            if b['status']!='FITTED':entry.update(group='REJECTED',pairs=[],gate=False);out.append(entry);continue
            m=b['selected'];L,G,N=responses(m);sigma=max(.02,m['validation_rollout_rmse_C'])
            entry['model']=dict(order=m['order'],delay_min=m['delay_steps'],tau_min=m['tau_s']/60,b=m['b'],steady_gain_C_per_u=m['steady_gain_C_per_u'],validation_rmse_C=m['validation_rollout_rmse_C'],G10=G,L10=L,noise_amplification=N,confidence_upper_bound=(.1*G)**2/((.1*G)**2+sigma**2),fit_rmse_C=m['fit_one_step_rmse_C'])
            d=next(x for x in audit['plants'][name]['decisions'] if x['budget_h']==h);entry['gate']=d['gate'];entry['pairs']=[]
            for day in [25,60]:
                es={e['method']:e for e in r['evaluations'] if e['day']==day and e['budget_h']==h};a,p=es['auto_pi'],es['consistent'];trace=rows(consume(ROOT/p['trace']));consume(ROOT/a['trace'])
                ready=[x for x in trace if x['observer_ready']];sat=[x for x in trace if x['u']<=0 or x['u']>=1];unsat=[x for x in trace if 0<x['u']<1]
                mean=lambda xs:sum(xs)/len(xs) if xs else None
                pair=dict(day=day,baseline_mae_C=a['metrics']['mae_C'],consistent_mae_C=p['metrics']['mae_C'],mae_gain_C=a['metrics']['mae_C']-p['metrics']['mae_C'],baseline_TV=a['metrics']['requested_TV_u'],consistent_TV=p['metrics']['requested_TV_u'],mean_abs_correction=mean([abs(x['correction_u']) for x in trace]),correction_at_bound_pct=100*sum(abs(x['correction_u'])>=.1-1e-9 for x in trace)/len(trace),correction_nonzero_pct=100*sum(abs(x['correction_u'])>1e-12 for x in trace)/len(trace),confidence_min=min(x['confidence'] for x in ready),confidence_max=max(x['confidence'] for x in ready),innovation_mean_C=mean([x['innovation_C'] for x in ready]),innovation_rms_C=math.sqrt(mean([x['innovation_C']**2 for x in ready])),saturation_pct=p['metrics']['saturation_pct'],mae_during_saturation_C=mean([abs(x['next_T']-22) for x in sat]),mae_outside_saturation_C=mean([abs(x['next_T']-22) for x in unsat]))
                entry['pairs'].append(pair)
            signs=[p['mae_gain_C'] for p in entry['pairs']]
            entry['group']='BOTH_IMPROVE' if all(x>0 for x in signs) else 'BOTH_WORSEN' if all(x<0 for x in signs) else 'EXACT_FALLBACK' if all(x==0 for x in signs) and all(p['correction_nonzero_pct']==0 for p in entry['pairs']) else 'MIXED'
            out.append(entry)
    source['scripts/analyze_boptest_device_groups.py']=sha(Path(__file__));source['digital_twin/control/consistent_pi.py']=sha(ROOT/'digital_twin/control/consistent_pi.py')
    result=dict(status='DESCRIPTIVE_ONLY',scope='FIVE_DEVELOPMENT_FMUS_NOT_CAUSAL',sources=source,groups=out)
    (ART/'device_groups.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    for e in out:
        print(e['plant'],e['budget_h'],e['group'],{k:round(v,5) for k,v in e.get('model',{}).items() if k in ['tau_min','G10','validation_rmse_C','confidence_upper_bound']})
        for p in e['pairs']:print(' ',p['day'],'gain',round(p['mae_gain_C'],7),'bound%',round(p['correction_at_bound_pct'],1),'sat%',round(p['saturation_pct'],1),'innovationMean',round(p['innovation_mean_C'],5),'TV',round(p['baseline_TV'],2),round(p['consistent_TV'],2))
if __name__=='__main__':main()
