from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
root_str = str(ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)

from digital_twin.evaluation.published_hybrid_comparison import (
    DEFAULT_HORIZONS,
    DEFAULT_INPUT_DIR,
    DEFAULT_OUTPUT_PATH,
    run_oh2024_inspired_comparison,
    write_oh2024_inspired_comparison,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the Oh et al. (2024)-inspired additive residual transfer comparison on SML2010."
    )
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--checkpoint", default="outputs/data/hybrid_residual_checkpoint.json")
    parser.add_argument(
        "--horizons",
        default=",".join(str(value) for value in DEFAULT_HORIZONS),
        help="Comma-separated positive horizons in minutes.",
    )
    args = parser.parse_args()

    horizons = [int(value.strip()) for value in args.horizons.split(",") if value.strip()]
    summary = run_oh2024_inspired_comparison(
        input_dir=Path(args.input_dir),
        horizons=horizons,
        checkpoint_path=Path(args.checkpoint),
    )
    output_path = write_oh2024_inspired_comparison(summary, Path(args.output))
    print(output_path)
    print(
        "status={status} evaluated_cases={cases} transfer_wins_vs_physics={wins}".format(
            status=summary["status"],
            cases=summary["summary"]["evaluated_cases"],
            wins=summary["summary"]["oh2024_inspired_wins_vs_raw_physics"],
        )
    )


if __name__ == "__main__":
    main()
