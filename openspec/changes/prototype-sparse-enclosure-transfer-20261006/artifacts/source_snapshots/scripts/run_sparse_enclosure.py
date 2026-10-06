"""Execute the preregistered source-blind transfer pilot exactly once per artifact directory."""
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
from digital_twin.control.sparse_enclosure import (
    HeatNetwork, TransferSettings, advance, SparseObserver, TransferController,
    fit_sparse_network,
)

CHANGE = ROOT / 'openspec/changes/prototype-sparse-enclosure-transfer-20261006'
ARTIFACTS = CHANGE / 'artifacts'
RIGS = {'contact_poor': replace(HeatNetwork(), contact=.45),
        'metal_path': replace(HeatNetwork(), contact=1.1),
        'duct_assumption': replace(HeatNetwork(), contact=1.1, plate_fan=1.3)}
SPLITS = {'validation': [610611, 610612], 'holdout': [610621, 610622]}
METHODS = ('fixed', 'pi', 'pid', 'rank_h1', 'rank_h6', 'rank_h6_no_correction')
OPEN_METHODS = ('nominal_physics', 'calibrated_physics', 'sparse_corrected')


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + '\n')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path, rows):
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def metrics(rows, settings=TransferSettings()):
    a = {key: np.array([r[key] for r in rows], dtype=float) for key in rows[0]}
    estimated_error = a['source_estimate'] - a['source_truth_current']
    forecast_error = a['source_prediction_next'] - a['source_truth_next']
    return {
        'n': len(rows), 'source_mae_C': float(np.mean(np.abs(estimated_error))),
        'source_rmse_C': float(np.sqrt(np.mean(estimated_error ** 2))),
        'prediction_mae_C': float(np.mean(np.abs(forecast_error))),
        'tracking_mae_C': float(np.mean(np.abs(a['source_truth_next'] - settings.target))),
        'max_source_C': float(np.max(a['source_truth_next'])),
        'overtemp_s': float(np.sum(a['source_truth_next'] > settings.limit) * settings.dt),
        'out_of_domain_steps': int(np.sum((a['source_truth_next'] < 20.) | (a['source_truth_next'] > 30.))),
        'command_variation': float(np.sum(np.abs(a['pwm'] - a['previous_pwm']))),
        'fan_energy_proxy_Wh': float(np.sum(2. * a['fan_truth_next'] ** 3) * settings.dt / 3600),
        'command_violations': int(np.sum((a['pwm'] < settings.pwm_min - 1e-10)
                                       | (a['pwm'] > settings.pwm_max + 1e-10)
                                       | (np.abs(a['pwm'] - a['previous_pwm']) > settings.slew + 1e-10))),
    }


