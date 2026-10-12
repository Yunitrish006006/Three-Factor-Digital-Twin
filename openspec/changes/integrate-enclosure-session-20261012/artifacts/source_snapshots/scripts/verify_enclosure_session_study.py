"""Independent metric/provenance/dynamics verification; no research rerun."""
import copy
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
from scipy.integrate import solve_ivp
from digital_twin.enclosure.session import Observation, EnclosureSession, HeatNetwork, SparseObserver

ARTIFACTS = ROOT/'openspec/changes/integrate-enclosure-session-20261012/artifacts'
OPEN_METHODS = ('nominal_physics','calibrated_physics','sparse_corrected')
CLOSED_METHODS = ('fixed','pi','pid','lqr','linear_mpc','rank_h1','rank_h6','rank_h6_no_correction')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, label):
    if not condition:
        raise ValueError(label)


def recompute_metrics(rows,task):
    arrays = {key:np.array([float(row[key]) for row in rows]) for key in rows[0]}
    estimate = arrays['source_estimate_C']-arrays['source_truth_current_C']
    forecast = arrays['source_prediction_next_C']-arrays['source_truth_next_C']
    tracking = arrays['source_truth_next_C']-28.
    variation = arrays['pwm']-arrays['previous_pwm']
    return {'n':len(rows),'source_mae_C':float(np.abs(estimate).mean()),
            'source_rmse_C':float(np.linalg.norm(estimate)/np.sqrt(len(rows))),
            'prediction_mae_C':float(np.abs(forecast).mean()),
            'prediction_rmse_C':float(np.linalg.norm(forecast)/np.sqrt(len(rows))),
            'tracking_mae_C':float(np.abs(tracking).mean()),
            'max_source_C':float(arrays['source_truth_next_C'].max()),
            'overtemp_s':float(np.count_nonzero(arrays['source_truth_next_C']>30)*5),
            'out_of_domain_steps':int(np.count_nonzero((arrays['source_truth_next_C']<20)|(arrays['source_truth_next_C']>30))),
            'command_variation':float(np.abs(variation).sum()),
            'fan_energy_proxy_Wh':float((arrays['fan_truth_next']**3).sum()/360.),
            'command_violations':int(np.count_nonzero((arrays['pwm']<.2-1e-9)|(arrays['pwm']>1+1e-9)
                                                     |(np.abs(variation)>.1+1e-9))) if task=='closed_loop' else 0,
            'warnings':int(arrays['warning'].sum()),'fallbacks':int(arrays['fallback'].sum()),
            'compute_mean_ms':float(arrays['compute_ms'].mean()),
            'compute_p95_ms':float(np.percentile(arrays['compute_ms'],95)),
            'compute_max_ms':float(arrays['compute_ms'].max())}


def independently_integrate(current,duty,inlet,power,parameters,extra):
    # Integrate only temperatures; fan has an independently analytic trajectory.
    ch,cp,ca = parameters['capacities']
    def heat(t,temp):
        fan = duty+(current[3]-duty)*np.exp(-t/parameters['fan_tau'])
        source_plate = parameters['contact']*(temp[0]-temp[1])
        plate_air = (parameters['plate_base']+parameters['plate_fan']*fan)*(temp[1]-temp[2])
        outlet = (parameters['air_base']+parameters['air_fan']*fan)*(temp[2]-inlet)
        direct = extra*(temp[0]-temp[2])
        bypass = parameters['bypass']*(temp[0]-inlet)
        return [(power-source_plate-bypass-direct)/ch,(source_plate-plate_air)/cp,(plate_air+direct-outlet)/ca]
    solution = solve_ivp(heat,(0.,5.),current[:3],rtol=1e-10,atol=1e-12)
    require(solution.success,'Independent integrator failure')
    return np.r_[solution.y[:,-1],duty+(current[3]-duty)*np.exp(-5/parameters['fan_tau'])]


