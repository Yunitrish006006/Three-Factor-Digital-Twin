"""Corrected controller regression on opened inputs; not a new closed-loop study."""
import csv
import json
import sys

from sparse_enclosure_corrections import ROOT, ORIGINAL, ARTIFACTS
sys.path.insert(0, str(ROOT))
import numpy as np
from digital_twin.control.sparse_enclosure import HeatNetwork, SparseObserver
from digital_twin.control.sparse_enclosure_v2 import TransferController


def replay():
    result = json.loads((ORIGINAL / 'result.json').read_text())
    calibrated = json.loads((ORIGINAL / 'calibration.json').read_text())
    differences = []
    steps = runs = 0
    max_prediction_difference = 0.
    for run in result['runs']:
        if run['task'] != 'closed_loop':
            continue
        with (ORIGINAL / run['csv']).open() as stream:
            rows = [{k:float(v) for k,v in row.items()} for row in csv.DictReader(stream)]
        values = dict(calibrated[run['rig']]['estimated_parameters'])
        values['capacities'] = tuple(values['capacities'])
        p = HeatNetwork(**values)
        observer = SparseObserver(p, rows[0]['inlet'], correction=run['method'] != 'rank_h6_no_correction')
        controller = TransferController(run['method'], p)
        for row in rows:
            raw = [row['plate_observed'], row['air_observed']]
            x = observer.update([*raw, row['fan_observed']])
            u, info = controller.step(x, row['inlet'], row['declared_power'], row['previous_pwm'], observed_plate_air=raw)
            prediction = observer.predict(row['pwm'], row['inlet'], row['declared_power'])
            max_prediction_difference = max(max_prediction_difference, abs(prediction[0] - row['source_prediction_next']))
            if not np.isclose(u, row['pwm'], atol=1e-10, rtol=0) or int(info['warning']) != row['warning']:
                differences.append({'csv':run['csv'], 'step':row['step'], 'old_pwm':row['pwm'],
                                    'new_pwm':u, 'old_warning':row['warning'], 'new_warning':info['warning']})
            steps += 1
        runs += 1
    return {'controller_version':TransferController.version, 'runs':runs, 'steps':steps,
            'command_or_warning_differences':differences,
            'maximum_prediction_difference':max_prediction_difference,
            'scope':'Input-only regression under archived actions. Any changed action needs a separate future closed-loop protocol; no opened input relabeled unseen.'}


if __name__ == '__main__':
    report = replay()
    (ARTIFACTS / 'v2_input_replay.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k:v for k,v in report.items() if k != 'command_or_warning_differences'}))
    print('changed command/warning steps:', len(report['command_or_warning_differences']))
