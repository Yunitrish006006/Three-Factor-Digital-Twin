import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from digital_twin.enclosure.aau_spatial import (
    MinuteSnapshot,
    SpatialSensor,
    complete_fragment_text,
    compute_range_offsets,
    evaluate_spatial_baselines,
    load_spatial_sensors,
)


ROOT = Path(__file__).resolve().parents[1]


class AAUSpatialBaselineTests(unittest.TestCase):
    def test_range_offsets_are_fixed_and_cover_extremes(self):
        offsets = compute_range_offsets(1000, 100, 4)
        self.assertEqual(offsets, [0, 300, 600, 900])

    def test_fragment_boundary_repair(self):
        text, discarded = complete_fragment_text(b"partial\nrow1\nrow2-partial", 500)
        self.assertEqual(text, "row1\n")
        self.assertEqual(discarded, 2)

    def test_room_design_contains_exactly_42_measurement_sensors(self):
        sensors = load_spatial_sensors(
            ROOT / "docs" / "templates" / "room_design_aau_server_room.json"
        )
        self.assertEqual(len(sensors), 42)
        self.assertEqual(len({sensor.csv_column for sensor in sensors}), 42)

    def test_evaluator_preserves_not_evaluable_small_fixture(self):
        sensors = [
            SpatialSensor("left", "a", "left", (0.0, 0.0, 0.0)),
            SpatialSensor("middle", "b", "middle", (1.0, 0.0, 0.0)),
            SpatialSensor("right", "c", "right", (2.0, 0.0, 0.0)),
        ]
        start = datetime(2026, 1, 1)
        snapshots = [
            MinuteSnapshot(start + timedelta(minutes=index), (20.0, 21.0, 22.0), 1000.0)
            for index in range(10)
        ]
        result = evaluate_spatial_baselines(sensors, snapshots)
        self.assertEqual(result["hypothesis"]["decision"], "not_evaluable")
        self.assertEqual(result["snapshot_count"], 10)
        self.assertAlmostEqual(
            result["per_sensor"]["middle"]["metrics"]["idw_3d_p2"]["mae_c"],
            0.0,
        )


if __name__ == "__main__":
    unittest.main()
