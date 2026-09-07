import unittest

from digital_twin.enclosure.aau_role import (
    bootstrap_day_improvement,
    classify_sensor_role,
    evaluate_role_conditioning,
    extract_frozen_role_map,
)


class AAURoleTest(unittest.TestCase):
    def test_classifies_only_registered_roles(self):
        self.assertEqual(classify_sensor_role("Rack 3 Front PT100"), "rack_front")
        self.assertEqual(classify_sensor_role("Rack 3 Rear PT100"), "rack_back")
        self.assertEqual(classify_sensor_role("Temperature Gradient 2"), "gradient")
        self.assertIsNone(classify_sensor_role("Cooling unit supply"))

    def test_extracts_role_map_from_dict_and_list_layouts(self):
        document = {
            "per_sensor": {"A": {"role": "rack_front"}},
            "other": [{"sensor_id": "B", "sensor_role": "rack_back"}],
            "legacy": {"gradient_1": {"csv_column": "Temperature mod 1 ch 1"}},
        }
        self.assertEqual(
            extract_frozen_role_map(document),
            {"A": "rack_front", "B": "rack_back", "Temperature mod 1 ch 1": "gradient"},
        )

    def test_role_conditioning_has_expected_win(self):
        roles = {
            "f1": "rack_front",
            "f2": "rack_front",
            "b1": "rack_back",
            "b2": "rack_back",
            "g1": "gradient",
            "g2": "gradient",
        }
        snapshots = [
            (
                "2026-01-01T00:00:00",
                {"f1": 20.0, "f2": 20.0, "b1": 30.0, "b2": 30.0, "g1": 50.0, "g2": 50.0},
            )
        ]
        result = evaluate_role_conditioning(snapshots, roles)
        self.assertEqual(result["role_conditioned"]["mae_c"], 0.0)
        self.assertEqual(result["per_sensor_wins"]["role_conditioned"], 6)

    def test_bootstrap_is_deterministic(self):
        values = {"2026-01-01": 1.0, "2026-01-02": 2.0}
        first = bootstrap_day_improvement(values, replicates=100, seed=7)
        second = bootstrap_day_improvement(values, replicates=100, seed=7)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
