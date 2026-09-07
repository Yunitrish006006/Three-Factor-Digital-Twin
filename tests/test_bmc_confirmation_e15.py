import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/run_bmc_confirmation_e15.py"
SPEC = importlib.util.spec_from_file_location("run_bmc_confirmation_e15", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class BmcConfirmationE15Tests(unittest.TestCase):
    def test_frozen_ridge_prediction_standardizes_features(self):
        row = {"a": 12.0, "b": 16.0}
        model = {
            "feature_names": ["a", "b"],
            "means": [10.0, 10.0],
            "scales": [2.0, 3.0],
            "coefficients": [5.0, 2.0, -1.0],
        }
        self.assertAlmostEqual(MODULE.predict_ridge(row, model), 5.0)

    def test_metrics_report_mae_rmse_and_interpolated_p95(self):
        observed = MODULE.metrics([0.0, 2.0], [1.0, 4.0])
        self.assertEqual(observed["count"], 2)
        self.assertAlmostEqual(observed["mae_c"], 1.5)
        self.assertAlmostEqual(observed["rmse_c"], (2.5) ** 0.5)
        self.assertAlmostEqual(observed["p95_c"], 1.95)


if __name__ == "__main__":
    unittest.main()
