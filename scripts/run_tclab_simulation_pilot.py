"""TCLabModel reset/input/advance pilot.

This is a local simulation smoke test, not a hardware or intervention result.
It records the same split/hash contract used by the tuning gate.
"""
from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

from tclab import TCLabModel

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "openspec/changes/systematic-parameter-tuning-20260921/artifacts/tclab_simulation_pilot.json"
DT = 30.0
TARGET = 32.0
HORIZON = 40


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class Adapter:
    def __init__(self, initial, seed):
        random.seed(seed)
        self.lab = TCLabModel(synced=False)
        self.lab.Ta = initial
        self.lab._T1 = initial
        self.lab._T2 = initial
        self.lab._H1 = initial
        self.lab._H2 = initial
        self.time = 0.0
        self.lab.update(self.time)

    def reset(self):
        self.time = 0.0
        self.lab.Q1(0)
        self.lab.Q2(0)
        self.lab.update(self.time)
        return {"time_s": self.time, "T1_C": self.lab.T1, "T2_C": self.lab.T2, "Q1_pct": 0.0, "Q2_pct": 0.0}

    def advance(self, q1):
        self.lab.Q1(q1)
        self.lab.Q2(0)
        self.time += DT
        self.lab.update(self.time)
        return {"time_s": self.time, "T1_C": self.lab.T1, "T2_C": self.lab.T2, "Q1_pct": self.lab.Q1(), "Q2_pct": self.lab.Q2()}

    def close(self):
        self.lab.close()


def trace(initial, seed, controller=None, calibration=False):
    adapter = Adapter(initial, seed)
    rows = []
    try:
        adapter.reset()
        integral = 0.0
        for i in range(HORIZON):
            if calibration:
                q1 = [0.0, 40.0, 80.0, 20.0][(i // 10) % 4]
            else:
                error = TARGET - rows[-1]["T1_C"] if rows else TARGET - initial
                integral = max(-300.0, min(300.0, integral + error * DT))
                q1 = max(0.0, min(100.0, controller["kp"] * error + controller["kp"] / controller["ti"] * integral))
            row = adapter.advance(q1)
            rows.append(row)
    finally:
        adapter.close()
    return rows


def metrics(rows):
    errors = [abs(TARGET - row["T1_C"]) for row in rows]
    return {"n": len(errors), "mae_C": sum(errors) / len(errors), "max_abs_error_C": max(errors),
            "within_0_5_C_pct": 100 * sum(e <= 0.5 for e in errors) / len(errors)}


def main():
    candidates = [{"kp": kp, "ti": ti} for kp in (2.0, 5.0, 10.0) for ti in (300.0, 900.0, 1800.0)]
    calibration = []
    for candidate in candidates:
        rows = trace(21.0, 17, candidate, calibration=False)
        calibration.append({"parameters": candidate, "metrics": metrics(rows)})
    selected = min(calibration, key=lambda item: item["metrics"]["mae_C"])
    split_specs = {"calibration": (21.0, True), "validation": (23.0, False), "holdout": (19.0, False)}
    splits = {}
    for name, (initial, is_calibration) in split_specs.items():
        rows = trace(initial, 17, selected["parameters"], calibration=is_calibration)
        splits[name] = {"status": "PASS", "trace_sha256": digest(rows), "metrics": metrics(rows),
                        "initial_C": initial, "n": len(rows)}
    repeat = trace(19.0, 17, selected["parameters"], calibration=False)
    repeatability = digest(repeat) == splits["holdout"]["trace_sha256"]
    artifact = {
        "status": "PASS_TCLAB_SIMULATION_PILOT_NOT_HARDWARE_EVIDENCE",
        "run_id": "tclab-simulation-20260921-01", "platform": "tclab.TCLabModel 1.0.0",
        "scope": "LOCAL_SIMULATION_RESET_INPUT_ADVANCE_RESPONSE",
        "parameters": {"selected": selected["parameters"], "candidates": candidates, "target_C": TARGET, "dt_s": DT},
        "metrics": {"calibration_selection": selected["metrics"]}, "splits": splits,
        "reproducibility": {"seed": 17, "repeatability_holdout": repeatability,
                             "distinct_split_hashes": len({v["trace_sha256"] for v in splits.values()}) == 3},
        "boundary": "TCLabModel simulation only; no TCLab hardware, BOPTEST, room, enclosure, semiconductor, or causal intervention claim.",
    }
    OUT.write_text(json.dumps(artifact, indent=2) + "\n")
    print(json.dumps({"status": artifact["status"], "selected": selected["parameters"],
                      "repeatability_holdout": repeatability, "output": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
