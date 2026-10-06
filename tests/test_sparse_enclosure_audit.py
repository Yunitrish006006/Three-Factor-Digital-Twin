import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('sparse_verify', ROOT / 'scripts/verify_sparse_enclosure.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SparseEvidenceAuditTests(unittest.TestCase):
    def test_valid_evidence(self):
        self.assertTrue(module.check_artifacts(module.ARTIFACTS)['passed'])

    def test_metric_and_decision_mutations_rejected(self):
        for mutate in ('metric', 'decision'):
            with tempfile.TemporaryDirectory() as tmp:
                dest = Path(tmp) / 'artifacts'
                shutil.copytree(module.ARTIFACTS, dest)
                path = dest / 'result.json'
                result = json.loads(path.read_text())
                if mutate == 'metric':
                    result['runs'][0]['metrics']['source_mae_C'] += 1.
                else:
                    result['decisions']['H-ENC-31'] = 'not_supported'
                path.write_text(json.dumps(result))
                self.assertFalse(module.check_artifacts(dest)['passed'], mutate)

    def test_frozen_parameter_mutation_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / 'artifacts'
            shutil.copytree(module.ARTIFACTS, dest)
            path = dest / 'calibration.json'
            data = json.loads(path.read_text())
            data['metal_path']['estimated_parameters']['contact'] += .1
            path.write_text(json.dumps(data))
            self.assertFalse(module.check_artifacts(dest)['passed'])
