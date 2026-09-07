#!/usr/bin/env python3
"""Run the preregistered E11D role-conditioned AAU confirmation."""

from __future__ import annotations

import csv
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from digital_twin.enclosure.aau_role import (  # noqa: E402
    ROLES,
    bootstrap_day_improvement,
    evaluate_role_conditioning,
    extract_frozen_role_map,
    load_minute_snapshots,
    resolve_header_roles,
    sha256_file,
)


MANIFEST = ROOT / "outputs/data/enclosure/aau_temperature_ranges_e11d_manifest.json"
E11C_RESULT = ROOT / "outputs/data/enclosure/aau_local_idw_confirmation.json"
OUTPUT = ROOT / "outputs/data/enclosure/aau_role_conditioned_confirmation.json"
EXPECTED_E11C_SHA256 = "0b667ca8bb959e332aeff0155b9dceb1318dca3f91a26c1aa5552fb6bfef7055"


def main() -> None:
    if sha256_file(E11C_RESULT) != EXPECTED_E11C_SHA256:
        raise RuntimeError("frozen E11C metadata artifact hash mismatch")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    prior = json.loads(E11C_RESULT.read_text(encoding="utf-8"))
    frozen = extract_frozen_role_map(prior)
    sample = manifest["csv_header"]
    dialect = csv.Sniffer().sniff(sample, delimiters=",;")
    header = next(csv.reader(io.StringIO(sample), dialect))
    resolved = resolve_header_roles(header, frozen)
    role_counts = {role: 0 for role in ROLES}
    roles = {}
    for sensor, role in resolved.values():
        roles[sensor] = role
        role_counts[role] += 1
    if len(roles) != 42 or role_counts != {"rack_front": 9, "rack_back": 28, "gradient": 5}:
        raise RuntimeError(f"expected frozen 42-sensor role map, received {len(roles)} {role_counts}")
    fragment_paths = [Path(item["path"]) for item in manifest["fragments"]]
    snapshots, parse_stats = load_minute_snapshots(fragment_paths, header, resolved)
    if not snapshots:
        raise RuntimeError("no complete one-minute snapshots")
    evaluation = evaluate_role_conditioning(snapshots, roles)
    bootstrap = bootstrap_day_improvement(evaluation.pop("paired_improvements_by_day"))
    conditions = {
        "role_mae_lower": evaluation["role_conditioned"]["mae_c"] < evaluation["global"]["mae_c"],
        "role_rmse_lower": evaluation["role_conditioned"]["rmse_c"] < evaluation["global"]["rmse_c"],
        "role_sensor_wins_at_least_26_of_42": evaluation["per_sensor_wins"]["role_conditioned"] >= 26,
        "bootstrap_ci_lower_above_zero": bootstrap["ci_95_lower_c"] > 0,
    }
    decision = "supported" if all(conditions.values()) else "not_supported"
    result = {
        "experiment": "E11D",
        "hypothesis": "H-ENC-04",
        "decision": decision,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "preregistration": "openspec/changes/evaluate-aau-role-conditioned-transfer/protocol.md",
        "inputs": {
            "manifest": str(MANIFEST.relative_to(ROOT)),
            "manifest_sha256": sha256_file(MANIFEST),
            "frozen_role_metadata": str(E11C_RESULT.relative_to(ROOT)),
            "frozen_role_metadata_sha256": EXPECTED_E11C_SHA256,
        },
        "role_counts": role_counts,
        "parse": parse_stats,
        "models": {
            "global": "leave-one-sensor-out arithmetic mean of all other eligible sensors",
            "role_conditioned": "leave-one-sensor-out arithmetic mean of other sensors with the same frozen role",
        },
        "evaluation": evaluation,
        "bootstrap": bootstrap,
        "conditions": conditions,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "decision": decision, "conditions": conditions}, indent=2))


if __name__ == "__main__":
    main()

