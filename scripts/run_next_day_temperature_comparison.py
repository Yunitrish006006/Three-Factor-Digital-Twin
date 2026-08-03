from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
root_str = str(ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)

from digital_twin.evaluation.next_day_temperature_comparison import (
    BOOTSTRAP_REPLICATES,
    BOOTSTRAP_SEED,
    DEFAULT_INPUT_DIR,
    DEFAULT_OUTPUT_PATH,
    run_next_day_temperature_comparison,
    write_next_day_temperature_comparison,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the leakage-controlled SML2010 next-day temperature comparison."
    )
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--checkpoint", default="outputs/data/hybrid_residual_checkpoint.json")
    parser.add_argument("--bootstrap-replicates", type=int, default=BOOTSTRAP_REPLICATES)
    parser.add_argument("--bootstrap-seed", type=int, default=BOOTSTRAP_SEED)
    args = parser.parse_args()

    summary = run_next_day_temperature_comparison(
        input_dir=Path(args.input_dir),
        checkpoint_path=Path(args.checkpoint),
        bootstrap_replicates=args.bootstrap_replicates,
        bootstrap_seed=args.bootstrap_seed,
    )
    output_path = write_next_day_temperature_comparison(
        summary,
        output_path=Path(args.output),
    )
    print(output_path)
    print(
        "status={status} H-ND-01={hypothesis} mean_relative_improvement_pct={improvement}".format(
            status=summary["status"],
            hypothesis=summary["decisions"]["H-ND-01"],
            improvement=summary.get("summary", {}).get(
                "mean_relative_mae_reduction_pct",
                "n/a",
            ),
        )
    )


if __name__ == "__main__":
    main()
