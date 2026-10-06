"""Independently recompute trace metrics and preregistered decisions; no experiment rerun."""
import csv
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / 'openspec/changes/prototype-sparse-enclosure-transfer-20261006/artifacts'


def check_artifacts(directory):
    directory = Path(directory)
    result = json.loads((directory / 'result.json').read_text())
    config = json.loads((directory / 'config.json').read_text())
    freeze = json.loads((directory / 'freeze.json').read_text())
    calibration = json.loads((directory / 'calibration.json').read_text())
    errors = []

    def require(value, message):
        if not value:
            errors.append(message)

    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    for relative, digest in freeze['source_hashes'].items():
        require(sha(directory / 'source_snapshots' / relative) == digest, f'snapshot hash: {relative}')
        require(sha(ROOT / relative) == digest, f'live frozen source changed: {relative}')
    for name in ('config', 'calibration'):
        require(sha(directory / f'{name}.json') == freeze[f'{name}_sha256'], f'{name} freeze hash')
    for filename, digest in freeze['calibration_trace_hashes'].items():
        require(sha(directory / filename) == digest, f'calibration trace hash {filename}')
        with (directory / filename).open() as f:
            cal_rows = list(csv.DictReader(f))
        require(len(cal_rows) == 120 and not any('truth' in key or 'source' in key for key in cal_rows[0]),
                f'sparse calibration contract {filename}')
    for name, cal in calibration.items():
        require(cal['nfev'] <= 30 and cal['input_temperature_channels'] == ['plate', 'air'], f'calibration budget {name}')
    recomputed, seen, total = {}, set(), 0
    for run in result['runs']:
        key = (run['task'], run['split'], run['rig'], run['seed'], run['method'])
        require(key not in seen, f'duplicate {key}')
        seen.add(key)
        with (directory / run['csv']).open() as f:
            rows = [{k: float(v) for k, v in row.items()} for row in csv.DictReader(f)]
        require(len(rows) == 180, f'length {key}')
        require(all(math.isfinite(v) for row in rows for v in row.values()), f'finite {key}')
        require([r['step'] for r in rows] == list(range(180)), f'time alignment {key}')
        require(run['seed'] in config['splits'][run['split']], f'split seed {key}')
        require(all(math.isclose(rows[i]['previous_pwm'], rows[i-1]['pwm'], abs_tol=1e-12)
                    for i in range(1, len(rows))), f'command continuity {key}')
        n, dt = len(rows), config['settings']['dt']
        est = [r['source_estimate'] - r['source_truth_current'] for r in rows]
        pred = [r['source_prediction_next'] - r['source_truth_next'] for r in rows]
        truth = [r['source_truth_next'] for r in rows]
        violations = sum(r['pwm'] < .2 - 1e-10 or r['pwm'] > 1 + 1e-10
                         or abs(r['pwm'] - r['previous_pwm']) > .1 + 1e-10 for r in rows)
        values = {'n': n, 'source_mae_C': sum(map(abs, est))/n,
                  'source_rmse_C': math.sqrt(sum(e*e for e in est)/n),
                  'prediction_mae_C': sum(map(abs, pred))/n,
                  'tracking_mae_C': sum(abs(t-28) for t in truth)/n,
                  'max_source_C': max(truth), 'overtemp_s': sum(t > 30 for t in truth)*dt,
                  'out_of_domain_steps': sum(t < 20 or t > 30 for t in truth),
                  'command_variation': sum(abs(r['pwm']-r['previous_pwm']) for r in rows),
                  'fan_energy_proxy_Wh': sum(2*r['fan_truth_next']**3 for r in rows)*dt/3600,
                  'command_violations': violations if run['task'] == 'closed_loop' else 0}
        if run['task'] == 'closed_loop':
            require(violations == 0, f'closed loop command bounds {key}')
        for metric, value in values.items():
            require(math.isclose(value, run['metrics'][metric], rel_tol=1e-9, abs_tol=1e-9), f'metric {key} {metric}')
        recomputed[key] = values
        total += n
    expected = {(task, split, rig, seed, method)
                for task, methods in (('open_loop', config['open_methods']), ('closed_loop', config['methods']))
                for split, seeds in config['splits'].items() for rig in config['rigs']
                for seed in seeds for method in methods}
    require(seen == expected and len(seen) == result['run_count'] == 108, 'complete design: 108 episodes')
    require(total == result['step_count'] == 19440, 'complete design: 19440 steps')
    for task, splits in result['aggregates'].items():
        for split, methods in splits.items():
            for method, aggregate in methods.items():
                members = [v for k,v in recomputed.items() if k[0] == task and k[1] == split and k[4] == method]
                for metric, reported in aggregate.items():
                    require(math.isclose(sum(v[metric] for v in members)/len(members), reported,
                                         rel_tol=1e-9, abs_tol=1e-9), f'aggregate {task} {split} {method} {metric}')
    openhold = result['aggregates']['open_loop']['holdout']
    base, corrected = openhold['calibrated_physics']['source_mae_C'], openhold['sparse_corrected']['source_mae_C']
    wins = sum(recomputed[('open_loop', 'holdout', rig, seed, 'sparse_corrected')]['source_mae_C']
               < recomputed[('open_loop', 'holdout', rig, seed, 'calibrated_physics')]['source_mae_C']
               for rig in config['rigs'] for seed in config['splits']['holdout'])
    hold = result['aggregates']['closed_loop']['holdout']
    one, six = hold['rank_h1'], hold['rank_h6']
    expected31 = 'supported' if corrected <= .9*base and wins >= 4 else 'not_supported'
    expected32 = 'supported' if six['tracking_mae_C'] <= .95*one['tracking_mae_C'] and six['overtemp_s'] <= one['overtemp_s'] and six['fan_energy_proxy_Wh'] <= 1.2*one['fan_energy_proxy_Wh'] else 'not_supported'
    require(result['decisions']['H-ENC-31'] == expected31, 'H-ENC-31 decision')
    require(result['decisions']['H-ENC-32'] == expected32, 'H-ENC-32 decision')
    require(result['decisions']['source_wins_of_6'] == wins, 'source wins')
    require(math.isclose(result['decisions']['source_mae_reduction_fraction'], 1-corrected/base), 'source reduction')
    require(math.isclose(result['decisions']['horizon_tracking_reduction_fraction'], 1-six['tracking_mae_C']/one['tracking_mae_C']), 'horizon reduction')
    require(result['physical_intervention'] == 'NOT_EVALUATED', 'physical boundary')
    return {'passed': not errors, 'errors': errors, 'verified_runs': len(seen), 'verified_steps': total,
            'source_truth_is_validation_only': True, 'calibration_fallbacks': sum(v['fallback'] for v in calibration.values())}


if __name__ == '__main__':
    verification = check_artifacts(ARTIFACTS)
    (ARTIFACTS / 'verification.json').write_text(json.dumps(verification, indent=2) + '\n')
    print(json.dumps(verification, indent=2))
    sys.exit(0 if verification['passed'] else 1)
