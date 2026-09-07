#!/usr/bin/env python3
"""Run preregistered E11E hierarchical role-local development."""

from __future__ import annotations

import csv
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from digital_twin.enclosure.aau_hierarchical import (  # noqa: E402
    evaluate_hierarchical_grid,
    extract_frozen_sensor_metadata,
)
from digital_twin.enclosure.aau_role import load_minute_snapshots, sha256_file  # noqa: E402


MANIFEST = ROOT / "outputs/data/enclosure/aau_temperature_ranges_e11e_manifest.json"
E11C_RESULT = ROOT / "outputs/data/enclosure/aau_local_idw_confirmation.json"
OUTPUT = ROOT / "outputs/data/enclosure/aau_hierarchical_development.json"
EXPECTED_E11C_SHA256 = "0b667ca8bb959e332aeff0155b9dceb1318dca3f91a26c1aa5552fb6bfef7055"


def main() -> None:
    if sha256_file(E11C_RESULT) != EXPECTED_E11C_SHA256:
        raise RuntimeError("frozen E11C metadata hash mismatch")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    prior = json.loads(E11C_RESULT.read_text(encoding="utf-8"))
    metadata = extract_frozen_sensor_metadata(prior)
    if len(metadata) != 42:
        raise RuntimeError(f"expected 42 frozen sensors, received {len(metadata)}")
    sample = manifest["csv_header"]
    dialect = csv.Sniffer().sniff(sample, delimiters=",;")
    header = next(csv.reader(io.StringIO(sample), dialect))
    header_indices = {column: index for index, column in enumerate(header)}
    missing = sorted(set(metadata) - set(header_indices))
    if missing:
        raise RuntimeError(f"frozen sensor columns missing from E11E header: {missing}")
    sensor_columns = {
        header_indices[column]: (column, str(item["role"])) for column, item in metadata.items()
    }
    fragment_paths = [Path(item["path"]) for item in manifest["fragments"]]
    snapshots, parse_stats = load_minute_snapshots(fragment_paths, header, sensor_columns)
    if not snapshots:
        raise RuntimeError("no complete E11E one-minute snapshots")
    evaluation = evaluate_hierarchical_grid(snapshots, metadata)
    result = {
        "experiment": "E11E", "purpose": "development_only", "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "preregistration": "openspec/changes/develop-aau-hierarchical-role-local/protocol.md",
        "inputs": {"manifest": str(MANIFEST.relative_to(ROOT)), "manifest_sha256": sha256_file(MANIFEST),
                   "frozen_metadata": str(E11C_RESULT.relative_to(ROOT)), "frozen_metadata_sha256": EXPECTED_E11C_SHA256},
        "parse": parse_stats, "sensor_count": len(metadata), "evaluation": evaluation,
        "e11f_accessed": False,
        "interpretation_limit": "E11E selects a candidate only; it does not confirm H-ENC-05 or generalization.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "development_decision": evaluation["development_decision"],
                      "selected_candidate": evaluation["selected_candidate"],
                      "passing_candidates": len(evaluation["passing_candidates"])}, indent=2))


if __name__ == "__main__":
    main()

