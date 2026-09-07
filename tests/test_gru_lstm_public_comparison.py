import math
import tempfile
import unittest
from pathlib import Path

from digital_twin.evaluation.gru_lstm_public_comparison import (
    GatedComparisonConfig,
    SimpleGRU,
    SimpleLSTM,
    _gru_parameter_count,
    _lstm_parameter_count,
    run_gru_lstm_public_comparison,
)
from tests.test_public_dataset_benchmark import PublicDatasetBenchmarkTests


class GRULSTMPublicComparisonTests(unittest.TestCase):
    def test_gru_and_lstm_are_deterministic_and_finite(self) -> None:
        config = GatedComparisonConfig(
            sequence_length=3,
            gru_hidden_units=3,
            lstm_hidden_units=2,
            epochs=3,
            batch_size=2,
            seed=7,
        )
        sequences = [
            [[float(index + step), float(index - step)] for step in range(3)]
            for index in range(8)
        ]
        targets = [[float(index + 3)] for index in range(8)]
        for model_type, hidden in ((SimpleGRU, 3), (SimpleLSTM, 2)):
            first = model_type(2, 1, hidden, config)
            second = model_type(2, 1, hidden, config)
            first_training = first.fit(sequences, targets)
            second_training = second.fit(sequences, targets)
            self.assertEqual(
                first_training["final_standardized_mse"],
                second_training["final_standardized_mse"],
            )
            self.assertEqual(first.predict(sequences[-1]), second.predict(sequences[-1]))
            self.assertTrue(first_training["all_epoch_losses_finite"])
            self.assertTrue(all(math.isfinite(value) for value in first.predict(sequences[-1])))

    def test_registered_parameter_counts_are_within_budget(self) -> None:
        vanilla = 148
        gru = _gru_parameter_count(13, 3, 4)
        lstm = _lstm_parameter_count(13, 2, 4)
        self.assertEqual(gru, 169)
        self.assertEqual(lstm, 140)
        self.assertLessEqual(abs(gru - vanilla) / vanilla, 0.15)
        self.assertLessEqual(abs(lstm - vanilla) / vanilla, 0.15)

    def test_fixture_comparison_preserves_six_method_parity(self) -> None:
        fixture = PublicDatasetBenchmarkTests()
        with tempfile.TemporaryDirectory() as tmp_dir:
            dataset_dir = Path(tmp_dir) / "sml2010"
            dataset_dir.mkdir(parents=True, exist_ok=True)
            fixture._write_sml2010_normalized_fixture(dataset_dir)
            result = run_gru_lstm_public_comparison(
                input_dir=dataset_dir,
                horizons=[1],
                cadence_minutes=1,
                config=GatedComparisonConfig(
                    sequence_length=4,
                    epochs=2,
                    batch_size=4,
                    seed=42,
                ),
            )
            self.assertEqual(result["status"], "COMPLETE")
            self.assertTrue(result["data_parity"]["all_horizons_passed"])
            self.assertEqual(len(result["cases"]), 4)
            for case in result["cases"]:
                self.assertEqual(
                    set(case["metrics"]),
                    {
                        "persistence",
                        "sequence_linear_regression",
                        "physics_structured_readout",
                        "vanilla_rnn",
                        "gru",
                        "lstm",
                    },
                )


if __name__ == "__main__":
    unittest.main()
