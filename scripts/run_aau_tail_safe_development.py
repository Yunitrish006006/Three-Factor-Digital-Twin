#!/usr/bin/env python3
"""Run E11G tail-safe development without accessing E11F."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_aau_hierarchical_development as e11e_runner
from digital_twin.enclosure.aau_tail_safe import evaluate_tail_safe_gating


E11E_RESULT = ROOT / "outputs/data/enclosure/aau_hierarchical_development.json"
OUTPUT = ROOT / "outputs/data/enclosure/aau_tail_safe_development.json"


class _CapturedInputs(BaseException):
    def __init__(self, snapshots: object, metadata: object) -> None:
        self.snapshots = snapshots
        self.metadata = metadata


def _capture_inputs(snapshots: object, metadata: object) -> dict[str, object]:
    raise _CapturedInputs(snapshots, metadata)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_frozen_e11e_inputs() -> tuple[object, object]:
    original = e11e_runner.evaluate_hierarchical_grid
    e11e_runner.evaluate_hierarchical_grid = _capture_inputs
    try:
        e11e_runner.main()
    except _CapturedInputs as captured:
        return captured.snapshots, captured.metadata
    finally:
        e11e_runner.evaluate_hierarchical_grid = original
    raise RuntimeError("E11E runner did not expose parsed inputs")


def main() -> None:
    prior = json.loads(E11E_RESULT.read_text(encoding="utf-8"))
    snapshots, metadata = load_frozen_e11e_inputs()
    evaluation = evaluate_tail_safe_gating(snapshots, metadata)
    output = {
        "experiment": "E11G",
        "purpose": "adaptive_tail_safe_development_on_e11e",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "e11e_result": str(E11E_RESULT.relative_to(ROOT)),
            "e11e_result_sha256": sha256_file(E11E_RESULT),
            "manifest": prior["inputs"]["manifest"],
            "manifest_sha256": prior["inputs"]["manifest_sha256"],
            "frozen_metadata": prior["inputs"]["frozen_metadata"],
            "frozen_metadata_sha256": prior["inputs"]["frozen_metadata_sha256"],
        },
        "parse": prior["parse"],
        "sensor_count": len(metadata),
        "evaluation": evaluation,
        "e11f_accessed": False,
        "interpretation_limit": (
            "Adaptive development evidence only; E11E informed the method and E11F remains untouched."
        ),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
