from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from digital_twin.enclosure.bmc_baseline import evaluate_bmc_paths, load_bmc_observations


class EnclosureBMCBaselineTests(unittest.TestCase):
    def test_parser_ignores_influx_comments_and_collects_required_channels(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            path = Path(temporary_dir) / "trace.csv"
            self._write_trace(path, rows=4)

            observations, counts = load_bmc_observations(path)

            self.assertEqual(len(observations), 4)
            self.assertEqual(counts["missing_required_rows"], 0)
            self.assertEqual(observations[0].total_power_w, 300.0)
            self.assertEqual(observations[0].mean_fan_rpm, 3150.0)

    def test_comparison_uses_identical_chronological_endpoints(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            path = Path(temporary_dir) / "trace.csv"
            self._write_trace(path, rows=80)

            summary = evaluate_bmc_paths([path])

            case = summary["cases"][0]
            self.assertEqual(case["status"], "ok")
            self.assertEqual(case["split"]["train_examples"], 47)
            self.assertEqual(set(case["metrics"]["test"]), {
                "persistence",
                "linear_readout",
                "thermal_balance_readout",
            })
            self.assertEqual(summary["protocol"]["temperature_domain_c"], [20.0, 30.0])

    def test_out_of_domain_air_states_remain_not_evaluated(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            path = Path(temporary_dir) / "hot_trace.csv"
            self._write_trace(path, rows=40, inlet_base=31.0, outlet_base=32.0)

            summary = evaluate_bmc_paths([path])

            case = summary["cases"][0]
            self.assertEqual(case["status"], "insufficient_in_scope_samples")
            self.assertGreater(case["exclusions"]["out_of_domain_pairs"], 0)
            self.assertEqual(summary["summary"]["status"], "not_evaluated")

    def _write_trace(
        self,
        path: Path,
        rows: int,
        inlet_base: float = 24.0,
        outlet_base: float = 25.0,
    ) -> None:
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        lines = [
            "#group,false,false,false,false,false,false,false,false,false",
            "_time,device_id,Inlet_Temp,Outlet_Temp,PSU1_Total_Power,PSU2_Total_Power,FAN1,FAN2,FAN3,FAN4",
        ]
        outlet = outlet_base
        for index in range(rows):
            timestamp = start + timedelta(minutes=index)
            inlet = inlet_base + 0.15 * ((index % 9) - 4) / 4.0
            power_one = 140.0 + float((index * 7) % 35)
            power_two = 160.0 + float((index * 5) % 25)
            fan = 3000.0 + float((index % 6) * 80)
            if index:
                outlet += 0.08 * (inlet - outlet) + 0.00045 * (power_one + power_two) - 0.00001 * fan
            lines.append(
                f"{timestamp.isoformat()},server-a,{inlet:.6f},{outlet:.6f},"
                f"{power_one:.3f},{power_two:.3f},{fan:.3f},{fan + 100:.3f},{fan + 200:.3f},{fan + 300:.3f}"
            )
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
