"""One-shot, research-only state/model information intervention. No actuation."""
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
import hashlib
import json
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
import scipy
from scipy.linalg import solve_discrete_are
from digital_twin.enclosure.session import (HeatNetwork, TransferSettings, SparseObserver,
    SessionController, Observation, fit_observations, equilibrium, linearize, steady_state, command)
from run_enclosure_session_study import plant_step, schedule, metrics, write_csv, write_json, digest

CHANGE=ROOT/'openspec/changes/diagnose-enclosure-lqr-20261019'
ARTIFACTS=CHANGE/'artifacts'
PANELS={
    'contact_shift':replace(HeatNetwork(),contact=.58,plate_fan=1.05,capacities=(24.,76.,33.),fan_tau=24.),
    'slow_fan':replace(HeatNetwork(),contact=.9,plate_fan=1.3,capacities=(21.,92.,27.),fan_tau=35.),
    'low_capacity':replace(HeatNetwork(),contact=1.15,plate_fan=.65,capacities=(15.,64.,23.),fan_tau=10.),
    'air_path':replace(HeatNetwork(),contact=.8,plate_fan=1.1,capacities=(25.,84.,38.),fan_tau=18.,air_base=.8,air_fan=1.9),
}
ARMS={'estimated_fitted':('lqr',False,False),'truth_fitted':('lqr',True,False),
      'estimated_exact':('lqr',False,True),'truth_exact':('lqr',True,True),'pi':('pi',False,False)}
SEEDS=(619201,619202)
STATE_NAMES=('source','plate','air','fan')


