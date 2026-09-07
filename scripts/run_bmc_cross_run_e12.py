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


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    items = {"train": [], "selection": [], "test": []}
    for item in manifest["files"]:
        items[item["split"]].append(item)
    if {key: len(value) for key, value in items.items()} != {
        "train": 12, "selection": 5, "test": 14,
    }:
        raise RuntimeError("unexpected E12 manifest split counts")
    parse_report = {}
    def load_split(split: str) -> dict[str, list[dict]]:
        loaded = {}
        for item in items[split]:
            path = RAW_DIR / item["filename"]
            if path.stat().st_size != item["bytes"] or sha256_path(path) != item["sha256"]:
                raise RuntimeError(f"frozen source mismatch: {item['filename']}")
            parsed = parse_influx_bmc(path)
            if len(parsed["rows"]) < 30:
                raise RuntimeError(f"insufficient valid rows: {item['filename']}")
            loaded[item["filename"]] = parsed["rows"]
            parse_report[item["filename"]] = {
                "split": split,
                "total_data_rows": parsed["total_data_rows"],
                "valid_rows": len(parsed["rows"]),
                "invalid_rows": parsed["invalid_rows"],
            }
        return loaded

    train_runs = load_split("train")
    selection_runs = load_split("selection")
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

    test_runs = load_split("test")
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


if __name__ == "__main__":
    main()
