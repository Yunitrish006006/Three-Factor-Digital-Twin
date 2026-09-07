from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import statistics
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple


TIME_COLUMN = "Time [Date/Time]"
POWER_COLUMNS = ("Power Ch 1 (W)", "Power Ch 2 (W)", "Power Ch 3 (W)")
METHODS = ("global_mean", "nearest_neighbor", "idw_3d_p2")


@dataclass(frozen=True)
class SpatialSensor:
    name: str
    csv_column: str
    source_label: str
    position: Tuple[float, float, float]


@dataclass(frozen=True)
class MinuteSnapshot:
    minute: datetime
    temperatures: Tuple[float, ...]
    total_power_w: float | None


def compute_range_offsets(total_size: int, range_size: int, count: int) -> List[int]:
    if total_size <= 0 or range_size <= 0 or count <= 0:
        raise ValueError("total_size, range_size, and count must be positive")
    if range_size > total_size:
        raise ValueError("range_size cannot exceed total_size")
    if count == 1:
        return [0]
    last_start = total_size - range_size
    offsets = [round(index * last_start / (count - 1)) for index in range(count)]
    if len(set(offsets)) != count:
        raise ValueError("range configuration produces duplicate offsets")
    return offsets


def load_spatial_sensors(room_design_path: Path) -> List[SpatialSensor]:
    payload = json.loads(room_design_path.read_text(encoding="utf-8"))
    sensors: List[SpatialSensor] = []
    seen_columns: set[str] = set()
    for item in payload.get("sensors", []):
        metadata = item.get("metadata", {})
        if not metadata.get("include_in_e11b"):
            continue
        column = metadata.get("csv_column")
        if not isinstance(column, str) or not column:
            raise ValueError(f"measurement sensor {item.get('name')} lacks csv_column")
        if column in seen_columns:
            raise ValueError(f"duplicate csv_column in room design: {column}")
        position = item.get("position", {})
        coordinates = tuple(float(position[axis]) for axis in ("x", "y", "z"))
        sensors.append(
            SpatialSensor(
                name=str(item["name"]),
                csv_column=column,
                source_label=str(metadata.get("source_label", item["name"])),
                position=coordinates,
            )
        )
        seen_columns.add(column)
    sensors.sort(key=lambda sensor: sensor.name)
    if len(sensors) != 42:
        raise ValueError(f"expected 42 E11B sensors, found {len(sensors)}")
    return sensors


def complete_fragment_text(raw: bytes, start_offset: int) -> tuple[str, int]:
    discarded = 0
    if start_offset > 0:
        first_newline = raw.find(b"\n")
        if first_newline < 0:
            return "", 1
        raw = raw[first_newline + 1 :]
        discarded += 1
    if raw and not raw.endswith(b"\n"):
        last_newline = raw.rfind(b"\n")
        if last_newline < 0:
            return "", discarded + 1
        raw = raw[: last_newline + 1]
        discarded += 1
    return raw.decode("utf-8-sig"), discarded


def _parse_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError("non-finite value")
    return parsed


