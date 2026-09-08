"""Preregistered two-stage startup control study, never retune on confirmation."""
import argparse
import json
from pathlib import Path
import boptest_predictive_startup_adapter as adapter
from run_boptest_cross_plant import ROOT, sha, fmu_path
from select_boptest_predictive_startup import ART, windows
from digital_twin.control.predictive_startup_pi import PredictiveStartupPI
CONFIG=ROOT/'scripts/boptest_startup_devices.json'
PREVIOUS=ROOT/'openspec/changes/model-consistent-compensation/artifacts'


def source_hashes():
    paths=[Path(__file__),CONFIG,ART.parent/'protocol.md']
    paths += [ROOT/'scripts'/n for n in ('boptest_predictive_startup_adapter.py','select_boptest_predictive_startup.py','run_boptest_cross_plant.py')]
    paths += [ROOT/'digital_twin/control'/n for n in ('predictive_startup_pi.py','startup_pi.py','portable_pi.py','delayed_dynamics.py')]
    for name,c in json.loads(CONFIG.read_text()).items():
        p=PREVIOUS/(name+'.json'); old=json.loads(p.read_text())
        paths += [p,ROOT/old['calibration_trace'],fmu_path(c)]
        prior=ROOT/'openspec/changes/startup-pi-boundary/artifacts'/(name+'_development.json')
        baseline=json.loads(prior.read_text())['evaluations'][0]
        paths += [prior,ROOT/baseline['trace']]
    return {str(p.relative_to(ROOT)):sha(p) for p in paths}


def main():
    p=argparse.ArgumentParser();p.add_argument('--plant',required=True);p.add_argument('--phase',choices=['development','confirmation'],required=True)
    args=p.parse_args();name,phase=args.plant,args.phase
    c=json.loads(CONFIG.read_text())[name];dest=ART/(name+'_'+phase+'.json')
    if dest.exists():raise SystemExit('Evidence exists')
    sources=source_hashes();freeze=ART/'freeze.json'
    if freeze.exists():assert json.loads(freeze.read_text())['sources']==sources
    else:
        with freeze.open('x') as f:json.dump(dict(sources=sources,before_any_simulation=True),f,indent=2)
    old=json.loads((PREVIOUS/(name+'.json')).read_text());model=old['banks']['2']['selected']
    selection=None
    if phase=='confirmation':
        selection=json.loads((ART/'selection.json').read_text())
        for path,h in selection['development_sources'].items():assert sha(ROOT/path)==h
        bands=[None,selection['selections'][name]['horizon_min']];days=[42,77];hours=24
    else:bands=[None,3,10,30];days=[8];hours=3
    r=dict(status='RUNNING',plant=name,phase=phase,config=c,model=model,freeze_sha256=sha(freeze),
           selection_sha256=sha(ART/'selection.json') if selection else None,evaluations=[],failures=[])
    def save():dest.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
    save()
    try:
        for day in days:
            baseline=None
            for j,band in enumerate(bands):
                if phase=='development' and j==0:
                    prior=ROOT/'openspec/changes/startup-pi-boundary/artifacts'/(name+'_development.json')
                    rec=dict(json.loads(prior.read_text())['evaluations'][0],horizon_min=None,reused=True,reference_source=str(prior.relative_to(ROOT)))
                    r['evaluations'].append(rec);baseline=rec;save();continue
                if j and band is None:
                    r['evaluations'].append(dict(baseline,method='selected_pi_reuse',reused=True));save();continue
                ctrl=PredictiveStartupPI(c['target_C'],c['step_s'],model,band)
                rows,rec=adapter.episode(c,f'{phase}_{day}_{band}',day*86400,hours,ctrl)
                rec.update(day=day,horizon_min=band,method='auto_pi' if band is None else 'startup',reused=False,
                           windows=windows(rows,c),exit_code=ctrl.exit_code,exit_min=ctrl.exit_min,zero_min=ctrl.zero_min)
                r['evaluations'].append(rec)
                if j==0:baseline=rec
                save();print(name,phase,day,band,rec['windows'],flush=True)
        r['status']='COMPLETED';save()
    except Exception as e:
        r['status']='FAILED';r['failures'].append(str(e));save();raise
if __name__=='__main__':main()
