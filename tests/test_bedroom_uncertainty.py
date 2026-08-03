import unittest

from scripts.run_bedroom_weekly_simulation import (
    _compare_observed_sensors,
    _leave_one_date_out_sensitivity,
    _paired_day_block_bootstrap,
)


def row(date, raw_temperature, calibrated_temperature):
    return {
        "date": date,
        "raw_pillow_abs_error": {
            "temperature": raw_temperature,
            "humidity": raw_temperature * 2.0,
            "illuminance": raw_temperature * 10.0,
        },
        "estimated_pillow_abs_error": {
            "temperature": calibrated_temperature,
            "humidity": calibrated_temperature * 2.0,
            "illuminance": calibrated_temperature * 10.0,
        },
    }


class BedroomUncertaintyTests(unittest.TestCase):
    def test_leave_one_date_out_preserves_positive_reduction(self):
        rows = [
            row("2026-04-14", 1.0, 0.5),
            row("2026-04-15", 2.0, 1.0),
            row("2026-04-16", 3.0, 2.0),
        ]
        result = _leave_one_date_out_sensitivity(rows)

        self.assertEqual(result["omission_unit"], "date")
        self.assertEqual(result["fold_count"], 3)
        self.assertEqual(
            [fold["omitted_date"] for fold in result["folds"]],
            ["2026-04-14", "2026-04-15", "2026-04-16"],
        )
        self.assertTrue(result["all_metric_minimum_reductions_positive"])
        self.assertEqual(
            result["metrics"]["temperature"]["minimum_absolute_mae_reduction"],
            0.75,
        )

    def test_leave_one_date_out_preserves_adverse_fold(self):
        rows = [
            row("2026-04-14", 1.0, 4.0),
            row("2026-04-15", 2.0, 1.0),
            row("2026-04-16", 2.0, 1.0),
        ]
        result = _leave_one_date_out_sensitivity(rows)

        self.assertFalse(result["all_metric_minimum_reductions_positive"])
        self.assertEqual(
            result["metrics"]["temperature"]["minimum_absolute_mae_reduction"],
            -1.0,
        )
        self.assertEqual(
            result["metrics"]["temperature"]["minimum_omitted_date"],
            "2026-04-15",
        )

    def test_leave_one_date_out_rejects_missing_date(self):
        with self.assertRaisesRegex(ValueError, "non-empty date"):
            _leave_one_date_out_sensitivity([row("", 1.0, 0.5)])

    def test_leave_one_date_out_requires_two_dates(self):
        with self.assertRaisesRegex(ValueError, "at least two dates"):
            _leave_one_date_out_sensitivity([row("2026-04-14", 1.0, 0.5)])

    def test_block_bootstrap_preserves_positive_paired_improvement(self):
        rows = [
            row("2026-04-14", 1.0, 0.25),
            row("2026-04-14", 1.2, 0.30),
            row("2026-04-15", 0.8, 0.20),
            row("2026-04-15", 1.4, 0.35),
        ]
        result = _paired_day_block_bootstrap(rows, replicates=200, seed=7)

        self.assertEqual(result["resampling_unit"], "date")
        self.assertEqual(result["cluster_count"], 2)
        self.assertEqual(result["snapshot_count"], 4)
        self.assertTrue(result["all_interval_lower_bounds_positive"])
        self.assertEqual(result["metrics"]["temperature"]["snapshots_improved"], 4)
        self.assertEqual(result["metrics"]["temperature"]["improved_fraction"], 1.0)

    def test_block_bootstrap_is_deterministic_for_a_fixed_seed(self):
        rows = [
            row("2026-04-14", 1.0, 0.4),
            row("2026-04-15", 0.8, 0.2),
            row("2026-04-16", 1.4, 0.7),
        ]
        first = _paired_day_block_bootstrap(rows, replicates=100, seed=42)
        second = _paired_day_block_bootstrap(rows, replicates=100, seed=42)
        self.assertEqual(first, second)

    def test_block_bootstrap_rejects_missing_date(self):
        invalid = row("", 1.0, 0.5)
        with self.assertRaisesRegex(ValueError, "non-empty date"):
            _paired_day_block_bootstrap([invalid], replicates=10, seed=1)

    def test_block_bootstrap_rejects_nonpositive_replicates(self):
        with self.assertRaisesRegex(ValueError, "greater than zero"):
            _paired_day_block_bootstrap([row("2026-04-14", 1.0, 0.5)], replicates=0)

    def test_sensor_comparison_ignores_unobserved_compensation_points(self):
        predicted = {
            "floor_sw": {"temperature": 25.0, "humidity": 50.0, "illuminance": 100.0},
            "floor_sw_comp_1": {"temperature": 30.0, "humidity": 70.0, "illuminance": 500.0},
        }
        observed = {
            "floor_sw": {"temperature": 24.0, "humidity": 48.0, "illuminance": 90.0},
        }
        result = _compare_observed_sensors(predicted, observed)
        self.assertEqual(result, {"temperature": 1.0, "humidity": 2.0, "illuminance": 10.0})


if __name__ == "__main__":
    unittest.main()
