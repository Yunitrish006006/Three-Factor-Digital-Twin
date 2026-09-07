from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from digital_twin.evaluation.kalman_filter_comparison import (
    DEFAULT_INPUT_DIR,
    DEFAULT_OUTPUT_PATH,
    KalmanComparisonConfig,
    run_kalman_filter_comparison,
    write_kalman_filter_comparison,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the registered same-data controlled Kalman filtering comparison on SML2010."
    )
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    summary = run_kalman_filter_comparison(
        input_dir=args.input_dir,
        config=KalmanComparisonConfig(seed=args.seed),
    )
    output_path = write_kalman_filter_comparison(summary, args.output)
    counts = summary["summary"]["lowest_mae_counts"]
    print(f"Wrote {output_path}")
    print(f"Status: {summary['status']}")
    print(
        "Lowest-MAE cases: "
        + ", ".join(f"{method}={count}" for method, count in counts.items())
    )
    print(f"All-case parity passed: {summary['summary']['all_cases_data_parity_passed']}")


if __name__ == "__main__":
    main()
