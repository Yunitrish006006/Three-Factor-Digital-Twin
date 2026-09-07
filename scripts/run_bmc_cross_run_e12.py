#!/usr/bin/env python3
"""Run the preregistered E12 BMC cross-run evaluation."""

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


MANIFEST = Path("outputs/data/enclosure/bmc_cross_run_e12_manifest.json")
RAW_DIR = Path("outputs/data/enclosure/bmc_cross_run_e12/raw")
RESULT = Path("outputs/data/enclosure/bmc_cross_run_e12_result.json")
FROZEN = Path("outputs/data/enclosure/bmc_cross_run_e12_frozen_model.json")


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    items = {"train": [], "selection": [], "test": []}
    for item in manifest["files"]:
        items[item["split"]].append(item)
    if {key: len(value) for key, value in items.items()} != {
        "train": 12, "selection": 5, "test": 14,
    }:
        raise RuntimeError("unexpected E12 manifest split counts")
    parse_report = {}
    def load_split(split: str) -> tuple[dict[str, list[dict]], list[dict]]:
        loaded = {}
        failures = []
        for item in items[split]:
            path = RAW_DIR / item["filename"]
            if path.stat().st_size != item["bytes"] or sha256_path(path) != item["sha256"]:
                raise RuntimeError(f"frozen source mismatch: {item['filename']}")
            parsed = parse_influx_bmc(path, normalize_units=False)
            if len(parsed["rows"]) < 30:
                failures.append({
                    "filename": item["filename"],
                    "valid_rows": len(parsed["rows"]),
                    "required_rows": 30,
                })
                parse_report[item["filename"]] = {
                    "split": split,
                    "total_data_rows": parsed["total_data_rows"],
                    "valid_rows": len(parsed["rows"]),
                    "invalid_rows": parsed["invalid_rows"],
                }
                continue
            loaded[item["filename"]] = parsed["rows"]
            parse_report[item["filename"]] = {
                "split": split,
                "total_data_rows": parsed["total_data_rows"],
                "valid_rows": len(parsed["rows"]),
                "invalid_rows": parsed["invalid_rows"],
            }
        return loaded, failures

    train_runs, train_failures = load_split("train")
    selection_runs, selection_failures = load_split("selection")
    development_failures = train_failures + selection_failures
    if development_failures:
        result = {
            "study_id": "E12",
            "status": "development_data_quality_failure",
            "decision": "h_enc_06_not_evaluated",
            "manifest_sha256": sha256_path(MANIFEST),
            "minimum_valid_rows": 30,
            "final_test_opened": False,
            "failures": development_failures,
            "parse_report": parse_report,
            "claim_boundary": "Pretest data-availability failure; no accuracy conclusion.",
        }
        RESULT.parent.mkdir(parents=True, exist_ok=True)
        RESULT.write_text(
            json.dumps(result, ensure_ascii=True, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(result, indent=2))
        return 1
    development = select_and_refit(train_runs, selection_runs)
    frozen_record = {
        "study_id": "E12",
        "manifest_sha256": sha256_path(MANIFEST),
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
        raise RuntimeError(f"unexpected final-test data failures: {test_failures}")
    final = evaluate_frozen(frozen_record["frozen_models"], test_runs)
    result = {
        "study_id": "E12",
        "manifest_sha256": sha256_path(MANIFEST),
        "frozen_model_sha256": frozen_sha256,
        "created_before_final_test_load": True,
        "split_file_counts": {split: len(group) for split, group in items.items()},
        "parse_report": parse_report,
        "experiment": {**development, **final},
        "limitations": [
            "One public dual-socket server; no cross-server confirmation.",
            "BMC component telemetry is not a room-coordinate spatial field.",
            "No physical PC chassis or NTC sensor was used.",
            "Workload and fan labels come from upstream documentation, not CSV columns.",
        ],
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(result, ensure_ascii=True, indent=2) + "\n", encoding="utf-8"
    )
    experiment = result["experiment"]
    print(json.dumps({
        "decision": experiment["decision"],
        "baseline": experiment["test"]["baseline"]["pooled"],
        "model": experiment["test"]["model"]["pooled"],
        "wins": experiment["test"]["model_run_wins"],
        "ci": experiment["test"]["run_bootstrap_95_ci_c"],
        "gates": experiment["gates"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
