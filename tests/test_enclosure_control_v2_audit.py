"""Adversarial evidence checks using isolated copies of completed evidence."""
import copy
import csv
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('control_v2_audit',ROOT/'scripts/verify_enclosure_control_v2.py')
audit_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit_module)
RUNNER=ROOT/'scripts/run_enclosure_control_v2.py'
DEFAULT=audit_module.DEFAULT


def write(path,value):path.write_text(json.dumps(value,allow_nan=False))


class ControlAuditTests(unittest.TestCase):
    def setUp(self):
        if not (DEFAULT/'result.json').exists():self.skipTest('Registered evidence not generated')
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.out=Path(self.temp.name)/'evidence';shutil.copytree(DEFAULT,self.out)
        self.result=audit_module.read_json(self.out/'result.json')
        self.config=audit_module.read_json(self.out/'freeze.json')['config']

    def test_rejects_timing_and_claim_manipulation(self):
        # Episode metrics must be recomputed rather than trusting matching JSON aggregates.
        run=self.result['runs'][0]
        bad=copy.deepcopy(run);bad['metrics']['control_p95_s']=1000.
        with self.assertRaises(audit_module.AuditError):
            audit_module.audit_episode(self.out,bad,self.config,bad['split'],bad['seed'],bad['method'],bad['parameters'])
        self.result['decisions']['H-CTRL-02']='ARBITRARY_UNCHECKED_CLAIM';write(self.out/'result.json',self.result)
        with patch.object(audit_module,'audit_episode',return_value=self.config['steps']):
            with self.assertRaisesRegex(audit_module.AuditError,'Decisions'):audit_module.audit(self.out)

    def test_rejects_missing_candidate_and_duplicate_evaluation(self):
        cal=audit_module.read_json(self.out/'calibration.json');cal['candidates']['pid'].pop();write(self.out/'calibration.json',cal)
        freeze=audit_module.read_json(self.out/'freeze.json');freeze['calibration_sha256']=audit_module.sha(self.out/'calibration.json');write(self.out/'freeze.json',freeze)
        self.result['freeze_sha256']=audit_module.sha(self.out/'freeze.json');write(self.out/'result.json',self.result)
        with patch.object(audit_module,'audit_episode',return_value=self.config['steps']):
            with self.assertRaisesRegex(audit_module.AuditError,'Missing candidate'):audit_module.audit(self.out)
        # Restore calibration/freeze, then independently reject duplicate formal identity.
        for name in ('calibration.json','freeze.json'):shutil.copy2(DEFAULT/name,self.out/name)
        self.result=audit_module.read_json(DEFAULT/'result.json');self.result['runs'][1]=copy.deepcopy(self.result['runs'][0]);write(self.out/'result.json',self.result)
        with patch.object(audit_module,'audit_episode',return_value=self.config['steps']):
            with self.assertRaisesRegex(audit_module.AuditError,'Evaluation episode set'):audit_module.audit(self.out)

    def test_rejects_changed_plant_and_disturbance_despite_updated_hash(self):
        run=copy.deepcopy(self.result['runs'][0]);path=self.out/run['trace_path'];rows=audit_module.read_rows(path)
        for field in ('next_cpu_C','inlet_C','safety_override'):
            changed=copy.deepcopy(rows);changed[0][field]+=1
            with path.open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=list(changed[0]));writer.writeheader();writer.writerows(changed)
            run['trace_sha256']=audit_module.sha(path)
            import hashlib
            run['numerical_sha256']=hashlib.sha256(json.dumps([{k:v for k,v in r.items() if k not in ('control_s','solver_s')} for r in changed],sort_keys=True,allow_nan=False).encode()).hexdigest()
            with self.assertRaises(audit_module.AuditError):
                audit_module.audit_episode(self.out,run,self.config,run['split'],run['seed'],run['method'],run['parameters'])

    def test_rejects_failed_attempt_and_incomplete_manifest(self):
        marker=audit_module.read_json(self.out/'evaluation_attempt.json');marker['status']='FAILED';write(self.out/'evaluation_attempt.json',marker)
        with self.assertRaisesRegex(audit_module.AuditError,'attempt status'):audit_module.audit(self.out)
        shutil.copy2(DEFAULT/'evaluation_attempt.json',self.out/'evaluation_attempt.json')
        freeze=audit_module.read_json(self.out/'freeze.json');freeze['sources'].pop('scripts/verify_enclosure_control_v2.py');write(self.out/'freeze.json',freeze)
        self.result['freeze_sha256']=audit_module.sha(self.out/'freeze.json');write(self.out/'result.json',self.result)
        with self.assertRaisesRegex(audit_module.AuditError,'Incomplete source manifest'):audit_module.audit(self.out)

    def test_attempt_is_consumed_after_failure_and_trace_preserved(self):
        spec=importlib.util.spec_from_file_location('control_v2_runner',RUNNER)
        runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
        out=Path(self.temp.name)/'failed_attempt'
        def failed(directory):
            (directory/'preserved.csv').write_text('failure evidence\n');raise RuntimeError('injected')
        with patch.object(runner,'calibrate',side_effect=failed):
            with self.assertRaisesRegex(RuntimeError,'injected'):runner.run_phase(out,'calibrate')
            with self.assertRaises(FileExistsError):runner.run_phase(out,'calibrate')
        self.assertEqual((out/'preserved.csv').read_text(),'failure evidence\n')
        self.assertEqual(json.loads((out/'calibration_attempt.json').read_text())['status'],'FAILED')

    def test_explicit_gate_is_not_assert(self):
        with self.assertRaises(audit_module.AuditError):audit_module.require(False,'injected')
        self.assertNotIn('assert ',(ROOT/'scripts/verify_enclosure_control_v2.py').read_text())


if __name__=='__main__':unittest.main()
