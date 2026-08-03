from __future__ import annotations

from datetime import datetime, timedelta
import unittest

from digital_twin.evaluation.next_day_temperature_comparison import (
    FEATURE_NAMES,
    _adaptive_online_predictions,
    _best_validation_record_by_candidate,
    _build_next_day_feature_rows,
    _fit_and_predict_candidate,
    _paired_daily_block_bootstrap,
)


class NextDayTemperatureComparisonTests(unittest.TestCase):
    def test_feature_builder_does_not_use_target_time_measurements(self) -> None:
        origin_time = datetime(2012, 4, 20, 12, 0)
        origin = self._record(origin_time, dining=21.0, room=22.0)
        lag_24h = self._record(origin_time - timedelta(days=1), dining=20.5, room=21.5)
        lag_7d = self._record(origin_time - timedelta(days=7), dining=19.5, room=20.5)
        lookup = {
            origin_time: origin,
            lag_24h["timestamp_dt"]: lag_24h,
            lag_7d["timestamp_dt"]: lag_7d,
        }
        first_sample = {
            "targets": {"dining_temperature": 24.0},
            "context": {
                "origin": origin,
                "future": self._record(origin_time + timedelta(days=1), dining=24.0, room=25.0),
            },
        }
        second_sample = {
            "targets": {"dining_temperature": 99.0},
            "context": {
                "origin": origin,
                "future": self._record(origin_time + timedelta(days=1), dining=99.0, room=-10.0),
            },
        }

        first_rows, _, _ = _build_next_day_feature_rows(
            [first_sample],
            lookup,
            [21.2],
            "dining_temperature",
        )
        second_rows, _, _ = _build_next_day_feature_rows(
            [second_sample],
            lookup,
            [21.2],
            "dining_temperature",
        )

        self.assertEqual(first_rows, second_rows)
        self.assertEqual(len(first_rows[0]), len(FEATURE_NAMES))

    def test_candidate_selection_uses_validation_mae_and_registered_order(self) -> None:
        records = [
            {
                "candidate": "seasonal_persistence",
                "parameter": None,
                "metrics": {"mae": 0.4},
            },
            {
                "candidate": "bias_corrected_persistence",
                "parameter": None,
                "metrics": {"mae": 0.3},
            },
            {
                "candidate": "damped_daily_trend",
                "parameter": 0.0,
                "metrics": {"mae": 0.5},
            },
            {
                "candidate": "damped_daily_trend",
                "parameter": 0.25,
                "metrics": {"mae": 0.2},
            },
            {
                "candidate": "persistence_physics_blend",
                "parameter": 0.0,
                "metrics": {"mae": 0.4},
            },
            {
                "candidate": "seasonal_residual_ridge",
                "parameter": 0.001,
                "metrics": {"mae": 0.6},
            },
        ]

        selected = _best_validation_record_by_candidate(records)

        self.assertEqual(selected["damped_daily_trend"]["parameter"], 0.25)
        self.assertNotIn("test_metrics", selected["damped_daily_trend"])

    def test_bias_corrected_candidate_fits_only_requested_partition(self) -> None:
        actual = [2.0, 3.0, 100.0, 100.0]
        current = [1.0, 2.0, 5.0, 6.0]
        predictions = _fit_and_predict_candidate(
            candidate="bias_corrected_persistence",
            parameter=None,
            actual=actual,
            current=current,
            lag_24h=current,
            physics=current,
            feature_rows=[[value] for value in current],
            fit_start=0,
            fit_end=2,
            predict_start=2,
            predict_end=4,
        )

        self.assertEqual(predictions, [6.0, 7.0])

    def test_daily_block_bootstrap_is_deterministic_and_paired(self) -> None:
        kwargs = {
            "actual": [10.0, 11.0, 12.0, 13.0],
            "persistence": [9.0, 10.0, 11.0, 12.0],
            "selected": [10.0, 11.0, 12.0, 13.0],
            "dates": ["2026-01-01", "2026-01-01", "2026-01-02", "2026-01-02"],
            "replicates": 100,
            "seed": 7,
        }

        first = _paired_daily_block_bootstrap(**kwargs)
        second = _paired_daily_block_bootstrap(**kwargs)

        self.assertEqual(first, second)
        self.assertEqual(first["observed_mae_reduction_c"], 1.0)
        self.assertGreater(first["mae_reduction_ci95_c"][0], 0.0)

    def test_adaptive_online_prediction_uses_only_completed_daily_deltas(self) -> None:
        origin_time = datetime(2012, 4, 20, 12, 0)
        origin = self._record(origin_time, dining=21.0, room=22.0)
        previous = self._record(
            origin_time - timedelta(days=1),
            dining=20.0,
            room=21.0,
        )
        lookup = {
            origin_time: origin,
            previous["timestamp_dt"]: previous,
        }
        sample = {
            "targets": {"dining_temperature": 99.0},
            "context": {
                "origin": origin,
                "future": self._record(
                    origin_time + timedelta(days=1),
                    dining=99.0,
                    room=-10.0,
                ),
            },
        }

        predictions, counts = _adaptive_online_predictions(
            [sample],
            lookup,
            "dining_temperature",
        )

        self.assertEqual(counts, [1])
        self.assertEqual(predictions["same_slot_mean_3d"], [22.0])

    @staticmethod
    def _record(
        timestamp: datetime,
        dining: float,
        room: float,
    ) -> dict:
        return {
            "timestamp_dt": timestamp,
            "dining_temperature": dining,
            "room_temperature": room,
            "dining_humidity": 45.0,
            "room_humidity": 46.0,
            "outdoor_temperature": 18.0,
            "outdoor_humidity": 60.0,
            "forecast_temperature": 20.0,
            "sunlight_illuminance": 1000.0,
            "rain_ratio": 0.0,
            "wind_speed": 1.0,
            "enthalpic_motor_1": 0.0,
            "enthalpic_motor_2": 0.0,
            "enthalpic_motor_turbo": 0.0,
        }


if __name__ == "__main__":
    unittest.main()