def commissioning(p,seed):
    rng=np.random.default_rng(seed);state=np.array([22.,22.,22.,.4]);rows=[]
    for k in range(180):
        power=.8 if (k//20)%2==0 else 2.8;duty=.25 if (k//15)%2==0 else .75
        obs=state[[1,2,3]]+rng.normal(size=3)*[.1,.1,.005]
        rows.append(asdict(Observation(5.*k,float(obs[0]),float(obs[1]),float(np.clip(obs[2],0,1)),22.,power))|{'pwm':duty})
        state=plant_step(state,duty,22.,power,p)
    return rows


def lqr_probe(x,p,inlet,power,previous):
    """Read-only diagnostics; the unchanged production controller still acts."""
    s=TransferSettings();center,ff=equilibrium(p,inlet,power,s)
    a,b,_=linearize(center,ff,inlet,power,p,s.dt)
    q,r=np.diag([1.,.25,.1,.02]),np.array([[.15]])
    riccati=solve_discrete_are(a,b,q,r)
    k=np.linalg.solve(r+b.T@riccati@b,b.T@riccati@a)
    raw=float(ff-(k@(x-center))[0]);amp=float(np.clip(raw,s.pwm_min,s.pwm_max))
    return {'raw_lqr_pwm':raw,'raw_valid':1,'amplitude_clipped':int(abs(raw-amp)>1e-9),
            'slew_limited':int(abs(command(amp,previous,s)-amp)>1e-9)}


def episode(p,fitted,seed,arm):
    method,true_state,exact_model=ARMS[arm]
    powers,inlets,noises=schedule(seed)
    state=np.r_[inlets[0]+np.array([1.5,.5,.2]),.4]
    observer=SparseObserver(fitted,float(inlets[0]))
    controller=SessionController(method,p if exact_model else fitted)
    previous=.4;rows=[]
    for k,(power,inlet) in enumerate(zip(powers,inlets)):
        obs=state[[1,2,3]]+noises[k];obs[2]=np.clip(obs[2],0,1)
        observation=Observation(5.*k,float(obs[0]),float(obs[1]),float(obs[2]),float(inlet),float(power))
        started=time.perf_counter();estimated=observer.update(obs)
        control=state.copy() if true_state else estimated.copy()
        duty,info=controller.step(control,inlet,power,previous,observed_plate_air=obs[:2])
        diag={'raw_lqr_pwm':0.,'raw_valid':0,'amplitude_clipped':0,'slew_limited':0}
        if method=='lqr' and not info['fallback']:
            diag=lqr_probe(control,controller.parameters,inlet,power,previous)
            expected=command(1. if info['warning'] else diag['raw_lqr_pwm'],previous)
            if abs(duty-expected)>1e-9:raise ValueError('Diagnostic altered/failed to match actual command')
        predicted=observer.predict(duty,inlet,power)
        elapsed=1000*(time.perf_counter()-started)
        following=plant_step(state,duty,inlet,power,p)
        warm=steady_state(p,inlet,power,.2)[0];cool=steady_state(p,inlet,power,1.)[0]
        row={**asdict(observation),'step':k,'pwm':duty,'previous_pwm':previous,
             'source_estimate_C':float(estimated[0]),'source_prediction_next_C':float(predicted[0]),
             'warning':int(info['warning']),'fallback':int(info['fallback']),'compute_ms':elapsed,
             **diag,'steady_target_outside_range':int(not cool<=28<=warm)}
        for i,name in enumerate(STATE_NAMES):
            row[name+'_truth_current'+('_C' if i<3 else '')]=float(state[i])
            row[name+'_truth_next'+('_C' if i<3 else '')]=float(following[i])
            row[name+'_estimated']=float(estimated[i]);row[name+'_control']=float(control[i])
        rows.append(row);state=following;previous=duty
    return rows


def all_metrics(rows):
    m=metrics(rows,'closed_loop')
    for key in ('amplitude_clipped','slew_limited','steady_target_outside_range'):
        m[key+'_fraction']=mean(float(r[key]) for r in rows)
    m['control_source_mae_C']=mean(abs(r['source_control']-r['source_truth_current_C']) for r in rows)
    m['raw_valid_steps']=sum(r['raw_valid'] for r in rows)
    return m


def summarize(runs):
    aggregate={a:{k:mean(r['metrics'][k] for r in runs if r['arm']==a) for k in runs[0]['metrics']} for a in ARMS}
    pairs=[]
    for panel in PANELS:
        for seed in SEEDS:
            r={x['arm']:x['metrics'] for x in runs if x['panel']==panel and x['seed']==seed}
            t={a:m['tracking_mae_C'] for a,m in r.items()}
            pairs.append({'panel':panel,'seed':seed,'tracking_mae_C':t,
              'model_effect_with_true_state_C':t['truth_fitted']-t['truth_exact'],
              'model_effect_with_estimated_state_C':t['estimated_fitted']-t['estimated_exact'],
              'state_effect_with_fitted_model_C':t['estimated_fitted']-t['truth_fitted'],
              'state_effect_with_exact_model_C':t['estimated_exact']-t['truth_exact'],
              'interaction_C':(t['estimated_fitted']-t['truth_fitted'])-(t['estimated_exact']-t['truth_exact'])})
    decisions={}
    for hid,base,variant in [('H-ENC-91','truth_fitted','truth_exact'),('H-ENC-92','estimated_fitted','truth_fitted')]:
        reduction=1-aggregate[variant]['tracking_mae_C']/aggregate[base]['tracking_mae_C']
        wins=sum(p['tracking_mae_C'][variant]<p['tracking_mae_C'][base] for p in pairs)
        passed=reduction>=.05 and wins>=6 and aggregate[variant]['overtemp_s']<=aggregate[base]['overtemp_s'] and aggregate[variant]['fallbacks']==0 and aggregate[base]['fallbacks']==0
        decisions[hid]={'status':'supported' if passed else 'not_supported','reduction_fraction':reduction,'wins_of_8':wins,'baseline':base,'variant':variant}
    return aggregate,pairs,decisions


def main():
    ARTIFACTS.mkdir(parents=True,exist_ok=True)
    with (ARTIFACTS/'attempt.json').open('x') as f:json.dump({'started_utc':datetime.now(timezone.utc).isoformat(),'status':'started; completion in result.json'},f)
    (ARTIFACTS/'traces').mkdir()
    sources=['scripts/run_enclosure_lqr_diagnostic.py','scripts/verify_enclosure_lqr_diagnostic.py','tests/test_enclosure_lqr_diagnostic.py',
      'digital_twin/enclosure/session.py','digital_twin/control/sparse_enclosure.py','digital_twin/control/sparse_enclosure_v2.py',
      'scripts/run_enclosure_session_study.py','scripts/verify_enclosure_session_study.py']+[str((CHANGE/n).relative_to(ROOT)) for n in ('protocol.md','research.md','design.md','proposal.md')]
    historical={str(p.relative_to(ROOT)):digest(p) for p in (ROOT/'openspec/changes').glob('*/artifacts/**/*') if p.is_file() and ARTIFACTS not in p.parents}
    config={'panels':{n:asdict(p) for n,p in PANELS.items()},'arms':ARMS,'seeds':SEEDS,'calibration_seeds':{n:619100+i for i,n in enumerate(PANELS)},'settings':asdict(TransferSettings()),'steps':120,'no_hidden_heat_bias':True,'observer':'fitted model in every arm','evidence_class':'same_family_simulation_information_intervention'}
    write_json(ARTIFACTS/'config.json',config);write_json(ARTIFACTS/'historical_hashes.json',historical)
    for name in sources:
        dest=ARTIFACTS/'source_snapshots'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/name).read_bytes())
    write_json(ARTIFACTS/'freeze.json',{'utc':datetime.now(timezone.utc).isoformat(),'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
      'source_hashes':{n:digest(ROOT/n) for n in sources},'config_sha256':digest(ARTIFACTS/'config.json'),'historical_manifest_sha256':digest(ARTIFACTS/'historical_hashes.json'),
      'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__}})
    started=time.perf_counter();fits={};calibration={}
    for i,(name,p) in enumerate(PANELS.items()):
        rows=commissioning(p,619100+i);write_csv(ARTIFACTS/f'calibration_{name}.csv',rows)
        fits[name],calibration[name]=fit_observations(rows)
        calibration[name]['csv_sha256']=digest(ARTIFACTS/f'calibration_{name}.csv')
        print('calibration',name,calibration[name]['success'],flush=True)
    write_json(ARTIFACTS/'calibration.json',calibration)
    runs=[]
    for name,p in PANELS.items():
        for seed in SEEDS:
            for arm in ARMS:
                rows=episode(p,fits[name],seed,arm);filename=f'traces/{name}_{seed}_{arm}.csv'
                write_csv(ARTIFACTS/filename,rows)
                runs.append({'panel':name,'seed':seed,'arm':arm,'csv':filename,'sha256':digest(ARTIFACTS/filename),'metrics':all_metrics(rows)})
        print('completed panel',name,flush=True)
    aggregate,pairs,decisions=summarize(runs)
    write_json(ARTIFACTS/'result.json',{'evidence_class':config['evidence_class'],'runs':runs,'aggregates':aggregate,'pairs':pairs,'decisions':decisions,
        'run_count':len(runs),'step_count':sum(r['metrics']['n'] for r in runs),'calibration_rows':720,
        'calibration_sha256':digest(ARTIFACTS/'calibration.json'),'completed_utc':datetime.now(timezone.utc).isoformat(),'wall_time_s':time.perf_counter()-started,
        'physical_validation':'NOT_EVALUATED','same_as_prior_study_conditions':False})
    print(json.dumps(decisions,indent=2),flush=True)


if __name__=='__main__':main()
