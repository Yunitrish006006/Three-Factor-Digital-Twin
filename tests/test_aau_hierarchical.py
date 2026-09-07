import unittest

from digital_twin.enclosure.aau_hierarchical import (
    build_neighbor_orders,
    candidate_specs,
    evaluate_hierarchical_grid,
    extract_frozen_sensor_metadata,
    idw_prediction,
)


class AAUHierarchicalTest(unittest.TestCase):
    def test_extracts_frozen_positions_roles_and_columns(self):
        document = {"evaluation": {"per_sensor": {
            "rack_1_front": {"csv_column": "T1", "position_m": {"x": 1, "y": 2, "z": 3}},
            "gradient_1": {"csv_column": "T2", "position_m": {"x_m": 4, "y_m": 5, "z_m": 6}},
        }}}
        metadata = extract_frozen_sensor_metadata(document)
        self.assertEqual(metadata["T1"]["role"], "rack_front")
        self.assertEqual(metadata["T2"]["position_m"], (4.0, 5.0, 6.0))

    def test_idw_uses_available_peers_when_k_is_larger(self):
        prediction = idw_prediction({"a": 10.0, "b": 20.0}, [("a", 1.0), ("b", 2.0)], 5, 1)
        self.assertAlmostEqual(prediction, 13.333333333333334)

    def test_grid_is_frozen_at_24_candidates(self):
        self.assertEqual(len(candidate_specs()), 24)

    def test_evaluates_all_roles_without_empty_groups(self):
        metadata = {}
        values = {}
        for role, base, x0 in (("rack_front", 20.0, 0.0), ("rack_back", 30.0, 10.0), ("gradient", 50.0, 20.0)):
            for index in range(2):
                sensor = f"{role}_{index}"
                metadata[sensor] = {"sensor_id": sensor, "role": role, "position_m": (x0 + index, 0.0, 0.0)}
                values[sensor] = base + index
        orders = build_neighbor_orders(metadata, same_role=True)
        self.assertTrue(all(len(peers) == 1 for peers in orders.values()))
        result = evaluate_hierarchical_grid([("2026-01-01T00:00:00", values)], metadata)
        self.assertEqual(result["candidate_count"], 24)
        self.assertIn(result["development_decision"], {"candidate_forwarded", "no_candidate_forwarded"})


if __name__ == "__main__":
    unittest.main()