def calibration_data(parameters):
    rng, rows = np.random.default_rng(610600), []
    state = np.array([22., 22., 22., .4])
    for k in range(120):
        power = .8 if (k // 20) % 2 == 0 else 2.8
        u = .25 if (k // 15) % 2 == 0 else .75
        noise = rng.normal(size=3) * [.1, .1, .005]
        rows.append({'step': k, 'inlet': 22., 'power': power, 'pwm': u,
                     'plate': float(state[1] + noise[0]), 'air': float(state[2] + noise[1]),
                     'fan': float(np.clip(state[3] + noise[2], 0., 1.))})
        state = advance(state, u, 22., power, parameters)
    return rows


def workload(seed):
    rng = np.random.default_rng(seed)
    powers = np.repeat(rng.uniform(.8, 3.2, size=6), 30)
    phase = rng.uniform(0, 2 * np.pi)
    inlets = 22 + .3 * np.sin(2 * np.pi * np.arange(180) / 180 + phase)
    noise = rng.normal(size=(180, 3)) * [.1, .1, .005]
    return powers, inlets, noise


def episode(parameters, identified, seed, task, method):
    powers, inlets, noise = workload(seed)
    state = np.r_[inlets[0] + np.array([1.5, .5, .2]), .4]
    model = HeatNetwork() if method == 'nominal_physics' else identified
    corrected = method not in ('nominal_physics', 'calibrated_physics', 'rank_h6_no_correction')
    observer = SparseObserver(model, inlets[0], correction=corrected)
    controller = TransferController(method, model) if task == 'closed_loop' else None
    previous, rows = .4, []
    for k, (power, inlet) in enumerate(zip(powers, inlets)):
        observation = state[[1, 2, 3]] + noise[k]
        observation[2] = np.clip(observation[2], 0., 1.)
        estimate = observer.update(observation)
        if controller:
            u, info = controller.step(estimate, inlet, power, previous)
        else:
            u, info = (.4 if (k // 25) % 2 == 0 else .8), {'warning': False}
        prediction = observer.predict(u, inlet, power)
        # Hidden source truth and extra heat remain on the simulation/scoring side.
        next_state = advance(state, u, inlet, power + .15, parameters)
        rows.append({
            'step': k, 'time_s': k * 5., 'inlet': float(inlet), 'declared_power': float(power),
            'plate_observed': float(observation[0]), 'air_observed': float(observation[1]),
            'fan_observed': float(observation[2]), 'source_truth_current': float(state[0]),
            'source_estimate': float(estimate[0]), 'source_prediction_next': float(prediction[0]),
            'source_truth_next': float(next_state[0]), 'fan_truth_next': float(next_state[3]),
            'previous_pwm': float(previous), 'pwm': float(u), 'warning': int(info['warning']),
        })
        previous, state = u, next_state
    return rows


def aggregates(runs):
    result = {}
    for task in ('open_loop', 'closed_loop'):
        result[task] = {}
        methods = OPEN_METHODS if task == 'open_loop' else METHODS
        for split in SPLITS:
            result[task][split] = {}
            for method in methods:
                selected = [r['metrics'] for r in runs if r['task'] == task
                            and r['split'] == split and r['method'] == method]
                result[task][split][method] = {
                    key: float(np.mean([m[key] for m in selected])) for key in selected[0]}
    return result


def decisions(runs, aggregate):
    hold = aggregate['open_loop']['holdout']
    base, sparse = hold['calibrated_physics']['source_mae_C'], hold['sparse_corrected']['source_mae_C']
    wins = sum(next(r['metrics']['source_mae_C'] for r in runs
                    if r['task'] == 'open_loop' and r['split'] == 'holdout'
                    and r['rig'] == rig and r['seed'] == seed and r['method'] == 'sparse_corrected')
               < next(r['metrics']['source_mae_C'] for r in runs
                      if r['task'] == 'open_loop' and r['split'] == 'holdout'
                      and r['rig'] == rig and r['seed'] == seed and r['method'] == 'calibrated_physics')
               for rig in RIGS for seed in SPLITS['holdout'])
    closed = aggregate['closed_loop']['holdout']
    one, six = closed['rank_h1'], closed['rank_h6']
    reduction = 1 - six['tracking_mae_C'] / one['tracking_mae_C']
    return {'H-ENC-31': 'supported' if sparse <= .9 * base and wins >= 4 else 'not_supported',
            'H-ENC-32': 'supported' if reduction >= .05 and six['overtemp_s'] <= one['overtemp_s']
            and six['fan_energy_proxy_Wh'] <= 1.2 * one['fan_energy_proxy_Wh'] else 'not_supported',
            'source_mae_reduction_fraction': 1 - sparse / base, 'source_wins_of_6': int(wins),
            'horizon_tracking_reduction_fraction': reduction}


def main():
    if (ARTIFACTS / 'result.json').exists() or (ARTIFACTS / 'freeze.json').exists():
        raise SystemExit('Refusing to overwrite this evaluated/frozen study')
    ARTIFACTS.mkdir(exist_ok=True)
    (ARTIFACTS / 'traces').mkdir(exist_ok=True)
    config = {'settings': asdict(TransferSettings()), 'rigs': {k: asdict(p) for k, p in RIGS.items()},
              'splits': SPLITS, 'methods': list(METHODS), 'open_methods': list(OPEN_METHODS),
              'calibration_seed': 610600, 'calibration_steps': 120, 'evaluation_steps': 180,
              'extra_unobserved_heat_W': .15, 'information_contract': ['plate', 'air', 'fan', 'inlet', 'power'],
              'evidence_class': 'temperature_only_assumed_network_simulation'}
    write_json(ARTIFACTS / 'config.json', config)
    calibration, identified = {}, {}
    for rig, parameters in RIGS.items():
        records = calibration_data(parameters)
        write_csv(ARTIFACTS / f'calibration_{rig}.csv', records)
        identified[rig], calibration[rig] = fit_sparse_network(records)
    write_json(ARTIFACTS / 'calibration.json', calibration)
    sources = ['digital_twin/control/sparse_enclosure.py', 'scripts/run_sparse_enclosure.py',
               'scripts/verify_sparse_enclosure.py', 'tests/test_sparse_enclosure.py',
               str((CHANGE / 'protocol.md').relative_to(ROOT)), str((CHANGE / 'research.md').relative_to(ROOT))]
    hashes = {p: digest(ROOT / p) for p in sources}
    snapshots = ARTIFACTS / 'source_snapshots'
    for relative in sources:
        target = snapshots / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / relative).read_bytes())
    freeze = {'utc': datetime.now(timezone.utc).isoformat(), 'source_hashes': hashes,
              'config_sha256': digest(ARTIFACTS / 'config.json'),
              'calibration_sha256': digest(ARTIFACTS / 'calibration.json'),
              'calibration_trace_hashes': {f'calibration_{rig}.csv': digest(ARTIFACTS / f'calibration_{rig}.csv') for rig in RIGS},
              'preregistration_commit': '69eea268569dfb2d84099f1948bb58ca87b0a8ae',
              'git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'environment': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__}}
    write_json(ARTIFACTS / 'freeze.json', freeze)
    started, runs = time.perf_counter(), []
    for task, methods in (('open_loop', OPEN_METHODS), ('closed_loop', METHODS)):
        for split, seeds in SPLITS.items():
            for rig, parameters in RIGS.items():
                for seed in seeds:
                    for method in methods:
                        rows = episode(parameters, identified[rig], seed, task, method)
                        filename = f'traces/{task}_{split}_{rig}_{seed}_{method}.csv'
                        write_csv(ARTIFACTS / filename, rows)
                        summary = metrics(rows)
                        if task == 'open_loop':
                            # Excitation steps intentionally need not meet closed-loop slew limits.
                            summary['command_violations'] = 0
                        runs.append({'task': task, 'split': split, 'rig': rig, 'seed': seed,
                                     'method': method, 'csv': filename, 'metrics': summary})
            print(f'{task} {split} complete', flush=True)
    aggregate = aggregates(runs)
    result = {'evidence_class': config['evidence_class'], 'run_count': len(runs),
              'step_count': sum(r['metrics']['n'] for r in runs), 'runs': runs, 'aggregates': aggregate,
              'decisions': decisions(runs, aggregate), 'wall_time_s': time.perf_counter() - started,
              'completed_utc': datetime.now(timezone.utc).isoformat(),
              'physical_intervention': 'NOT_EVALUATED', 'original_three_factor_transfer': 'NOT_EVALUATED'}
    write_json(ARTIFACTS / 'result.json', result)
    print(json.dumps({'run_count': result['run_count'], 'step_count': result['step_count'],
                      'decisions': result['decisions'], 'wall_time_s': result['wall_time_s']}, indent=2))


if __name__ == '__main__':
    main()
