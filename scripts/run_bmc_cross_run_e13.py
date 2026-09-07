#!/usr/bin/env python3
"""Run preregistered E13 after preserving the E12 availability failure."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from digital_twin.enclosure.bmc_virtual_sensor import (
    evaluate_frozen,
    parse_influx_bmc,
    select_and_refit,
)


EXPECTED_MANIFEST_SHA256 = "9f0ef4e25805af89ac1f59ae1e13f39bf036a510dcbe07f4a2d3ccd4f78cad74"
MIN_VALID_ROWS = 10
MANIFEST = Path("outputs/data/enclosure/bmc_cross_run_e12_manifest.json")
RAW_DIR = Path("outputs/data/enclosure/bmc_cross_run_e12/raw")
FROZEN = Path("outputs/data/enclosure/bmc_cross_run_e13_frozen_model.json")
RESULT = Path("outputs/data/enclosure/bmc_cross_run_e13_result.json")


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    if sha256_path(MANIFEST) != EXPECTED_MANIFEST_SHA256:
        raise RuntimeError("E13 requires the exact frozen E12 manifest")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    items = {"train": [], "selection": [], "test": []}
    for item in manifest["files"]:
        items[item["split"]].append(item)
    parse_report = {}

    def load_split(split: str):
        loaded = {}
        failures = []
        for item in items[split]:
            path = RAW_DIR / item["filename"]
            if path.stat().st_size != item["bytes"] or sha256_path(path) != item["sha256"]:
                raise RuntimeError(f"frozen source mismatch: {item['filename']}")
            parsed = parse_influx_bmc(path)
            count = len(parsed["rows"])
            parse_report[item["filename"]] = {
                "split": split,
                "total_data_rows": parsed["total_data_rows"],
                "valid_rows": count,
                "invalid_rows": parsed["invalid_rows"],
            }
            if count < MIN_VALID_ROWS:
                failures.append({"filename": item["filename"], "valid_rows": count})
            else:
                loaded[item["filename"]] = parsed["rows"]
        return loaded, failures

    train_runs, train_failures = load_split("train")
    selection_runs, selection_failures = load_split("selection")
    development_failures = train_failures + selection_failures
    if development_failures:
        RESULT.write_text(json.dumps({
            "study_id": "E13",
            "decision": "h_enc_07_not_supported",
            "status": "development_data_quality_failure",
            "final_test_opened": False,
            "failures": development_failures,
            "parse_report": parse_report,
        }, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
        return

    development = select_and_refit(train_runs, selection_runs)
    frozen_record = {
        "study_id": "E13",
        "manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "minimum_valid_rows": MIN_VALID_ROWS,
        "created_before_final_test_load": True,
        "final_test_filenames": [item["filename"] for item in items["test"]],
        **development,
    }
    FROZEN.write_text(
        json.dumps(frozen_record, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    frozen_sha256 = sha256_path(FROZEN)

    test_runs, test_failures = load_split("test")
    if test_failures:
        result = {
            "study_id": "E13",
            "decision": "h_enc_07_not_supported",
            "status": "final_test_data_quality_failure",
            "manifest_sha256": EXPECTED_MANIFEST_SHA256,
            "frozen_model_sha256": frozen_sha256,
            "created_before_final_test_load": True,
            "failures": test_failures,
            "parse_report": parse_report,
        }
    else:
        final = evaluate_frozen(frozen_record["frozen_models"], test_runs)
        result = {
            "study_id": "E13",
            "status": "completed",
            "manifest_sha256": EXPECTED_MANIFEST_SHA256,
            "frozen_model_sha256": frozen_sha256,
            "created_before_final_test_load": True,
            "minimum_valid_rows": MIN_VALID_ROWS,
            "split_file_counts": {key: len(value) for key, value in items.items()},
            "parse_report": parse_report,
            "experiment": {**development, **final},
            "limitations": [
                "One public dual-socket server; no cross-server confirmation.",
                "BMC component telemetry is not a room-coordinate spatial field.",
                "No physical PC chassis or NTC sensor was used.",
                "E13 follows an E12 development-only availability failure.",
            ],
        }
    RESULT.write_text(
        json.dumps(result, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": result["status"],
        "decision": result.get("experiment", {}).get("decision", result.get("decision")),
        "frozen_model_sha256": frozen_sha256,
        "test_failures": test_failures,
        "test": result.get("experiment", {}).get("test"),
        "gates": result.get("experiment", {}).get("gates"),
    }, indent=2))


if __name__ == "__main__":
    main()
