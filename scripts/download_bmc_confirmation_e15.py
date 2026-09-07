#!/usr/bin/env python3
"""Download the preregistered E15 BMC confirmation files and record hashes."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import date
from pathlib import Path
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "outputs/data/enclosure/bmc_confirmation_e15/raw"
MANIFEST_PATH = ROOT / "outputs/data/enclosure/bmc_confirmation_e15_manifest.json"
BASE_URL = "https://raw.githubusercontent.com/arealuser/bmcdata/master/data"
FILENAMES = (
    "202308022155.csv",
    "202308022222.csv",
    "202308051737.csv",
    "202308051757.csv",
    "202308051827.csv",
    "202308052003.csv",
    "202309212229.csv",
    "202309221110.csv",
    "202309222035.csv",
    "202310252044.csv",
    "202310252102.csv",
    "202310252230.csv",
    "202405241724.csv",
    "202405241940.csv",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(url: str, destination: Path) -> None:
    temporary = destination.with_suffix(destination.suffix + ".part")
    with urlopen(url, timeout=120) as response, temporary.open("wb") as output:
        while chunk := response.read(1024 * 1024):
            output.write(chunk)
    os.replace(temporary, destination)


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    records = []
    for filename in FILENAMES:
        destination = RAW_DIR / filename
        url = f"{BASE_URL}/{filename}"
        if not destination.exists() or destination.stat().st_size == 0:
            download(url, destination)
        records.append(
            {
                "filename": filename,
                "url": url,
                "bytes": destination.stat().st_size,
                "sha256": sha256(destination),
            }
        )

    manifest = {
        "study_id": "E15",
        "retrieval_date": date.today().isoformat(),
        "source_repository": "https://github.com/arealuser/bmcdata",
        "source_license": "MIT",
        "source_note": "Mutable master URLs are frozen by complete-file SHA-256.",
        "confirmation_file_count": len(records),
        "files": records,
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {MANIFEST_PATH} with {len(records)} files")


if __name__ == "__main__":
    main()
