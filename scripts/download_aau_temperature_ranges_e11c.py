#!/usr/bin/env python3
"""Download preregistered, E11B-disjoint AAU byte ranges for E11C."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = "https://zenodo.org/api/records/19398358/files/AAU_temperature_and_power_use.csv/content"
SOURCE_BYTES = 706160545
RANGE_SIZE = 4194304
OFFSETS = (
    31907556,
    95722669,
    159537782,
    223352894,
    287168007,
    350983120,
    414798233,
    478613346,
    542428459,
    606243571,
    670058684,
)
E11B_OFFSETS = (
    0,
    63815113,
    127630226,
    191445338,
    255260451,
    319075564,
    382890677,
    446705790,
    510520903,
    574336015,
    638151128,
    701966241,
)
CSV_HEADER = tuple(
    "Time [Date/Time],Power Ch 1 (W),Power Ch 2 (W),Power Ch 3 (W),"
    "Temperature mod 1 ch 1,Temperature mod 1 ch 2,Temperature mod 1 ch 3,Temperature mod 1 ch 4,Temperature mod 1 ch 5,Temperature mod 1 ch 6,Temperature mod 1 ch 7,Temperature mod 1 ch 8,"
    "Temperature mod 2 ch 1,Temperature mod 2 ch 2,Temperature mod 2 ch 3,Temperature mod 2 ch 4,Temperature mod 2 ch 5,Temperature mod 2 ch 6,Temperature mod 2 ch 7,Temperature mod 2 ch 8,"
    "Temperature mod 3 ch 1,Temperature mod 3 ch 2,Temperature mod 3 ch 3,Temperature mod 3 ch 4,Temperature mod 3 ch 5,Temperature mod 3 ch 6,Temperature mod 3 ch 7,Temperature mod 3 ch 8,"
    "Temperature mod 4 ch 1,Temperature mod 4 ch 2,Temperature mod 4 ch 3,Temperature mod 4 ch 4,Temperature mod 4 ch 5,Temperature mod 4 ch 6,Temperature mod 4 ch 7,Temperature mod 4 ch 8,"
    "Temperature mod 5 ch 1,Temperature mod 5 ch 2,Temperature mod 5 ch 3,Temperature mod 5 ch 4,"
    "Temperature mod 6 ch 1,Temperature mod 6 ch 2,Temperature mod 6 ch 3,Temperature mod 6 ch 4,"
    "Temperature mod 7 ch 1,Temperature mod 7 ch 2,Temperature mod 7 ch 3,Temperature mod 7 ch 4,"
    "Temperature mod 8 ch 1,Temperature mod 8 ch 2,Temperature mod 8 ch 3,Temperature mod 8 ch 4"
    .split(",")
)


def intervals_overlap(left_start: int, right_start: int) -> bool:
    left_end = left_start + RANGE_SIZE - 1
    right_end = right_start + RANGE_SIZE - 1
    return left_start <= right_end and right_start <= left_end


def validate_offsets() -> None:
    if len(OFFSETS) != 11 or len(set(OFFSETS)) != 11:
        raise ValueError("E11C requires 11 unique gap-centered offsets")
    for offset in OFFSETS:
        if offset < 0 or offset + RANGE_SIZE > SOURCE_BYTES:
            raise ValueError(f"out-of-bounds offset: {offset}")
        if any(intervals_overlap(offset, discovery) for discovery in E11B_OFFSETS):
            raise ValueError(f"E11C offset overlaps E11B: {offset}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=Path("/tmp/aau_server_room_temperature_ranges_e11c"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "outputs/data/enclosure/aau_temperature_ranges_e11c_manifest.json",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    validate_offsets()
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    fragments = []
    for index, start in enumerate(OFFSETS):
        end = start + RANGE_SIZE - 1
        path = args.raw_dir / f"range_{index:02d}_{start}_{end}.csv"
        retrieval = "reused_existing_exact_size_fragment"
        if not path.exists() or path.stat().st_size != RANGE_SIZE:
            request = Request(
                SOURCE_URL,
                headers={
                    "Range": f"bytes={start}-{end}",
                    "User-Agent": "school-e11c-research/1.0",
                },
            )
            with urlopen(request, timeout=120) as response:
                if response.status != 206:
                    raise RuntimeError(f"range {index}: expected HTTP 206, got {response.status}")
                content_range = response.headers.get("Content-Range", "")
                if not content_range.startswith(f"bytes {start}-{end}/"):
                    raise RuntimeError(f"range {index}: unexpected Content-Range {content_range!r}")
                payload = response.read(RANGE_SIZE + 1)
            if len(payload) != RANGE_SIZE:
                raise RuntimeError(f"range {index}: expected {RANGE_SIZE} bytes, got {len(payload)}")
            temporary = path.with_suffix(path.suffix + ".part")
            temporary.write_bytes(payload)
            temporary.replace(path)
            retrieval = "http_206"
        print(f"range {index + 1}/11: {start}-{end} {retrieval}", flush=True)
        fragments.append(
            {
                "index": index,
                "start": start,
                "end": end,
                "bytes": path.stat().st_size,
                "path": str(path),
                "sha256": sha256_file(path),
                "retrieval": retrieval,
            }
        )

    manifest = {
        "schema_version": "aau-temperature-ranges-e11c-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "doi": "10.5281/zenodo.19398358",
            "url": SOURCE_URL,
            "record_id": 19398358,
            "version": "v4",
            "file": "AAU_temperature_and_power_use.csv",
            "bytes": SOURCE_BYTES,
            "md5": "fdb84fef0733db5a0a9564e028725494",
            "license": None,
            "license_note": "Zenodo record is public but REST rights metadata was null on 2026-08-23",
        },
        "sampling": {
            "strategy": "eleven_gap_centered_disjoint_byte_ranges",
            "range_count": len(OFFSETS),
            "range_size_bytes": RANGE_SIZE,
            "offsets": list(OFFSETS),
            "e11b_offsets": list(E11B_OFFSETS),
            "overlap_check": "passed",
        },
        "csv_header": list(CSV_HEADER),
        "csv_header_provenance": "source byte-zero schema fixed before E11C; no byte-zero observation row is used",
        "fragments": fragments,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}", flush=True)


if __name__ == "__main__":
    main()