def load_minute_snapshots(
    ranges_manifest_path: Path,
    sensors: Sequence[SpatialSensor],
) -> tuple[List[MinuteSnapshot], Dict[str, int]]:
    manifest = json.loads(ranges_manifest_path.read_text(encoding="utf-8"))
    fragments = sorted(manifest["fragments"], key=lambda item: int(item["index"]))
    expected_columns = [sensor.csv_column for sensor in sensors]
    manifest_header = manifest.get("csv_header")
    header: List[str] | None = list(manifest_header) if manifest_header is not None else None
    minute_temperatures: Dict[datetime, List[List[float]]] = {}
    minute_power: Dict[datetime, List[float]] = {}
    counts = {
        "fragments": len(fragments),
        "boundary_records_discarded": 0,
        "rows_seen": 0,
        "rows_accepted": 0,
        "rows_malformed": 0,
        "rows_missing_or_nonfinite": 0,
    }

    if header is not None:
        required = [TIME_COLUMN, *POWER_COLUMNS, *expected_columns]
        missing = [column for column in required if column not in header]
        if missing:
            raise ValueError(f"AAU manifest CSV header missing columns: {missing}")

    for fragment in fragments:
        path = Path(fragment["path"])
        raw = path.read_bytes()
        actual_sha256 = hashlib.sha256(raw).hexdigest()
        if actual_sha256 != fragment["sha256"]:
            raise ValueError(f"fragment checksum mismatch: {path}")
        text, discarded = complete_fragment_text(raw, int(fragment["start"]))
        counts["boundary_records_discarded"] += discarded
        reader = csv.reader(io.StringIO(text))
        if int(fragment["start"]) == 0:
            try:
                current_header = next(reader)
            except StopIteration as exc:
                raise ValueError("first fragment contains no CSV header") from exc
            header = current_header
            required = [TIME_COLUMN, *POWER_COLUMNS, *expected_columns]
            missing = [column for column in required if column not in header]
            if missing:
                raise ValueError(f"AAU CSV header missing columns: {missing}")
        if header is None:
            raise ValueError("range zero must be the first manifest fragment")
        indices = {column: header.index(column) for column in [TIME_COLUMN, *POWER_COLUMNS, *expected_columns]}

        for row in reader:
            counts["rows_seen"] += 1
            if len(row) != len(header):
                counts["rows_malformed"] += 1
                continue
            try:
                timestamp = datetime.strptime(row[indices[TIME_COLUMN]], "%Y-%m-%d %H:%M:%S")
                minute = timestamp.replace(second=0, microsecond=0)
                values = [_parse_float(row[indices[column]]) for column in expected_columns]
                power_values = [_parse_float(row[indices[column]]) for column in POWER_COLUMNS]
            except (ValueError, IndexError):
                counts["rows_missing_or_nonfinite"] += 1
                continue
            buckets = minute_temperatures.setdefault(minute, [[] for _ in sensors])
            for index, value in enumerate(values):
                buckets[index].append(value)
            minute_power.setdefault(minute, []).append(sum(power_values))
            counts["rows_accepted"] += 1

    snapshots: List[MinuteSnapshot] = []
    for minute in sorted(minute_temperatures):
        buckets = minute_temperatures[minute]
        if any(not values for values in buckets):
            continue
        temperatures = tuple(float(statistics.median(values)) for values in buckets)
        powers = minute_power.get(minute, [])
        snapshots.append(
            MinuteSnapshot(
                minute=minute,
                temperatures=temperatures,
                total_power_w=float(statistics.median(powers)) if powers else None,
            )
        )
    counts["eligible_minutes"] = len(snapshots)
    return snapshots, counts


def _distance(a: SpatialSensor, b: SpatialSensor) -> float:
    return math.sqrt(sum((left - right) ** 2 for left, right in zip(a.position, b.position)))


def _percentile(values: Sequence[float], quantile: float) -> float:
    if not values:
        return math.nan
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    fraction = position - lower
    return float(ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction)


def _error_metrics(errors: Sequence[float]) -> Dict[str, float]:
    return {
        "mae_c": float(statistics.fmean(errors)),
        "rmse_c": math.sqrt(float(statistics.fmean(error * error for error in errors))),
        "p95_absolute_error_c": _percentile(errors, 0.95),
    }


