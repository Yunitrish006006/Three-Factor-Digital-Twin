"""Replay declared inputs only to audit source-blind estimation and control logs."""
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
from digital_twin.control.sparse_enclosure import HeatNetwork, SparseObserver, TransferController
from verify_sparse_enclosure import ARTIFACTS, check_artifacts


def audit(directory=ARTIFACTS):
    directory = Path(directory)
    verification = check_artifacts(directory)
    result = json.loads((directory / 'result.json').read_text())
    calibrated = json.loads((directory / 'calibration.json').read_text())
    errors = list(verification['errors'])
    for run in result['runs']:
        with (directory / run['csv']).open() as f:
            rows = [{k:float(v) for k,v in r.items()} for r in csv.DictReader(f)]
        values = dict(calibrated[run['rig']]['estimated_parameters'])
        values['capacities'] = tuple(values['capacities'])
        model = HeatNetwork() if run['method'] == 'nominal_physics' else HeatNetwork(**values)
        corrected = run['method'] not in ('nominal_physics', 'calibrated_physics', 'rank_h6_no_correction')
        observer = SparseObserver(model, rows[0]['inlet'], correction=corrected)
        controller = TransferController(run['method'], model) if run['task'] == 'closed_loop' else None
        previous = .4
        for row in rows:
            # No *_truth column is read by estimation, prediction or selection.
            estimate = observer.update([row['plate_observed'], row['air_observed'], row['fan_observed']])
            u = (controller.step(estimate, row['inlet'], row['declared_power'], previous)[0]
                 if controller else (.4 if (int(row['step']) // 25) % 2 == 0 else .8))
            prediction = observer.predict(u, row['inlet'], row['declared_power'])
            if not np.allclose([estimate[0], prediction[0], u],
                               [row['source_estimate'], row['source_prediction_next'], row['pwm']],
                               rtol=1e-10, atol=1e-10):
                errors.append(f"source-blind replay mismatch: {run['csv']} step {row['step']}")
                break
            previous = u
    return {**verification, 'passed': not errors, 'errors': errors,
            'input_only_replayed_runs': len(result['runs'])}


if __name__ == '__main__':
    data = audit()
    (ARTIFACTS / 'input_replay_audit.json').write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps(data, indent=2))
    sys.exit(0 if data['passed'] else 1)
