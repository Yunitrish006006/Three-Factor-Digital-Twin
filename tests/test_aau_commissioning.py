import unittest

from digital_twin.enclosure.aau_commissioning import (
    calibrated_prediction,
    commissioning_specs,
    fit_candidate,
    huber_affine,
    select_commissioning_model,
)


class CommissioningTests(unittest.TestCase):
    def test_candidate_grid_is_fixed(self) -> None:
        specs = commissioning_specs()
        self.assertEqual(8, len(specs))
        self.assertIn("local_median_l100", specs)
        self.assertIn("e11g_huber_affine", specs)

    def test_median_offset_uses_shrinkage(self) -> None:
        records = [(21.0, 20.0, 20.0), (22.0, 21.0, 21.0)]
        spec = {"base": "local", "calibration": "median_offset", "shrinkage": 0.5}
        model = fit_candidate(records, spec, None)
        self.assertEqual(0.5, model["offset_c"])
        self.assertEqual(20.5, calibrated_prediction((0.0, 20.0, 20.0), model, None))

    def test_huber_affine_recovers_linear_relation(self) -> None:
        x_values = [float(value) for value in range(10)]
        y_values = [1.2 * value + 2.0 for value in x_values]
        slope, intercept = huber_affine(x_values, y_values)
        self.assertAlmostEqual(1.2, slope, places=6)
        self.assertAlmostEqual(2.0, intercept, places=6)

    def test_selection_uses_separate_validation_records(self) -> None:
        calibration = [(21.0, 20.0, 20.0), (22.0, 21.0, 21.0)] * 10
        selection = [(23.0, 22.0, 22.0), (24.0, 23.0, 23.0)] * 10
        model_id, model = select_commissioning_model(calibration, selection, None)
        self.assertNotEqual("baseline_local_idw_k3_p2", model_id)
        self.assertIsNotNone(model)

    def test_frozen_model_does_not_refit(self) -> None:
        model = {
            "base": "local",
            "calibration": "median_offset",
            "offset_c": 1.0,
            "shrinkage": 1.0,
        }
        self.assertEqual(21.0, calibrated_prediction((100.0, 20.0, 30.0), model, None))



if __name__ == "__main__":
    unittest.main()
