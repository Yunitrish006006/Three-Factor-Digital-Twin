#!/usr/bin/env python3
"""Record one durable E15 attempt without changing the frozen evaluator."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "outputs/data/enclosure"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(root: Path = ROOT) -> int:
    data = root / "outputs/data/enclosure"
    attempt = data / "bmc_confirmation_e15_attempt.json"
    result = data / "bmc_confirmation_e15_result.json"
    log = data / "bmc_confirmation_e15_execution.log"
    if attempt.exists() or result.exists():
        raise SystemExit("E15 already attempted; preserve the existing record and do not rerun.")
    inputs = [
        "scripts/run_bmc_confirmation_e15.py",
        "digital_twin/enclosure/bmc_virtual_sensor.py",
        "outputs/data/enclosure/bmc_confirmation_e15_manifest.json",
        "outputs/data/enclosure/bmc_corrected_e14c_frozen_model.json",
    ]
    receipt = {
        "study_id": "E15",
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "started",
        "input_sha256": {name: sha256(root / name) for name in inputs},
        "log": str(log.relative_to(root)),
        "execution_policy": "One attempt; evaluator, models, gates, and files unchanged.",
    }
    data.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents a concurrent or interrupted attempt being repeated.
    with attempt.open("x", encoding="utf-8") as handle:
        json.dump(receipt, handle, indent=2)
        handle.write("\n")
    code = 1
    try:
        with log.open("x", encoding="utf-8") as output:
            completed = subprocess.run(
                [sys.executable, "scripts/run_bmc_confirmation_e15.py"],
                cwd=root, stdout=output, stderr=subprocess.STDOUT, check=False,
            )
        code = completed.returncode
        receipt["exit_code"] = code
        receipt["status"] = "completed" if code == 0 and result.exists() else "execution_failed"
        if code == 0 and not result.exists():
            code = 1
            receipt["error"] = "Evaluator exited successfully without producing its result."
        if result.exists():
            receipt["result_sha256"] = sha256(result)
    except BaseException as error:
        receipt["status"] = "execution_interrupted"
        receipt["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        receipt["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        temporary = attempt.with_suffix(".json.part")
        temporary.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        temporary.replace(attempt)
    print(json.dumps(receipt, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(execute())
