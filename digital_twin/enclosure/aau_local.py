"""Fixed local-neighborhood confirmation for AAU server-room temperatures."""

from __future__ import annotations

from collections import defaultdict
from math import isfinite, sqrt
import random
from typing import Dict, List, Sequence

from .aau_spatial import MinuteSnapshot, SpatialSensor


def _distance(a: SpatialSensor, b: SpatialSensor) -> float:
    return sqrt(sum((left - right) ** 2 for left, right in zip(a.position, b.position)))


def _percentile(values: Sequence[float], quantile: float) -> float:
    if not values:
        raise ValueError("percentile requires at least one value")
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def _metrics(errors: Sequence[float]) -> Dict[str, float]:
    if not errors:
        raise ValueError("metrics require at least one error")
    absolute = [abs(error) for error in errors]
    return {
        "mae_c": sum(absolute) / len(absolute),
        "rmse_c": sqrt(sum(error * error for error in errors) / len(errors)),
        "p95_absolute_error_c": _percentile(absolute, 0.95),
    }


def _idw_prediction(
    target_index: int,
    neighbor_indices: Sequence[int],
    sensors: Sequence[SpatialSensor],
    temperatures: Sequence[float],
    power: float,
) -> float:
    weighted_sum = 0.0
    weight_sum = 0.0
    for neighbor_index in neighbor_indices:
        distance = _distance(sensors[target_index], sensors[neighbor_index])
        if distance <= 0.0:
            return temperatures[neighbor_index]
        weight = 1.0 / (distance**power)
        weighted_sum += weight * temperatures[neighbor_index]
        weight_sum += weight
    return weighted_sum / weight_sum


