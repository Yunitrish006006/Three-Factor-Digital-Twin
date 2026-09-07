#!/usr/bin/env python3
"""Run the frozen E11F commissioning confirmation exactly once."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from digital_twin.enclosure.aau_commissioning import evaluate_frozen_confirmation
from scripts.run_aau_hierarchical_development import (
    extract_frozen_sensor_metadata,
    load_minute_snapshots,
)


MANIFEST = ROOT / "outputs/data/enclosure/aau_temperature_ranges_e11f_manifest.json"
METADATA = ROOT / "outputs/data/enclosure/aau_local_idw_confirmation.json"
E11G_RESULT = ROOT / "outputs/data/enclosure/aau_tail_safe_development.json"
E11H_RESULT = ROOT / "outputs/data/enclosure/aau_commissioning_development.json"
OUTPUT = ROOT / "outputs/data/enclosure/aau_commissioning_confirmation_e11f.json"
EXPECTED_E11H_SHA256 = "b76ecfe3e597d0641515df60b0d6636ed9a0ff1e23ebcb2852a225d4eee490e9"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> None:
    if sha256_file(E11H_RESULT) != EXPECTED_E11H_SHA256:
        raise ValueError("frozen E11H result hash changed")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    metadata_document = json.loads(METADATA.read_text(encoding="utf-8"))
    e11g = json.loads(E11G_RESULT.read_text(encoding="utf-8"))
    e11h = json.loads(E11H_RESULT.read_text(encoding="utf-8"))
    metadata = extract_frozen_sensor_metadata(metadata_document)
    header = next(csv.reader([manifest["csv_header"]]))
    sensor_columns = {
        index: (column, column)
        for index, column in enumerate(header)
        if column in metadata
    }
    fragment_paths = [Path(item["path"]) for item in manifest["fragments"]]
    snapshots, diagnostics = load_minute_snapshots(fragment_paths, header, sensor_columns)
    evaluation = evaluate_frozen_confirmation(
        snapshots,
        metadata,
        e11g["evaluation"]["deployment_map"],
        e11h["evaluation"]["selected_models"],
    )
    e11f_days = set(evaluation["day_mae_improvement_c"])
    e11h_days = set(e11h["evaluation"]["chronology"]["calibration_days"])
    e11h_days.add(e11h["evaluation"]["chronology"]["selection_day"])
    e11h_days.update(e11h["evaluation"]["chronology"]["test_days"])
    e11g_days = set(e11g["evaluation"]["day_mae_improvement_c"])
    evaluation["calendar_overlap"] = {
        "e11f_days": sorted(e11f_days),
        "overlap_with_e11g": sorted(e11f_days & e11g_days),
        "overlap_with_e11h": sorted(e11f_days & e11h_days),
        "calendar_day_disjoint": not bool(e11f_days & (e11g_days | e11h_days)),
        "claim_limit": "unseen bytes within one AAU campaign",
    }
    result = {
        "experiment": "E11F",
        "purpose": "one_time_frozen_commissioning_confirmation",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "manifest": str(MANIFEST.relative_to(ROOT)),
            "manifest_sha256": sha256_file(MANIFEST),
            "frozen_metadata_sha256": sha256_file(METADATA),
            "e11g_result_sha256": sha256_file(E11G_RESULT),
            "e11h_result_sha256": sha256_file(E11H_RESULT),
        },
        "parse": diagnostics,
        "evaluation": evaluation,
        "refit_performed": False,
        "interpretation_limit": (
            "Calibration-assisted unseen-byte confirmation within one campaign; not cross-enclosure or NTC hardware validation."
        ),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

