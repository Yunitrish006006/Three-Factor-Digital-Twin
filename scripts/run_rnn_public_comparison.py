from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
root_str = str(ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)

from digital_twin.evaluation.rnn_public_comparison import (
    DEFAULT_HORIZONS,
    DEFAULT_INPUT_DIR,
    DEFAULT_OUTPUT_PATH,
    run_rnn_public_comparison,
    write_rnn_public_comparison,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the same-data vanilla RNN comparison on SML2010 S2 tasks."
    )
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument(
        "--horizons",
        default=",".join(str(value) for value in DEFAULT_HORIZONS),
        help="Comma-separated positive horizons in minutes.",
    )
    args = parser.parse_args()
    horizons = [int(value.strip()) for value in args.horizons.split(",") if value.strip()]
    summary = run_rnn_public_comparison(
        input_dir=Path(args.input_dir),
        horizons=horizons,
    )
    output_path = write_rnn_public_comparison(summary, Path(args.output))
    print(output_path)
    print(
        "status={status} evaluated_cases={cases} parity={parity} rnn_lowest_mae={wins}".format(
            status=summary["status"],
            cases=summary["summary"]["evaluated_cases"],
            parity=summary["data_parity"]["all_horizons_passed"],
            wins=summary["summary"]["lowest_mae_counts"]["vanilla_rnn"],
        )
    )


if __name__ == "__main__":
    main()
