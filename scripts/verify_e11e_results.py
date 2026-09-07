#!/usr/bin/env python3
"""Verify E11E development evidence and synchronized artifacts."""

from __future__ import annotations

import hashlib
import json
import math
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "outputs/data/enclosure/aau_temperature_ranges_e11e_manifest.json"
RESULT = ROOT / "outputs/data/enclosure/aau_hierarchical_development.json"
MANIFEST_SHA = "873e155bceaaac530f004b1ef14d1cceb8356af83f5a9ace1638ec54a34919d6"
RESULT_SHA = "c345e1320bd7e1aed21fd67f04e661d555a18e6e0fd312f638bc350300eb732a"


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
        return any(token.encode() in archive.read(name) for name in archive.namelist() if name.endswith(".xml"))


def main() -> None:
    require(sha256(MANIFEST) == MANIFEST_SHA, "manifest SHA mismatch")
    require(sha256(RESULT) == RESULT_SHA, "result SHA mismatch")
    manifest = json.loads(MANIFEST.read_text())
    result = json.loads(RESULT.read_text())
    require(len(manifest["fragments"]) == 11, "fragment count mismatch")
    reserved = set(manifest["reserved_e11f_starts_not_requested"])
    require(not reserved.intersection(item["start"] for item in manifest["fragments"]), "E11F range accessed")
    for item in manifest["fragments"]:
        path = Path(item["path"])
        require(path.stat().st_size == 4_194_304 and sha256(path) == item["sha256"], f"raw mismatch {path}")
    evaluation = result["evaluation"]
    require(result["e11f_accessed"] is False, "E11F access flag mismatch")
    require(evaluation["development_decision"] == "no_candidate_forwarded", "decision mismatch")
    require(evaluation["selected_candidate"] is None and len(evaluation["passing_candidates"]) == 0, "candidate mismatch")
    best = evaluation["metrics"]["role_local_k5_p2"]
    require(math.isclose(best["mae_c"], 1.0186541515690029), "best MAE mismatch")
    require(math.isclose(best["p95_absolute_error_c"], 3.7699216381940865), "best P95 mismatch")
    require(evaluation["candidate_gates"]["role_local_k5_p2"]["sensor_wins"] == 25, "win count mismatch")
    require(all(not gate["conditions"]["p95_lower_than_stronger_baseline"] for gate in evaluation["candidate_gates"].values()), "unexpected P95 pass")
    sources = ["docs/thesis/thesis_draft_zh.md", "scripts/build_thesis_docx.py", "docs/papers/ieee/paper.tex",
               "scripts/build_thesis_pptx.py", "docs/thesis/presentation_outline_zh.md",
               "docs/thesis/presentation_outline_zh_30min.md",
               "docs/reports/professor_complete_experiment_overview_2026-08-03_zh.md"]
    for relative in sources:
        text = (ROOT / relative).read_text(encoding="utf-8")
        normalized = text.replace("\\_", "_")
        require("1.0187" in normalized and "no_candidate_forwarded" in normalized, f"stale source {relative}")
    for relative in ["docs/papers/thesis/thesis_draft_zh.docx", "outputs/papers/thesis_draft_zh.docx",
                     "outputs/papers/thesis_presentation_zh.pptx", "outputs/papers/thesis_presentation_zh_30min.pptx"]:
        require(archive_contains(ROOT / relative, "no_candidate_forwarded"), f"stale archive {relative}")
    print("E11E verification passed: development decision, untouched E11F, 7 sources, and outputs")


if __name__ == "__main__":
    main()
