"""One-shot E-ENC-71 study: select from commissioning, then open fresh seeds."""
import csv
from dataclasses import asdict, replace
from datetime import datetime, timezone
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
from digital_twin.enclosure.calibrated_session import (
    ThermalPathParameters, StructureObserver, CalibratedEnclosureSession, fit_structures,
)
from digital_twin.enclosure.session import Observation, TransferSettings
from run_enclosure_session_study import plant_step, metrics, write_json, write_csv, digest

CHANGE = ROOT/'openspec/changes/select-enclosure-structure-20261012'
ARTIFACTS = CHANGE/'artifacts'
OPEN = ('S_physics', 'S_corrected', 'selected_physics', 'selected_corrected')
CLOSED = ('S_pi', 'selected_pi', 'S_rank_h6', 'selected_rank_h6')
RIGS = {
    'proportional': ('validation', ThermalPathParameters(contact=.65, plate_fan=1.05, capacities=(22.,88.,33.), fan_tau=20.)),
    'independent_caps': ('validation', ThermalPathParameters(contact=.85, plate_fan=1., capacities=(29.,60.,40.), fan_tau=25.)),
    'path_variant': ('validation', ThermalPathParameters(contact=1.05, plate_fan=1.3, capacities=(18.,104.,25.), fan_tau=11., source_air=.14)),
    'contact_variant': ('holdout', ThermalPathParameters(contact=.48, plate_fan=.95, capacities=(28.,90.,35.), fan_tau=32.)),
    'path_capacity': ('holdout', ThermalPathParameters(contact=.95, plate_fan=1.25, capacities=(19.,108.,23.), fan_tau=13., source_air=.18)),
    'convection_mismatch': ('holdout', ThermalPathParameters(contact=.9, plate_fan=1.1, capacities=(25.,72.,38.), fan_tau=18., source_air=.08, air_fan=1.9)),
}
SEEDS = {'validation': (612711,612712), 'holdout': (612721,612722)}


