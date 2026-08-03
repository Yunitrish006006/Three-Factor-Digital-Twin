import math
import tempfile
import unittest
from pathlib import Path

from digital_twin.evaluation.rnn_public_comparison import (
    RNNConfig,
    VanillaElmanRNN,
    _shared_sequence_endpoints,
    run_rnn_public_comparison,
)
from tests.test_public_dataset_benchmark import PublicDatasetBenchmarkTests


class RNNPublicComparisonTests(unittest.TestCase):
    def test_vanilla_rnn_is_deterministic(self) -> None:
        config = RNNConfig(sequence_length=3, hidden_units=3, epochs=4, batch_size=2, seed=7)
        sequences = [
            [[float(index + step)] for step in range(3)]
            for index in range(8)
        ]
        targets = [[float(index + 3)] for index in range(8)]
        first = VanillaElmanRNN(input_size=1, output_size=1, config=config)
        second = VanillaElmanRNN(input_size=1, output_size=1, config=config)
        first_summary = first.fit(sequences, targets)
        second_summary = second.fit(sequences, targets)
        self.assertEqual(first_summary, second_summary)
        self.assertEqual(first.predict(sequences[-1]), second.predict(sequences[-1]))
        self.assertTrue(all(math.isfinite(value) for value in first.predict(sequences[-1])))

    def test_shared_sequence_endpoints_rejects_time_gap_for_every_method(self) -> None:
        fixture = PublicDatasetBenchmarkTests()
        with tempfile.TemporaryDirectory() as tmp_dir:
            dataset_dir = Path(tmp_dir) / "sml2010"
            dataset_dir.mkdir(parents=True, exist_ok=True)
            fixture._write_sml2010_normalized_fixture(dataset_dir)
            from digital_twin.core.public_dataset_benchmark import (
                _build_sml2010_response_samples,
                _load_sml2010_records,
                _read_csv_rows,
            )

            records = _load_sml2010_records(
                _read_csv_rows(dataset_dir / "corner_sensor_timeseries.csv"),
                _read_csv_rows(dataset_dir / "outdoor_environment.csv"),
                _read_csv_rows(dataset_dir / "auxiliary_features.csv"),
            )
            samples = _build_sml2010_response_samples(records, 1, task_id="S2")
            endpoints = _shared_sequence_endpoints(samples, sequence_length=4, cadence_minutes=1)
            self.assertTrue(endpoints)
            samples[2]["context"]["origin"]["timestamp_dt"] = samples[1]["context"]["origin"]["timestamp_dt"]
            changed = _shared_sequence_endpoints(samples, sequence_length=4, cadence_minutes=1)
            self.assertLess(len(changed), len(endpoints))

    def test_integration_preserves_same_test_hash_for_all_targets(self) -> None:
        fixture = PublicDatasetBenchmarkTests()
        with tempfile.TemporaryDirectory() as tmp_dir:
            dataset_dir = Path(tmp_dir) / "sml2010"
            dataset_dir.mkdir(parents=True, exist_ok=True)
            fixture._write_sml2010_normalized_fixture(dataset_dir)
            summary = run_rnn_public_comparison(
                input_dir=dataset_dir,
                horizons=[1],
                config=RNNConfig(sequence_length=4, hidden_units=3, epochs=2, batch_size=4, seed=42),
                cadence_minutes=1,
            )
            self.assertTrue(summary["data_parity"]["all_horizons_passed"])
            cases = [case for case in summary["cases"] if case["status"] == "ok"]
            self.assertEqual(len(cases), 4)
            self.assertEqual(len({case["shared_test_endpoint_hash"] for case in cases}), 1)
            self.assertEqual(len({case["shared_test_input_hash"] for case in cases}), 1)
            contracts = summary["data_parity"]["horizon_audits"][0]["method_data_contracts"]
            self.assertEqual(len({item["shared_test_input_hash"] for item in contracts.values()}), 1)
            for case in cases:
                self.assertEqual(set(case["metrics"]), {
                    "persistence",
                    "sequence_linear_regression",
                    "physics_structured_readout",
                    "vanilla_rnn",
                })

    def test_insufficient_data_produces_no_ranking(self) -> None:
        fixture = PublicDatasetBenchmarkTests()
        with tempfile.TemporaryDirectory() as tmp_dir:
            dataset_dir = Path(tmp_dir) / "sml2010"
            dataset_dir.mkdir(parents=True, exist_ok=True)
            fixture._write_sml2010_normalized_fixture(dataset_dir)
            summary = run_rnn_public_comparison(
                input_dir=dataset_dir,
                horizons=[999999],
                config=RNNConfig(sequence_length=4, hidden_units=3, epochs=1, batch_size=4),
            )
            self.assertEqual(summary["status"], "NOT_EVALUATED")
            self.assertFalse(summary["data_parity"]["all_horizons_passed"])


if __name__ == "__main__":
    unittest.main()
