import tempfile
import unittest
from pathlib import Path

from digital_twin.enclosure.bmc_virtual_sensor import (
    evaluate_frozen,
    evaluate_rows,
    fit_ridge,
    parse_influx_bmc,
    select_and_refit,
)
from scripts.download_bmc_cross_run_e12 import SPLITS, validate_split
from scripts.run_bmc_cross_run_e13 import (
    EXPECTED_MANIFEST_SHA256,
    MIN_VALID_ROWS,
)
from scripts.audit_bmc_section_parser_e14a import oracle_bmc_count


class BmcVirtualSensorTests(unittest.TestCase):
    def test_e13_recovery_constants_are_frozen(self):
        self.assertEqual(MIN_VALID_ROWS, 10)
        self.assertEqual(len(EXPECTED_MANIFEST_SHA256), 64)

    def test_split_is_disjoint_and_frozen_size(self):
        validate_split()
        self.assertEqual({key: len(value) for key, value in SPLITS.items()}, {
            "train": 12, "selection": 5, "test": 14,
        })

    def test_parser_uses_names_and_tolerates_extra_columns(self):
        content = """#group,false\n,result,table,_time,_measurement,device_id,Inlet_Temp,Outlet_Temp,Cpu1_Temp,Cpu2_Temp,FAN1,FAN2,FAN3,FAN4,PSU1_Total_Power,PSU2_Total_Power,extra\n,,0,2026-01-01T00:00:00Z,sdgp,bmc,20,25,40,39,1000,1100,1200,1300,100,110,x\n"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.csv"
            path.write_text(content, encoding="utf-8")
            result = parse_influx_bmc(path)
        self.assertEqual(result["total_data_rows"], 1)
        self.assertEqual(len(result["rows"]), 1)
        self.assertEqual(result["rows"][0]["target"], 40.0)
        self.assertAlmostEqual(result["rows"][0]["fan_krpm"], 1.15)

    def test_parser_resets_sections_and_rejects_host_rows(self):
        content = """#group,false
#datatype,string
,result,table,_time,_measurement,device_id,Inlet_Temp,Outlet_Temp,Cpu1_Temp,Cpu2_Temp,FAN1,FAN2,FAN3,FAN4,PSU1_Total_Power,PSU2_Total_Power
,,0,2026-01-01T00:00:00Z,sdgp,bmc,20,25,40,39,1000,1100,1200,1300,100,110
#group,false
,result,table,_time,_measurement,device_id,counter1,counter2,counter3,counter4,counter5,counter6,counter7,counter8,counter9,counter10
,,1,2026-01-01T00:00:01Z,sdgp,host,2000000000,3000000000,4,5,6,7,8,9,10,11
#group,false
,result,table,_time,_measurement,device_id,Inlet_Temp,Outlet_Temp,Cpu1_Temp,Cpu2_Temp,FAN1,FAN2,FAN3,FAN4,PSU1_Total_Power,PSU2_Total_Power
,,2,2026-01-01T00:00:02Z,sdgp,bmc,21,26,41,40,1001,1101,1201,1301,101,111
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "multi.csv"
            path.write_text(content, encoding="utf-8")
            parsed = parse_influx_bmc(path)
            oracle = oracle_bmc_count(path)
        self.assertEqual(len(parsed["rows"]), 2)
        self.assertEqual(oracle["count"], 2)
        self.assertEqual(parsed["section_count"], 3)
        self.assertEqual(parsed["bmc_section_count"], 2)
        self.assertNotIn("2026-01-01T00:00:01Z", [row["time"] for row in parsed["rows"]])
        self.assertTrue(all(row["device_id"] == "bmc" for row in parsed["rows"]))

    def test_parser_normalizes_raw_hwmon_units_once_per_section(self):
        content = """#group,false
,result,table,_time,_measurement,device_id,Inlet_Temp,Outlet_Temp,Cpu1_Temp,Cpu2_Temp,FAN1,FAN2,FAN3,FAN4,PSU1_Total_Power,PSU2_Total_Power
,,0,2023-07-19T07:54:52Z,sdgp,bmc,34500,34500,36500,37000,5500,5510,5520,5530,122000000,123000000
,,0,2023-07-19T07:55:03Z,sdgp,bmc,34500,34500,37000,37000,3800,3840,3860,3860,119000000,119000000
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "raw-units.csv"
            path.write_text(content, encoding="utf-8")
            parsed = parse_influx_bmc(path)
        self.assertEqual(len(parsed["rows"]), 2)
        first = parsed["rows"][0]
        self.assertEqual(parsed["unit_sections"][0]["regime"], "raw_hwmon")
        self.assertTrue(parsed["unit_sections"][0]["concordant"])
        self.assertAlmostEqual(first["inlet"], 34.5)
        self.assertAlmostEqual(first["target"], 37.0)
        self.assertAlmostEqual(first["power_100w"] * 100.0, 245.0)

    def test_ridge_fits_simple_thermal_relation(self):
        rows = []
        for index in range(1, 30):
            inlet = 20.0 + index / 10.0
            outlet = inlet + 4.0
            rows.append({
                "inlet": inlet,
                "outlet": outlet,
                "fan_krpm": 2.0,
                "power_100w": 3.0,
                "thermal_rise": 4.0,
                "power_per_fan": 1.5,
                "target": 5.0 + 1.2 * inlet,
            })
        model = fit_ridge(rows, "thermal_pair", 0.01)
        result = evaluate_rows(model, rows)
        self.assertLess(result["mae_c"], 0.01)

    def test_two_phase_api_freezes_without_test_argument(self):
        def make_rows(offset):
            return [{
                "inlet": 20.0 + index,
                "outlet": 22.0 + index,
                "fan_krpm": 2.0,
                "power_100w": 3.0,
                "thermal_rise": 2.0,
                "power_per_fan": 1.5,
                "target": 26.0 + index + offset,
            } for index in range(30)]

        development = select_and_refit(
            {"train.csv": make_rows(0.0)},
            {"selection.csv": make_rows(0.1)},
        )
        self.assertEqual(development["development_file_counts"]["train"], 1)
        final = evaluate_frozen(
            development["frozen_models"],
            {f"test-{index}.csv": make_rows(0.2) for index in range(14)},
        )
        self.assertIn("decision", final)
        self.assertEqual(final["test"]["baseline"]["pooled"]["count"], 420)


if __name__ == "__main__":
    unittest.main()
