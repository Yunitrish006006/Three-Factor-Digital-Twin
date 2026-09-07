#!/usr/bin/env python3
"""Download and freeze complete BMCDATA CSV runs for E12."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from urllib.request import urlopen


SOURCE_BASE = "https://raw.githubusercontent.com/arealuser/bmcdata/master/data"
OUTPUT_DIR = Path("outputs/data/enclosure/bmc_cross_run_e12/raw")
MANIFEST_PATH = Path("outputs/data/enclosure/bmc_cross_run_e12_manifest.json")
SPLITS = {
    "train": [
        "202304252143", "202304252201", "202304252221", "202304261725",
        "202304281100", "202304281732", "202306172153", "202306181509",
        "202306181534", "202306181653", "202306191023", "202306191544",
    ],
    "selection": [
        "202307052240", "202307052309", "202307191620", "202307201552",
        "202307211550",
    ],
    "test": [
        "202307301643", "202307301734", "202307301819", "202307301853",
        "202307302018", "202307311829", "202308011635", "202308011759",
        "202308051600", "202308051718", "202401042141", "202401042237",
        "202401042338", "202401050043",
    ],
}


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_split() -> None:
    groups = [set(names) for names in SPLITS.values()]
    if sum(len(group) for group in groups) != len(set().union(*groups)):
        raise RuntimeError("E12 split filenames overlap")


def download(url: str, path: Path) -> None:
    with urlopen(url, timeout=30) as response, path.open("wb") as handle:
        while True:
            block = response.read(1024 * 1024)
            if not block:
                break
            handle.write(block)


def main() -> None:
    validate_split()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    frozen = None
    if MANIFEST_PATH.exists():
        frozen = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    expected = {
        item["filename"]: item for item in frozen.get("files", [])
    } if frozen else {}
    records = []
    for split, stems in SPLITS.items():
        for stem in stems:
            filename = f"{stem}.csv"
            url = f"{SOURCE_BASE}/{filename}"
            path = OUTPUT_DIR / filename
            if not path.exists():
                download(url, path)
            record = {
                "filename": filename,
                "split": split,
                "url": url,
                "bytes": path.stat().st_size,
                "sha256": sha256_path(path),
            }
            if filename in expected:
                prior = expected[filename]
                for field in ("split", "bytes", "sha256"):
                    if record[field] != prior[field]:
                        raise RuntimeError(
                            f"frozen manifest mismatch for {filename}: {field}"
                        )
            records.append(record)
    manifest = {
        "study_id": "E12",
        "retrieval_date": str(date.today()),
        "source_repository": "https://github.com/arealuser/bmcdata",
        "source_license": "MIT",
        "source_note": "Mutable master URLs are frozen by complete-file SHA-256.",
        "split_counts": {key: len(value) for key, value in SPLITS.items()},
        "files": records,
    }
    if frozen and manifest != frozen:
        raise RuntimeError("existing E12 manifest metadata changed")
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"E12 manifest frozen: {len(records)} files at {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