def evaluate_spatial_baselines(
    sensors: Sequence[SpatialSensor],
    snapshots: Sequence[MinuteSnapshot],
) -> Dict[str, object]:
    if len(sensors) < 2:
        raise ValueError("at least two sensors are required")
    if not snapshots:
        raise ValueError("at least one snapshot is required")
    errors: Dict[str, Dict[str, List[float]]] = {
        sensor.name: {method: [] for method in METHODS} for sensor in sensors
    }
    neighbor_order: Dict[int, List[tuple[float, str, int]]] = {}
    for target_index, target in enumerate(sensors):
        candidates = []
        for observed_index, observed in enumerate(sensors):
            if observed_index == target_index:
                continue
            candidates.append((_distance(target, observed), observed.name, observed_index))
        neighbor_order[target_index] = sorted(candidates)

    for snapshot in snapshots:
        if len(snapshot.temperatures) != len(sensors):
            raise ValueError("snapshot temperature count does not match sensors")
        for target_index, target in enumerate(sensors):
            actual = snapshot.temperatures[target_index]
            neighbors = neighbor_order[target_index]
            observed_values = [snapshot.temperatures[index] for _, _, index in neighbors]
            predictions = {
                "global_mean": float(statistics.fmean(observed_values)),
                "nearest_neighbor": float(snapshot.temperatures[neighbors[0][2]]),
            }
            weighted_sum = 0.0
            weight_total = 0.0
            for distance, _, observed_index in neighbors:
                weight = 1.0 / (distance * distance + 1e-12)
                weighted_sum += weight * snapshot.temperatures[observed_index]
                weight_total += weight
            predictions["idw_3d_p2"] = weighted_sum / weight_total
            for method, prediction in predictions.items():
                errors[target.name][method].append(abs(prediction - actual))

    per_sensor: Dict[str, object] = {}
    wins = {method: 0 for method in METHODS}
    for sensor in sensors:
        method_metrics = {method: _error_metrics(errors[sensor.name][method]) for method in METHODS}
        lowest = min(metrics["mae_c"] for metrics in method_metrics.values())
        winners = [
            method
            for method, metrics in method_metrics.items()
            if abs(metrics["mae_c"] - lowest) <= 1e-12
        ]
        for method in winners:
            wins[method] += 1
        per_sensor[sensor.name] = {
            "csv_column": sensor.csv_column,
            "source_label": sensor.source_label,
            "position_m": dict(zip(("x", "y", "z"), sensor.position)),
            "metrics": method_metrics,
            "lowest_mae_methods": winners,
        }

    macro = {
        method: {
            metric: float(
                statistics.fmean(
                    per_sensor[sensor.name]["metrics"][method][metric] for sensor in sensors
                )
            )
            for metric in ("mae_c", "rmse_c", "p95_absolute_error_c")
        }
        for method in METHODS
    }
    win_fractions = {method: wins[method] / len(sensors) for method in METHODS}
    if len(sensors) < 36 or len(snapshots) < 120:
        decision = "not_evaluable"
        reasons = [
            reason
            for condition, reason in (
                (len(sensors) < 36, "fewer_than_36_sensors"),
                (len(snapshots) < 120, "fewer_than_120_eligible_minutes"),
            )
            if condition
        ]
    else:
        supported = (
            macro["idw_3d_p2"]["mae_c"] < macro["global_mean"]["mae_c"]
            and macro["idw_3d_p2"]["mae_c"] < macro["nearest_neighbor"]["mae_c"]
            and win_fractions["idw_3d_p2"] >= 0.60
        )
        decision = "supported" if supported else "not_supported"
        reasons = [] if supported else ["one_or_more_pre_registered_conditions_failed"]

    powers = [snapshot.total_power_w for snapshot in snapshots if snapshot.total_power_w is not None]
    return {
        "sensor_count": len(sensors),
        "snapshot_count": len(snapshots),
        "time_range": {
            "start": min(snapshot.minute for snapshot in snapshots).isoformat(),
            "end": max(snapshot.minute for snapshot in snapshots).isoformat(),
        },
        "power_summary_w": {
            "minimum": min(powers) if powers else None,
            "median": float(statistics.median(powers)) if powers else None,
            "maximum": max(powers) if powers else None,
        },
        "macro_metrics": macro,
        "sensor_wins": wins,
        "sensor_win_fractions": win_fractions,
        "per_sensor": per_sensor,
        "hypothesis": {
            "id": "H-ENC-02",
            "decision": decision,
            "reasons": reasons,
            "required_idw_sensor_win_fraction": 0.60,
        },
    }
