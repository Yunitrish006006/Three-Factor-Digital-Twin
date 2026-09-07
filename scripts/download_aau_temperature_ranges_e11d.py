#!/usr/bin/env python3
"""Download preregistered AAU v4 byte ranges for E11D."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


URL = "https://zenodo.org/records/19398358/files/AAU_temperature_and_power_use.csv?download=1"
RANGE_BYTES = 4_194_304
STARTS = [
    15_953_778,
    79_768_891,
    143_584_004,
    207_399_117,
    271_214_230,
    335_029_343,
    398_844_456,
    462_659_569,
    526_474_682,
    590_289_795,
    654_104_908,
]
E11B_STARTS = [i * 63_815_113 for i in range(12)]
E11C_STARTS = [
    31_907_556,
    95_722_669,
    159_537_782,
    223_352_894,
    287_168_007,
    350_983_120,
    414_798_233,
    478_613_346,
    542_428_459,
    606_243_571,
    670_058_684,
]


def overlaps(start_a: int, start_b: int) -> bool:
    return start_a < start_b + RANGE_BYTES and start_b < start_a + RANGE_BYTES


def validate_ranges() -> None:
    forbidden = [("E11B", start) for start in E11B_STARTS] + [
        ("E11C", start) for start in E11C_STARTS
    ]
    for index, start in enumerate(STARTS):
        for other in STARTS[index + 1 :]:
            if overlaps(start, other):
                raise ValueError(f"E11D overlap: {start} and {other}")
        for experiment, other in forbidden:
            if overlaps(start, other):
                raise ValueError(f"E11D {start} overlaps {experiment} {other}")


def request_range(url: str, start: int, end: int) -> tuple[bytes, object]:
    request = urllib.request.Request(
        url,
        headers={"Range": f"bytes={start}-{end}", "User-Agent": "school-e11d/1.0"},
    )
    response = urllib.request.urlopen(request, timeout=120)
    if response.status != 206:
        raise RuntimeError(f"expected HTTP 206, received {response.status}")
    payload = response.read()
    if len(payload) != end - start + 1:
        raise RuntimeError(f"expected {end - start + 1} bytes, received {len(payload)}")
    return payload, response.headers


def read_curl_range(path: Path, headers_path: Path, start: int, end: int) -> tuple[bytes, dict[str, str]]:
    payload = path.read_bytes()
    if len(payload) != end - start + 1:
        raise RuntimeError(f"expected {end - start + 1} bytes in {path}, received {len(payload)}")
    header_text = headers_path.read_text(encoding="iso-8859-1")
    statuses = re.findall(r"^HTTP/\S+\s+(\d+)", header_text, flags=re.MULTILINE)
    if not statuses or statuses[-1] != "206":
        raise RuntimeError(f"expected final HTTP 206 in {headers_path}, received {statuses}")
    ranges = re.findall(r"^content-range:\s*(.+)$", header_text, flags=re.MULTILINE | re.IGNORECASE)
    return payload, {"Content-Range": ranges[-1].strip() if ranges else None}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=URL)
    parser.add_argument("--output-dir", type=Path, default=Path("/tmp/aau_server_room_temperature_ranges_e11d"))
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("outputs/data/enclosure/aau_temperature_ranges_e11d_manifest.json"),
    )
    parser.add_argument(
        "--from-existing-curl",
        action="store_true",
        help="validate curl-downloaded fragments in output-dir and build the manifest without network access",
    )
    args = parser.parse_args()
    validate_ranges()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if args.from_existing_curl:
        schema, schema_headers = read_curl_range(
            args.output_dir / "schema.part", args.output_dir / "schema.headers", 0, 65_535
        )
    else:
        schema, schema_headers = request_range(args.url, 0, 65_535)
    first_newline = schema.find(b"\n")
    if first_newline < 0:
        raise RuntimeError("CSV header did not fit in schema request")
    csv_header = schema[:first_newline].decode("utf-8-sig").rstrip("\r")
    fragments = []
    for index, start in enumerate(STARTS, 1):
        end = start + RANGE_BYTES - 1
        path = args.output_dir / f"fragment_{index:02d}_{start}_{end}.csv.part"
        if args.from_existing_curl:
            payload, headers = read_curl_range(
                path, args.output_dir / f"fragment_{index:02d}.headers", start, end
            )
        else:
            payload, headers = request_range(args.url, start, end)
            path.write_bytes(payload)
        digest = hashlib.sha256(payload).hexdigest()
        fragments.append(
            {
                "index": index,
                "start": start,
                "end": end,
                "bytes": len(payload),
                "sha256": digest,
                "path": str(path),
                "http_status": 206,
                "content_range": headers.get("Content-Range"),
            }
        )
        print(f"downloaded {index}/{len(STARTS)} start={start} sha256={digest[:12]}", flush=True)
    manifest = {
        "experiment": "E11D",
        "dataset": "AAU Server Room v4",
        "doi": "10.5281/zenodo.19398358",
        "url": args.url,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "range_bytes": RANGE_BYTES,
        "offset_policy": "fixed quarter-gap offsets preregistered before observation retrieval",
        "schema_request": {
            "start": 0,
            "end": 65_535,
            "use": "CSV header only; no observations accepted",
            "http_status": 206,
            "content_range": schema_headers.get("Content-Range"),
        },
        "csv_header": csv_header,
        "boundary_policy": "discard first and last records from each observation fragment",
        "fragments": fragments,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.manifest}", flush=True)


if __name__ == "__main__":
    main()
