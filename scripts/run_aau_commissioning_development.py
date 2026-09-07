#!/usr/bin/env python3
"""Run E11H chronological commissioning development."""

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

from digital_twin.enclosure.aau_commissioning import evaluate_commissioning
from scripts.run_aau_hierarchical_development import (
    extract_frozen_sensor_metadata,
    load_minute_snapshots,
)


MANIFEST = ROOT / "outputs/data/enclosure/aau_temperature_ranges_e11h_manifest.json"
METADATA = ROOT / "outputs/data/enclosure/aau_local_idw_confirmation.json"
E11G_RESULT = ROOT / "outputs/data/enclosure/aau_tail_safe_development.json"
OUTPUT = ROOT / "outputs/data/enclosure/aau_commissioning_development.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    metadata_document = json.loads(METADATA.read_text(encoding="utf-8"))
    e11g = json.loads(E11G_RESULT.read_text(encoding="utf-8"))
    metadata = extract_frozen_sensor_metadata(metadata_document)
    header = next(csv.reader([manifest["csv_header"]]))
    sensor_columns = {
        index: (column, column)
        for index, column in enumerate(header)
        if column in metadata
    }
    fragment_paths = [Path(item["path"]) for item in manifest["fragments"]]
    snapshots, diagnostics = load_minute_snapshots(fragment_paths, header, sensor_columns)
    evaluation = evaluate_commissioning(
        snapshots,
        metadata,
        e11g["evaluation"]["deployment_map"],
    )
    result = {
        "experiment": "E11H",
        "purpose": "new_split_commissioning_calibration_development",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "manifest": str(MANIFEST.relative_to(ROOT)),
            "manifest_sha256": sha256_file(MANIFEST),
            "frozen_metadata": str(METADATA.relative_to(ROOT)),
            "frozen_metadata_sha256": sha256_file(METADATA),
            "e11g_result": str(E11G_RESULT.relative_to(ROOT)),
            "e11g_result_sha256": sha256_file(E11G_RESULT),
        },
        "parse": diagnostics,
        "sensor_count": len(metadata),
        "evaluation": evaluation,
        "e11f_accessed": False,
        "interpretation_limit": (
            "Commissioning-assisted development evidence; not zero-shot transfer or E11F confirmation."
        ),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

