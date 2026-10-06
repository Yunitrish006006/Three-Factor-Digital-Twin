#!/usr/bin/env python3
"""Additional calibration selection, repeatability and claim audit."""
import hashlib
import json
import math
from pathlib import Path

from run_enclosure_mpc import CHANGE, episode, metrics, sha
from verify_enclosure_mpc import read_rows, audit


def main():
    out=CHANGE/'artifacts'
    verification=audit(out)
    freeze=json.loads((out/'freeze.json').read_text())
    calibration=json.loads((out/'calibration.json').read_text())
    checked=0
    for method,candidates in calibration.items():
        for i,candidate in enumerate(candidates):
            scores=[]
            for run in candidate['runs']:
                path=out/f'calibration_candidates/{method}_{i}'/run['trace_path']
                assert sha(path)==run['trace_sha256']
                actual=metrics(read_rows(path))
                for key,value in actual.items():
                    expected=run['metrics'][key]
                    assert value==expected if value is None else math.isclose(value,expected,abs_tol=1e-9,rel_tol=1e-9)
                scores.append(actual['selection_score']);checked+=1
            assert math.isclose(sum(scores)/len(scores),candidate['score'],rel_tol=1e-9)
        selected=min(enumerate(candidates),key=lambda pair:(pair[1]['score'],pair[0]))[1]
        assert selected['parameters']==freeze['selected'][method]
    result=json.loads((out/'result.json').read_text())
    holdout=result['aggregates']['holdout']
    gain=1-holdout['mpc']['tracking_mae_C']/holdout['pid']['tracking_mae_C']
    paired=all(next(r for r in result['runs'] if r['method']=='mpc' and r['split']=='holdout' and r['seed']==seed)['metrics']['overtemp_s']
               <=next(r for r in result['runs'] if r['method']=='pid' and r['split']=='holdout' and r['seed']==seed)['metrics']['overtemp_s']
               for seed in freeze['seeds']['holdout'])
    assert result['decisions']['H-MPC-02']==('SUPPORTED_SIMULATION_ONLY' if gain>=.05 and paired else 'NOT_SUPPORTED')
    repeated=[]
    # Determinism check on the same synthetic fixture is not new held-out evidence.
    for split,seed in [('holdout',31),('overload',41)]:
        rows=episode('mpc',freeze['selected']['mpc'],split,seed)
        numerical=[{k:v for k,v in row.items() if k!='solve_s'} for row in rows]
        digest=hashlib.sha256(json.dumps(numerical,sort_keys=True,allow_nan=False).encode()).hexdigest()
        original=next(r for r in result['runs'] if r['method']=='mpc' and r['split']==split and r['seed']==seed)
        assert digest==original['numerical_sha256'], (split,'repeat mismatch')
        repeated.append({'split':split,'seed':seed,'numerical_sha256':digest})
    verification.update(calibration_candidate_episodes=checked,
                        selection_recalculated='PASS',hypothesis_02_recalculated='PASS',
                        repeatability_checks=repeated,
                        repeatability_scope='same synthetic fixtures; no new independent evidence')
    (out/'closure_audit.json').write_text(json.dumps(verification,indent=2)+'\n')
    print(json.dumps(verification,indent=2))


if __name__=='__main__':main()
