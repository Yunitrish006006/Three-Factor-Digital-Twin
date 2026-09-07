from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from digital_twin.evaluation.rnn_3d_field_comparison import (
    DEFAULT_OUTPUT_PATH,
    DEFAULT_RNN_CONFIG,
    run_rnn_3d_field_comparison,
    write_rnn_3d_field_comparison,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the registered same-task pure RNN 3-D field comparison."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()
    summary = run_rnn_3d_field_comparison(rnn_config=DEFAULT_RNN_CONFIG)
    output_path = write_rnn_3d_field_comparison(summary, args.output)
    print(f"Wrote {output_path}")
    print(json.dumps(summary["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
