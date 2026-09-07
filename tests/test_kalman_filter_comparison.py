from __future__ import annotations

import math
import unittest
from datetime import datetime, timedelta

from digital_twin.evaluation.kalman_filter_comparison import (
    METHOD_NAMES,
    KalmanComparisonConfig,
    ScalarRandomWalkKalman,
    evaluate_controlled_filter_case,
)


class KalmanFilterComparisonTests(unittest.TestCase):
    def test_scalar_filter_update_is_finite_and_bounded(self) -> None:
        model = ScalarRandomWalkKalman(
            process_variance=0.1,
            measurement_variance=1.0,
            state=20.0,
            covariance=1.0,
        )
        estimate, innovation, gain = model.update(22.0)
        self.assertGreater(estimate, 20.0)
        self.assertLess(estimate, 22.0)
        self.assertEqual(innovation, 2.0)
        self.assertGreater(gain, 0.0)
        self.assertLess(gain, 1.0)

    def test_case_is_deterministic_and_preserves_data_parity(self) -> None:
        start = datetime(2026, 1, 1, 0, 0)
        timestamps = [start + timedelta(minutes=15 * index) for index in range(60)]
        clean = [22.0 + math.sin(index / 7.0) for index in range(60)]
        config = KalmanComparisonConfig(seed=7)
        first = evaluate_controlled_filter_case(
            timestamps,
            clean,
            target="room_temperature",
            unit="degC",
            noise_profile="nominal",
            noise_std=1.0,
            config=config,
        )
        second = evaluate_controlled_filter_case(
            timestamps,
            clean,
            target="room_temperature",
            unit="degC",
            noise_profile="nominal",
            noise_std=1.0,
            config=config,
        )
        self.assertEqual(first, second)
        self.assertTrue(first["data_parity"]["passed"])
        contracts = first["data_parity"]["method_contracts"]
        self.assertEqual(set(contracts), set(METHOD_NAMES))
        self.assertEqual(len({item["corrupted_observation_hash"] for item in contracts.values()}), 1)

    def test_cadence_gap_resets_filter_and_moving_history(self) -> None:
        start = datetime(2026, 1, 1, 0, 0)
        timestamps = [start + timedelta(minutes=15 * index) for index in range(30)]
        timestamps.extend(start + timedelta(days=2, minutes=15 * index) for index in range(30))
        clean = [20.0 + index * 0.02 for index in range(60)]
        result = evaluate_controlled_filter_case(
            timestamps,
            clean,
            target="dining_temperature",
            unit="degC",
            noise_profile="low",
            noise_std=0.5,
        )
        self.assertEqual(result["filter_diagnostics"]["cadence_gap_resets"], 1)
        self.assertEqual(result["filter_diagnostics"]["segment_initializations"], 2)

    def test_non_kalman_winner_is_not_coerced(self) -> None:
        start = datetime(2026, 1, 1, 0, 0)
        timestamps = [start + timedelta(minutes=15 * index) for index in range(80)]
        clean = [float(index % 2) * 10.0 for index in range(80)]
        result = evaluate_controlled_filter_case(
            timestamps,
            clean,
            target="room_humidity",
            unit="pctRH",
            noise_profile="low",
            noise_std=0.01,
        )
        self.assertIn(result["lowest_mae_method"], METHOD_NAMES)
        self.assertEqual(result["lowest_mae_method"], "raw_noisy")

    def test_protocol_rejects_unregistered_window(self) -> None:
        with self.assertRaisesRegex(ValueError, "three-record"):
            KalmanComparisonConfig(moving_average_window=5)
            evaluate_controlled_filter_case(
                [datetime(2026, 1, 1) + timedelta(minutes=15 * index) for index in range(10)],
                [20.0 for _ in range(10)],
                target="room_temperature",
                unit="degC",
                noise_profile="low",
                noise_std=0.5,
                config=KalmanComparisonConfig(moving_average_window=5),
            )


if __name__ == "__main__":
    unittest.main()
