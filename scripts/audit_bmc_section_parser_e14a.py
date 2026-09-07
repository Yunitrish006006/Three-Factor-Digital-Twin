#!/usr/bin/env python3
"""Run the preregistered E14A section-aware parser correctness audit."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from digital_twin.enclosure.bmc_virtual_sensor import parse_influx_bmc


EXPECTED_MANIFEST_SHA256 = "9f0ef4e25805af89ac1f59ae1e13f39bf036a510dcbe07f4a2d3ccd4f78cad74"
MANIFEST = Path("outputs/data/enclosure/bmc_cross_run_e12_manifest.json")
RAW_DIR = Path("outputs/data/enclosure/bmc_cross_run_e12/raw")
RESULT = Path("outputs/data/enclosure/bmc_section_parser_e14a_result.json")
KNOWN_HOST_FILE = "202401050043.csv"
KNOWN_HOST_TIME = "2024-01-04T16:07:43Z"
ORACLE_REQUIRED_COLUMNS = (
    "_time", "_measurement", "device_id", "Inlet_Temp", "Outlet_Temp",
    "Cpu1_Temp", "Cpu2_Temp",
    "FAN1", "FAN2", "FAN3", "FAN4", "PSU1_Total_Power",
    "PSU2_Total_Power",
)
EXTREMA_FIELDS = (
    "inlet", "outlet", "cpu1", "cpu2", "target", "fan_krpm",
    "power_100w", "thermal_rise", "power_per_fan",
)


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def oracle_bmc_count(path: Path) -> dict:
    """Independent lexical section scanner; does not call production helpers."""
    header = None
    capable = False
    count = 0
    sections = 0
    capable_sections = 0
    with path.open("r", encoding="utf-8", newline="") as handle:
        for raw in handle:
            if raw.startswith("#group"):
                sections += 1
                header = None
                capable = False
                continue
            if raw.startswith("#") or not raw.strip():
                continue
            cells = next(csv.reader([raw]))
            if header is None:
                header = cells
                capable = all(name in header for name in ORACLE_REQUIRED_COLUMNS)
                if capable:
                    capable_sections += 1
                continue
            if not capable or len(cells) != len(header):
                continue
            measurement_index = header.index("_measurement")
            device_index = header.index("device_id")
            if cells[measurement_index] == "sdgp" and cells[device_index] == "bmc":
                count += 1
    return {
        "count": count,
        "section_count": sections,
        "bmc_capable_section_count": capable_sections,
    }


def update_extrema(extrema: dict, row: dict) -> None:
    for field in EXTREMA_FIELDS:
        value = row[field]
        current = extrema.setdefault(field, {"min": value, "max": value})
        current["min"] = min(current["min"], value)
        current["max"] = max(current["max"], value)


def main() -> None:
    manifest_hash_ok = sha256_path(MANIFEST) == EXPECTED_MANIFEST_SHA256
    if not manifest_hash_ok:
        raise RuntimeError("E14A requires the exact frozen manifest")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    file_reports = []
    extrema = {}
    source_violations = 0
    known_host_time_accepted = False
    raw_hashes_ok = True
    for item in manifest["files"]:
        path = RAW_DIR / item["filename"]
        raw_ok = path.stat().st_size == item["bytes"] and sha256_path(path) == item["sha256"]
        raw_hashes_ok = raw_hashes_ok and raw_ok
        parsed = parse_influx_bmc(path)
        oracle = oracle_bmc_count(path)
        for row in parsed["rows"]:
            update_extrema(extrema, row)
            if row["measurement"] != "sdgp" or row["device_id"] != "bmc":
                source_violations += 1
            if item["filename"] == KNOWN_HOST_FILE and row["time"] == KNOWN_HOST_TIME:
                known_host_time_accepted = True
        file_reports.append({
            "filename": item["filename"],
            "split": item["split"],
            "raw_hash_ok": raw_ok,
            "production_count": len(parsed["rows"]),
            "oracle_count": oracle["count"],
            "count_match": len(parsed["rows"]) == oracle["count"],
            "section_count": parsed["section_count"],
            "production_bmc_section_count": parsed["bmc_section_count"],
            "oracle_bmc_section_count": oracle["bmc_capable_section_count"],
            "invalid_bmc_rows": parsed["invalid_rows"],
            "rejected_non_bmc_rows": parsed["rejected_non_bmc_rows"],
        })
    temperature_fields = ("inlet", "outlet", "cpu1", "cpu2", "target")
    gates = {
        "manifest_hash_exact": manifest_hash_ok,
        "all_raw_hashes_exact": raw_hashes_ok,
        "all_31_files_audited": len(file_reports) == 31,
        "all_31_counts_match_oracle": all(item["count_match"] for item in file_reports),
        "all_files_have_bmc_rows": all(item["production_count"] > 0 for item in file_reports),
        "zero_accepted_source_violations": source_violations == 0,
        "known_host_timestamp_excluded": not known_host_time_accepted,
        "all_mapped_temperatures_below_1000_c": all(
            extrema[field]["max"] < 1000.0 for field in temperature_fields
        ),
    }
    result = {
        "study_id": "E14A",
        "hypothesis": "H-DATA-01",
        "manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "file_reports": file_reports,
        "accepted_extrema": extrema,
        "source_violations": source_violations,
        "known_host_file": KNOWN_HOST_FILE,
        "known_host_time": KNOWN_HOST_TIME,
        "known_host_time_accepted": known_host_time_accepted,
        "gates": gates,
        "decision": "h_data_01_supported" if all(gates.values()) else "h_data_01_not_supported",
        "claim_boundary": "Parser correctness only; no model accuracy or hardware claim.",
    }
    RESULT.write_text(
        json.dumps(result, ensure_ascii=True, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "decision": result["decision"],
        "total_accepted_rows": sum(item["production_count"] for item in file_reports),
        "mismatches": [item["filename"] for item in file_reports if not item["count_match"]],
        "empty_files": [item["filename"] for item in file_reports if item["production_count"] == 0],
        "accepted_extrema": extrema,
        "gates": gates,
    }, indent=2))


if __name__ == "__main__":
    main()
