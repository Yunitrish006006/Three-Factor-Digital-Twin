import unittest

from digital_twin.enclosure.aau_tail_safe import (
    advancement_gates,
    gated_prediction,
    select_sensor_spec,
    tail_safe_specs,
)


class TailSafeTests(unittest.TestCase):
    def test_candidate_grid_is_fixed(self) -> None:
        specs = tail_safe_specs()
        self.assertEqual(30, len(specs))
        self.assertIn("clip_a100_t050", specs)
        self.assertIn("fallback_a075_t150", specs)

    def test_clip_limits_role_correction(self) -> None:
        spec = {"family": "clip", "alpha": 1.0, "threshold_c": 0.5}
        self.assertEqual(20.5, gated_prediction(20.0, 22.0, spec))

    def test_fallback_rejects_large_disagreement(self) -> None:
        spec = {"family": "fallback", "alpha": 0.75, "threshold_c": 0.5}
        self.assertEqual(20.0, gated_prediction(20.0, 22.0, spec))
        self.assertAlmostEqual(20.3, gated_prediction(20.0, 20.4, spec))

    def test_sensor_selection_requires_all_metric_margins(self) -> None:
        records = {
            f"2026-08-{day:02d}": [(21.0, 20.0, 21.0), (22.0, 21.0, 22.0)]
            for day in range(1, 6)
        }
        selected = select_sensor_spec(records, sorted(records), tail_safe_specs())
        self.assertNotEqual("baseline_local_idw_k3_p2", selected)

    def test_gate_rejects_insufficient_sensor_coverage(self) -> None:
        baseline = {"mae_c": 1.1, "rmse_c": 1.7, "p95_absolute_error_c": 3.5}
        model = {"mae_c": 1.0, "rmse_c": 1.6, "p95_absolute_error_c": 3.4}
        bootstrap = {"ci_95_lower_c": 0.01}
        gates = advancement_gates(baseline, model, 25, bootstrap)
        self.assertFalse(gates["sensor_wins_at_least_26"])


if __name__ == "__main__":
    unittest.main()
