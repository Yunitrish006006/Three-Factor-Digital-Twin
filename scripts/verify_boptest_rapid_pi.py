"""Recalculate the pilot table from recorded transition CSVs."""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pilot', ROOT / 'scripts/run_boptest_rapid_pi.py')
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)


def main():
    path = ROOT / 'openspec/changes/pilot-boptest-rapid-pi/artifacts/result.json'
    r = json.loads(path.read_text())
    assert r['status'] == 'COMPLETED_DEVELOPMENT_ONLY'
    assert r['runner_sha256'] == pilot.sha(pilot.__file__)
    assert r['protocol_sha256'] == pilot.sha(pilot.CHANGE / 'protocol.md')
    assert r['fmu_sha256'] == pilot.sha(pilot.FMU)
    assert len(r['grid']) == 9 and len(r['evaluations']) == 14
    initial = {}
    v2path = path.with_name('result_v2.json')
    v2 = json.loads(v2path.read_text())
    assert v2['status'] == 'COMPLETED_DEVELOPMENT_ONLY'
    assert v2['v1_sha256'] == pilot.sha(path)
    assert v2['protocol_sha256'] == pilot.sha(pilot.CHANGE / 'protocol-v2.md')
    assert v2['runner_sha256'] == pilot.sha(ROOT / 'scripts/run_boptest_rapid_pi_v2.py')
    assert len(v2['evaluations']) == 2
    records = [r['identification']] + r['grid'] + r['evaluations'] + v2['evaluations']
    for rec in records:
        trace = ROOT / rec['trace']
        assert hashlib.sha256(trace.read_bytes()).hexdigest() == rec['sha256']
        with trace.open() as f:
            rows = [{k: float(v) for k, v in row.items()} for row in csv.DictReader(f)]
        for a, b in zip(rows, rows[1:]):
            assert abs(b['time_s'] - a['time_s'] - 60) < 1e-9
            assert abs(a['next_T'] - b['T']) < 1e-9
        assert len(rows) == rec['scored_hours'] * 60
        for key, value in pilot.metrics(rows).items():
            assert abs(value - rec['metrics'][key]) < 1e-9, (trace, key)
        if 'day' in rec:
            expected = initial.setdefault(rec['day'], rows[0]['T'])
            assert abs(expected - rows[0]['T']) < 1e-9, 'warmup state mismatch'
            assert rows[0]['time_s'] > max(f['fit_end_s'] for f in r['fits'].values())
            if rec['controller'] != 'embedded':
                assert all(12 <= row['command'] <= 40 for row in rows)
                assert all(abs(row['fan'] - .5) < 1e-9 for row in rows)
    selected = min(r['grid'], key=lambda item: item['metrics']['mae_C'])
    assert r['selected_grid'] == {k: selected[k] for k in ('kp', 'ti')}
    for e in v2['evaluations']:
        grid = next(item['metrics'] for item in r['evaluations'] if item['day'] == e['day'] and item['controller'] == 'grid_pi')
        m = e['metrics']
        assert e['within_exploratory_grid_margin'] == (m['mae_C'] <= grid['mae_C'] + .05 and m['max_abs_error_C'] <= grid['max_abs_error_C'] + .5)
    assert v2['within_exploratory_grid_margin_both_dates'] == all(e['within_exploratory_grid_margin'] for e in v2['evaluations'])
    print(f'PASS: {len(records)} traces, 16 evaluation episodes, metrics, hashes, bounds, chronological separation and equal warmup room temperature.')


if __name__ == '__main__':
    main()
