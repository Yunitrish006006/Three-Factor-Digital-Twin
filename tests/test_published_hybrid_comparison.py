import tempfile
import unittest
from pathlib import Path

from digital_twin.evaluation.published_hybrid_comparison import (
    _metric_summary,
    _standardize_split,
    run_oh2024_inspired_comparison,
)
from tests.test_public_dataset_benchmark import PublicDatasetBenchmarkTests


class PublishedHybridComparisonTests(unittest.TestCase):
    def test_standardization_uses_training_statistics(self) -> None:
        train, test = _standardize_split([[1.0], [3.0]], [[5.0]])

        self.assertEqual(train, [[-1.0], [1.0]])
        self.assertEqual(test, [[3.0]])

    def test_metric_summary_contains_paper_aligned_metrics(self) -> None:
        metrics = _metric_summary([20.0, 22.0], [20.0, 23.0])

        self.assertEqual(set(metrics), {"mae", "rmse", "correlation", "r2", "cvrmse_pct"})
        self.assertAlmostEqual(metrics["mae"], 0.5)
        self.assertTrue(metrics["cvrmse_pct"] > 0.0)

    def test_focused_transfer_uses_common_split_and_five_comparators(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            dataset_dir = Path(tmp_dir) / "sml2010"
            dataset_dir.mkdir(parents=True, exist_ok=True)
            PublicDatasetBenchmarkTests()._write_sml2010_normalized_fixture(dataset_dir)

            summary = run_oh2024_inspired_comparison(
                input_dir=dataset_dir,
                horizons=[1],
                checkpoint_path=Path(tmp_dir) / "missing_checkpoint.json",
            )

            self.assertEqual(summary["status"], "PARTIAL")
            self.assertEqual(summary["decisions"]["H-PHB-01"], "not_evaluated")
            self.assertEqual(len(summary["cases"]), 2)
            for case in summary["cases"]:
                self.assertEqual(case["status"], "ok")
                self.assertEqual(
                    set(case["metrics"]),
                    {
                        "persistence",
                        "direct_linear_regression",
                        "raw_physics_prior",
                        "hybrid_digital_twin_readout",
                        "oh2024_inspired_additive_residual",
                    },
                )
                self.assertEqual(
                    case["train_samples"] + case["test_samples"],
                    case["sample_count"],
                )

    def test_missing_exact_horizon_is_visible(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            dataset_dir = Path(tmp_dir) / "sml2010"
            dataset_dir.mkdir(parents=True, exist_ok=True)
            PublicDatasetBenchmarkTests()._write_sml2010_normalized_fixture(dataset_dir)

            summary = run_oh2024_inspired_comparison(
                input_dir=dataset_dir,
                horizons=[999],
                checkpoint_path=Path(tmp_dir) / "missing_checkpoint.json",
            )

            self.assertEqual(summary["status"], "NOT_EVALUATED")
            self.assertTrue(all(case["status"] == "insufficient_samples" for case in summary["cases"]))


if __name__ == "__main__":
    unittest.main()
