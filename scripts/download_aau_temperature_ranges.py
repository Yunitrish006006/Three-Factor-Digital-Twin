from __future__ import annotations

import hashlib
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT))

from digital_twin.enclosure.aau_spatial import compute_range_offsets  # noqa: E402


SOURCE_DOI = "10.5281/zenodo.19398358"
SOURCE_URL = "https://zenodo.org/api/records/19398358/files/AAU_temperature_and_power_use.csv/content"
SOURCE_SIZE = 706_160_545
SOURCE_MD5 = "fdb84fef0733db5a0a9564e028725494"
RANGE_SIZE = 4_194_304
RANGE_COUNT = 12
RAW_DIR = Path("/tmp/aau_server_room_temperature_ranges")
MANIFEST_PATH = ROOT / "outputs" / "data" / "enclosure" / "aau_temperature_ranges_manifest.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _download_range(index: int, start: int, end: int) -> dict:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"range_{index:02d}_{start}_{end}.csv"
    expected_size = end - start + 1
    if path.is_file() and path.stat().st_size == expected_size:
        return {
            "index": index,
            "start": start,
            "end": end,
            "bytes": expected_size,
            "path": str(path),
            "sha256": _sha256(path),
            "retrieval": "reused_existing_exact_size_fragment",
        }

    request = urllib.request.Request(
        SOURCE_URL,
        headers={
            "Range": f"bytes={start}-{end}",
            "User-Agent": "school-e11b-research/1.0",
        },
    )
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                status = getattr(response, "status", None)
                content_range = response.headers.get("Content-Range")
                if status != 206:
                    raise RuntimeError(f"expected HTTP 206 for Range request, got {status}")
                data = response.read(expected_size + 1)
                if len(data) != expected_size:
                    raise RuntimeError(
                        f"range {index} expected {expected_size} bytes, received {len(data)}"
                    )
            temporary = path.with_suffix(path.suffix + ".part")
            temporary.write_bytes(data)
            temporary.replace(path)
            return {
                "index": index,
                "start": start,
                "end": end,
                "bytes": expected_size,
                "path": str(path),
                "sha256": hashlib.sha256(data).hexdigest(),
                "content_range": content_range,
                "retrieval": "downloaded",
                "attempt": attempt,
            }
        except Exception as exc:  # preserve final external-data failure
            last_error = exc
            if attempt < 3:
                time.sleep(2**attempt)
    raise RuntimeError(f"failed to retrieve range {index}: {last_error}")


def main() -> None:
    offsets = compute_range_offsets(SOURCE_SIZE, RANGE_SIZE, RANGE_COUNT)
    fragments = []
    for index, start in enumerate(offsets):
        end = start + RANGE_SIZE - 1
        fragment = _download_range(index, start, end)
        fragments.append(fragment)
        print(f"range {index + 1}/{RANGE_COUNT}: {start}-{end} {fragment['retrieval']}")

    payload = {
        "schema_version": "aau-temperature-ranges-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "doi": SOURCE_DOI,
            "url": SOURCE_URL,
            "record_id": 19398358,
            "version": "v4",
            "file": "AAU_temperature_and_power_use.csv",
            "bytes": SOURCE_SIZE,
            "md5": SOURCE_MD5,
            "license": None,
            "license_note": "Zenodo record is public but REST rights metadata was null on 2026-08-23",
        },
        "sampling": {
            "strategy": "twelve_evenly_spaced_byte_ranges",
            "range_count": RANGE_COUNT,
            "range_size_bytes": RANGE_SIZE,
            "offsets": offsets,
        },
        "fragments": fragments,
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
