#!/usr/bin/env python3
"""Verify E11B machine evidence and synchronized source claims."""

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "outputs/data/enclosure/aau_spatial_baseline.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    parsing = result["parsing"]
    evaluation = result["evaluation"]
    metrics = evaluation["macro_metrics"]
    wins_by_method = evaluation["sensor_wins"]
    decision = evaluation["hypothesis"]

    require(parsing["eligible_minutes"] == 1641, "snapshot count drift")
    require(evaluation["sensor_count"] == 42, "sensor count drift")
    require(decision["decision"] == "not_supported", "H-ENC-02 decision drift")
    expected = {
        "global_mean": (2.2934647677512436, 6),
        "nearest_neighbor": (1.1746036495748817, 30),
        "idw_3d_p2": (1.6868251860571795, 6),
    }
    for name, (mae, wins) in expected.items():
        require(math.isclose(metrics[name]["mae_c"], mae, rel_tol=0.0, abs_tol=1e-12), f"{name} MAE drift")
        require(wins_by_method[name] == wins, f"{name} win-count drift")

    synchronized = (
        ROOT / "docs/thesis/thesis_draft_zh.md",
        ROOT / "scripts/build_thesis_docx.py",
        ROOT / "docs/papers/ieee/paper.tex",
        ROOT / "scripts/build_thesis_pptx.py",
        ROOT / "docs/thesis/presentation_outline_zh.md",
        ROOT / "docs/thesis/presentation_outline_zh_30min.md",
        ROOT / "docs/reports/professor_complete_experiment_overview_2026-08-03_zh.md",
    )
    for path in synchronized:
        text = path.read_text(encoding="utf-8")
        for token in ("E11B", "1.175", "1.687", "1,641", "H-ENC-02"):
            require(token in text, f"{path}: missing {token}")

    print("E11B result consistency: 7 synchronized sources verified")


if __name__ == "__main__":
    main()
