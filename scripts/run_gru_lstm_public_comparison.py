#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from digital_twin.evaluation.gru_lstm_public_comparison import (
    DEFAULT_HORIZONS,
    DEFAULT_INPUT_DIR,
    DEFAULT_OUTPUT_PATH,
    run_gru_lstm_public_comparison,
    write_gru_lstm_public_comparison,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the preregistered simple GRU/LSTM SML2010 comparison."
    )
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument(
        "--horizons",
        default=",".join(str(value) for value in DEFAULT_HORIZONS),
    )
    args = parser.parse_args()
    output_path = Path(args.output)
    if output_path.exists():
        raise SystemExit(f"Refusing to overwrite existing result: {output_path}")
    horizons = [int(value.strip()) for value in args.horizons.split(",") if value.strip()]
    result = run_gru_lstm_public_comparison(
        input_dir=Path(args.input_dir),
        horizons=horizons,
    )
    write_gru_lstm_public_comparison(result, output_path)
    print(output_path)
    print(
        "status={status} decision={decision} gru_wins={gru} lstm_wins={lstm} forwarded={forwarded}".format(
            status=result["status"],
            decision=result["decisions"]["H-RNNGATE-01"],
            gru=result["summary"]["mae_wins_vs_vanilla_rnn"]["gru"],
            lstm=result["summary"]["mae_wins_vs_vanilla_rnn"]["lstm"],
            forwarded=",".join(result["summary"]["forwarded_candidates"]) or "none",
        )
    )


if __name__ == "__main__":
    main()
