"""Separate reference scorer; never feeds truth back into the enclosure session."""
import argparse
import csv
import json
import math
from pathlib import Path


def score(proposals, references):
    truth = {}
    for row in references:
        timestamp,temperature = float(row['time_s']),float(row['source_reference_C'])
        if not math.isfinite(timestamp) or not math.isfinite(temperature) or timestamp<0 or timestamp in truth:
            raise ValueError('Reference timestamps and temperatures must be finite and unique')
        truth[timestamp] = temperature
    estimates,forecasts = [],[]
    seen = set()
    for row in proposals['commands']:
        timestamp = float(row['time_s'])
        if timestamp in seen or not math.isfinite(timestamp):
            raise ValueError('Duplicate/invalid proposal timestamp')
        seen.add(timestamp)
        if timestamp not in truth:
            raise ValueError('Missing co-timed reference temperature')
        estimate = float(row['source_estimate_C'])
        prediction = float(row['source_prediction_next_C'])
        if not math.isfinite(estimate) or not math.isfinite(prediction):
            raise ValueError('Nonfinite prediction')
        estimates.append(estimate-truth[timestamp])
        if timestamp+5. in truth:
            forecasts.append(prediction-truth[timestamp+5.])
    if not estimates:
        raise ValueError('No scored samples')
    def metrics(errors):
        return {'n':len(errors),'mae_C':sum(abs(v) for v in errors)/len(errors),
                'rmse_C':math.sqrt(sum(v*v for v in errors)/len(errors))} if errors else {'n':0,'status':'NOT_EVALUATED'}
    return {'current_estimate':metrics(estimates),'next_sample_forecast':metrics(forecasts),
            'missing_next_reference_count':len(estimates)-len(forecasts),
            'source_reference_used_for_control':False,
            'evidence_class':'supplied_reference_comparison_requires_provenance'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--proposals',type=Path,required=True)
    p.add_argument('--reference',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    with args.reference.open(newline='') as stream:
        references=list(csv.DictReader(stream))
    report=score(json.loads(args.proposals.read_text()),references)
    with args.output.open('x') as stream:
        json.dump(report,stream,indent=2,allow_nan=False)
        stream.write('\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
