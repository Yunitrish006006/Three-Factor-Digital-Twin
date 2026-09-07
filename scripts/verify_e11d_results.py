#!/usr/bin/env python3
"""Verify E11D evidence, raw hashes, synchronized sources, and generated outputs."""

from __future__ import annotations

import hashlib
import json
import math
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "outputs/data/enclosure/aau_temperature_ranges_e11d_manifest.json"
RESULT = ROOT / "outputs/data/enclosure/aau_role_conditioned_confirmation.json"
EXPECTED_MANIFEST_SHA = "3c030b7765f73fce878dd584faefd436f29e47203ef8ca95c923d4b56dc54f4e"
EXPECTED_RESULT_SHA = "1a7750cfaba8d87916ac96066d783cc8c335746dcf77d34d84c60516b5c4a747"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def archive_contains(path: Path, token: str) -> bool:
    with zipfile.ZipFile(path) as archive:
        return any(
            token.encode("utf-8") in archive.read(name)
            for name in archive.namelist()
            if name.endswith(".xml")
        )


def main() -> None:
    require(sha256(MANIFEST) == EXPECTED_MANIFEST_SHA, "manifest SHA-256 mismatch")
    require(sha256(RESULT) == EXPECTED_RESULT_SHA, "result SHA-256 mismatch")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(len(manifest["fragments"]) == 11, "expected 11 fragments")
    for item in manifest["fragments"]:
        path = Path(item["path"])
        require(path.stat().st_size == 4_194_304, f"byte count mismatch: {path}")
        require(sha256(path) == item["sha256"], f"raw SHA-256 mismatch: {path}")
        require(item["http_status"] == 206, f"HTTP status mismatch: {path}")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    require(result["decision"] == "supported", "H-ENC-04 decision mismatch")
    require(all(result["conditions"].values()), "not all registered conditions passed")
    evaluation = result["evaluation"]
    require(math.isclose(evaluation["global"]["mae_c"], 2.397198185633272), "global MAE mismatch")
    require(math.isclose(evaluation["role_conditioned"]["mae_c"], 1.6516642735658955), "role MAE mismatch")
    require(evaluation["per_sensor_wins"]["role_conditioned"] == 30, "sensor-win count mismatch")
    source_paths = [
        "docs/thesis/thesis_draft_zh.md",
        "scripts/build_thesis_docx.py",
        "docs/papers/ieee/paper.tex",
        "scripts/build_thesis_pptx.py",
        "docs/thesis/presentation_outline_zh.md",
        "docs/thesis/presentation_outline_zh_30min.md",
        "docs/reports/professor_complete_experiment_overview_2026-08-03_zh.md",
    ]
    for relative in source_paths:
        text = (ROOT / relative).read_text(encoding="utf-8")
        require("H-ENC-04" in text and "1.6517" in text, f"stale E11D source: {relative}")
    archives = [
        "docs/papers/thesis/thesis_draft_zh.docx",
        "outputs/papers/thesis_draft_zh.docx",
        "outputs/papers/thesis_presentation_zh.pptx",
        "outputs/papers/thesis_presentation_zh_30min.pptx",
    ]
    for relative in archives:
        require(archive_contains(ROOT / relative, "H-ENC-04"), f"stale generated archive: {relative}")
    outputs = [
        "docs/papers/thesis/thesis_draft_zh.pdf",
        "outputs/papers/thesis_draft_zh.pdf",
        "docs/papers/ieee/paper.pdf",
    ]
    for relative in outputs:
        path = ROOT / relative
        require(path.read_bytes()[:4] == b"%PDF" and path.stat().st_size > 10_000, f"invalid PDF: {relative}")
    print("E11D verification passed: evidence, 7 synchronized sources, raw fragments, and outputs")


if __name__ == "__main__":
    main()

