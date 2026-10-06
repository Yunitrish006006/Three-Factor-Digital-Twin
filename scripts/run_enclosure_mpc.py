#!/usr/bin/env python3
"""Calibrate, freeze, then evaluate assumed-model enclosure controllers."""
import argparse
from dataclasses import asdict, replace
from datetime import datetime, timezone
import csv
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import random
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from digital_twin.control.enclosure_mpc import (
    ControlSettings, ThermalParameters, EnclosurePlant, EnclosureMPC, EnclosureBaseline,
)

CHANGE = ROOT / 'openspec/changes/implement-enclosure-mpc-20261005'
STEPS = 120
SEEDS = {'calibration': [11, 12, 13], 'validation': [21, 22, 23],
         'holdout': [31, 32, 33], 'mismatch': [41, 42, 43], 'overload': [41, 42, 43]}
SOURCES = ['digital_twin/control/enclosure_mpc.py', 'scripts/run_enclosure_mpc.py',
           'scripts/verify_enclosure_mpc.py', 'scripts/enclosure_mpc_requirements.txt',
           'openspec/changes/implement-enclosure-mpc-20261005/protocol.md',
           'openspec/changes/implement-enclosure-mpc-20261005/research.md']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n')


def source_hashes():
    return {p: sha(ROOT/p) for p in SOURCES}


