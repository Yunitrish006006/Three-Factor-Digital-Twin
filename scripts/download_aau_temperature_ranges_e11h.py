#!/usr/bin/env python3
"""Validate and freeze fixed E11H AAU byte-range fragments downloaded by curl."""

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
    7976889,
    71792002,
    135607115,
    199422228,
    263237341,
    327052454,
    390867567,
    454682680,
    518497793,
    582312906,
    646128019,
)
E11F_STARTS = (
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
RAW_DIR = Path("/tmp/aau_server_room_temperature_ranges_e11h")
MANIFEST = ROOT / "outputs/data/enclosure/aau_temperature_ranges_e11h_manifest.json"
E11E_MANIFEST = ROOT / "outputs/data/enclosure/aau_temperature_ranges_e11e_manifest.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
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


def existing_intervals() -> list[tuple[int, int, str]]:
    intervals: list[tuple[int, int, str]] = []
    for path in sorted((ROOT / "outputs/data/enclosure").glob("*manifest.json")):
        if path == MANIFEST:
            continue
        document = json.loads(path.read_text(encoding="utf-8"))
        for start, end in intervals_from_document(document):
            if start == 0 and end <= 65535:
                continue
            intervals.append((start, end, path.name))
    for start in E11F_STARTS:
        intervals.append((start, start + RANGE_BYTES - 1, "reserved_e11f"))
    return intervals


def validate_intervals() -> None:
    occupied = existing_intervals()
    proposed = [(start, start + RANGE_BYTES - 1) for start in STARTS]
    for start, end in proposed:
        if end >= TOTAL_BYTES:
            raise ValueError(f"range exceeds object: {start}-{end}")
        for used_start, used_end, source in occupied:
            if max(start, used_start) <= min(end, used_end):
                raise ValueError(
                    f"E11H range {start}-{end} overlaps {source} {used_start}-{used_end}"
                )
    for index, (start, end) in enumerate(proposed):
        for other_start, other_end in proposed[index + 1 :]:
            if max(start, other_start) <= min(end, other_end):
                raise ValueError("E11H proposed ranges overlap each other")


def fragment_path(index: int, start: int, end: int) -> Path:
    return RAW_DIR / f"fragment_{index:02d}_{start}_{end}.csv.part"


def freeze_manifest() -> None:
    validate_intervals()
    source = json.loads(E11E_MANIFEST.read_text(encoding="utf-8"))
    fragments: list[dict[str, object]] = []
    for index, start in enumerate(STARTS, 1):
        end = start + RANGE_BYTES - 1
        path = fragment_path(index, start, end)
        if not path.exists():
            raise FileNotFoundError(path)
        if path.stat().st_size != RANGE_BYTES:
            raise ValueError(f"wrong fragment size: {path} has {path.stat().st_size}")
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
        "experiment": "E11H",
        "purpose": "new_split_commissioning_development",
        "dataset": "AAU Server Room v4",
        "doi": "10.5281/zenodo.19398358",
        "url": URL,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "range_bytes": RANGE_BYTES,
        "offset_policy": "fixed one-eighth phase with manifest-wide and E11F overlap rejection",
        "reserved_e11f_starts_not_requested": list(E11F_STARTS),
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

