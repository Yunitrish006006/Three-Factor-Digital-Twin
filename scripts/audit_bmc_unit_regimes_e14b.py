#!/usr/bin/env python3
"""Run the preregistered E14B BMC unit-regime audit."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from digital_twin.enclosure.bmc_virtual_sensor import parse_influx_bmc
from scripts.audit_bmc_section_parser_e14a import oracle_bmc_count


EXPECTED_MANIFEST_SHA256 = "9f0ef4e25805af89ac1f59ae1e13f39bf036a510dcbe07f4a2d3ccd4f78cad74"
EXPECTED_E14A_SHA256 = "348d6525a7f495302a7e076f38f4705c5d3214a62d13546961cf8e1546e94833"
EXPECTED_RAW_FILES = {
    "202307191620.csv", "202307201552.csv", "202307211550.csv",
}
MANIFEST = Path("outputs/data/enclosure/bmc_cross_run_e12_manifest.json")
E14A_RESULT = Path("outputs/data/enclosure/bmc_section_parser_e14a_result.json")
RAW_DIR = Path("outputs/data/enclosure/bmc_cross_run_e12/raw")
RESULT = Path("outputs/data/enclosure/bmc_unit_regimes_e14b_result.json")
KNOWN_FILE = "202307191620.csv"
KNOWN_TIME = "2023-07-19T07:54:52Z"
FIELDS = (
    "inlet", "outlet", "cpu1", "cpu2", "target", "fan_krpm",
    "power_100w", "thermal_rise", "power_per_fan",
)


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def update_extrema(extrema: dict, row: dict) -> None:
    for field in FIELDS:
        value = row[field]
        current = extrema.setdefault(field, {"min": value, "max": value})
        current["min"] = min(current["min"], value)
        current["max"] = max(current["max"], value)


def close(actual: float, expected: float) -> bool:
    return math.isclose(actual, expected, rel_tol=0.0, abs_tol=1e-9)


def main() -> None:
    if sha256_path(MANIFEST) != EXPECTED_MANIFEST_SHA256:
        raise RuntimeError("E14B manifest hash mismatch")
    if sha256_path(E14A_RESULT) != EXPECTED_E14A_SHA256:
        raise RuntimeError("E14B E14A-result hash mismatch")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    e14a = json.loads(E14A_RESULT.read_text(encoding="utf-8"))
    e14a_counts = {
        item["filename"]: item["production_count"] for item in e14a["file_reports"]
    }
    file_reports = []
    extrema = {}
    inferred_raw_files = set()
    known_row = None
    for item in manifest["files"]:
        path = RAW_DIR / item["filename"]
        parsed = parse_influx_bmc(path)
        oracle = oracle_bmc_count(path)
        regimes = [section["regime"] for section in parsed["unit_sections"]]
        if "raw_hwmon" in regimes:
            inferred_raw_files.add(item["filename"])
        for row in parsed["rows"]:
            update_extrema(extrema, row)
            if item["filename"] == KNOWN_FILE and row["time"] == KNOWN_TIME:
                known_row = row
        file_reports.append({
            "filename": item["filename"],
            "split": item["split"],
            "accepted_rows": len(parsed["rows"]),
            "e14a_rows": e14a_counts[item["filename"]],
            "oracle_rows": oracle["count"],
            "counts_preserved": (
                len(parsed["rows"]) == e14a_counts[item["filename"]] == oracle["count"]
            ),
            "unit_sections": parsed["unit_sections"],
            "all_sections_concordant": all(
                section["concordant"] for section in parsed["unit_sections"]
            ),
        })
    known_example_ok = known_row is not None and all((
        close(known_row["inlet"], 34.5),
        close(known_row["outlet"], 34.5),
        close(known_row["cpu1"], 36.5),
        close(known_row["cpu2"], 37.0),
        close(known_row["power_100w"] * 100.0, 245.0),
    ))
    normalized_files_scale_one = all(
        all(
            section["temperature_scale"] == 1.0 and section["power_scale"] == 1.0
            for section in report["unit_sections"]
        )
        for report in file_reports if report["filename"] not in EXPECTED_RAW_FILES
    )
    temperature_fields = ("inlet", "outlet", "cpu1", "cpu2", "target")
    gates = {
        "all_4038_rows_preserved": sum(item["accepted_rows"] for item in file_reports) == 4038,
        "all_per_file_counts_preserved": all(item["counts_preserved"] for item in file_reports),
        "exact_three_raw_files_identified": inferred_raw_files == EXPECTED_RAW_FILES,
        "all_sections_unit_concordant": all(
            item["all_sections_concordant"] for item in file_reports
        ),
        "all_normalized_files_scale_one": normalized_files_scale_one,
        "all_temperatures_in_0_150_c": all(
            extrema[field]["min"] >= 0.0 and extrema[field]["max"] <= 150.0
            for field in temperature_fields
        ),
        "summed_psu_power_in_0_5000_w": (
            extrema["power_100w"]["min"] * 100.0 >= 0.0
            and extrema["power_100w"]["max"] * 100.0 <= 5000.0
        ),
        "known_raw_example_exact": known_example_ok,
    }
    result = {
        "study_id": "E14B",
        "hypothesis": "H-DATA-02",
        "manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "e14a_result_sha256": EXPECTED_E14A_SHA256,
        "expected_raw_files": sorted(EXPECTED_RAW_FILES),
        "inferred_raw_files": sorted(inferred_raw_files),
        "file_reports": file_reports,
        "normalized_extrema": extrema,
        "known_example": known_row,
        "gates": gates,
        "decision": "h_data_02_supported" if all(gates.values()) else "h_data_02_not_supported",
        "claim_boundary": "Retrospective unit correctness only; no model confirmation.",
    }
    RESULT.write_text(
        json.dumps(result, ensure_ascii=True, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "decision": result["decision"],
        "inferred_raw_files": result["inferred_raw_files"],
        "normalized_extrema": extrema,
        "known_example": known_row,
        "gates": gates,
    }, indent=2))


if __name__ == "__main__":
    main()