def scenario(split, seed):
    rng = random.Random(seed)
    # Entire trace is known only to the evaluator, never passed to the controller.
    schedules = {
        'calibration': ([60,120,180,90], [90,180,240,120]),
        'validation': ([100,190,70,160], [140,260,100,220]),
        'holdout': ([70,200,110,180,80], [100,280,160,250,120]),
        'mismatch': ([70,200,110,180,80], [100,280,160,250,120]),
        'overload': ([450], [600]),
    }
    cpu, gpu = schedules[split]
    rows = []
    for i in range(STEPS):
        segment = min(len(cpu)-1, i * len(cpu) // STEPS)
        inlet = 29. + (seed % 3 - 1) + 2. * (i >= STEPS//2) + rng.uniform(-.2,.2)
        rows.append({'inlet_C': inlet, 'cpu_W': max(0.,cpu[segment]+rng.uniform(-5,5)),
                     'gpu_W': max(0.,gpu[segment]+rng.uniform(-8,8))})
    return rows


def controller(method, values):
    if method == 'mpc':
        return EnclosureMPC(settings=replace(ControlSettings(), **values))
    return EnclosureBaseline(method, **values)


def episode(method, values, split, seed):
    pars, settings = ThermalParameters(), ControlSettings()
    if split == 'mismatch':
        pars = replace(pars, capacities=tuple(.7*v for v in pars.capacities),
                       fan_gains=tuple(.65*v for v in pars.fan_gains), fan_tau_s=40.)
    plant, ctl = EnclosurePlant(pars), controller(method, values)
    initial = (58.+seed%3, 59.+seed%3)
    plant.reset(initial)
    previous, rows = .5, []
    for index, disturbance in enumerate(scenario(split, seed)):
        state = plant.state.copy()
        powers = (disturbance['cpu_W'], disturbance['gpu_W'])
        u, info = ctl.step(state, disturbance['inlet_C'], powers, previous)
        future = plant.step(u, disturbance['inlet_C'], powers, settings.dt_s)
        rows.append({'step': index, 'time_s': index*settings.dt_s,
                     'cpu_C': state[0], 'gpu_C': state[1], 'fan': state[2],
                     **disturbance, 'previous_pwm': previous, 'pwm': u,
                     'rpm': future[2]*pars.max_rpm, 'next_fan': future[2],
                     'next_cpu_C': future[0], 'next_gpu_C': future[1],
                     'pred_cpu_C': info['predicted'][0], 'pred_gpu_C': info['predicted'][1],
                     'fallback': int(info['fallback']), 'reason': info['reason'],
                     'solver_status': info['solver_status'], 'slack_max_C': info['slack_max_C'],
                     'safety_override': int(info['safety_override']), 'solve_s': info['solve_s']})
        previous = u
    return rows


def metrics(rows):
    import numpy as np
    s = ControlSettings()
    temp = np.array([[r['next_cpu_C'],r['next_gpu_C']] for r in rows])
    pred = np.array([[r['pred_cpu_C'],r['pred_gpu_C']] for r in rows])
    error, violation = temp-s.targets_C, np.maximum(0.,temp-s.limits_C)
    u = np.array([r['pwm'] for r in rows])
    delta = u-np.array([r['previous_pwm'] for r in rows])
    time_values = np.array([r['solve_s'] for r in rows])
    settling = None
    within = np.all(np.abs(error)<=2., axis=1)
    for i in range(len(rows)-5):
        if within[i:i+6].all():
            settling = (i+1)*s.dt_s
            break
    return {
        'tracking_mae_C': float(np.abs(error).mean()), 'tracking_rmse_C': float(np.sqrt((error**2).mean())),
        'cpu_mae_C': float(np.abs(error[:,0]).mean()), 'gpu_mae_C': float(np.abs(error[:,1]).mean()),
        'cpu_rmse_C': float(np.sqrt((error[:,0]**2).mean())), 'gpu_rmse_C': float(np.sqrt((error[:,1]**2).mean())),
        'prediction_mae_C': float(np.abs(pred-temp).mean()), 'prediction_rmse_C': float(np.sqrt(((pred-temp)**2).mean())),
        'max_cpu_C': float(temp[:,0].max()), 'max_gpu_C': float(temp[:,1].max()),
        'overtemp_s': int(np.any(violation>0,axis=1).sum())*s.dt_s,
        'cpu_overtemp_s': int((violation[:,0]>0).sum())*s.dt_s,
        'gpu_overtemp_s': int((violation[:,1]>0).sum())*s.dt_s,
        'pwm_total_variation': float(np.abs(delta).sum()),
        'bounds_violations': int(((u<s.pwm_min-1e-8)|(u>s.pwm_max+1e-8)).sum()),
        'slew_violations': int((np.abs(delta)>s.max_delta+1e-8).sum()),
        'fan_energy_proxy_Wh': float((10*u**3).sum()*s.dt_s/3600),
        'fallback_n': sum(int(r['fallback']) for r in rows),
        'safety_override_n': sum(int(r['safety_override']) for r in rows),
        'slack_max_C': max([float(r['slack_max_C']) for r in rows if r['slack_max_C'] is not None] or [0.]),
        'solve_p50_s': float(np.median(time_values)), 'solve_p95_s': float(np.quantile(time_values,.95)),
        'solve_max_s': float(time_values.max()), 'settling_time_s': settling,
        'whole_system_energy_Wh': None, 'throttling': None,
        'selection_score': float(((error/5)**2).mean()+.01*(u**3).mean()+1e4*(violation**2).mean()),
    }


def save_episode(out, method, values, split, seed):
    rows = episode(method, values, split, seed)
    name = f'{split}_{seed}_{method}'
    path = out/'traces'/f'{name}.csv'
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='') as f:
        writer = csv.DictWriter(f,fieldnames=rows[0].keys())
        writer.writeheader(); writer.writerows(rows)
    numerical = [{k: v for k,v in r.items() if k!='solve_s'} for r in rows]
    numerical_hash = hashlib.sha256(json.dumps(numerical,sort_keys=True,allow_nan=False).encode()).hexdigest()
    return {'id': name, 'method': method,'split': split,'seed': seed,'n': len(rows),
            'trace_path': str(path.relative_to(out)), 'trace_sha256': sha(path),
            'numerical_sha256': numerical_hash, 'metrics': metrics(rows)}


def candidates():
    return {'fixed': [{'pwm':u} for u in (.4,.6,.8,1.)],
            'pid': [{'kp':kp,'ki':ki,'kd':kd} for kp in (.01,.03,.06)
                    for ki in (0.,.0001,.0003) for kd in (0.,.05)],
            'mpc': [{'input_weight':r} for r in (.1,1.,10.)]}


def calibrate(out):
    if (out/'freeze.json').exists() or (out/'calibration.json').exists():
        raise SystemExit('Calibration already exists; use a new --output-dir')
    # Preserve every candidate episode, including unsuccessful choices.
    records, selected = {}, {}
    for method, choices in candidates().items():
        records[method] = []
        for index, values in enumerate(choices):
            runs = [save_episode(out/f'calibration_candidates/{method}_{index}',method,values,'calibration',seed)
                    for seed in SEEDS['calibration']]
            score = sum(r['metrics']['selection_score'] for r in runs)/len(runs)
            records[method].append({'parameters':values,'score':score,'runs':runs})
        best = min(enumerate(records[method]),key=lambda pair:(pair[1]['score'],pair[0]))
        selected[method] = best[1]['parameters']
        print('selected', method, selected[method], 'score=',best[1]['score'],flush=True)
    write_json(out/'calibration.json',records)
    freeze = {'status':'FROZEN_BEFORE_EVALUATION','registered_at':datetime.now(timezone.utc).isoformat(),
              'selected':selected,'parameters':asdict(ThermalParameters()),'settings':asdict(ControlSettings()),
              'seeds':SEEDS,'steps':STEPS,'sources':source_hashes(), 'calibration_sha256':sha(out/'calibration.json'),
              'environment':{'python':platform.python_version(),'numpy':importlib.metadata.version('numpy'),
                             'scipy':importlib.metadata.version('scipy')},
              'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'git_dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()),
              'boundary':'ASSUMED_MODEL_SIMULATION_NOT_PHYSICAL_CONTROL'}
    write_json(out/'freeze.json',freeze)


