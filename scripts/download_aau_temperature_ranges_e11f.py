#!/usr/bin/env python3
"""Validate and freeze the one-time reserved E11F AAU fragments."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
URL = "https://zenodo.org/records/19398358/files/AAU_temperature_and_power_use.csv?download=1"
RANGE_BYTES = 4 * 1024 * 1024
TOTAL_BYTES = 706160545
STARTS = (
    55838224,
    119653337,
    183468450,
    247283563,
    311098676,
    374913789,
    438728902,
    502544015,
    566359128,
    630174241,
    693989354,
)
RAW_DIR = Path("/tmp/aau_server_room_temperature_ranges_e11f")
MANIFEST = ROOT / "outputs/data/enclosure/aau_temperature_ranges_e11f_manifest.json"
E11E_MANIFEST = ROOT / "outputs/data/enclosure/aau_temperature_ranges_e11e_manifest.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def intervals_from_document(value: object) -> list[tuple[int, int]]:
    intervals: list[tuple[int, int]] = []
    if isinstance(value, dict):
        if isinstance(value.get("start"), int) and isinstance(value.get("end"), int):
            intervals.append((int(value["start"]), int(value["end"])))
        for child in value.values():
            intervals.extend(intervals_from_document(child))
    elif isinstance(value, list):
        for child in value:
            intervals.extend(intervals_from_document(child))
    return intervals


def validate_intervals() -> None:
    occupied: list[tuple[int, int, str]] = []
    for path in sorted((ROOT / "outputs/data/enclosure").glob("*manifest.json")):
        if path == MANIFEST:
            continue
        document = json.loads(path.read_text(encoding="utf-8"))
        for start, end in intervals_from_document(document):
            if start == 0 and end <= 65535:
                continue
            occupied.append((start, end, path.name))
    proposed = [(start, start + RANGE_BYTES - 1) for start in STARTS]
    for start, end in proposed:
        if end >= TOTAL_BYTES:
            raise ValueError(f"range exceeds object: {start}-{end}")
        for used_start, used_end, source in occupied:
            if max(start, used_start) <= min(end, used_end):
                raise ValueError(
                    f"E11F range {start}-{end} overlaps {source} {used_start}-{used_end}"
                )


def fragment_path(index: int, start: int, end: int) -> Path:
    return RAW_DIR / f"fragment_{index:02d}_{start}_{end}.csv.part"


def freeze_manifest() -> None:
    validate_intervals()
    source = json.loads(E11E_MANIFEST.read_text(encoding="utf-8"))
    fragments: list[dict[str, object]] = []
    for index, start in enumerate(STARTS, 1):
        end = start + RANGE_BYTES - 1
        path = fragment_path(index, start, end)
        if not path.exists() or path.stat().st_size != RANGE_BYTES:
            raise ValueError(f"missing or wrong-sized fragment: {path}")
        fragments.append(
            {
                "index": index,
                "start": start,
                "end": end,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "path": str(path),
                "http_status": 206,
                "content_range": f"bytes {start}-{end}/{TOTAL_BYTES}",
            }
        )
    document = {
        "experiment": "E11F",
        "purpose": "one_time_commissioning_confirmation",
        "dataset": "AAU Server Room v4",
        "doi": "10.5281/zenodo.19398358",
        "url": URL,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "range_bytes": RANGE_BYTES,
        "offset_policy": "reserved seven-eighth phase accessed once after E11H advancement",
        "csv_header": source["csv_header"],
        "boundary_policy": "discard first and last records from each observation fragment",
        "fragments": fragments,
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {MANIFEST}")


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check-overlaps", action="store_true")
    mode.add_argument("--from-existing-curl", action="store_true")
    args = parser.parse_args()
    if args.check_overlaps:
        validate_intervals()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        for index, start in enumerate(STARTS, 1):
            end = start + RANGE_BYTES - 1
            print(f"{index:02d} {start}-{end} {fragment_path(index, start, end)}")
        return
    freeze_manifest()


if __name__ == "__main__":
    main()

