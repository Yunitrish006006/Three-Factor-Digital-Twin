from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from digital_twin.enclosure.aau_spatial import (  # noqa: E402
    evaluate_spatial_baselines,
    load_minute_snapshots,
    load_spatial_sensors,
)


DEFAULT_ROOM = ROOT / "docs" / "templates" / "room_design_aau_server_room.json"
DEFAULT_RANGES = ROOT / "outputs" / "data" / "enclosure" / "aau_temperature_ranges_manifest.json"
DEFAULT_OUTPUT = ROOT / "outputs" / "data" / "enclosure" / "aau_spatial_baseline.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the pre-registered AAU E11B spatial baseline.")
    parser.add_argument("--room-design", type=Path, default=DEFAULT_ROOM)
    parser.add_argument("--ranges-manifest", type=Path, default=DEFAULT_RANGES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    sensors = load_spatial_sensors(args.room_design)
    snapshots, parsing = load_minute_snapshots(args.ranges_manifest, sensors)
    evaluation = evaluate_spatial_baselines(sensors, snapshots)
    ranges_manifest = json.loads(args.ranges_manifest.read_text(encoding="utf-8"))
    payload = {
        "schema_version": "aau-spatial-baseline-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "experiment_id": "E11B",
        "source": ranges_manifest["source"],
        "sampling": ranges_manifest["sampling"],
        "room_design": str(args.room_design.relative_to(ROOT)),
        "coordinate_mapping": {
            "included_high_confidence_channels": len(sensors),
            "excluded_ambiguous_cooling_channels": 6,
            "transform": "x=(cad_x_mm-100)/1000, y=(cad_y_mm-100)/1000, z=cad_z_mm/1000",
        },
        "parsing": parsing,
        "evaluation": evaluation,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    summary = {
        "output": str(args.output),
        "eligible_minutes": parsing["eligible_minutes"],
        "macro_mae_c": {
            method: metrics["mae_c"]
            for method, metrics in evaluation["macro_metrics"].items()
        },
        "sensor_wins": evaluation["sensor_wins"],
        "hypothesis": evaluation["hypothesis"],
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