def audit_trace(rows,run,config,calibration):
    require(len(rows)==120,'Trace sample count')
    plant = config['rigs'][run['rig']]
    require(run['split']==plant['split'] and run['seed'] in config['seeds'][run['split']],'Split identity')
    rng = np.random.default_rng(run['seed'])
    power_sequence = np.repeat(rng.uniform(.8,3.2,6),20)
    phase = rng.uniform(0,2*np.pi)
    inlets = 22+.3*np.sin(2*np.pi*np.arange(120)/120+phase)
    noises = rng.normal(size=(120,3))*[.1,.1,.005]
    state = np.r_[inlets[0]+[1.5,.5,.2],.4]
    model = HeatNetwork() if run['method']=='nominal_physics' else HeatNetwork(**calibration[run['rig']]['parameters'])
    corrected = run['method'] not in ('nominal_physics','calibrated_physics','rank_h6_no_correction')
    session = EnclosureSession(model,float(inlets[0]),run['method'],corrected) if run['task']=='closed_loop' else None
    observer = SparseObserver(model,float(inlets[0]),correction=corrected) if session is None else None
    previous,max_difference = .4,0.
    for k,row in enumerate(rows):
        obs = Observation.from_row(row)
        require(int(row['step'])==k and abs(obs.time_s-5*k)<1e-9,'Timestamp/step corruption')
        require(abs(obs.inlet_C-inlets[k])<1e-10 and abs(obs.power_W-power_sequence[k])<1e-10,'Workload provenance')
        current = np.array([float(row[key]) for key in ('source_truth_current_C','plate_truth_current_C',
                                                        'air_truth_current_C','fan_truth_current')])
        require(np.allclose(current,state,rtol=0,atol=1e-8),'Truth initial state/continuity corruption')
        measured = current[[1,2,3]]+noises[k]
        measured[2] = np.clip(measured[2],0,1)
        require(np.allclose([obs.plate_C,obs.air_C,obs.fan_fraction],measured,rtol=0,atol=1e-10),'Observation/noise provenance')
        duty = float(row['pwm'])
        require(abs(float(row['previous_pwm'])-previous)<1e-9,'Previous command continuity')
        if session:
            expected = session.process(obs)
            for key in ('source_estimate_C','source_prediction_next_C','pwm'):
                require(abs(float(row[key])-expected[key])<1e-7,'Input-only session replay mismatch: '+key)
            require(int(row['warning'])==int(expected['warning']) and int(row['fallback'])==int(expected['fallback']),
                    'Warning/fallback contract mismatch')
            require(.2-1e-9<=duty<=1+1e-9 and abs(duty-previous)<=.1+1e-9,'Command violation')
            raw_warning = max(float(row['source_estimate_C']),obs.plate_C,obs.air_C)>=29.5
            require(int(row['warning'])==int(raw_warning),'Raw sensor warning masked')
        else:
            estimated = observer.update([obs.plate_C,obs.air_C,obs.fan_fraction])
            require(abs(duty-(.4 if (k//25)%2==0 else .8))<1e-9,'Open-loop command mismatch')
            predicted = observer.predict(duty,obs.inlet_C,obs.power_W)
            require(abs(float(row['source_estimate_C'])-estimated[0])<1e-7
                    and abs(float(row['source_prediction_next_C'])-predicted[0])<1e-7,'Open-loop replay mismatch')
        require(float(row['compute_ms'])>=0 and np.isfinite(float(row['compute_ms'])),'Invalid computation time')
        following = np.array([float(row[key]) for key in ('source_truth_next_C','plate_truth_next_C','air_truth_next_C','fan_truth_next')])
        independent = independently_integrate(current,duty,obs.inlet_C,obs.power_W+.15,
                                               plant['parameters'],plant['extra_source_air_conductance'])
        difference = float(np.max(np.abs(following-independent)))
        require(difference<1e-5,'Independent plant dynamics corruption')
        max_difference = max(max_difference,difference)
        previous,state = duty,following
    return max_difference


def compare_nested(expected,actual,label):
    require(expected.keys()==actual.keys(),label+' keys')
    for key,value in expected.items():
        if isinstance(value,dict):
            compare_nested(value,actual[key],label+'/'+key)
        elif isinstance(value,(int,float)):
            require(np.isclose(value,actual[key],rtol=1e-9,atol=1e-9),label+'/'+key)
        else:
            require(value==actual[key],label+'/'+key)


def verify(artifacts=ARTIFACTS):
    artifacts = Path(artifacts)
    config,calibration,result,freeze = [json.loads((artifacts/name).read_text())
                                       for name in ('config.json','calibration.json','result.json','freeze.json')]
    require(datetime.fromisoformat(freeze['utc'])<datetime.fromisoformat(result['completed_utc']),'Freeze order')
    require(result['run_count']==88 and result['step_count']==10560 and len(result['runs'])==88,'Design count')
    require(tuple(config['methods'])==CLOSED_METHODS and tuple(config['open_methods'])==OPEN_METHODS,'Method completeness')
    for relative,digest in freeze['source_hashes'].items():
        require(sha(ROOT/relative)==digest and sha(artifacts/'source_snapshots'/relative)==digest,'Frozen source drift: '+relative)
    for relative,digest in freeze['input_hashes'].items():
        require(sha(artifacts/relative)==digest,'Frozen input drift: '+relative)
    historical = json.loads((artifacts/'historical_manifest.json').read_text())
    for relative,digest in historical.items():
        require(sha(ROOT/relative)==digest,'Historical evidence changed: '+relative)
    for rig,fit in calibration.items():
        require(fit['nfev']<=40 and fit['residual_calls']>=fit['nfev'],'Calibration budget metadata')
        require(fit['input_channels']==list(Observation.__dataclass_fields__),'Truth in calibration contract')
        with (artifacts/f'calibration_{rig}.csv').open(newline='') as stream:
            records = list(csv.DictReader(stream))
        require(len(records)==180 and all(float(row['time_s'])==k*5 for k,row in enumerate(records)),'Calibration records/cadence')
    seen,maximum = set(),0.
    for run in result['runs']:
        identity = (run['task'],run['rig'],run['seed'],run['method'])
        require(identity not in seen,'Duplicate episode')
        seen.add(identity)
        path = artifacts/run['csv']
        require(sha(path)==run['sha256'],'CSV hash mismatch')
        with path.open(newline='') as stream:
            rows = list(csv.DictReader(stream))
        compare_nested(recompute_metrics(rows,run['task']),run['metrics'],'CSV metrics')
        maximum = max(maximum,audit_trace(rows,run,config,calibration))
    expected = {(task,rig,seed,method) for rig,p in config['rigs'].items()
                for seed in config['seeds'][p['split']]
                for task,methods in [('open_loop',OPEN_METHODS),('closed_loop',CLOSED_METHODS)] for method in methods}
    require(seen==expected,'Missing/out-of-design episode')
    for task,methods in [('open_loop',OPEN_METHODS),('closed_loop',CLOSED_METHODS)]:
        for split in config['seeds']:
            for method in methods:
                selected = [r['metrics'] for r in result['runs'] if (r['task'],r['split'],r['method'])==(task,split,method)]
                macro = {key:float(np.mean([v[key] for v in selected])) for key in selected[0]}
                compare_nested(macro,result['aggregates'][task][split][method],'Macro aggregation')
    hold = result['aggregates']['open_loop']['holdout']
    reduction = 1-hold['sparse_corrected']['source_mae_C']/hold['calibrated_physics']['source_mae_C']
    pairs = {(r['rig'],r['seed']) for r in result['runs'] if r['task']=='open_loop' and r['split']=='holdout'}
    wins = 0
    for rig,seed in pairs:
        selected = {r['method']:r['metrics']['source_mae_C'] for r in result['runs']
                    if r['task']=='open_loop' and r['rig']==rig and r['seed']==seed}
        wins += selected['sparse_corrected']<selected['calibrated_physics']
    one,six = [result['aggregates']['closed_loop']['holdout'][m] for m in ('rank_h1','rank_h6')]
    tracking = 1-six['tracking_mae_C']/one['tracking_mae_C']
    decision = {'H-ENC-51':'supported' if reduction>=.1 and wins>=3 else 'not_supported',
                'H-ENC-52':'supported' if tracking>=.05 and six['overtemp_s']<=one['overtemp_s']
                and six['fan_energy_proxy_Wh']<=1.2*one['fan_energy_proxy_Wh'] else 'not_supported',
                'source_mae_reduction_fraction':reduction,'source_wins_of_4':int(wins),
                'horizon_tracking_reduction_fraction':tracking}
    compare_nested(decision,result['decisions'],'Hypothesis decisions')
    require(all(result[key]=='NOT_EVALUATED' for key in ('physical_identification','physical_actuation','humidity_light_transfer')),
            'Evidence class escalation')
    # Actual mutation probes on opened stored traces; they are validation, not fresh study.
    sample = next(r for r in result['runs'] if r['task']=='closed_loop' and r['method']=='rank_h6')
    with (artifacts/sample['csv']).open(newline='') as stream:
        original = list(csv.DictReader(stream))
    rejected = []
    for mutation in ('timestamp','coordinated_truth','fan_endpoint','raw_observation'):
        rows = copy.deepcopy(original)
        if mutation=='timestamp':
            rows[1]['time_s'] = '6'
        elif mutation=='coordinated_truth':
            for row in rows:
                for key in ('source_truth_current_C','source_truth_next_C'):
                    row[key] = str(float(row[key])+1)
        elif mutation=='fan_endpoint':
            rows[0]['fan_truth_next'] = '0.99'
        else:
            rows[0]['plate_C'] = '45'
        try:
            audit_trace(rows,sample,config,calibration)
        except ValueError:
            rejected.append(mutation)
        else:
            raise ValueError('Mutation accepted: '+mutation)
    wrong = copy.deepcopy(sample['metrics'])
    wrong['source_mae_C'] += 1
    try:
        compare_nested(recompute_metrics(original,sample['task']),wrong,'Mutated metrics')
    except ValueError:
        rejected.append('metrics')
    require(len(rejected)==5,'Mutation completeness')
    return {'status':'PASS','episodes':88,'rows':10560,'historical_files_unchanged':len(historical),
            'max_independent_state_difference':maximum,'mutation_rejections':rejected,
            'scope':'Full metrics, split completeness, time/noise/plant provenance and input-only replay. No hardware evidence.'}


if __name__ == '__main__':
    report = verify()
    (ARTIFACTS/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
