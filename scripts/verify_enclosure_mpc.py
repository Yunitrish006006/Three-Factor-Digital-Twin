#!/usr/bin/env python3
"""Read-only independent audit of frozen enclosure control evidence."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT/'openspec/changes/implement-enclosure-mpc-20261005/artifacts'
INT_FIELDS={'step','fallback','safety_override'}
TEXT_FIELDS={'reason','solver_status'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path):
    with path.open(newline='') as stream:
        return [{k: (v if k in TEXT_FIELDS else int(v) if k in INT_FIELDS
                     else None if v=='' else float(v)) for k,v in row.items()}
                for row in csv.DictReader(stream)]


def audit(out):
    f=json.loads((out/'freeze.json').read_text())
    result=json.loads((out/'result.json').read_text())
    assert result['freeze_sha256']==sha(out/'freeze.json'), 'Freeze tampered'
    assert f['calibration_sha256']==sha(out/'calibration.json'), 'Calibration tampered'
    assert all(sha(ROOT/p)==h for p,h in f['sources'].items()), 'Frozen source changed'
    assert f['registered_at']<result['evaluated_at'], 'Chronology invalid'
    expected={(split,seed,method) for split in ('validation','holdout','mismatch','overload')
              for seed in f['seeds'][split] for method in ('fixed','pid','mpc')}
    assert {(r['split'],r['seed'],r['method']) for r in result['runs']}==expected
    assert len(result['runs'])==len(expected)==36
    setting=f['settings']; dt=setting['dt_s']
    comparisons={}; checked=0
    for run in result['runs']:
        path=out/run['trace_path']
        assert sha(path)==run['trace_sha256'], run['id']+' trace hash'
        rows=read_rows(path)
        assert len(rows)==run['n']==f['steps']
        numerical=[{k:v for k,v in row.items() if k!='solve_s'} for row in rows]
        assert hashlib.sha256(json.dumps(numerical,sort_keys=True,allow_nan=False).encode()).hexdigest()==run['numerical_sha256']
        err=[]; pred_err=[]; over=0; energy=0.; tv=0.; bounds=0; slew=0
        parity=[]
        for index,row in enumerate(rows):
            assert row['step']==index and row['time_s']==index*dt
            assert all(math.isfinite(v) for k,v in row.items() if isinstance(v,(int,float)))
            assert abs(row['rpm']-6000*row['next_fan'])<1e-8
            if index:
                prev=rows[index-1]
                assert row['previous_pwm']==prev['pwm']
                assert row['cpu_C']==prev['next_cpu_C'] and row['gpu_C']==prev['next_gpu_C']
                assert row['fan']==prev['next_fan']
            else:
                assert row['previous_pwm']==.5 and row['fan']==.5
            e=[row['next_cpu_C']-60.,row['next_gpu_C']-60.]
            err.append(e)
            pred_err.extend([row['pred_cpu_C']-row['next_cpu_C'],row['pred_gpu_C']-row['next_gpu_C']])
            over+=int(row['next_cpu_C']>80. or row['next_gpu_C']>85.)
            energy+=10*row['pwm']**3*dt/3600
            tv+=abs(row['pwm']-row['previous_pwm'])
            bounds+=int(row['pwm']<.2-1e-8 or row['pwm']>1+1e-8)
            slew+=int(abs(row['pwm']-row['previous_pwm'])>.1+1e-8)
            assert bounds==0 and slew==0
            if row['fallback'] or row['safety_override']:
                assert abs(row['pwm']-min(1.,row['previous_pwm']+.1))<1e-8
            parity.append((row['inlet_C'],row['cpu_W'],row['gpu_W']))
        key=(run['split'],run['seed'])
        if key in comparisons:
            assert comparisons[key]==parity, 'Comparator disturbances differ'
        comparisons[key]=parity
        flat=[v for e in err for v in e]
        independent={'tracking_mae_C':statistics.mean(abs(v) for v in flat),
                     'tracking_rmse_C':math.sqrt(statistics.mean(v*v for v in flat)),
                     'cpu_mae_C':statistics.mean(abs(e[0]) for e in err),
                     'gpu_mae_C':statistics.mean(abs(e[1]) for e in err),
                     'prediction_mae_C':statistics.mean(abs(v) for v in pred_err),
                     'prediction_rmse_C':math.sqrt(statistics.mean(v*v for v in pred_err)),
                     'max_cpu_C':max(row['next_cpu_C'] for row in rows),
                     'max_gpu_C':max(row['next_gpu_C'] for row in rows),
                     'overtemp_s':over*dt,'fan_energy_proxy_Wh':energy,
                     'pwm_total_variation':tv,'bounds_violations':bounds,'slew_violations':slew,
                     'fallback_n':sum(row['fallback'] for row in rows),
                     'safety_override_n':sum(row['safety_override'] for row in rows)}
        for metric,value in independent.items():
            assert math.isclose(value,run['metrics'][metric],rel_tol=1e-9,abs_tol=1e-9), (run['id'],metric)
        assert run['metrics']['whole_system_energy_Wh'] is None and run['metrics']['throttling'] is None
        checked+=len(rows)
    for split, methods in result['aggregates'].items():
        for method, aggregated in methods.items():
            subset=[r['metrics'] for r in result['runs'] if r['split']==split and r['method']==method]
            for key,value in aggregated.items():
                assert math.isclose(value,statistics.mean(m[key] for m in subset),rel_tol=1e-9,abs_tol=1e-9)
    nominal=[r for r in result['runs'] if r['method']=='mpc' and r['split'] in ('validation','holdout')]
    feasible=all(r['metrics']['solve_p95_s']<dt and r['metrics']['fallback_n']/r['n']<=.05 for r in nominal)
    assert result['decisions']['H-MPC-01']==('SUPPORTED_SIMULATION_ONLY' if feasible else 'NOT_SUPPORTED')
    assert result['decisions']['E8']==result['decisions']['physical_enclosure']=='NOT_EVALUATED'
    return {'status':'PASS','runs':len(expected),'rows':checked,
            'source_freeze_trace_hashes':'PASS','independent_metrics':'PASS',
            'baseline_disturbance_parity':'PASS','commands_and_fallback':'PASS',
            'result_sha256':sha(out/'result.json'), 'scope':'ASSUMED_MODEL_ONLY'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir',type=Path,default=DEFAULT)
    p.add_argument('--report',type=Path,help='Optional location to save verification report')
    args=p.parse_args()
    report=audit(args.output_dir)
    if args.report:
        args.report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
