"""Added scorer audit. Never overwrite frozen evidence or feed truth to control."""
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

from sparse_enclosure_corrections import ORIGINAL, ARTIFACTS, REFERENCE_COMMIT, sha
from verify_sparse_enclosure import check_artifacts

NUMERICAL_TOLERANCE_C = .01


def load_rows(path):
    with Path(path).open() as stream:
        return [{key: float(value) for key, value in row.items()} for row in csv.DictReader(stream)]


def check_trace(rows, run, config):
    """Independent equations/integration, using only logged commands as actions."""
    errors = []
    maxima = {'source_C': 0., 'observed_temperature_C': 0., 'fan': 0.}
    def require(ok, label):
        if not ok:
            errors.append(label)
    dt = config['settings']['dt']
    require(len(rows) == config['evaluation_steps'], 'trace length')
    require(all(math.isfinite(v) for row in rows for v in row.values()), 'finite trace')
    require(all(row['step'] == k and math.isclose(row['time_s'], k * dt, abs_tol=1e-9, rel_tol=0.)
                for k, row in enumerate(rows)), 'timestamp/step alignment')
    require(all(math.isclose(rows[k]['source_truth_next'], rows[k+1]['source_truth_current'],
                             abs_tol=1e-10, rel_tol=0.) for k in range(len(rows)-1)), 'source truth continuity')
    if errors:
        return errors, maxima
    rng = np.random.default_rng(run['seed'])
    powers = np.repeat(rng.uniform(.8, 3.2, size=6), 30)
    phase = rng.uniform(0., 2 * np.pi)
    inlets = 22 + .3 * np.sin(2 * np.pi * np.arange(180) / 180 + phase)
    noise = rng.normal(size=(180, 3)) * [.1, .1, .005]
    state = inlets[0] + np.array([1.5, .5, .2])
    fan = .4
    require(math.isclose(rows[0]['source_truth_current'], state[0], abs_tol=1e-10, rel_tol=0.), 'initial source truth')
    require(math.isclose(rows[0]['previous_pwm'], .4, abs_tol=1e-10, rel_tol=0.), 'initial PWM')
    p = config['rigs'][run['rig']]
    c = np.array(p['capacities'])
    for k, row in enumerate(rows):
        label = f'step {k}'
        require(math.isclose(row['declared_power'], powers[k], abs_tol=1e-10, rel_tol=0.), label + ' declared power provenance')
        require(math.isclose(row['inlet'], inlets[k], abs_tol=1e-10, rel_tol=0.), label + ' inlet provenance')
        observed = state[1:] + noise[k, :2]
        temp_difference = np.max(np.abs(observed - [row['plate_observed'], row['air_observed']]))
        maxima['observed_temperature_C'] = max(maxima['observed_temperature_C'], float(temp_difference))
        require(temp_difference <= NUMERICAL_TOLERANCE_C, label + ' observed temperature/noise provenance')
        expected_fan_observation = np.clip(fan + noise[k, 2], 0., 1.)
        require(math.isclose(row['fan_observed'], expected_fan_observation, abs_tol=1e-10, rel_tol=0.), label + ' fan observation provenance')
        difference = abs(row['source_truth_current'] - state[0])
        maxima['source_C'] = max(maxima['source_C'], float(difference))
        require(difference <= NUMERICAL_TOLERANCE_C, label + ' current source dynamics')
        u, inlet = row['pwm'], inlets[k]
        power = powers[k] + config['extra_unobserved_heat_W']
        fan_start = fan
        def rhs(t, x):
            f = u + (fan_start - u) * np.exp(-t / p['fan_tau'])
            sp = p['contact'] * (x[0] - x[1])
            pa = (p['plate_base'] + p['plate_fan'] * f) * (x[1] - x[2])
            out = (p['air_base'] + p['air_fan'] * f) * (x[2] - inlet)
            bypass = p['bypass'] * (x[0] - inlet)
            return np.array([power - sp - bypass, sp - pa, pa - out]) / c
        solved = solve_ivp(rhs, (0., dt), state, rtol=1e-10, atol=1e-11)
        require(solved.success, label + ' reference integration')
        state = solved.y[:, -1]
        fan = u + (fan_start - u) * np.exp(-dt / p['fan_tau'])
        difference = abs(row['source_truth_next'] - state[0])
        maxima['source_C'] = max(maxima['source_C'], float(difference))
        require(difference <= NUMERICAL_TOLERANCE_C, label + ' next source dynamics')
        difference = abs(row['fan_truth_next'] - fan)
        maxima['fan'] = max(maxima['fan'], float(difference))
        require(difference <= 1e-10, label + ' fan endpoint dynamics')
    return errors, maxima


def check_integrity(directory=ORIGINAL):
    directory = Path(directory)
    errors, maxima = [], {'source_C': 0., 'observed_temperature_C': 0., 'fan': 0.}
    count = steps = 0
    try:
        legacy = check_artifacts(directory)
        errors.extend(legacy['errors'])
        manifest = json.loads((ARTIFACTS / 'reference_trace_manifest.json').read_text())
        if manifest['reference_commit'] != REFERENCE_COMMIT:
            errors.append('historical reference commit mismatch')
        for relative, digest in manifest['sha256'].items():
            if sha(directory / relative) != digest:
                errors.append('historical byte identity: ' + relative)
        result = json.loads((directory / 'result.json').read_text())
        config = json.loads((directory / 'config.json').read_text())
        for run in result['runs']:
            rows = load_rows(directory / run['csv'])
            found, differences = check_trace(rows, run, config)
            errors.extend(f"{run['csv']}: {error}" for error in found)
            for key, value in differences.items():
                maxima[key] = max(maxima[key], value)
            count += 1
            steps += len(rows)
    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        errors.append(f'malformed or missing evidence: {type(exc).__name__}: {exc}')
    return {'passed': not errors, 'errors': errors, 'verified_runs': count, 'verified_steps': steps,
            'reference_commit': REFERENCE_COMMIT, 'numerical_tolerance_C': NUMERICAL_TOLERANCE_C,
            'maximum_reference_difference': maxima,
            'scope': 'Retrospective scorer integrity, not a new holdout evaluation or controller truth input.'}


if __name__ == '__main__':
    report = check_integrity()
    ARTIFACTS.mkdir(exist_ok=True)
    (ARTIFACTS / 'scorer_integrity.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    sys.exit(0 if report['passed'] else 1)
