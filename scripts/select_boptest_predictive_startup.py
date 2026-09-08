"""Frozen window metrics and automatic development-only boundary selection."""
import json
from run_boptest_cross_plant import ROOT, metrics, sha
ART=ROOT/'openspec/changes/predictive-startup-boundary/artifacts'


def windows(rows,c):
    n=int(3600/c['step_s']); hold=int(900/c['step_s'])
    onset=None
    for i in range(len(rows)-hold+1):
        if all(abs(r['next_T']-c['target_C'])<=.1 for r in rows[i:i+hold]):
            onset=(i+1)*c['step_s']/60; break
    return dict(early=metrics(rows[:n],c),late=metrics(rows[n:],c),
                acquisition_onset_min=onset,acquisition_confirmation_min=None if onset is None else onset+(hold-1)*c['step_s']/60)


def gate(base,candidate):
    b,e=base['early'],candidate['early']; t,l=base['late'],candidate['late']
    a,z=base['acquisition_onset_min'],candidate['acquisition_onset_min']
    checks=dict(early_gain=b['mae_C']-e['mae_C']>=max(.001,.01*b['mae_C']),
                early_peak=e['max_abs_error_C']<=b['max_abs_error_C']+max(.02,.05*b['max_abs_error_C']),
                late_mae=l['mae_C']<=t['mae_C']+max(.002,.05*t['mae_C']),
                late_peak=l['max_abs_error_C']<=t['max_abs_error_C']+max(.02,.05*t['max_abs_error_C']),
                late_tv=l['requested_TV_u']<=1.1*t['requested_TV_u']+.02,
                acquisition=a is None or z is not None and z<=a+1)
    return dict(passed=all(checks.values()),checks=checks)


def select(records):
    base=records[0]['windows']; decisions=[dict(horizon_min=r['horizon_min'],**gate(base,r['windows'])) for r in records[1:]]
    eligible=[r for r,d in zip(records[1:],decisions) if d['passed']]
    chosen=min(eligible,key=lambda r:(r['windows']['early']['mae_C'],r['horizon_min'])) if eligible else records[0]
    return dict(horizon_min=chosen['horizon_min'],decisions=decisions)


def main():
    dest=ART/'selection.json'
    if dest.exists(): raise SystemExit('Selection exists')
    configs=json.loads((ROOT/'scripts/boptest_startup_devices.json').read_text())
    result=dict(selections={},development_sources={})
    for name in configs:
        p=ART/(name+'_development.json'); r=json.loads(p.read_text()); assert r['status']=='COMPLETED'
        result['selections'][name]=select(r['evaluations'])
        result['development_sources'][str(p.relative_to(ROOT))]=sha(p)
    dest.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result['selections'],indent=2))
if __name__=='__main__':main()
