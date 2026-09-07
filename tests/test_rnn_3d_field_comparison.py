import unittest

from digital_twin.core.scenarios import build_validation_scenarios
from digital_twin.evaluation.rnn_3d_field_comparison import (
    FORBIDDEN_INPUT_TERMS,
    INPUT_FEATURE_NAMES,
    METHOD_NAMES,
    build_pure_rnn_field_dataset,
    build_sensor_token_sequence,
    run_rnn_3d_field_comparison,
)
from digital_twin.evaluation.rnn_public_comparison import RNNConfig
from digital_twin.neural.hybrid_residual import _truth_and_estimated_results
from digital_twin.core.demo import synthesize_sensor_observations
from digital_twin.physics.model import DigitalTwinModel, METRICS


class RNN3DFieldComparisonTests(unittest.TestCase):
    def test_sensor_sequence_uses_eight_tokens_without_physics_features(self) -> None:
        scenario = build_validation_scenarios()[0]
        truth, _estimated = _truth_and_estimated_results(DigitalTwinModel(), scenario)
        observed = synthesize_sensor_observations(truth.sensor_predictions, scenario.sensors)
        sequence = build_sensor_token_sequence(
            scenario,
            observed,
            truth.field.point(0, 0, 0),
        )

        self.assertEqual(len(sequence), 8)
        self.assertTrue(all(len(row) == len(INPUT_FEATURE_NAMES) for row in sequence))
        self.assertFalse(
            any(term in name.lower() for name in INPUT_FEATURE_NAMES for term in FORBIDDEN_INPUT_TERMS)
        )

    def test_dataset_uses_deterministic_point_count_and_three_targets(self) -> None:
        scenario = build_validation_scenarios()[0]
        first = build_pure_rnn_field_dataset([scenario], max_points_per_scenario=12)
        second = build_pure_rnn_field_dataset([scenario], max_points_per_scenario=12)

        self.assertEqual(len(first.sequences), 12)
        self.assertEqual(first.query_ids, second.query_ids)
        self.assertEqual(first.sequences, second.sequences)
        self.assertTrue(all(len(target) == len(METRICS) for target in first.targets))

    def test_small_loo_comparison_is_complete_and_parity_audited(self) -> None:
        scenarios = build_validation_scenarios()[:3]
        summary = run_rnn_3d_field_comparison(
            scenarios=scenarios,
            max_points_per_scenario=8,
            rnn_config=RNNConfig(
                sequence_length=8,
                hidden_units=3,
                epochs=2,
                batch_size=4,
                learning_rate=0.01,
                gradient_clip=1.0,
                seed=42,
            ),
            hybrid_hidden_dim=3,
            hybrid_epochs=2,
            hybrid_learning_rate=0.01,
        )

        self.assertEqual(summary["status"], "COMPLETE")
        self.assertEqual(len(summary["folds"]), 3)
        for fold in summary["folds"]:
            self.assertTrue(fold["data_parity"]["passed"])
            self.assertEqual(set(fold["field_mae"]), set(METHOD_NAMES))
            self.assertNotIn(fold["holdout_scenario"], fold["train_scenarios"])


if __name__ == "__main__":
    unittest.main()
