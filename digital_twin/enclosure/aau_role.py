"""Role-conditioned AAU temperature reconstruction for E11D."""

from __future__ import annotations

import csv
import hashlib
import io
import math
import random
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path


ROLES = ("rack_front", "rack_back", "gradient")


def classify_sensor_role(name: str) -> str | None:
    normalized = re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()
    if "gradient" in normalized:
        return "gradient"
    if "front" in normalized:
        return "rack_front"
    if "back" in normalized or "rear" in normalized:
        return "rack_back"
    return None


def extract_frozen_role_map(document: object) -> dict[str, str]:
    """Extract sensor-role pairs without depending on one JSON layout."""
    found: dict[str, str] = {}

    def visit(value: object, parent_key: str | None = None) -> None:
        if isinstance(value, dict):
            inherited_role = classify_sensor_role(parent_key or "")
            csv_column = value.get("csv_column")
            if inherited_role and isinstance(csv_column, str):
                found[csv_column] = inherited_role
            role = next(
                (
                    value[key]
                    for key in ("sensor_role", "role", "category", "group")
                    if isinstance(value.get(key), str) and value[key] in ROLES
                ),
                None,
            )
            if role:
                sensor = next(
                    (
                        value[key]
                        for key in ("sensor_id", "sensor_name", "sensor", "name")
                        if isinstance(value.get(key), str)
                    ),
                    parent_key,
                )
                if sensor:
                    found[sensor] = role
            for key, child in value.items():
                visit(child, key)
        elif isinstance(value, list):
            for child in value:
                visit(child, parent_key)

    visit(document)
    return found


def resolve_header_roles(header: list[str], frozen: dict[str, str]) -> dict[int, tuple[str, str]]:
    compact = lambda value: re.sub(r"[^a-z0-9]", "", value.lower())
    frozen_compact = {compact(name): (name, role) for name, role in frozen.items()}
    resolved: dict[int, tuple[str, str]] = {}
    for index, column in enumerate(header):
        key = compact(column)
        if key in frozen_compact:
            _, role = frozen_compact[key]
            resolved[index] = (column, role)
            continue
        role = classify_sensor_role(column)
        if role:
            resolved[index] = (column, role)
    return resolved


def parse_minute(value: str) -> str:
    text = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        parsed = datetime.strptime(value.strip(), "%Y-%m-%d %H:%M:%S")
    return parsed.replace(second=0, microsecond=0).isoformat()


def load_minute_snapshots(
    fragment_paths: list[Path],
    header: list[str],
    sensor_columns: dict[int, tuple[str, str]],
) -> tuple[list[tuple[str, dict[str, float]]], dict[str, int]]:
    timestamp_index = next(
        (i for i, name in enumerate(header) if "time" in name.lower() or "date" in name.lower()),
        0,
    )
    sums: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    stats = {
        "fragments": len(fragment_paths),
        "boundary_records_discarded": 0,
        "rows_seen": 0,
        "rows_accepted": 0,
        "malformed_rows": 0,
        "nonfinite_values": 0,
    }
    delimiter = ";" if header and ";" in header[0] else ","
    for path in fragment_paths:
        payload = path.read_bytes()
        first = payload.find(b"\n")
        last = payload.rfind(b"\n")
        if first < 0 or last <= first:
            raise ValueError(f"fragment has no complete records: {path}")
        stats["boundary_records_discarded"] += 2
        text = payload[first + 1 : last].decode("utf-8-sig")
        for row in csv.reader(io.StringIO(text), delimiter=delimiter):
            stats["rows_seen"] += 1
            if len(row) != len(header):
                stats["malformed_rows"] += 1
                continue
            try:
                minute = parse_minute(row[timestamp_index])
            except (ValueError, IndexError):
                stats["malformed_rows"] += 1
                continue
            stats["rows_accepted"] += 1
            for index, (sensor, _) in sensor_columns.items():
                try:
                    number = float(row[index])
                except (ValueError, IndexError):
                    continue
                if not math.isfinite(number):
                    stats["nonfinite_values"] += 1
                    continue
                sums[minute][sensor] += number
                counts[minute][sensor] += 1
    sensors = {sensor for sensor, _ in sensor_columns.values()}
    snapshots = []
    for minute in sorted(sums):
        if all(counts[minute].get(sensor, 0) for sensor in sensors):
            snapshots.append(
                (
                    minute,
                    {sensor: sums[minute][sensor] / counts[minute][sensor] for sensor in sensors},
                )
            )
    stats["eligible_minute_snapshots"] = len(snapshots)
    return snapshots, stats


def percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] * (upper - position) + ordered[upper] * (position - lower)


def summarize(errors: list[float]) -> dict[str, float | int]:
    return {
        "n": len(errors),
        "mae_c": sum(errors) / len(errors),
        "rmse_c": math.sqrt(sum(value * value for value in errors) / len(errors)),
        "p95_absolute_error_c": percentile(errors, 0.95),
    }


def evaluate_role_conditioning(
    snapshots: list[tuple[str, dict[str, float]]], roles: dict[str, str]
) -> dict[str, object]:
    global_errors: list[float] = []
    role_errors: list[float] = []
    paired_by_day: dict[str, list[float]] = defaultdict(list)
    per_sensor: dict[str, dict[str, object]] = {}
    per_role_errors: dict[str, dict[str, list[float]]] = {
        role: {"global": [], "role_conditioned": []} for role in ROLES
    }
    sensor_errors: dict[str, dict[str, list[float]]] = {
        sensor: {"global": [], "role_conditioned": []} for sensor in roles
    }
    for minute, values in snapshots:
        day = minute[:10]
        for sensor, actual in values.items():
            peers = [value for other, value in values.items() if other != sensor]
            role_peers = [
                value
                for other, value in values.items()
                if other != sensor and roles[other] == roles[sensor]
            ]
            if not role_peers:
                raise ValueError(f"no same-role peer for {sensor}")
            global_error = abs(actual - sum(peers) / len(peers))
            role_error = abs(actual - sum(role_peers) / len(role_peers))
            global_errors.append(global_error)
            role_errors.append(role_error)
            paired_by_day[day].append(global_error - role_error)
            sensor_errors[sensor]["global"].append(global_error)
            sensor_errors[sensor]["role_conditioned"].append(role_error)
            per_role_errors[roles[sensor]]["global"].append(global_error)
            per_role_errors[roles[sensor]]["role_conditioned"].append(role_error)
    role_wins = 0
    global_wins = 0
    ties = 0
    for sensor in sorted(sensor_errors):
        global_summary = summarize(sensor_errors[sensor]["global"])
        role_summary = summarize(sensor_errors[sensor]["role_conditioned"])
        if role_summary["mae_c"] < global_summary["mae_c"]:
            winner = "role_conditioned"
            role_wins += 1
        elif global_summary["mae_c"] < role_summary["mae_c"]:
            winner = "global"
            global_wins += 1
        else:
            winner = "tie"
            ties += 1
        per_sensor[sensor] = {
            "role": roles[sensor],
            "global": global_summary,
            "role_conditioned": role_summary,
            "winner": winner,
        }
    return {
        "global": summarize(global_errors),
        "role_conditioned": summarize(role_errors),
        "paired_mae_improvement_c": sum(global_errors) / len(global_errors)
        - sum(role_errors) / len(role_errors),
        "paired_improvements_by_day": {
            day: sum(values) / len(values) for day, values in sorted(paired_by_day.items())
        },
        "per_role": {
            role: {model: summarize(errors) for model, errors in models.items()}
            for role, models in per_role_errors.items()
        },
        "per_sensor": per_sensor,
        "per_sensor_wins": {
            "role_conditioned": role_wins,
            "global": global_wins,
            "ties": ties,
        },
    }


def bootstrap_day_improvement(
    improvements_by_day: dict[str, float], replicates: int = 20_000, seed: int = 20_260_823
) -> dict[str, object]:
    days = sorted(improvements_by_day)
    values = [improvements_by_day[day] for day in days]
    generator = random.Random(seed)
    estimates = []
    for _ in range(replicates):
        sample = [generator.choice(values) for _ in values]
        estimates.append(sum(sample) / len(sample))
    return {
        "unit": "calendar_day",
        "day_blocks": len(days),
        "replicates": replicates,
        "seed": seed,
        "ci_95_lower_c": percentile(estimates, 0.025),
        "ci_95_upper_c": percentile(estimates, 0.975),
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()
