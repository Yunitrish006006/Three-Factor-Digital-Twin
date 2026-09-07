#!/usr/bin/env python3
"""Verify frozen E11G evidence and synchronized artifact wording."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/data/enclosure/aau_tail_safe_development.json"
EXPECTED_SHA256 = "aef099fea6b37036fd32644f4897e2aea5e47922d525f072b7b01592928466ed"
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
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def archive_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        return "\n".join(
            archive.read(name).decode("utf-8", errors="ignore")
            for name in archive.namelist()
            if name.endswith((".xml", ".rels"))
        )


def close(actual: float, expected: float) -> bool:
    return abs(actual - expected) < 1e-12


def main() -> None:
    require(sha256(RESULT) == EXPECTED_SHA256, "E11G result hash changed")
    data = json.loads(RESULT.read_text(encoding="utf-8"))
    evaluation = data["evaluation"]
    baseline = evaluation["metrics"]["baseline_local_idw_k3_p2"]
    model = evaluation["metrics"]["tail_safe_sensor_map_v1"]
    require(data["e11f_accessed"] is False, "E11F access flag changed")
    e11f_manifest = ROOT / "outputs/data/enclosure/aau_temperature_ranges_e11f_manifest.json"
    if e11f_manifest.exists():
        e11f_result_path = ROOT / "outputs/data/enclosure/aau_commissioning_confirmation_e11f.json"
        require(e11f_result_path.exists(), "E11F manifest exists without a confirmation result")
        e11f_result = json.loads(e11f_result_path.read_text(encoding="utf-8"))
        require(e11f_result["refit_performed"] is False, "later E11F access performed refitting")
        require(
            e11f_result["inputs"]["e11h_result_sha256"]
            == "b76ecfe3e597d0641515df60b0d6636ed9a0ff1e23ebcb2852a225d4eee490e9",
            "later E11F access lacks the frozen E11H advancement hash",
        )
        require(
            e11f_result["generated_at_utc"] > data["generated_at_utc"],
            "E11F access predates E11G development",
        )
    require(evaluation["development_decision"] == "no_candidate_forwarded", "decision changed")
    require(evaluation["candidate_count"] == 30, "candidate count changed")
    require(evaluation["day_blocks"] == 12, "day-block count changed")
    require(evaluation["measurement_count"] == 63084, "measurement count changed")
    require(close(float(baseline["mae_c"]), 1.1167968571706295), "baseline MAE changed")
    require(close(float(model["mae_c"]), 0.8944718805024479), "model MAE changed")
    require(close(float(model["rmse_c"]), 1.5415274406001196), "model RMSE changed")
    require(close(float(model["p95_absolute_error_c"]), 3.10125144219617), "model P95 changed")
    require(evaluation["sensor_wins"] == 21, "sensor wins changed")
    failed = sorted(name for name, passed in evaluation["gates"].items() if not passed)
    require(failed == ["sensor_wins_at_least_26"], f"unexpected failed gates: {failed}")
    require(
        close(float(evaluation["bootstrap"]["ci_95_lower_c"]), 0.18465399061000484),
        "bootstrap lower bound changed",
    )
    outcomes = {"wins": 0, "ties": 0, "losses": 0}
    for metrics in evaluation["per_sensor_mae"].values():
        delta = float(metrics["baseline_mae_c"]) - float(metrics["model_mae_c"])
        outcomes["wins" if delta > 1e-12 else "losses" if delta < -1e-12 else "ties"] += 1
    require(outcomes == {"wins": 21, "ties": 20, "losses": 1}, f"sensor outcomes changed: {outcomes}")
    for relative in SOURCE_PATHS:
        normalized = (ROOT / relative).read_text(encoding="utf-8").replace("\\_", "_")
        if relative.startswith("scripts/build_"):
            require("sync_e11g_generated_artifacts" in normalized, f"missing E11G hook {relative}")
        else:
            require("0.8945" in normalized and "no_candidate_forwarded" in normalized, f"stale source {relative}")
    hook = (ROOT / "scripts/sync_e11g_generated_artifacts.py").read_text(encoding="utf-8")
    require("0.8945" in hook and "no_candidate_forwarded" in hook, "stale E11G synchronization hook")
    for relative in ARCHIVE_PATHS:
        text = archive_text(ROOT / relative)
        require("0.8945" in text and "no_candidate_forwarded" in text, f"stale archive {relative}")
    print("E11G verification passed: adaptive metrics, failed coverage gate, sources, outputs, and valid later E11F provenance")


if __name__ == "__main__":
    main()
