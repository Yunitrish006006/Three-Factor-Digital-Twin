"""Development evaluation of fixed-q PI and model-consistent bounded compensation."""
import argparse
import json
from pathlib import Path
import boptest_consistent_adapter as adapter
from run_boptest_cross_plant import ROOT,sha,fmu_path
from digital_twin.control.consistent_pi import ConsistentPI
CONFIG=ROOT/'scripts/boptest_consistent_devices.json'
ART=ROOT/'openspec/changes/model-consistent-compensation/artifacts'

def old_path(name):
    change='improve-portable-dynamics' if name in ('air','hydronic') else 'evaluate-more-boptest-devices'
    return ROOT/'openspec/changes'/change/'artifacts'/(name+'.json')

def source_hashes():
    configs=json.loads(CONFIG.read_text())
    paths=[Path(__file__),CONFIG,ART.parent/'protocol.md',ROOT/'scripts/boptest_consistent_adapter.py',ROOT/'scripts/run_boptest_cross_plant.py']
    paths += [ROOT/'digital_twin/control'/n for n in ('consistent_pi.py','delayed_dynamics.py','portable_pi.py')]
    for name,c in configs.items():
        p=old_path(name);old=json.loads(p.read_text());paths += [p,ROOT/old['calibration_trace'],fmu_path(c)]
    return {str(p.relative_to(ROOT)):sha(p) for p in paths}

def main():
    p=argparse.ArgumentParser();p.add_argument('--plant',choices=list(json.loads(CONFIG.read_text())),required=True);name=p.parse_args().plant
    c=json.loads(CONFIG.read_text())[name];ART.mkdir(parents=True,exist_ok=True);dest=ART/(name+'.json');freeze=ART/'freeze.json'
    if dest.exists():raise SystemExit('Evidence exists; no overwrite')
    sources=source_hashes()
    if freeze.exists():assert json.loads(freeze.read_text())['sources']==sources,'Frozen sources changed'
    else:freeze.write_text(json.dumps(dict(sources=sources,before_any_simulation=True),indent=2)+'\n')
    old=json.loads(old_path(name).read_text())
    r=dict(status='RUNNING',plant=name,config=c,sources=sources,freeze_sha256=sha(freeze),calibration_trace=old['calibration_trace'],banks=old['banks'],evaluations=[],skips=[],failures=[],trial_hours=0,fixed_q=.5)
    def save():
        tmp=dest.with_suffix('.tmp');tmp.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');tmp.replace(dest)
    save()
    try:
        for h in (2,6):
            if r['banks'][str(h)]['status']!='FITTED':r['skips'].append(dict(budget_h=h,reason=r['banks'][str(h)]['status']))
        for day in (25,60):
            for h in (2,6):
                bank=r['banks'][str(h)]
                if bank['status']!='FITTED':continue
                for method in ('auto_pi','consistent'):
                    ctrl=ConsistentPI(c['target_C'],c['step_s'],bank['selected'],enabled=method=='consistent')
                    _,rec=adapter.episode(c,f'eval_{day}_{h}_{method}',day*86400,24,ctrl)
                    r['evaluations'].append(dict(day=day,budget_h=h,method=method,q=.5,active_adaptation_h=h,**rec));save()
                    print(name,day,h,method,rec['metrics']['mae_C'],flush=True)
        r['status']='COMPLETED';save()
    except Exception as e:
        r['status']='FAILED';r['failures'].append(dict(type=type(e).__name__,message=str(e)));save();raise
if __name__=='__main__':main()
