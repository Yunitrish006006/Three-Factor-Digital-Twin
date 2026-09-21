#!/usr/bin/env python3
"""Evaluate temperature prediction conditional on recorded control actions.

This is an exploratory replay of existing BOPTEST traces.  It does not execute
new FMU episodes and is not causal or hardware evidence.  The one-step RC
predictor is frozen from the existing development calibration fit; each
sampled row already contains the executed locked-controller action.
"""
from __future__ import annotations

import csv
import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACE_DIR = ROOT / "openspec/changes/systematic-parameter-tuning-20260921/artifacts/traces"
OUT = ROOT / "openspec/changes/systematic-parameter-tuning-20260921/artifacts/action_conditioned_replay.json"
SAMPLE_PER_TRACE = 100
SEED = 20260921
# Existing development fit for the 6-hour RC identification trace:
# delta_T = a*(outdoor-T) + b*(command-T) + c*(solar/1000) + d.
RC_COEFFICIENTS = (0.09239478306626148, 0.0876338932542221, 0.0, 2.3341317241424564)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path: Path) -> list[dict[str, float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [{key: float(value) for key, value in row.items()} for row in csv.DictReader(handle)]


def evaluate(path: Path, rng: random.Random) -> dict:
    rows = load(path)
    sample = rng.sample(rows, min(SAMPLE_PER_TRACE, len(rows)))
    a, b, c, d = RC_COEFFICIENTS
    records = []
    for row in sample:
        predicted_next = row["T"] + a * (row["outdoor"] - row["T"]) + b * (row["command"] - row["T"]) + c * (row["solar"] / 1000.0) + d
        prediction_error = predicted_next - row["next_T"]
        records.append({
            "time_s": row["time_s"],
            "temperature_C": row["T"],
            "command": row["command"],
            "action_valid": 12.0 <= row["command"] <= 40.0,
            "predicted_next_temperature_C": predicted_next,
            "next_temperature_C": row["next_T"],
            "prediction_error_C": prediction_error,
        })
    errors = [item["prediction_error_C"] for item in records]
    return {
        "trace": path.name,
        "trace_sha256": sha256(path),
        "rows_total": len(rows),
        "sample_count": len(records),
        "action_valid_count": sum(item["action_valid"] for item in records),
        "metrics": {
            "mae_C": sum(abs(error) for error in errors) / len(errors) if errors else None,
            "rmse_C": (sum(error * error for error in errors) / len(errors)) ** 0.5 if errors else None,
            "within_0_5_C_pct": 100 * sum(abs(error) <= 0.5 for error in errors) / len(errors) if errors else None,
        },
        "samples": records,
    }


def main() -> None:
    rng = random.Random(SEED)
    evaluations = [evaluate(path, rng) for path in sorted(TRACE_DIR.glob("*_locked.csv"))]
    total = sum(item["sample_count"] for item in evaluations)
    errors = [sample["prediction_error_C"] for item in evaluations for sample in item["samples"]]
    artifact = {
        "status": "PASS_ACTION_CONDITIONED_TEMPERATURE_PREDICTION_REPLAY_NOT_CAUSAL_EVIDENCE",
        "run_id": "action-conditioned-replay-20260921-01",
        "scope": "RANDOM_SAMPLED_EXISTING_BOPTEST_LOCKED_TRACES",
        "prediction_target": "one_step_next_T_after_executed_locked_controller_action",
        "sampling": {"seed": SEED, "sample_per_trace": SAMPLE_PER_TRACE},
        "predictor": {"type": "frozen_first_order_RC", "coefficients": RC_COEFFICIENTS, "source": "pilot-boptest-rapid-pi development fit 6h"},
        "evaluations": evaluations,
        "summary": {"trace_count": len(evaluations), "sample_count": total, "action_valid_count": sum(item["action_valid_count"] for item in evaluations),
                     "mae_C": sum(abs(error) for error in errors) / len(errors) if errors else None,
                     "rmse_C": (sum(error * error for error in errors) / len(errors)) ** 0.5 if errors else None,
                     "within_0_5_C_pct": 100 * sum(abs(error) <= 0.5 for error in errors) / len(errors) if errors else None},
        "boundary": "Existing custom BOPTEST trace replay only; no new FMU execution, official REST/KPI equivalence, physical chassis, or causal intervention claim.",
    }
    OUT.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "summary": artifact["summary"], "output": str(OUT)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
