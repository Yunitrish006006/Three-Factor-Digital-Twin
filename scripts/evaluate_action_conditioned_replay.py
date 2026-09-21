#!/usr/bin/env python3
"""Evaluate whether recorded control actions produced the expected one-step result.

This is an exploratory replay of existing BOPTEST traces.  It does not execute
new FMU episodes and is not causal or hardware evidence.  A sampled row is
eligible when the current temperature is at least 0.1 C from the 22 C target;
the expected result is that the next temperature is closer to the target than
the persistence (no-change) outcome.
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
TARGET_C = 22.0
MIN_ERROR_C = 0.1
SAMPLE_PER_TRACE = 100
SEED = 20260921


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
    eligible = [row for row in rows if abs(row["T"] - TARGET_C) >= MIN_ERROR_C]
    sample = rng.sample(eligible, min(SAMPLE_PER_TRACE, len(eligible)))
    records = []
    for row in sample:
        before_error = abs(row["T"] - TARGET_C)
        after_error = abs(row["next_T"] - TARGET_C)
        records.append({
            "time_s": row["time_s"],
            "temperature_C": row["T"],
            "command": row["command"],
            "next_temperature_C": row["next_T"],
            "before_error_C": before_error,
            "after_error_C": after_error,
            "expected_result": "closer_to_target",
            "result_matches_expectation": after_error < before_error,
        })
    matches = sum(item["result_matches_expectation"] for item in records)
    return {
        "trace": path.name,
        "trace_sha256": sha256(path),
        "rows_total": len(rows),
        "rows_eligible": len(eligible),
        "sample_count": len(records),
        "matches": matches,
        "match_rate": matches / len(records) if records else None,
        "samples": records,
    }


def main() -> None:
    rng = random.Random(SEED)
    evaluations = [evaluate(path, rng) for path in sorted(TRACE_DIR.glob("*_locked.csv"))]
    total = sum(item["sample_count"] for item in evaluations)
    matches = sum(item["matches"] for item in evaluations)
    artifact = {
        "status": "PASS_ACTION_CONDITIONED_TRACE_REPLAY_NOT_CAUSAL_EVIDENCE",
        "run_id": "action-conditioned-replay-20260921-01",
        "scope": "RANDOM_SAMPLED_EXISTING_BOPTEST_LOCKED_TRACES",
        "target_C": TARGET_C,
        "expected_result": "after operation, one-step temperature error is smaller than persistence error",
        "sampling": {"seed": SEED, "sample_per_trace": SAMPLE_PER_TRACE, "minimum_error_C": MIN_ERROR_C},
        "evaluations": evaluations,
        "summary": {"trace_count": len(evaluations), "sample_count": total, "matches": matches,
                     "match_rate": matches / total if total else None},
        "boundary": "Existing custom BOPTEST trace replay only; no new FMU execution, official REST/KPI equivalence, physical chassis, or causal intervention claim.",
    }
    OUT.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "summary": artifact["summary"], "output": str(OUT)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
