#!/usr/bin/env python3
"""Independent, read-only verification of version 2 enclosure evidence.

Only the Python standard library is used. No controller or experiment runner
is imported. All gates remain active under ``python -O``.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import random
import statistics
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / 'openspec/changes/validate-enclosure-four-controllers-20261005/artifacts'
METHODS = ('fixed', 'pid', 'lqr', 'mpc')
SPLITS = ('validation', 'holdout', 'plant_holdout', 'overload')
TEXT_FIELDS = {'reason', 'solver_status'}
INT_FIELDS = {'step', 'fallback', 'safety_override', 'deadline'}
NULL_FIELDS = {'accepted_slack_max_C', 'primal_residual', 'dual_residual'}


class AuditError(ValueError):
    """Evidence does not satisfy the registered contract."""


def require(condition, message):
    if not condition:
        raise AuditError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    def invalid(value):
        raise AuditError('Nonfinite JSON: ' + value)
    return json.loads(Path(path).read_text(), parse_constant=invalid)


def read_rows(path):
    with Path(path).open(newline='') as stream:
        reader = csv.DictReader(stream)
        require(reader.fieldnames is not None and len(reader.fieldnames) == len(set(reader.fieldnames)),
                'Missing or duplicate CSV columns')
        rows = []
        for raw in reader:
            require(None not in raw, 'Malformed CSV row')
            row = {}
            for key, value in raw.items():
                require(value is not None, 'Missing CSV value: ' + key)
                if key in TEXT_FIELDS:
                    row[key] = value
                elif key in INT_FIELDS:
                    row[key] = int(value)
                elif key in NULL_FIELDS and value == '':
                    row[key] = None
                else:
                    row[key] = float(value)
                    require(math.isfinite(row[key]), 'Nonfinite CSV: ' + key)
            rows.append(row)
        return rows


def close(actual, expected, label, tolerance=1e-8):
    if expected is None or isinstance(expected, (str, bool)):
        require(actual == expected, label)
    elif isinstance(expected, dict):
        require(isinstance(actual, dict) and actual.keys() == expected.keys(), label + ': keys')
        for key, value in expected.items():
            close(actual[key], value, label + '.' + key, tolerance)
    elif isinstance(expected, (list, tuple)):
        require(isinstance(actual, (list, tuple)) and len(actual) == len(expected), label + ': length')
        for index, value in enumerate(expected):
            close(actual[index], value, label + '[' + str(index) + ']', tolerance)
    else:
        require(isinstance(actual, (int, float)) and math.isfinite(actual)
                and math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance), label)


def quantile(values, probability):
    ordered = sorted(values)
    index = (len(ordered) - 1) * probability
    lower = int(math.floor(index))
    upper = int(math.ceil(index))
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (index - lower)


def metrics(rows, config):
    """Recompute every reported metric from persisted rows, without NumPy."""
    require(bool(rows), 'Empty episode')
    s = config['settings']
    dt = s['dt_s']
    errors = [[r['next_cpu_C'] - s['targets_C'][0],
               r['next_gpu_C'] - s['targets_C'][1]] for r in rows]
    violations = [[max(0., r['next_cpu_C'] - s['limits_C'][0]),
                   max(0., r['next_gpu_C'] - s['limits_C'][1])] for r in rows]
    flat = [value for pair in errors for value in pair]
    pred = [r[k] - r[n] for r in rows for k, n in
            (('pred_cpu_C', 'next_cpu_C'), ('pred_gpu_C', 'next_gpu_C'))]
    u = [r['pwm'] for r in rows]
    delta = [r['pwm'] - r['previous_pwm'] for r in rows]
    timings = [r['control_s'] for r in rows]
    in_band = [all(abs(value) <= 2. for value in pair) for pair in errors]
    window = math.ceil(60. / dt)
    band_entry = next(((index + 1) * dt for index in range(len(rows) - window + 1)
                       if all(in_band[index:index + window])), None)
    slack = [r['accepted_slack_max_C'] for r in rows if r['accepted_slack_max_C'] is not None]
    result = {
        'tracking_mae_C': statistics.mean(abs(v) for v in flat),
        'tracking_rmse_C': math.sqrt(statistics.mean(v * v for v in flat)),
        'prediction_mae_C': statistics.mean(abs(v) for v in pred),
        'prediction_rmse_C': math.sqrt(statistics.mean(v * v for v in pred)),
        'max_cpu_C': max(r['next_cpu_C'] for r in rows),
        'max_gpu_C': max(r['next_gpu_C'] for r in rows),
        'overtemp_s': sum(any(v > 0 for v in pair) for pair in violations) * dt,
        'pwm_total_variation': sum(abs(v) for v in delta),
        'bounds_violations': sum(v < s['pwm_min'] - 1e-8 or v > s['pwm_max'] + 1e-8 for v in u),
        'slew_violations': sum(abs(v) > s['max_delta'] + 1e-8 for v in delta),
        'fan_energy_proxy_Wh': sum(10. * v ** 3 for v in u) * dt / 3600.,
        'fallback_n': sum(r['fallback'] for r in rows),
        'safety_override_n': sum(r['safety_override'] for r in rows),
        'accepted_slack_max_C': max(slack) if slack else None,
        'applied_violation_max_C': max(r['applied_violation_C'] for r in rows),
        'deadline_n': sum(r['deadline'] for r in rows),
        'control_p50_s': statistics.median(timings),
        'control_p95_s': quantile(timings, .95),
        'control_max_s': max(timings),
        'solver_p95_s': quantile([r['solver_s'] for r in rows], .95),
        'band_entry_60s_s': band_entry,
        'whole_system_power_W': None,
        'throttling_time_s': None,
        'selection_score': (statistics.mean(v * v / 25. for v in flat)
                            + .01 * statistics.mean(v ** 3 for v in u)
                            + 1e4 * statistics.mean(v * v for pair in violations for v in pair)),
    }
    for index, name in enumerate(('cpu', 'gpu')):
        result[name + '_mae_C'] = statistics.mean(abs(pair[index]) for pair in errors)
        result[name + '_rmse_C'] = math.sqrt(statistics.mean(pair[index] ** 2 for pair in errors))
        result[name + '_overtemp_s'] = sum(pair[index] > 0 for pair in violations) * dt
    return result


def aggregate(runs, config):
    result = {}
    for split in SPLITS:
        result[split] = {}
        for method in METHODS:
            subset = [r['metrics'] for r in runs if r['split'] == split and r['method'] == method]
            require(bool(subset), 'Missing aggregate episodes')
            result[split][method] = {
                key: statistics.mean(m[key] for m in subset) if all(m[key] is not None for m in subset) else None
                for key in subset[0]}
            result[split][method]['episodes_n'] = len(subset)
            result[split][method]['band_entry_60s_achieved_n'] = sum(m['band_entry_60s_s'] is not None for m in subset)
    return result


def decisions(runs, aggregates, config):
    supported = 'SUPPORTED_SIMULATION_ONLY'
    rejected = 'NOT_SUPPORTED'
    feasible = all(r['metrics']['bounds_violations'] == 0 and r['metrics']['slew_violations'] == 0
                   and r['metrics']['control_p95_s'] < config['settings']['dt_s']
                   and r['metrics']['fallback_n'] / r['n'] <= .05 for r in runs)
    result = {'H-CTRL-01': supported if feasible else rejected}
    for number, comparator in ((2, 'pid'), (3, 'lqr')):
        baseline = aggregates['holdout'][comparator]['tracking_mae_C']
        candidate = aggregates['holdout']['mpc']['tracking_mae_C']
        gain = (baseline - candidate) / baseline if baseline > 0 else None
        pairs = {(r['seed'], r['method']): r['metrics'] for r in runs if r['split'] == 'holdout'}
        safe = all(pairs[seed, 'mpc']['overtemp_s'] <= pairs[seed, comparator]['overtemp_s']
                   for seed in config['seeds']['holdout'])
        result['H-CTRL-0' + str(number)] = supported if gain is not None and gain >= .05 and safe else rejected
        result['holdout_relative_mae_gain_vs_' + comparator] = gain
    result.update(physical_enclosure='NOT_EVALUATED', E8='NOT_EVALUATED', NTC='NOT_EVALUATED',
                  boundary=config['boundary'])
    return result


def scenario(config, split, seed):
    rng = random.Random(seed)
    cpu, gpu = config['schedules'][split]
    rows = []
    for index in range(config['steps']):
        segment = min(len(cpu) - 1, index * len(cpu) // config['steps'])
        inlet = 29. + (seed % 3 - 1) + 1.5 * (index >= 40) + .5 * (index >= 80) + rng.uniform(-.2, .2)
        rows.append((inlet, max(0., cpu[segment] + rng.uniform(-5., 5.)),
                     max(0., gpu[segment] + rng.uniform(-8., 8.))))
    return rows


def parameters(config, split, seed):
    p = {key: list(value) if isinstance(value, list) else value for key, value in config['parameters'].items()}
    if split == 'plant_holdout':
        variant = config['variants'][config['seeds'][split].index(seed)]
        for key, factor in (('capacities', 'capacity_factors'), ('conductances', 'conductance_factors'),
                            ('fan_gains', 'fan_gain_factors')):
            p[key] = [a * b for a, b in zip(p[key], variant[factor])]
        p['fan_tau_s'] = variant['fan_tau_s']
    return p


def plant_step(state, pwm, inlet, powers, p, dt):
    """Independent scalar reconstruction of the registered numerical plant."""
    x = list(state)
    count = math.ceil(dt)
    step = dt / count
    for _ in range(count):
        for node in (0, 1):
            loss = (p['conductances'][node] + p['fan_gains'][node] * x[2]) * (x[node] - inlet)
            x[node] += step * (powers[node] - loss) / p['capacities'][node]
        x[2] = pwm + (x[2] - pwm) * math.exp(-step / p['fan_tau_s'])
    return x


def prediction(state, pwm, inlet, powers, config):
    """ZOH via a convergent power series of the augmented affine matrix.

    The state has three components plus constants for PWM and affine drift.
    Scaling and squaring avoids large Taylor terms without a SciPy dependency.
    """
    p = config['parameters']
    dt = config['settings']['dt_s']
    matrix = [[0.] * 5 for _ in range(5)]
    for node in (0, 1):
        cooling = p['conductances'][node] + p['fan_gains'][node] * state[2]
        matrix[node][node] = -cooling / p['capacities'][node]
        matrix[node][2] = -p['fan_gains'][node] * (state[node] - inlet) / p['capacities'][node]
        drift = (powers[node] - cooling * (state[node] - inlet)) / p['capacities'][node]
        matrix[node][4] = drift - sum(matrix[node][j] * state[j] for j in range(3))
    matrix[2][2] = -1. / p['fan_tau_s']
    matrix[2][3] = 1. / p['fan_tau_s']
    norm = max(sum(abs(v * dt) for v in row) for row in matrix)
    squarings = max(0, math.ceil(math.log2(norm))) if norm else 0
    small = [[v * dt / (2 ** squarings) for v in row] for row in matrix]
    def multiply(a, b):
        return [[sum(a[i][k] * b[k][j] for k in range(5)) for j in range(5)] for i in range(5)]
    term = [[float(i == j) for j in range(5)] for i in range(5)]
    exponential = [row[:] for row in term]
    for order in range(1, 100):
        term = [[v / order for v in row] for row in multiply(term, small)]
        exponential = [[a + b for a, b in zip(row, add)] for row, add in zip(exponential, term)]
        if max(abs(v) for row in term for v in row) < 1e-16:
            break
    else:
        raise AuditError('Independent ZOH series did not converge')
    for _ in range(squarings):
        exponential = multiply(exponential, exponential)
    full = [*state, pwm, 1.]
    states = []
    for _ in range(config['settings']['horizon']):
        next_state = [sum(row[j] * full[j] for j in range(5)) for row in exponential[:3]]
        states.append(next_state)
        full = [*next_state, pwm, 1.]
    return states


def safe_path(root, relative):
    require(isinstance(relative, str), 'Non-string path')
    path = (root / relative).resolve()
    require(path.is_relative_to(root.resolve()), 'Path escapes evidence directory')
    return path


def audit_episode(root, run, config, split, seed, method, values):
    require(run['split'] == split and run['seed'] == seed and run['method'] == method,
            'Episode identity')
    close(run['parameters'], values, 'Episode parameters', 0.)
    path = safe_path(root, run['trace_path'])
    require(sha(path) == run['trace_sha256'], 'Trace hash: ' + run['id'])
    rows = read_rows(path)
    require(len(rows) == run['n'] == config['steps'], 'Episode length')
    numerical = [{key: value for key, value in row.items() if key not in ('control_s', 'solver_s')}
                 for row in rows]
    digest = hashlib.sha256(json.dumps(numerical, sort_keys=True, allow_nan=False).encode()).hexdigest()
    require(digest == run['numerical_sha256'], 'Numerical hash: ' + run['id'])
    s = config['settings']
    p = parameters(config, split, seed)
    disturbances = scenario(config, split, seed)
    state = [58. + seed % 3, 59. + seed % 3, .5]
    previous = .5
    for index, (row, disturbance) in enumerate(zip(rows, disturbances)):
        prefix = run['id'] + ':' + str(index)
        require(row['step'] == index and row['time_s'] == index * s['dt_s'], prefix + ': step/time')
        close([row['cpu_C'], row['gpu_C'], row['fan']], state, prefix + ': state')
        close(row['previous_pwm'], previous, prefix + ': previous PWM')
        close([row['inlet_C'], row['cpu_W'], row['gpu_W']], disturbance, prefix + ': scenario', 1e-12)
        require(all(row[key] in (0, 1) for key in ('fallback', 'safety_override', 'deadline')), prefix + ': flag')
        require(0. <= row['solver_s'] <= row['control_s'] and row['control_s'] >= 0., prefix + ': timing')
        require(row['deadline'] == int(row['control_s'] >= s['dt_s']), prefix + ': deadline')
        expected_warning = any(state[i] >= s['warnings_C'][i] for i in (0, 1))
        require(row['safety_override'] == int(expected_warning), prefix + ': warning')
        if row['deadline']:
            require(row['fallback'] == 1, prefix + ': deadline fallback')
        require(bool(row['reason']) == bool(row['fallback']), prefix + ': fallback reason')
        require(s['pwm_min'] - 1e-8 <= row['pwm'] <= s['pwm_max'] + 1e-8
                and abs(row['pwm'] - previous) <= s['max_delta'] + 1e-8, prefix + ': PWM constraints')
        if row['fallback'] or expected_warning:
            close(row['pwm'], min(s['pwm_max'], previous + s['max_delta']), prefix + ': protection')
        next_state = plant_step(state, row['pwm'], disturbance[0], disturbance[1:], p, s['dt_s'])
        close([row['next_cpu_C'], row['next_gpu_C'], row['next_fan']], next_state, prefix + ': plant')
        close(row['rpm'], next_state[2] * p['max_rpm'], prefix + ': RPM')
        predicted = prediction(state, row['pwm'], disturbance[0], disturbance[1:], config)
        close([row['pred_cpu_C'], row['pred_gpu_C']], predicted[0][:2], prefix + ': prediction')
        violation = max(0., *(point[i] - s['limits_C'][i] + s['margin_C'] for point in predicted for i in (0, 1)))
        close(row['applied_violation_C'], violation, prefix + ': applied violation')
        if method != 'mpc' or row['fallback']:
            require(row['accepted_slack_max_C'] is None, prefix + ': unaccepted slack')
        else:
            require(row['accepted_slack_max_C'] is not None and row['accepted_slack_max_C'] >= -1e-8,
                    prefix + ': missing accepted slack')
            require(row['solver_status'].lower() == 'solved', prefix + ': solver success')
            require(all(row[key] is not None and 0. <= row[key] <= 1e-5
                        for key in ('primal_residual', 'dual_residual')), prefix + ': solver residual')
        state, previous = next_state, row['pwm']
    require(math.isfinite(run['episode_wall_s']) and run['episode_wall_s'] >= sum(r['control_s'] for r in rows) - 1e-8,
            'Episode wall timing')
    recomputed = metrics(rows, config)
    close(run['metrics'], recomputed, 'Metrics: ' + run['id'])
    return len(rows)


def timestamp(value):
    result = datetime.fromisoformat(value)
    require(result.tzinfo is not None, 'Timestamp lacks timezone')
    return result


def audit(out, check_sources=True):
    out = Path(out)
    freeze = read_json(out / 'freeze.json')
    result = read_json(out / 'result.json')
    calibration = read_json(out / 'calibration.json')
    config = freeze['config']
    require(config['version'] == 2 and set(config['candidates']) == set(METHODS), 'Config version/methods')
    require(all(len(config['candidates'][m]) == 3 for m in METHODS), 'Candidate budget')
    require(all(len(config['seeds'][split]) == len(set(config['seeds'][split])) == 3
                for split in ('calibration', *SPLITS)), 'Seed completeness/duplicates')
    require(len(set(seed for values in config['seeds'].values() for seed in values)) == 15,
            'Split seed overlap')
    require(result['freeze_sha256'] == sha(out / 'freeze.json'), 'Freeze hash')
    require(freeze['calibration_sha256'] == sha(out / 'calibration.json'), 'Calibration hash')
    expected_sources = {'digital_twin/control/enclosure_mpc.py', 'digital_twin/control/enclosure_control_v2.py', 'scripts/run_enclosure_control_v2.py', 'scripts/verify_enclosure_control_v2.py', 'scripts/enclosure_control_v2_requirements.txt', *('openspec/changes/validate-enclosure-four-controllers-20261005/' + n for n in ('config.json', 'protocol.md', 'research.md'))}
    require(set(freeze['sources']) == expected_sources, 'Incomplete source manifest')
    require(freeze['status'] == 'FROZEN_BEFORE_EVALUATION' and freeze['boundary'] == config['boundary'], 'Freeze status/boundary')
    for relative, digest in freeze['sources'].items():
        snapshot = safe_path(out / 'source_snapshots', relative)
        require(sha(snapshot) == digest, 'Source snapshot: ' + relative)
        if check_sources:
            require(sha(safe_path(ROOT, relative)) == digest, 'Current source changed: ' + relative)
    config_paths = [p for p in freeze['sources'] if p.endswith('/config.json')]
    require(len(config_paths) == 1, 'Frozen config source missing/ambiguous')
    close(config, read_json(out / 'source_snapshots' / config_paths[0]), 'Frozen config', 0.)
    cal_attempt = read_json(out / 'calibration_attempt.json')
    eval_attempt = read_json(out / 'evaluation_attempt.json')
    for name, attempt in (('calibration', cal_attempt), ('evaluation', eval_attempt)):
        require(attempt['status'] == 'COMPLETED' and bool(attempt['command']), name + ': attempt status/command')
        require(timestamp(attempt['started_at']) <= timestamp(attempt['finished_at']), name + ': chronology')
    require(timestamp(cal_attempt['started_at']) <= timestamp(freeze['registered_at'])
            <= timestamp(cal_attempt['finished_at']) <= timestamp(eval_attempt['started_at'])
            <= timestamp(result['evaluated_at']) <= timestamp(eval_attempt['finished_at']), 'Freeze/evaluation chronology')
    require(result['boundary'] == config['boundary'], 'Evidence boundary')
    require(result['status'] == 'COMPLETED_EXPLORATORY_ASSUMED_MODEL_SIMULATION', 'Result status')
    require(set(calibration['candidates']) == set(METHODS), 'Calibration methods')
    checked = 0
    selected = {}
    all_paths = set()
    for method in METHODS:
        candidates = calibration['candidates'][method]
        require(len(candidates) == len(config['candidates'][method]), 'Missing candidate')
        for index, candidate in enumerate(candidates):
            close(candidate['parameters'], config['candidates'][method][index], 'Candidate parameters', 0.)
            runs = candidate['runs']
            require(len(runs) == len(config['seeds']['calibration'])
                    and {r['seed'] for r in runs} == set(config['seeds']['calibration']), 'Calibration seed set')
            for run in runs:
                require(run['candidate_index'] == index, 'Candidate index')
                path = safe_path(out, run['trace_path'])
                require(path not in all_paths, 'Reused trace path')
                all_paths.add(path)
                checked += audit_episode(out, run, config, 'calibration', run['seed'], method, candidate['parameters'])
            close(candidate['score'], statistics.mean(r['metrics']['selection_score'] for r in runs), 'Candidate score')
        selected[method] = min(enumerate(candidates), key=lambda item: (item[1]['score'], item[0]))[1]['parameters']
    close(calibration['selected'], selected, 'Calibration selection', 0.)
    close(freeze['selected'], selected, 'Frozen selection', 0.)
    runs = result['runs']
    expected = {(split, seed, method) for split in SPLITS for seed in config['seeds'][split] for method in METHODS}
    require(len(runs) == len(expected) == 48 and {(r['split'], r['seed'], r['method']) for r in runs} == expected,
            'Evaluation episode set')
    require(len({r['id'] for r in runs}) == len(runs), 'Duplicate episode IDs')
    for run in runs:
        require(run['candidate_index'] is None, 'Evaluation contains calibration candidate index')
        path = safe_path(out, run['trace_path'])
        require(path not in all_paths, 'Reused trace path')
        all_paths.add(path)
        checked += audit_episode(out, run, config, run['split'], run['seed'], run['method'], selected[run['method']])
    aggregates = aggregate(runs, config)
    close(result['aggregates'], aggregates, 'Aggregates')
    close(result['decisions'], decisions(runs, aggregates, config), 'Decisions')
    return {'status': 'PASS', 'calibration_episodes': 36, 'evaluation_episodes': 48,
            'rows': checked, 'independent_metrics': 'PASS', 'independent_dynamics': 'PASS',
            'candidate_selection': 'PASS', 'decisions': 'PASS', 'attempt_chronology': 'PASS',
            'source_snapshots': 'PASS', 'current_sources_checked': check_sources,
            'result_sha256': sha(out / 'result.json'), 'scope': config['boundary']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=DEFAULT)
    parser.add_argument('--snapshots-only', action='store_true', help='Audit historical snapshots without requiring current sources')
    args = parser.parse_args()
    print(json.dumps(audit(args.output_dir, check_sources=not args.snapshots_only), indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
