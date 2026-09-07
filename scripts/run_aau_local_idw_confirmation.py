#!/usr/bin/env python3
"""Run the preregistered E11C local-IDW confirmation."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from digital_twin.enclosure.aau_local import evaluate_local_idw_confirmation
from digital_twin.enclosure.aau_spatial import load_minute_snapshots, load_spatial_sensors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--room-design",
        type=Path,
        default=ROOT / "docs/templates/room_design_aau_server_room.json",
    )
    parser.add_argument(
        "--ranges-manifest",
        type=Path,
        default=ROOT / "outputs/data/enclosure/aau_temperature_ranges_e11c_manifest.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "outputs/data/enclosure/aau_local_idw_confirmation.json",
    )
    parser.add_argument("--bootstrap-seed", type=int, default=20260823)
    parser.add_argument("--bootstrap-replicates", type=int, default=20000)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = json.loads(args.ranges_manifest.read_text(encoding="utf-8"))
    sensors = load_spatial_sensors(args.room_design)
    snapshots, parsing = load_minute_snapshots(args.ranges_manifest, sensors)
    evaluation = evaluate_local_idw_confirmation(
        sensors,
        snapshots,
        neighbor_count=3,
        distance_power=2.0,
        bootstrap_seed=args.bootstrap_seed,
        bootstrap_replicates=args.bootstrap_replicates,
    )
    output = {
        "schema_version": "aau-local-idw-confirmation-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "experiment_id": "E11C",
        "source": manifest["source"],
        "sampling": manifest["sampling"],
        "room_design": str(args.room_design.relative_to(ROOT)),
        "parsing": parsing,
        "evaluation": evaluation,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    print(json.dumps({
        "snapshots": evaluation["snapshot_count"],
        "macro_metrics": evaluation["macro_metrics"],
        "pairwise_sensor_results": evaluation["pairwise_sensor_results"],
        "bootstrap": evaluation["bootstrap"],
        "hypothesis": evaluation["hypothesis"],
    }, indent=2))


if __name__ == "__main__":
    main()