def commissioning(p):
    rng, state, rows = np.random.default_rng(612700), np.array([22.,22.,22.,.4]), []
    for k in range(180):
        power, duty = (.8 if (k//20)%2==0 else 2.8), (.25 if (k//15)%2==0 else .75)
        observed = state[[1,2,3]]+rng.normal(size=3)*[.1,.1,.005]
        rows.append(asdict(Observation(5.*k, float(observed[0]), float(observed[1]),
                                      float(np.clip(observed[2],0,1)), 22., power)) | {'pwm': duty})
        state = plant_step(state,duty,22.,power,p,p.source_air)
    return rows


def episode(p, candidates, chosen, seed, task, method):
    rng = np.random.default_rng(seed)
    powers = np.repeat(rng.uniform(.8,3.2,6),20)
    phase = rng.uniform(0,2*np.pi)
    inlets = 22+.3*np.sin(2*np.pi*np.arange(120)/120+phase)
    noise = rng.normal(size=(120,3))*[.1,.1,.005]
    state = np.r_[inlets[0]+[1.5,.5,.2],.4]
    structure = 'S' if method.startswith('S_') else chosen
    model = ThermalPathParameters(**candidates[structure]['parameters'])
    correction = not method.endswith('_physics')
    session = CalibratedEnclosureSession(model,float(inlets[0]),'pi' if method.endswith('_pi') else 'rank_h6') if task=='closed_loop' else None
    observer = StructureObserver(model,float(inlets[0]),correction=correction) if session is None else None
    previous, rows = .4, []
    for k,(power,inlet) in enumerate(zip(powers,inlets)):
        observed = state[[1,2,3]]+noise[k]
        observed[2] = np.clip(observed[2],0,1)
        obs = Observation(5.*k,float(observed[0]),float(observed[1]),float(observed[2]),float(inlet),float(power))
        if session:
            output = session.process(obs)
        else:
            started = time.perf_counter()
            estimate = observer.update(observed)
            duty = .4 if (k//25)%2==0 else .8
            prediction = observer.predict(duty,float(inlet),float(power))
            output = {'source_estimate_C':float(estimate[0]),'source_prediction_next_C':float(prediction[0]),
                      'pwm':duty,'previous_pwm':previous,'warning':0,'fallback':0,
                      'compute_ms':1000*(time.perf_counter()-started)}
        following = plant_step(state,output['pwm'],float(inlet),float(power)+.15,p,p.source_air)
        rows.append({**asdict(obs),**output,'step':k,
                     **{f'{name}_truth_current{suffix}':float(state[i]) for i,(name,suffix) in enumerate(
                         [('source','_C'),('plate','_C'),('air','_C'),('fan','')])},
                     **{f'{name}_truth_next{suffix}':float(following[i]) for i,(name,suffix) in enumerate(
                         [('source','_C'),('plate','_C'),('air','_C'),('fan','')])}})
        previous,state = output['pwm'],following
    return rows


def aggregate(runs):
    return {task:{split:{method:{key:float(np.mean([r['metrics'][key] for r in runs
              if (r['task'],r['split'],r['method'])==(task,split,method)])) for key in runs[0]['metrics']}
              for method in methods} for split in SEEDS} for task,methods in [('open_loop',OPEN),('closed_loop',CLOSED)]}


def decisions(runs,a):
    h=a['open_loop']['holdout']; c=a['closed_loop']['holdout']
    gain=1-h['selected_corrected']['source_mae_C']/h['S_corrected']['source_mae_C']
    wins=0
    for rig,(split,_) in RIGS.items():
        if split!='holdout':
            continue
        for seed in SEEDS[split]:
            pair={r['method']:r['metrics']['source_mae_C'] for r in runs
                  if (r['task'],r['rig'],r['seed'])==('open_loop',rig,seed)}
            wins+=pair['selected_corrected']<pair['S_corrected']
    tracking=1-c['selected_rank_h6']['tracking_mae_C']/c['S_rank_h6']['tracking_mae_C']
    return {'H-ENC-71':'supported' if gain>=.1 and wins>=4 else 'not_supported',
            'H-ENC-72':'supported' if tracking>=.05 and c['selected_rank_h6']['overtemp_s']<=c['S_rank_h6']['overtemp_s']
                and c['selected_rank_h6']['fan_energy_proxy_Wh']<=1.2*c['S_rank_h6']['fan_energy_proxy_Wh'] else 'not_supported',
            'source_mae_reduction_fraction':gain,'source_wins_of_6':int(wins),
            'tracking_reduction_fraction':tracking}


def main():
    ARTIFACTS.mkdir(exist_ok=True)
    with (ARTIFACTS/'receipt.json').open('x') as stream:
        json.dump({'started_utc':datetime.now(timezone.utc).isoformat(),'status':'started'},stream)
    (ARTIFACTS/'traces').mkdir()
    config={'rigs':{rig:{'split':split,'parameters':asdict(p)} for rig,(split,p) in RIGS.items()},
            'settings':asdict(TransferSettings()),'seeds':SEEDS,'open_methods':OPEN,'closed_methods':CLOSED,
            'steps':120,'calibration_steps':180,'training_rows':120,'selection_rows':60,
            'calibration_seed':612700,'hidden_extra_heat_W':.15,'selection_min_improvement_fraction':.05,
            'evidence_class':'commissioning_selected_assumed_model_temperature_simulation'}
    write_json(ARTIFACTS/'config.json',config)
    calibration={}
    for rig,(_,p) in RIGS.items():
        records=commissioning(p)
        write_csv(ARTIFACTS/f'calibration_{rig}.csv',records)
        _,calibration[rig]=fit_structures(records)
        print(f'calibration {rig}: selected={calibration[rig]["selected_structure"]}, '+
              str({s:round(v['selection_score'],4) for s,v in calibration[rig]['candidates'].items()}),flush=True)
    write_json(ARTIFACTS/'calibration.json',calibration)
    sources=['digital_twin/enclosure/calibrated_session.py','scripts/run_calibrated_enclosure.py',
             'scripts/run_enclosure_structure_study.py','scripts/verify_enclosure_structure_study.py',
             'tests/test_enclosure_structure.py','digital_twin/enclosure/session.py',
             'digital_twin/control/sparse_enclosure.py','digital_twin/control/sparse_enclosure_v2.py',
             'scripts/run_enclosure_session_study.py','scripts/verify_enclosure_session_study.py',
             str((CHANGE/'protocol.md').relative_to(ROOT)),str((CHANGE/'research.md').relative_to(ROOT))]
    for relative in sources:
        path=ARTIFACTS/'source_snapshots'/relative
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes((ROOT/relative).read_bytes())
    history={str(p.relative_to(ROOT)):digest(p) for folder in (
        'prototype-sparse-enclosure-transfer-20261006','correct-sparse-enclosure-review-20261006',
        'validate-enclosure-four-controllers-20261005','implement-enclosure-mpc-20261005',
        'integrate-enclosure-session-20261012') for p in (ROOT/'openspec/changes'/folder/'artifacts').rglob('*') if p.is_file()}
    write_json(ARTIFACTS/'historical_manifest.json',history)
    inputs=[ARTIFACTS/name for name in ('config.json','calibration.json','historical_manifest.json')]+list(ARTIFACTS.glob('calibration_*.csv'))
    write_json(ARTIFACTS/'freeze.json',{'utc':datetime.now(timezone.utc).isoformat(),
        'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'source_hashes':{r:digest(ROOT/r) for r in sources},'input_hashes':{p.name:digest(p) for p in inputs},
        'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__}})
    started,runs=time.perf_counter(),[]
    for task,methods in [('open_loop',OPEN),('closed_loop',CLOSED)]:
        for rig,(split,p) in RIGS.items():
            fit=calibration[rig]
            for seed in SEEDS[split]:
                for method in methods:
                    rows=episode(p,fit['candidates'],fit['selected_structure'],seed,task,method)
                    name=f'traces/{task}_{rig}_{seed}_{method}.csv'
                    write_csv(ARTIFACTS/name,rows)
                    runs.append({'task':task,'split':split,'rig':rig,'seed':seed,'method':method,'csv':name,
                                 'sha256':digest(ARTIFACTS/name),'metrics':metrics(rows,task)})
            print(f'{task} {rig} complete',flush=True)
    a=aggregate(runs)
    result={'evidence_class':config['evidence_class'],'run_count':len(runs),'step_count':sum(r['metrics']['n'] for r in runs),
            'runs':runs,'aggregates':a,'decisions':decisions(runs,a),
            'physical_identification':'NOT_EVALUATED','physical_actuation':'NOT_EVALUATED','humidity_light_transfer':'NOT_EVALUATED',
            'completed_utc':datetime.now(timezone.utc).isoformat(),'wall_time_s':time.perf_counter()-started}
    write_json(ARTIFACTS/'result.json',result)
    print(json.dumps({k:result[k] for k in ('run_count','step_count','decisions','wall_time_s')},indent=2),flush=True)


if __name__=='__main__':
    main()
