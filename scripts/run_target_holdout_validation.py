#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
root_str = str(ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)

from digital_twin.core.scenarios import build_validation_scenarios
from digital_twin.core.validation import run_synthetic_holdout_validation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run role-aware target-point holdout validation. Validation values are read only "
            "after calibration and are never passed into fitting."
        )
    )
    parser.add_argument(
        "--scenario",
        action="append",
        default=[],
        help="Scenario name to run. May be provided more than once. Default: all core scenarios.",
    )
    parser.add_argument(
        "--no-observation-noise",
        action="store_true",
        help="Use exact synthetic input observations instead of deterministic measurement noise.",
    )
    parser.add_argument(
        "--output",
        default="outputs/data/target_holdout_validation_summary.json",
        help="Output JSON path relative to the repository root.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scenarios = build_validation_scenarios()
    available = {scenario.name: scenario for scenario in scenarios}

    requested = args.scenario or [scenario.name for scenario in scenarios]
    unknown = sorted(set(requested) - set(available))
    if unknown:
        raise SystemExit(
            "Unknown scenario(s): " + ", ".join(unknown) + ". Available: " + ", ".join(sorted(available))
        )

    results = [
        run_synthetic_holdout_validation(
            available[name],
            observation_noise=not args.no_observation_noise,
        )
        for name in requested
    ]
    summary = {
        "evidence_scope": "synthetic_target_point_holdout",
        "description": (
            "Controlled validation of held-out target locations. Only input sensor observations "
            "are used for calibration; validation truth is read after prediction."
        ),
        "scenarios": results,
        "all_leakage_checks_passed": all(not result["leakage_detected"] for result in results),
    }

    output_path = ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {output_path}")
    print(f"Scenarios: {len(results)}")
    print(f"Leakage checks passed: {summary['all_leakage_checks_passed']}")
    for result in results:
        metric_text = ", ".join(
            f"{metric} MAE={values['mae']:.4f}"
            for metric, values in result["metrics"].items()
        )
        print(f"- {result['scenario']}: {metric_text}")


if __name__ == "__main__":
    main()
