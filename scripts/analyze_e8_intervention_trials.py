from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from digital_twin.evaluation.intervention import analyze_intervention_dataset


DEFAULT_INPUT = ROOT / "docs" / "templates" / "e8_intervention_trials_template.json"
DEFAULT_OUTPUT = ROOT / "outputs" / "data" / "e8_intervention_summary.json"
DEFAULT_MARKDOWN = ROOT / "outputs" / "data" / "e8_intervention_summary.md"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate and analyze preregistered E8 intervention trials."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()

    dataset = json.loads(args.input.read_text(encoding="utf-8"))
    summary = analyze_intervention_dataset(dataset)
    _guard_synthetic_evidence(summary, args.output)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(_render_markdown(summary), encoding="utf-8")
    print(f"Wrote {args.output}")
    print(f"Wrote {args.markdown}")
    print(
        json.dumps(
            {
                "evidence_status": summary["evidence_status"],
                "completed_trials": summary["trial_counts"]["completed"],
                "excluded_trials": summary["trial_counts"]["excluded"],
            },
            ensure_ascii=False,
        )
    )


def _guard_synthetic_evidence(summary: Dict[str, object], output: Path) -> None:
    if summary["source_evidence_class"] != "SYNTHETIC_TEST":
        return
    try:
        output.resolve().relative_to((ROOT / "outputs" / "data").resolve())
    except ValueError:
        return
    raise ValueError(
        "Synthetic E8 fixtures cannot be written under outputs/data or treated as evidence."
    )


def _render_markdown(summary: Dict[str, object]) -> str:
    counts = summary["trial_counts"]
    metrics = summary["metrics"]
    lines = [
        "# E8 Intervention Validation Status",
        "",
        f"- Evidence status: `{summary['evidence_status']}`",
        f"- Study: `{summary['study_id']}`",
        f"- Room: `{summary['room_id']}`",
        f"- Completed trials: `{counts['completed']}`",
        f"- Excluded trials: `{counts['excluded']}`",
        "",
        "## Preregistered Metrics",
        "",
        "| Metric | Current value |",
        "| --- | ---: |",
        _metric_row("Top-ranked success rate", metrics["top_ranked_success_rate"]),
        _metric_row(
            "Top-ranked mean actual improvement",
            metrics["top_ranked_mean_actual_improvement"],
        ),
        _metric_row(
            "Mean absolute prediction error",
            metrics["mean_absolute_prediction_error"],
        ),
        _metric_row(
            "Matched-block top-1 regret",
            metrics["matched_block_top1_regret_mean"],
        ),
        _metric_row(
            "Matched-block Spearman correlation",
            metrics["matched_block_spearman_mean"],
        ),
        "",
        "## Claim Boundary",
        "",
        str(summary["claim_boundary"]),
        "",
    ]
    return "\n".join(lines)


def _metric_row(label: str, value: object) -> str:
    rendered = "`null`" if value is None else f"{float(value):.6f}"
    return f"| {label} | {rendered} |"


if __name__ == "__main__":
    main()
