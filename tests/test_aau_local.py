import unittest
from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path
import tempfile

from digital_twin.enclosure.aau_local import evaluate_local_idw_confirmation
from digital_twin.enclosure.aau_spatial import MinuteSnapshot, SpatialSensor, load_minute_snapshots


class AauLocalConfirmationTests(unittest.TestCase):
    def setUp(self):
        self.sensors = [
            SpatialSensor(f"s{index}", f"c{index}", f"S{index}", (float(index), 0.0, 0.0))
            for index in range(5)
        ]
        start = datetime(2026, 8, 1)
        self.snapshots = [
            MinuteSnapshot(
                start + timedelta(days=index // 2, minutes=index),
                tuple(float(sensor + index) for sensor in range(5)),
                2400.0,
            )
            for index in range(6)
        ]

    def test_reports_all_fixed_methods_and_pairwise_counts(self):
        result = evaluate_local_idw_confirmation(
            self.sensors,
            self.snapshots,
            bootstrap_replicates=100,
        )
        self.assertEqual(
            set(result["macro_metrics"]),
            {"nearest_neighbor", "local_idw_k3_p2", "global_idw_p2"},
        )
        pairwise = result["pairwise_sensor_results"]
        self.assertEqual(
            pairwise["local_idw_wins"] + pairwise["nearest_neighbor_wins"] + pairwise["ties"],
            len(self.sensors),
        )

    def test_bootstrap_is_deterministic(self):
        first = evaluate_local_idw_confirmation(
            self.sensors,
            self.snapshots,
            bootstrap_seed=7,
            bootstrap_replicates=100,
        )["bootstrap"]
        second = evaluate_local_idw_confirmation(
            self.sensors,
            self.snapshots,
            bootstrap_seed=7,
            bootstrap_replicates=100,
        )["bootstrap"]
        self.assertEqual(first, second)

    def test_rejects_invalid_neighbor_count(self):
        with self.assertRaises(ValueError):
            evaluate_local_idw_confirmation(
                self.sensors,
                self.snapshots,
                neighbor_count=1,
                bootstrap_replicates=10,
            )

    def test_nonzero_fragment_uses_manifest_header_without_discovery_rows(self):
        header = [
            "Time [Date/Time]",
            "Power Ch 1 (W)",
            "Power Ch 2 (W)",
            "Power Ch 3 (W)",
            "c0",
            "c1",
        ]
        raw = b"discarded partial\n2026-08-01 12:00:30,1,2,3,20,21\ntrailing partial"
        with tempfile.TemporaryDirectory() as directory:
            fragment = Path(directory) / "fragment.csv"
            fragment.write_bytes(raw)
            manifest = Path(directory) / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "csv_header": header,
                        "fragments": [
                            {
                                "index": 0,
                                "start": 100,
                                "path": str(fragment),
                                "sha256": hashlib.sha256(raw).hexdigest(),
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            sensors = [
                SpatialSensor("s0", "c0", "S0", (0.0, 0.0, 0.0)),
                SpatialSensor("s1", "c1", "S1", (1.0, 0.0, 0.0)),
            ]
            snapshots, counts = load_minute_snapshots(manifest, sensors)
        self.assertEqual(len(snapshots), 1)
        self.assertEqual(snapshots[0].temperatures, (20.0, 21.0))
        self.assertEqual(counts["rows_accepted"], 1)


if __name__ == "__main__":
    unittest.main()