def evaluate_local_idw_confirmation(
    sensors: Sequence[SpatialSensor],
    snapshots: Sequence[MinuteSnapshot],
    *,
    neighbor_count: int = 3,
    distance_power: float = 2.0,
    bootstrap_seed: int = 20260823,
    bootstrap_replicates: int = 20000,
) -> Dict[str, object]:
    if neighbor_count < 2:
        raise ValueError("neighbor_count must be at least 2")
    if neighbor_count >= len(sensors):
        raise ValueError("neighbor_count must be smaller than sensor count")
    if distance_power <= 0.0:
        raise ValueError("distance_power must be positive")
    if bootstrap_replicates <= 0:
        raise ValueError("bootstrap_replicates must be positive")
    if not snapshots:
        raise ValueError("at least one snapshot is required")

    methods = ("nearest_neighbor", "local_idw_k3_p2", "global_idw_p2")
    aggregate_errors: Dict[str, List[float]] = {name: [] for name in methods}
    sensor_errors: Dict[str, Dict[str, List[float]]] = {
        sensor.name: {name: [] for name in methods} for sensor in sensors
    }
    day_improvements: Dict[str, List[float]] = defaultdict(list)

    neighbor_orders: List[List[int]] = []
    for target_index, target in enumerate(sensors):
        observed = [index for index in range(len(sensors)) if index != target_index]
        observed.sort(key=lambda index: (_distance(target, sensors[index]), sensors[index].name))
        neighbor_orders.append(observed)

    for snapshot in snapshots:
        if len(snapshot.temperatures) != len(sensors):
            raise ValueError("snapshot temperature count does not match sensor count")
        if not all(isfinite(value) for value in snapshot.temperatures):
            raise ValueError("snapshot contains non-finite temperature")
        day = snapshot.minute.date().isoformat()
        for target_index, sensor in enumerate(sensors):
            ordered = neighbor_orders[target_index]
            truth = snapshot.temperatures[target_index]
            predictions = {
                "nearest_neighbor": snapshot.temperatures[ordered[0]],
                "local_idw_k3_p2": _idw_prediction(
                    target_index,
                    ordered[:neighbor_count],
                    sensors,
                    snapshot.temperatures,
                    distance_power,
                ),
                "global_idw_p2": _idw_prediction(
                    target_index,
                    ordered,
                    sensors,
                    snapshot.temperatures,
                    distance_power,
                ),
            }
            absolute = {}
            for method, prediction in predictions.items():
                error = prediction - truth
                aggregate_errors[method].append(error)
                sensor_errors[sensor.name][method].append(error)
                absolute[method] = abs(error)
            day_improvements[day].append(
                absolute["nearest_neighbor"] - absolute["local_idw_k3_p2"]
            )

    macro_metrics = {method: _metrics(errors) for method, errors in aggregate_errors.items()}
    per_sensor: Dict[str, object] = {}
    local_wins = 0
    nearest_wins = 0
    ties = 0
    for sensor in sensors:
        metrics = {method: _metrics(sensor_errors[sensor.name][method]) for method in methods}
        local_mae = metrics["local_idw_k3_p2"]["mae_c"]
        nearest_mae = metrics["nearest_neighbor"]["mae_c"]
        if local_mae < nearest_mae:
            local_wins += 1
            pairwise_winner = "local_idw_k3_p2"
        elif nearest_mae < local_mae:
            nearest_wins += 1
            pairwise_winner = "nearest_neighbor"
        else:
            ties += 1
            pairwise_winner = "tie"
        per_sensor[sensor.name] = {
            "csv_column": sensor.csv_column,
            "source_label": sensor.source_label,
            "position_m": {"x": sensor.position[0], "y": sensor.position[1], "z": sensor.position[2]},
            "metrics": metrics,
            "pairwise_winner": pairwise_winner,
        }

    days = sorted(day_improvements)
    rng = random.Random(bootstrap_seed)
    bootstrap_values: List[float] = []
    for _ in range(bootstrap_replicates):
        selected = [days[rng.randrange(len(days))] for _ in days]
        total = sum(sum(day_improvements[day]) for day in selected)
        count = sum(len(day_improvements[day]) for day in selected)
        bootstrap_values.append(total / count)

    observed_improvement = (
        macro_metrics["nearest_neighbor"]["mae_c"]
        - macro_metrics["local_idw_k3_p2"]["mae_c"]
    )
    bootstrap = {
        "unit": "calendar_day",
        "block_count": len(days),
        "seed": bootstrap_seed,
        "replicates": bootstrap_replicates,
        "paired_mae_improvement_c": observed_improvement,
        "ci95_lower_c": _percentile(bootstrap_values, 0.025),
        "ci95_upper_c": _percentile(bootstrap_values, 0.975),
    }
    evaluable = len(sensors) == 42 and len(snapshots) >= 120
    conditions = {
        "local_mae_lower": macro_metrics["local_idw_k3_p2"]["mae_c"]
        < macro_metrics["nearest_neighbor"]["mae_c"],
        "local_rmse_lower": macro_metrics["local_idw_k3_p2"]["rmse_c"]
        < macro_metrics["nearest_neighbor"]["rmse_c"],
        "local_sensor_wins_at_least_26": local_wins >= 26,
        "bootstrap_ci95_lower_above_zero": bootstrap["ci95_lower_c"] > 0.0,
    }
    decision = "not_evaluable" if not evaluable else (
        "supported" if all(conditions.values()) else "not_supported"
    )
    return {
        "settings": {
            "neighbor_count": neighbor_count,
            "distance_power": distance_power,
            "tie_break": "sensor_name",
        },
        "sensor_count": len(sensors),
        "snapshot_count": len(snapshots),
        "macro_metrics": macro_metrics,
        "pairwise_sensor_results": {
            "local_idw_wins": local_wins,
            "nearest_neighbor_wins": nearest_wins,
            "ties": ties,
        },
        "bootstrap": bootstrap,
        "per_sensor": per_sensor,
        "hypothesis": {
            "id": "H-ENC-03",
            "decision": decision,
            "conditions": conditions,
            "required_local_sensor_wins": 26,
        },
    }
