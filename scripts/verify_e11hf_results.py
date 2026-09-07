#!/usr/bin/env python3
"""Verify E11H development and E11F frozen confirmation synchronization."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
E11H = ROOT / "outputs/data/enclosure/aau_commissioning_development.json"
E11F = ROOT / "outputs/data/enclosure/aau_commissioning_confirmation_e11f.json"
E11H_MANIFEST = ROOT / "outputs/data/enclosure/aau_temperature_ranges_e11h_manifest.json"
E11F_MANIFEST = ROOT / "outputs/data/enclosure/aau_temperature_ranges_e11f_manifest.json"
EXPECTED = {
    E11H: "b76ecfe3e597d0641515df60b0d6636ed9a0ff1e23ebcb2852a225d4eee490e9",
    E11F: "14c606e26f4da454b96d1e8911189df65e498f64f6b7fd1fac2f567461db5c3a",
    E11H_MANIFEST: "79a46e8f0df311292864d2c155597416af4ae4320d631f1dbd8a0b4206d012f0",
    E11F_MANIFEST: "d31e94a21124eeb789d1c2935ef7673781c7fddc2c3b31f447c70ffe739c214e",
}
SOURCE_PATHS = (
    "docs/thesis/thesis_draft_zh.md",
    "scripts/build_thesis_docx.py",
    "docs/papers/ieee/paper.tex",
    "scripts/build_thesis_pptx.py",
    "docs/thesis/presentation_outline_zh.md",
    "docs/thesis/presentation_outline_zh_30min.md",
    "docs/reports/professor_complete_experiment_overview_2026-08-03_zh.md",
)
ARCHIVE_PATHS = (
    "docs/papers/thesis/thesis_draft_zh.docx",
    "outputs/papers/thesis_draft_zh.docx",
    "outputs/papers/thesis_presentation_zh.pptx",
    "outputs/papers/thesis_presentation_zh_30min.pptx",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(actual: float, expected: float) -> bool:
    return abs(actual - expected) < 1e-12


def archive_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        return "\n".join(
            archive.read(name).decode("utf-8", errors="ignore")
            for name in archive.namelist()
            if name.endswith((".xml", ".rels"))
        )


def verify_manifest(path: Path) -> None:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    require(len(manifest["fragments"]) == 11, f"wrong fragment count {path}")
    for item in manifest["fragments"]:
        raw = Path(item["path"])
        require(raw.exists() and raw.stat().st_size == 4194304, f"bad raw fragment {raw}")
        require(sha256(raw) == item["sha256"], f"raw hash changed {raw}")


def main() -> None:
    for path, expected in EXPECTED.items():
        require(sha256(path) == expected, f"hash changed: {path}")
    verify_manifest(E11H_MANIFEST)
    verify_manifest(E11F_MANIFEST)
    e11h = json.loads(E11H.read_text(encoding="utf-8"))
    e11f = json.loads(E11F.read_text(encoding="utf-8"))
    h_eval = e11h["evaluation"]
    f_eval = e11f["evaluation"]
    require(h_eval["development_decision"] == "candidate_forwarded_to_e11f", "E11H decision changed")
    require(f_eval["confirmation_decision"] == "h_enc_05_supported_within_campaign", "E11F decision changed")
    require(e11f["refit_performed"] is False, "E11F refit flag changed")
    require(all(h_eval["gates"].values()) and all(f_eval["gates"].values()), "gate changed")
    require(h_eval["sensor_wins"] == 39 and f_eval["sensor_wins"] == 39, "sensor wins changed")
    h_model = h_eval["metrics"]["commissioning_sensor_map_v1"]
    f_model = f_eval["metrics"]["frozen_commissioning_sensor_map_v1"]
    require(close(float(h_model["mae_c"]), 0.4039132376297797), "E11H MAE changed")
    require(close(float(f_model["mae_c"]), 0.3965785782815501), "E11F MAE changed")
    require(close(float(f_model["rmse_c"]), 0.6723091414856732), "E11F RMSE changed")
    require(close(float(f_model["p95_absolute_error_c"]), 1.275633370788728), "E11F P95 changed")
    overlap = f_eval["calendar_overlap"]
    require(overlap["calendar_day_disjoint"] is False, "calendar overlap changed")
    require(len(overlap["overlap_with_e11g"]) == 11, "E11G overlap count changed")
    require(len(overlap["overlap_with_e11h"]) == 8, "E11H overlap count changed")
    for relative in SOURCE_PATHS:
        normalized = (ROOT / relative).read_text(encoding="utf-8").replace("\\_", "_")
        if relative.startswith("scripts/build_"):
            require("sync_e11hf_generated_artifacts" in normalized, f"missing E11HF hook {relative}")
        else:
            require("0.3966" in normalized and "h_enc_05_supported_within_campaign" in normalized, f"stale source {relative}")
    hook = (ROOT / "scripts/sync_e11hf_generated_artifacts.py").read_text(encoding="utf-8")
    require("0.3966" in hook and "h_enc_05_supported_within_campaign" in hook, "stale E11HF hook")
    for relative in ARCHIVE_PATHS:
        text = archive_text(ROOT / relative)
        require("0.3966" in text and "h_enc_05_supported_within_campaign" in text, f"stale archive {relative}")
    print("E11H/E11F verification passed: hashes, raw fragments, frozen no-refit result, calendar limit, sources, and outputs")


if __name__ == "__main__":
    main()

