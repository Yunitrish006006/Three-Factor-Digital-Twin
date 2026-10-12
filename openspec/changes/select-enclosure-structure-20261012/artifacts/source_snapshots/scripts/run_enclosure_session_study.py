"""One-shot fresh exploratory study. Frozen prior studies/E15 are never rerun."""
import csv
from dataclasses import asdict, replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
import scipy
from scipy.integrate import solve_ivp
from digital_twin.enclosure.session import (
    HeatNetwork, TransferSettings, SparseObserver, EnclosureSession, Observation,
    METHODS, fit_observations,
)

CHANGE = ROOT / 'openspec/changes/integrate-enclosure-session-20261012'
ARTIFACTS = CHANGE / 'artifacts'
OPEN_METHODS = ('nominal_physics', 'calibrated_physics', 'sparse_corrected')
RIGS = {
    'capacity_variant': ('validation', replace(HeatNetwork(), contact=.6, plate_fan=1., capacities=(23.,92.,34.5), fan_tau=22.), 0.),
    'duct_variant': ('validation', replace(HeatNetwork(), contact=1.2, plate_fan=1.4, capacities=(17.,68.,25.5), fan_tau=9.), 0.),
    'contact_capacity': ('holdout', replace(HeatNetwork(), contact=.5, plate_fan=.9, capacities=(27.,88.,36.), fan_tau=30.), 0.),
    'extra_path': ('holdout', replace(HeatNetwork(), contact=1., plate_fan=1.2, capacities=(18.,100.,24.), fan_tau=12.), .12),
}
SEEDS = {'validation': (612111,612112), 'holdout': (612121,612122)}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n')


def write_csv(path, rows):
    with Path(path).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def plant_step(state, duty, inlet, power, p, extra_path=0.):
    """Truth solver deliberately independent of estimator RK4 implementation."""
    def rhs(t, x):
        source_plate = p.contact*(x[0]-x[1])
        plate_air = (p.plate_base+p.plate_fan*x[3])*(x[1]-x[2])
        air_out = (p.air_base+p.air_fan*x[3])*(x[2]-inlet)
        source_out = p.bypass*(x[0]-inlet)
        source_air = extra_path*(x[0]-x[2])
        return [(power-source_plate-source_out-source_air)/p.capacities[0],
                (source_plate-plate_air)/p.capacities[1],
                (plate_air+source_air-air_out)/p.capacities[2],
                (duty-x[3])/p.fan_tau]
    fit = solve_ivp(rhs, (0.,5.), state, rtol=1e-8, atol=1e-10)
    if not fit.success:
        raise ArithmeticError('Independent simulation plant failed')
    return fit.y[:,-1]


