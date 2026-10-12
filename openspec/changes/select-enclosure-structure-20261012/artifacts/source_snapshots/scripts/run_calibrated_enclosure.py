"""Offline structure-selected session; independent reference scoring remains separate."""
import argparse
import csv
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from digital_twin.enclosure.calibrated_session import CalibratedEnclosureSession,fit_structures
from digital_twin.enclosure.session import Observation


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--commissioning',type=Path,required=True)
    p.add_argument('--method',choices=('pi','rank_h6'),default='rank_h6')
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.output.exists():
        p.error('Refusing to overwrite existing analysis')
    with args.commissioning.open(newline='') as stream:
        model,calibration=fit_structures(list(csv.DictReader(stream)))
    with args.input.open(newline='') as stream:
        observations=[Observation.from_row(row) for row in csv.DictReader(stream)]
    if not observations:
        raise ValueError('Empty observation stream')
    session=CalibratedEnclosureSession(model,observations[0].inlet_C,args.method)
    outputs=[session.process(obs) for obs in observations]
    with args.output.open('x') as stream:
        json.dump({'mode':'offline_command_proposals','hardware_actuation':'NOT_EVALUATED',
                   'source_reference_input':False,'calibration':calibration,'commands':outputs},stream,
                  ensure_ascii=False,indent=2,allow_nan=False)
        stream.write('\n')
    print(f'{len(outputs)} offline proposals; selected {calibration["selected_structure"]}; no hardware actuation')


if __name__=='__main__':
    main()
