"""Offline measured-CSV analysis only; outputs PWM proposals, never actuates hardware."""
import argparse
import csv
from dataclasses import asdict
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from digital_twin.enclosure.session import EnclosureSession, Observation, METHODS, fit_observations, HeatNetwork


def process_csv(path, parameters, method):
    with Path(path).open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError('Empty observation CSV')
    # Validate entire stream before committing any output file.
    observations = [Observation.from_row(row) for row in rows]
    session = EnclosureSession(parameters, observations[0].inlet_C, method)
    return [session.process(obs) for obs in observations]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--method', choices=METHODS, default='rank_h6')
    parser.add_argument('--model-json', type=Path)
    parser.add_argument('--calibration-csv', type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Refusing to overwrite an existing analysis')
    if args.model_json and args.calibration_csv:
        parser.error('Choose explicit model or calibration data, not both')
    parameters, calibration = HeatNetwork(), None
    if args.model_json:
        parameters = HeatNetwork(**json.loads(args.model_json.read_text()))
    if args.calibration_csv:
        with args.calibration_csv.open(newline='') as stream:
            parameters, calibration = fit_observations(list(csv.DictReader(stream)))
    proposals = process_csv(args.input, parameters, args.method)
    report = {'mode': 'offline_command_proposals', 'hardware_actuation': 'NOT_EVALUATED',
              'reference_truth_input': False, 'method': args.method,
              'model_parameters': asdict(parameters), 'calibration': calibration, 'commands': proposals}
    with args.output.open('x') as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write('\n')
    print(f'{len(proposals)} offline command proposals saved; no hardware actuation')


if __name__ == '__main__':
    main()
