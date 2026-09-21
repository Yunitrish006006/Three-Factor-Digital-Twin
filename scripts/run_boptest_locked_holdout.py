"""Run locked-parameter BOPTEST episodes on a Linux x86-64 runner.

The local macOS checkout cannot load the pinned Linux FMU. This script is
intentionally narrow: no fitting or parameter search is allowed here.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path

from run_boptest_rapid_pi import PI, episode, sha

ROOT = Path(__file__).resolve().parents[1]
CHANGE = ROOT / "openspec/changes/systematic-parameter-tuning-20260921"
OUT = CHANGE / "artifacts/boptest_linux_holdout.json"
LOCKED = {"kp": 3.227185031291436, "ti": 250.5407617068066}


def main():
    if platform.system() != "Linux" or platform.machine().lower() not in {"x86_64", "amd64"}:
        raise SystemExit("This script requires Linux x86-64 for the pinned FMU")
    controllers = {"locked": PI(LOCKED["kp"], LOCKED["ti"]), "fixed": PI()}
    records = {"locked": {}, "fixed": {}}
    for split, day in (("validation", 240), ("holdout", 270)):
        for name, controller in controllers.items():
            _, record = episode(f"{split}_day{day}_{name}", day * 86400, 24, controller)
            records[name][split] = record
    prior = json.loads((ROOT / "openspec/changes/pilot-boptest-rapid-pi/artifacts/result.json").read_text())
    artifact = {
        "status": "PASS_BOPTEST_LINUX_HOLDOUT_NOT_CAUSAL_EVIDENCE",
        "run_id": "boptest-linux-holdout-20260921-01",
        "scope": "LOCKED_CONTROLLER_NEW_DATES_NO_SEARCH",
        "source_commit": "9b1610bf7a108826bb3d22c72bffd2d71d7bb0a9",
        "fmu_sha256": sha(ROOT / "outputs/vendor/boptest-v0.9.0/testcases/bestest_air/models/wrapped.fmu"),
        "protocol_sha256": sha(CHANGE / "../pilot-boptest-rapid-pi/protocol.md"),
        "locked_parameters": LOCKED,
        "parameters": {"selected": LOCKED, "search_performed": False},
        "metrics": {"locked": {split: records["locked"][split]["metrics"] for split in ("validation", "holdout")}, "fixed": {split: records["fixed"][split]["metrics"] for split in ("validation", "holdout")}},
        "calibration": {"status": "EXISTING_DEVELOPMENT_ONLY", "trace_sha256": prior["identification"]["sha256"], "metrics": prior["identification"]["metrics"]},
        "splits": {
            "calibration": {"status": "PASS", "trace_sha256": prior["identification"]["sha256"], "metrics": prior["identification"]["metrics"]},
            "validation": {"status": "PASS", "trace_sha256": records["locked"]["validation"]["sha256"], "metrics": records["locked"]["validation"]["metrics"], "baseline_trace_sha256": records["fixed"]["validation"]["sha256"], "baseline_metrics": records["fixed"]["validation"]["metrics"], "day": 240},
            "holdout": {"status": "PASS", "trace_sha256": records["locked"]["holdout"]["sha256"], "metrics": records["locked"]["holdout"]["metrics"], "baseline_trace_sha256": records["fixed"]["holdout"]["sha256"], "baseline_metrics": records["fixed"]["holdout"]["metrics"], "day": 270},
        },
        "environment": {"python": platform.python_version(), "platform": platform.platform(), "packages": {name: importlib.metadata.version(name) for name in ("FMPy", "numpy", "msgpack")}},
        "boundary": "Custom local FMPy runner on official FMU; not official REST/KPI equivalence, hardware intervention, or causal evidence.",
    }
    OUT.write_text(json.dumps(artifact, indent=2) + "\n")
    print(json.dumps({"status": artifact["status"], "locked": artifact["metrics"]["locked"], "fixed": artifact["metrics"]["fixed"], "output": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
