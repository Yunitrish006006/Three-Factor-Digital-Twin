"""Adaptive development revision; same dates are reused, not confirmation."""
import json
import math
from pathlib import Path
import run_boptest_rapid_pi as pilot


def main():
    path = pilot.CHANGE / 'artifacts/result_v2.json'
    if path.exists():
        raise SystemExit('V2 evidence exists; preserve it before a separate rerun.')
    v1path = pilot.CHANGE / 'artifacts/result.json'
    v1 = json.loads(v1path.read_text())
    if v1['status'] != 'COMPLETED_DEVELOPMENT_ONLY':
        raise SystemExit('V1 must finish first.')
    fit = v1['fits']['2']
    if fit['status'] != 'FITTED':
        raise SystemExit('No valid 2 h model: v2 is not evaluated.')
    a, b, c, d = fit['coefficients']
    response_s = max(3 * pilot.DT, fit['ti'] / 2)
    kp = fit['ti'] / (b / (a + b) * response_s)
    pilot.OUT = pilot.ROOT / 'outputs/boptest_rapid_pi/v2'
    result = {'status': 'RUNNING', 'scope': 'ADAPTIVE_DEVELOPMENT_REUSED_EVALUATION_DATES',
              'v1_sha256': pilot.sha(v1path), 'protocol_sha256': pilot.sha(pilot.CHANGE / 'protocol-v2.md'),
              'runner_sha256': pilot.sha(__file__), 'base_runner_sha256': pilot.sha(pilot.__file__),
              'calibration_hours': 2, 'response_s': response_s, 'kp': kp, 'ti': fit['ti'],
              'environment_feedforward_used': False,
              'environment_feedforward_reason': 'rank-deficient night calibration; solar not identifiable',
              'evaluations': [], 'failures': []}

    def save():
        path.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')

    save()
    try:
        passes = []
        for day in (3, 180):
            _, rec = pilot.episode(f'day{day}_auto_2h_v2', day * 86400, 24, pilot.PI(kp, fit['ti']))
            grid = next(e['metrics'] for e in v1['evaluations'] if e['day'] == day and e['controller'] == 'grid_pi')
            m = rec['metrics']
            passed = m['mae_C'] <= grid['mae_C'] + .05 and m['max_abs_error_C'] <= grid['max_abs_error_C'] + .5
            passes.append(passed)
            result['evaluations'].append(dict(day=day, controller='auto_2h_v2', calibration_hours=2,
                                              within_exploratory_grid_margin=passed, **rec))
            save()
            print(day, m, flush=True)
        result['within_exploratory_grid_margin_both_dates'] = all(passes)
        result['status'] = 'COMPLETED_DEVELOPMENT_ONLY'
        save()
    except Exception as exc:
        result['status'] = 'FAILED'
        result['failures'].append({'type': type(exc).__name__, 'message': str(exc)})
        save()
        raise


if __name__ == '__main__':
    main()
