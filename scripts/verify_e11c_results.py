#!/usr/bin/env python3
"""Verify E11C evidence and synchronized source claims."""

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "outputs/data/enclosure/aau_local_idw_confirmation.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    parsing = result["parsing"]
    evaluation = result["evaluation"]
    metrics = evaluation["macro_metrics"]
    pairwise = evaluation["pairwise_sensor_results"]
    bootstrap = evaluation["bootstrap"]
    hypothesis = evaluation["hypothesis"]

    require(result["sampling"]["range_count"] == 11, "range count drift")
    require(result["sampling"]["overlap_check"] == "passed", "overlap status drift")
    require(parsing["eligible_minutes"] == 1505, "snapshot count drift")
    require(evaluation["sensor_count"] == 42, "sensor count drift")
    require(hypothesis["decision"] == "not_supported", "H-ENC-03 decision drift")
    require(pairwise == {"local_idw_wins": 21, "nearest_neighbor_wins": 21, "ties": 0}, "win-count drift")

    expected_mae = {
        "nearest_neighbor": 1.301080954659073,
        "local_idw_k3_p2": 1.2227765078344883,
        "global_idw_p2": 1.8442944096457452,
    }
    for method, expected in expected_mae.items():
        require(
            math.isclose(metrics[method]["mae_c"], expected, rel_tol=0.0, abs_tol=1e-12),
            f"{method} MAE drift",
        )
    require(
        math.isclose(bootstrap["ci95_lower_c"], 0.05463577789723185, rel_tol=0.0, abs_tol=1e-12),
        "bootstrap lower-bound drift",
    )
    require(hypothesis["conditions"]["local_sensor_wins_at_least_26"] is False, "breadth condition drift")

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
        for token in ("E11C", "1.301", "1.223", "1,505", "H-ENC-03", "21/42"):
            require(token in text, f"{path}: missing {token}")

    print("E11C result consistency: 7 synchronized sources verified")


if __name__ == "__main__":
    main()
