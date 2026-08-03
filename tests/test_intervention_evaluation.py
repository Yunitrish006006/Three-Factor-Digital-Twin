import copy
import json
import unittest
from pathlib import Path

from digital_twin.evaluation.intervention import (
    InterventionValidationError,
    analyze_intervention_dataset,
    comfort_penalty,
)


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "docs" / "templates" / "e8_intervention_trials_template.json"


class InterventionEvaluationTests(unittest.TestCase):
    def test_empty_template_remains_not_evaluated(self) -> None:
        dataset = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        summary = analyze_intervention_dataset(dataset)

        self.assertEqual(summary["evidence_status"], "NOT_EVALUATED")
        self.assertEqual(summary["trial_counts"]["completed"], 0)
        self.assertIsNone(summary["metrics"]["top_ranked_success_rate"])
        self.assertIsNone(summary["metrics"]["matched_block_top1_regret_mean"])

    def test_known_penalty_and_trial_metrics(self) -> None:
        dataset = _dataset_with_trials(
            _trial("trial_top", "top_ranked", "cool"),
        )
        summary = analyze_intervention_dataset(dataset)

        self.assertEqual(summary["evidence_status"], "SYNTHETIC_TEST_ONLY")
        self.assertAlmostEqual(
            comfort_penalty(
                dataset["trials"][0]["before"]["values"],
                dataset["trials"][0]["target"],
            ),
            4.1,
        )
        result = summary["trials"][0]
        self.assertAlmostEqual(result["penalty_before"], 4.1)
        self.assertAlmostEqual(result["penalty_after"], 0.5)
        self.assertAlmostEqual(result["actual_improvement"], 3.6)
        self.assertAlmostEqual(result["absolute_prediction_error"], 0.5)
        self.assertEqual(
            result["direction_agreement"],
            {
                "temperature": True,
                "humidity": True,
                "illuminance": True,
            },
        )
        self.assertAlmostEqual(summary["metrics"]["top_ranked_success_rate"], 1.0)

    def test_matched_block_metrics_use_measured_action_arms(self) -> None:
        dataset = _dataset_with_trials(
            _trial("trial_top", "top_ranked", "cool"),
            _trial(
                "trial_alt",
                "alternative_action",
                "window",
                after_values={
                    "temperature": 27.5,
                    "humidity": 62.0,
                    "illuminance": 160.0,
                },
            ),
        )
        summary = analyze_intervention_dataset(dataset)

        self.assertEqual(summary["metrics"]["matched_block_count_top1_regret"], 1)
        self.assertEqual(
            summary["metrics"]["matched_block_count_rank_correlation"],
            1,
        )
        self.assertAlmostEqual(
            summary["metrics"]["matched_block_top1_regret_mean"],
            0.0,
        )
        self.assertAlmostEqual(
            summary["metrics"]["matched_block_spearman_mean"],
            1.0,
        )

    def test_missing_completed_observation_is_rejected(self) -> None:
        trial = _trial("trial_top", "top_ranked", "cool")
        del trial["after"]["values"]["humidity"]
        dataset = _dataset_with_trials(trial)

        with self.assertRaisesRegex(
            InterventionValidationError,
            "after.values.humidity",
        ):
            analyze_intervention_dataset(dataset)

    def test_top_ranked_trial_must_execute_rank_one_action(self) -> None:
        dataset = _dataset_with_trials(
            _trial("trial_top", "top_ranked", "window"),
        )

        with self.assertRaisesRegex(
            InterventionValidationError,
            "must execute rank-1 action cool",
        ):
            analyze_intervention_dataset(dataset)

    def test_out_of_range_settling_requires_deviation(self) -> None:
        trial = _trial("trial_top", "top_ranked", "cool")
        trial["settling_minutes"] = 45.0
        dataset = _dataset_with_trials(trial)
        with self.assertRaisesRegex(
            InterventionValidationError,
            "outside the registered interval",
        ):
            analyze_intervention_dataset(dataset)

        dataset["trials"][0]["protocol_deviations"] = [
            "Cooling response had not stabilized by minute 30."
        ]
        summary = analyze_intervention_dataset(dataset)
        self.assertEqual(summary["trials"][0]["protocol_deviation_count"], 1)

    def test_recorded_prediction_must_match_target_formula(self) -> None:
        trial = _trial("trial_top", "top_ranked", "cool")
        trial["predicted_ranking"][0]["predicted_improvement"] = 999.0

        with self.assertRaisesRegex(
            InterventionValidationError,
            "inconsistent with computed value",
        ):
            analyze_intervention_dataset(_dataset_with_trials(trial))

    def test_unknown_trial_field_is_rejected(self) -> None:
        trial = _trial("trial_top", "top_ranked", "cool")
        trial["unregistered_outcome"] = 1.0

        with self.assertRaisesRegex(
            InterventionValidationError,
            "contains unsupported fields",
        ):
            analyze_intervention_dataset(_dataset_with_trials(trial))


def _dataset_with_trials(*trials):
    dataset = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    dataset["evidence_class"] = "SYNTHETIC_TEST"
    dataset["study"]["status"] = "DATA_COLLECTION_IN_PROGRESS"
    dataset["trials"] = [copy.deepcopy(trial) for trial in trials]
    return dataset


def _trial(
    trial_id,
    condition,
    executed_action,
    *,
    after_values=None,
):
    target = {
        "temperature": {"value": 25.0, "tolerance": 1.0, "weight": 1.0},
        "humidity": {"value": 50.0, "tolerance": 10.0, "weight": 0.5},
        "illuminance": {"value": 100.0, "tolerance": 50.0, "weight": 0.2},
    }
    before_values = {
        "temperature": 29.0,
        "humidity": 70.0,
        "illuminance": 300.0,
    }
    before_penalty = comfort_penalty(before_values, target)
    predictions = [
        (
            1,
            "cool",
            {
                "temperature": 26.0,
                "humidity": 55.0,
                "illuminance": 110.0,
            },
        ),
        (
            2,
            "window",
            {
                "temperature": 27.0,
                "humidity": 60.0,
                "illuminance": 120.0,
            },
        ),
    ]
    ranking = []
    for rank, action_name, predicted_after in predictions:
        penalty = comfort_penalty(predicted_after, target)
        ranking.append(
            {
                "rank": rank,
                "action_name": action_name,
                "predicted_after": predicted_after,
                "predicted_penalty": penalty,
                "predicted_improvement": before_penalty - penalty,
            }
        )

    return {
        "trial_id": trial_id,
        "block_id": "block_001",
        "status": "COMPLETED",
        "condition": condition,
        "started_at": "2026-07-26T09:00:00+08:00",
        "completed_at": "2026-07-26T09:22:00+08:00",
        "target": target,
        "before": {
            "values": before_values,
            "external": {
                "outdoor_temperature": 31.0,
                "outdoor_humidity": 73.0,
                "sunlight_illuminance": 18000.0,
            },
        },
        "predicted_ranking": ranking,
        "executed_action": executed_action,
        "settling_minutes": 22.0,
        "after": {
            "values": after_values
            or {
                "temperature": 26.5,
                "humidity": 55.0,
                "illuminance": 90.0,
            },
            "external": {
                "outdoor_temperature": 31.1,
                "outdoor_humidity": 72.5,
                "sunlight_illuminance": 17500.0,
            },
        },
        "protocol_deviations": [],
        "operator_notes": "Synthetic unit-test fixture; never thesis evidence.",
    }


if __name__ == "__main__":
    unittest.main()