def evaluate(out):
    if (out/'result.json').exists():
        raise SystemExit('Evaluation exists; preserve it and use a new --output-dir')
    freeze = json.loads((out/'freeze.json').read_text())
    if freeze['sources'] != source_hashes() or freeze['calibration_sha256'] != sha(out/'calibration.json'):
        raise SystemExit('Source/calibration changed after freeze')
    runs=[]
    for split in ('validation','holdout','mismatch','overload'):
        for seed in SEEDS[split]:
            for method, values in freeze['selected'].items():
                runs.append(save_episode(out,method,values,split,seed))
        print('completed',split,flush=True)
    aggregates = {}
    for split in ('validation','holdout','mismatch','overload'):
        aggregates[split] = {}
        for method in freeze['selected']:
            subset=[r['metrics'] for r in runs if r['method']==method and r['split']==split]
            aggregates[split][method] = {k:sum(m[k] for m in subset)/len(subset)
                for k in subset[0] if all(m[k] is not None for m in subset)}
    nominal=[r for r in runs if r['method']=='mpc' and r['split'] in ('validation','holdout')]
    feasible=all(r['metrics']['bounds_violations']==0 and r['metrics']['slew_violations']==0
                 and r['metrics']['solve_p95_s']<ControlSettings().dt_s
                 and r['metrics']['fallback_n']/r['n']<=.05 for r in nominal)
    hold=aggregates['holdout']
    gain=(hold['pid']['tracking_mae_C']-hold['mpc']['tracking_mae_C'])/hold['pid']['tracking_mae_C']
    safe=all(next(r for r in runs if r['split']=='holdout' and r['seed']==seed and r['method']=='mpc')['metrics']['overtemp_s']
             <=next(r for r in runs if r['split']=='holdout' and r['seed']==seed and r['method']=='pid')['metrics']['overtemp_s']
             for seed in SEEDS['holdout'])
    write_json(out/'result.json',{'status':'COMPLETED_EXPLORATORY_ASSUMED_MODEL_SIMULATION',
                'evaluated_at':datetime.now(timezone.utc).isoformat(),'freeze_sha256':sha(out/'freeze.json'),
                'runs':runs,'aggregates':aggregates,
                'decisions':{'H-MPC-01':'SUPPORTED_SIMULATION_ONLY' if feasible else 'NOT_SUPPORTED',
                             'H-MPC-02':'SUPPORTED_SIMULATION_ONLY' if gain>=.05 and safe else 'NOT_SUPPORTED',
                             'holdout_relative_mae_gain_vs_pid':gain,
                             'physical_enclosure':'NOT_EVALUATED','E8':'NOT_EVALUATED','LQR':'TODO'},
                'boundary':freeze['boundary']})
    print(json.dumps(aggregates['holdout'],indent=2),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase',choices=['calibrate','evaluate'],required=True)
    parser.add_argument('--output-dir',type=Path,default=CHANGE/'artifacts')
    args=parser.parse_args()
    (calibrate if args.phase=='calibrate' else evaluate)(args.output_dir)


if __name__=='__main__':
    main()
