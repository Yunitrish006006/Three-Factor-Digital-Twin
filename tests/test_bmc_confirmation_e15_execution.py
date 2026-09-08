import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/execute_bmc_confirmation_e15.py"
SPEC = importlib.util.spec_from_file_location("execute_e15", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class E15ExecutionTests(unittest.TestCase):
    def fixture(self, root):
        for name in (
            "scripts/run_bmc_confirmation_e15.py",
            "digital_twin/enclosure/bmc_virtual_sensor.py",
            "outputs/data/enclosure/bmc_confirmation_e15_manifest.json",
            "outputs/data/enclosure/bmc_corrected_e14c_frozen_model.json",
        ):
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{}")
        return root / "outputs/data/enclosure"

    def test_failed_evaluation_is_recorded_and_cannot_be_retried(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = self.fixture(root)
            with patch.object(MODULE.subprocess, "run", return_value=subprocess.CompletedProcess([], 1)) as run:
                self.assertEqual(MODULE.execute(root), 1)
                with self.assertRaises(SystemExit):
                    MODULE.execute(root)
                self.assertEqual(run.call_count, 1)
            receipt = json.loads((data / "bmc_confirmation_e15_attempt.json").read_text())
            self.assertEqual(receipt["status"], "execution_failed")
            self.assertEqual(len(receipt["input_sha256"]), 4)
            self.assertNotIn("result_sha256", receipt)

    def test_success_requires_a_result(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = self.fixture(root)
            with patch.object(MODULE.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)):
                self.assertEqual(MODULE.execute(root), 1)
            receipt = json.loads((data / "bmc_confirmation_e15_attempt.json").read_text())
            self.assertEqual(receipt["status"], "execution_failed")

    def test_success_records_result_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = self.fixture(root)
            result = data / "bmc_confirmation_e15_result.json"
            def finish(*args, **kwargs):
                result.write_text('{"hypothesis_decision":"h_enc_08_not_supported"}')
                return subprocess.CompletedProcess([], 0)
            with patch.object(MODULE.subprocess, "run", side_effect=finish):
                self.assertEqual(MODULE.execute(root), 0)
            receipt = json.loads((data / "bmc_confirmation_e15_attempt.json").read_text())
            self.assertEqual(receipt["status"], "completed")
            self.assertEqual(receipt["result_sha256"], MODULE.sha256(result))