def schedule(seed, n=120):
    rng = np.random.default_rng(seed)
    powers = np.repeat(rng.uniform(.8,3.2,6), n//6)
    phase = rng.uniform(0.,2*np.pi)
    inlets = 22+.3*np.sin(2*np.pi*np.arange(n)/n+phase)
    noise = rng.normal(size=(n,3))*[.1,.1,.005]
    return powers, inlets, noise


def calibrate(parameters, extra_path):
    rng, rows = np.random.default_rng(612100), []
    state = np.array([22.,22.,22.,.4])
    for k in range(180):
        power, duty = (.8 if (k//20)%2 == 0 else 2.8), (.25 if (k//15)%2 == 0 else .75)
        noise = rng.normal(size=3)*[.1,.1,.005]
        observed = state[[1,2,3]]+noise
        rows.append(asdict(Observation(5.*k, float(observed[0]), float(observed[1]),
                                        float(np.clip(observed[2],0,1)), 22.,power)) | {'pwm': duty})
        state = plant_step(state,duty,22.,power,parameters,extra_path)
    return rows


def episode(parameters, extra_path, identified, seed, task, method):
    power_sequence, inlets, noise = schedule(seed)
    state = np.r_[inlets[0]+np.array([1.5,.5,.2]),.4]
    model = HeatNetwork() if method == 'nominal_physics' else identified
    correction = method not in ('nominal_physics','calibrated_physics','rank_h6_no_correction')
    session = EnclosureSession(model,float(inlets[0]),method,correction) if task == 'closed_loop' else None
    observer = SparseObserver(model,float(inlets[0]),correction=correction) if session is None else None
    previous, rows = .4, []
    for k, (power,inlet) in enumerate(zip(power_sequence,inlets)):
        observed = state[[1,2,3]]+noise[k]
        observed[2] = np.clip(observed[2],0,1)
        observation = Observation(5.*k,float(observed[0]),float(observed[1]),float(observed[2]),float(inlet),float(power))
        if session:
            output = session.process(observation)
        else:
            started = time.perf_counter()
            estimate = observer.update(observed)
            duty = .4 if (k//25)%2 == 0 else .8
            prediction = observer.predict(duty,float(inlet),float(power))
            output = {'source_estimate_C':float(estimate[0]),'source_prediction_next_C':float(prediction[0]),
                      'pwm':duty,'previous_pwm':previous,'warning':False,'fallback':False,
                      'compute_ms':1000*(time.perf_counter()-started)}
        next_state = plant_step(state,output['pwm'],float(inlet),float(power)+.15,parameters,extra_path)
        row = {**asdict(observation), **output, 'step': k,
               'source_truth_current_C':float(state[0]),'plate_truth_current_C':float(state[1]),
               'air_truth_current_C':float(state[2]),'fan_truth_current':float(state[3]),
               'source_truth_next_C':float(next_state[0]),'plate_truth_next_C':float(next_state[1]),
               'air_truth_next_C':float(next_state[2]),'fan_truth_next':float(next_state[3])}
        row['warning'],row['fallback'] = int(row['warning']),int(row['fallback'])
        rows.append(row)
        previous,state = output['pwm'],next_state
    return rows


def metrics(rows, task):
    a = {k:np.array([r[k] for r in rows],dtype=float) for k in rows[0]}
    error = a['source_estimate_C']-a['source_truth_current_C']
    predicted = a['source_prediction_next_C']-a['source_truth_next_C']
    delta = a['pwm']-a['previous_pwm']
    violations = np.sum((a['pwm']<.2-1e-9)|(a['pwm']>1+1e-9)|(np.abs(delta)>.1+1e-9))
    return {'n':len(rows),'source_mae_C':float(np.mean(np.abs(error))),
            'source_rmse_C':float(np.sqrt(np.mean(error**2))),
            'prediction_mae_C':float(np.mean(np.abs(predicted))),
            'prediction_rmse_C':float(np.sqrt(np.mean(predicted**2))),
            'tracking_mae_C':float(np.mean(np.abs(a['source_truth_next_C']-28))),
            'max_source_C':float(a['source_truth_next_C'].max()),
            'overtemp_s':float(5*np.sum(a['source_truth_next_C']>30)),
            'out_of_domain_steps':int(np.sum((a['source_truth_next_C']<20)|(a['source_truth_next_C']>30))),
            'command_variation':float(np.abs(delta).sum()),
            'fan_energy_proxy_Wh':float(np.sum(2*a['fan_truth_next']**3)*5/3600),
            'command_violations':int(violations) if task == 'closed_loop' else 0,
            'warnings':int(a['warning'].sum()),'fallbacks':int(a['fallback'].sum()),
            'compute_mean_ms':float(a['compute_ms'].mean()),'compute_p95_ms':float(np.percentile(a['compute_ms'],95)),
            'compute_max_ms':float(a['compute_ms'].max())}


def aggregates(runs):
    result = {}
    for task,methods in [('open_loop',OPEN_METHODS),('closed_loop',METHODS)]:
        result[task] = {}
        for split in SEEDS:
            result[task][split] = {}
            for method in methods:
                selected = [r['metrics'] for r in runs if (r['task'],r['split'],r['method']) == (task,split,method)]
                result[task][split][method] = {k:float(np.mean([m[k] for m in selected])) for k in selected[0]}
    return result


def decisions(runs, aggregate):
    estimation = aggregate['open_loop']['holdout']
    reduction = 1-estimation['sparse_corrected']['source_mae_C']/estimation['calibrated_physics']['source_mae_C']
    pairs = {(r['rig'],r['seed']) for r in runs if r['task']=='open_loop' and r['split']=='holdout'}
    wins = 0
    for rig,seed in pairs:
        by_method = {r['method']:r['metrics']['source_mae_C'] for r in runs
                     if r['task']=='open_loop' and r['rig']==rig and r['seed']==seed}
        wins += by_method['sparse_corrected']<by_method['calibrated_physics']
    one,six = [aggregate['closed_loop']['holdout'][m] for m in ('rank_h1','rank_h6')]
    tracking = 1-six['tracking_mae_C']/one['tracking_mae_C']
    return {'H-ENC-51':'supported' if reduction>=.1 and wins>=3 else 'not_supported',
            'H-ENC-52':'supported' if tracking>=.05 and six['overtemp_s']<=one['overtemp_s']
            and six['fan_energy_proxy_Wh']<=1.2*one['fan_energy_proxy_Wh'] else 'not_supported',
            'source_mae_reduction_fraction':reduction,'source_wins_of_4':int(wins),
            'horizon_tracking_reduction_fraction':tracking}


def main():
    ARTIFACTS.mkdir(exist_ok=True)
    # Receipt persists through failure/interruption. Never silently rerun opened evaluation.
    with (ARTIFACTS/'receipt.json').open('x') as stream:
        json.dump({'started_utc':datetime.now(timezone.utc).isoformat(),'status':'started'},stream)
    (ARTIFACTS/'traces').mkdir(exist_ok=True)
    config = {'rigs':{rig:{'split':split,'parameters':asdict(p),'extra_source_air_conductance':extra}
                      for rig,(split,p,extra) in RIGS.items()},'settings':asdict(TransferSettings()),
              'seeds':SEEDS,'methods':METHODS,'open_methods':OPEN_METHODS,'steps':120,
              'calibration_steps':180,'calibration_seed':612100,'hidden_extra_heat_W':.15,
              'evidence_class':'commissioning_assisted_assumed_model_temperature_simulation'}
    write_json(ARTIFACTS/'config.json',config)
    fitted, calibration = {}, {}
    for rig,(_,p,extra) in RIGS.items():
        records = calibrate(p,extra)
        write_csv(ARTIFACTS/f'calibration_{rig}.csv',records)
        fitted[rig],calibration[rig] = fit_observations(records)
        print(f'calibration {rig}: success={calibration[rig]["success"]}, residual_calls={calibration[rig]["residual_calls"]}',flush=True)
    write_json(ARTIFACTS/'calibration.json',calibration)
    sources = ['digital_twin/enclosure/session.py','digital_twin/enclosure/__init__.py',
               'scripts/run_enclosure_session.py','scripts/run_enclosure_session_study.py',
               'scripts/verify_enclosure_session_study.py','tests/test_enclosure_session.py',
               str((CHANGE/'protocol.md').relative_to(ROOT)),str((CHANGE/'research.md').relative_to(ROOT))]
    sources += ['digital_twin/control/sparse_enclosure.py','digital_twin/control/sparse_enclosure_v2.py']
    snapshot = ARTIFACTS/'source_snapshots'
    for source in sources:
        path = snapshot/source
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes((ROOT/source).read_bytes())
    old_paths = ['openspec/changes/prototype-sparse-enclosure-transfer-20261006/artifacts',
                 'openspec/changes/correct-sparse-enclosure-review-20261006/artifacts',
                 'openspec/changes/validate-enclosure-four-controllers-20261005/artifacts',
                 'openspec/changes/implement-enclosure-mpc-20261005/artifacts']
    old_hashes = {str(p.relative_to(ROOT)):digest(p) for prefix in old_paths for p in (ROOT/prefix).rglob('*') if p.is_file()}
    write_json(ARTIFACTS/'historical_manifest.json',old_hashes)
    frozen = [ARTIFACTS/'config.json',ARTIFACTS/'calibration.json',ARTIFACTS/'historical_manifest.json']
    frozen += list(ARTIFACTS.glob('calibration_*.csv'))
    freeze = {'utc':datetime.now(timezone.utc).isoformat(),
              'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'source_hashes':{p:digest(ROOT/p) for p in sources},
              'input_hashes':{p.name:digest(p) for p in frozen},
              'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__}}
    write_json(ARTIFACTS/'freeze.json',freeze)
    started,runs = time.perf_counter(),[]
    for task,methods in [('open_loop',OPEN_METHODS),('closed_loop',METHODS)]:
        for rig,(split,p,extra) in RIGS.items():
            for seed in SEEDS[split]:
                for method in methods:
                    rows = episode(p,extra,fitted[rig],seed,task,method)
                    filename = f'traces/{task}_{rig}_{seed}_{method}.csv'
                    write_csv(ARTIFACTS/filename,rows)
                    runs.append({'task':task,'split':split,'rig':rig,'seed':seed,'method':method,
                                 'csv':filename,'sha256':digest(ARTIFACTS/filename),'metrics':metrics(rows,task)})
            print(f'{task} {rig} complete',flush=True)
    aggregate = aggregates(runs)
    result = {'evidence_class':config['evidence_class'],'run_count':len(runs),'step_count':sum(r['metrics']['n'] for r in runs),
              'runs':runs,'aggregates':aggregate,'decisions':decisions(runs,aggregate),
              'physical_identification':'NOT_EVALUATED','physical_actuation':'NOT_EVALUATED',
              'humidity_light_transfer':'NOT_EVALUATED','oral_presentation':'NOT_RECORDED',
              'completed_utc':datetime.now(timezone.utc).isoformat(),'wall_time_s':time.perf_counter()-started}
    write_json(ARTIFACTS/'result.json',result)
    print(json.dumps({'runs':len(runs),'steps':result['step_count'],'decisions':result['decisions'],
                      'wall_time_s':result['wall_time_s']},indent=2),flush=True)


if __name__ == '__main__':
    main()
