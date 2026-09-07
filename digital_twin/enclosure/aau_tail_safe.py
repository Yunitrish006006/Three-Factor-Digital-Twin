"""Tail-safe adaptive gating for AAU enclosure-temperature development."""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Iterable

from .aau_hierarchical import (
    bootstrap_day_improvement,
    build_neighbor_orders,
    idw_prediction,
    summarize,
)


Record = tuple[float, float, float]


def tail_safe_specs() -> dict[str, dict[str, float | str]]:
    specs: dict[str, dict[str, float | str]] = {}
    for family in ("clip", "fallback"):
        for alpha in (0.50, 0.75, 1.00):
            for threshold in (0.25, 0.50, 1.00, 1.50, 2.00):
                model_id = f"{family}_a{int(alpha * 100):03d}_t{int(threshold * 100):03d}"
                specs[model_id] = {
                    "family": family,
                    "alpha": alpha,
                    "threshold_c": threshold,
                }
    return specs


def gated_prediction(base: float, role: float, spec: dict[str, float | str]) -> float:
    alpha = float(spec["alpha"])
    threshold = float(spec["threshold_c"])
    delta = role - base
    if spec["family"] == "clip":
        correction = max(-threshold, min(threshold, delta))
        return base + alpha * correction
    if spec["family"] == "fallback":
        return base + alpha * delta if abs(delta) <= threshold else base
    raise ValueError(f"unknown gate family: {spec['family']}")


def _errors(records: Iterable[Record], spec: dict[str, float | str] | None) -> list[float]:
    errors: list[float] = []
    for truth, base, role in records:
        prediction = base if spec is None else gated_prediction(base, role, spec)
        errors.append(abs(prediction - truth))
    return errors


def select_sensor_spec(
    records_by_day: dict[str, list[Record]],
    training_days: list[str],
    specs: dict[str, dict[str, float | str]],
    minimum_improvement_c: float = 0.02,
    minimum_day_fraction: float = 0.60,
) -> str:
    training_records = [record for day in training_days for record in records_by_day[day]]
    baseline = summarize(_errors(training_records, None))
    required_day_wins = math.ceil(minimum_day_fraction * len(training_days))
    eligible: list[tuple[float, float, float, str]] = []

    baseline_daily_mae = {
        day: summarize(_errors(records_by_day[day], None))["mae_c"] for day in training_days
    }
    for model_id, spec in specs.items():
        candidate = summarize(_errors(training_records, spec))
        if float(baseline["mae_c"]) - float(candidate["mae_c"]) < minimum_improvement_c:
            continue
        if float(baseline["rmse_c"]) - float(candidate["rmse_c"]) < minimum_improvement_c:
            continue
        if (
            float(baseline["p95_absolute_error_c"])
            - float(candidate["p95_absolute_error_c"])
            < minimum_improvement_c
        ):
            continue
        day_wins = sum(
            summarize(_errors(records_by_day[day], spec))["mae_c"] < baseline_daily_mae[day]
            for day in training_days
        )
        if day_wins < required_day_wins:
            continue
        eligible.append(
            (
                float(candidate["p95_absolute_error_c"]),
                float(candidate["mae_c"]),
                float(candidate["rmse_c"]),
                model_id,
            )
        )
    return min(eligible)[3] if eligible else "baseline_local_idw_k3_p2"


def advancement_gates(
    baseline: dict[str, float | int],
    model: dict[str, float | int],
    sensor_wins: int,
    bootstrap: dict[str, object],
) -> dict[str, bool]:
    return {
        "lower_mae": float(model["mae_c"]) < float(baseline["mae_c"]),
        "lower_rmse": float(model["rmse_c"]) < float(baseline["rmse_c"]),
        "lower_p95": float(model["p95_absolute_error_c"])
        < float(baseline["p95_absolute_error_c"]),
        "sensor_wins_at_least_26": sensor_wins >= 26,
        "bootstrap_lower_above_zero": float(bootstrap["ci_95_lower_c"]) > 0.0,
        "absolute_mae_at_most_1_25": float(model["mae_c"]) <= 1.25,
        "absolute_rmse_at_most_1_90": float(model["rmse_c"]) <= 1.90,
        "absolute_p95_at_most_4_00": float(model["p95_absolute_error_c"]) <= 4.00,
    }


def evaluate_tail_safe_gating(
    snapshots: list[tuple[str, dict[str, float]]],
    metadata: dict[str, dict[str, object]],
) -> dict[str, object]:
    specs = tail_safe_specs()
    all_neighbors = build_neighbor_orders(metadata, same_role=False)
    role_neighbors = build_neighbor_orders(metadata, same_role=True)
    records: dict[str, dict[str, list[Record]]] = defaultdict(lambda: defaultdict(list))

    for timestamp, values in snapshots:
        day = timestamp[:10]
        for sensor_id in sorted(metadata):
            if sensor_id not in values:
                continue
            base = idw_prediction(values, all_neighbors[sensor_id], k=3, power=2.0)
            role = idw_prediction(values, role_neighbors[sensor_id], k=5, power=2.0)
            records[sensor_id][day].append((values[sensor_id], base, role))

    days = sorted({day for sensor_days in records.values() for day in sensor_days})
    if len(days) < 4:
        raise ValueError("tail-safe evaluation requires at least four day blocks")

    baseline_errors: list[float] = []
    model_errors: list[float] = []
    baseline_by_sensor: dict[str, list[float]] = defaultdict(list)
    model_by_sensor: dict[str, list[float]] = defaultdict(list)
    day_improvements: dict[str, float] = {}
    fold_selection_counts: Counter[str] = Counter()
    fold_maps: dict[str, dict[str, str]] = {}

    for held_day in days:
        training_days = [day for day in days if day != held_day]
        fold_map: dict[str, str] = {}
        held_baseline: list[float] = []
        held_model: list[float] = []
        for sensor_id in sorted(records):
            if held_day not in records[sensor_id]:
                continue
            selected = select_sensor_spec(records[sensor_id], training_days, specs)
            fold_map[sensor_id] = selected
            fold_selection_counts[selected] += 1
            spec = None if selected == "baseline_local_idw_k3_p2" else specs[selected]
            for truth, base, role in records[sensor_id][held_day]:
                prediction = base if spec is None else gated_prediction(base, role, spec)
                base_error = abs(base - truth)
                model_error = abs(prediction - truth)
                baseline_errors.append(base_error)
                model_errors.append(model_error)
                baseline_by_sensor[sensor_id].append(base_error)
                model_by_sensor[sensor_id].append(model_error)
                held_baseline.append(base_error)
                held_model.append(model_error)
        fold_maps[held_day] = fold_map
        day_improvements[held_day] = sum(held_baseline) / len(held_baseline) - sum(held_model) / len(held_model)

    baseline_metrics = summarize(baseline_errors)
    model_metrics = summarize(model_errors)
    per_sensor = {
        sensor_id: {
            "baseline_mae_c": sum(baseline_by_sensor[sensor_id]) / len(baseline_by_sensor[sensor_id]),
            "model_mae_c": sum(model_by_sensor[sensor_id]) / len(model_by_sensor[sensor_id]),
        }
        for sensor_id in sorted(baseline_by_sensor)
    }
    sensor_wins = sum(v["model_mae_c"] < v["baseline_mae_c"] for v in per_sensor.values())
    bootstrap = bootstrap_day_improvement(day_improvements, replicates=20000, seed=20260823)
    gates = advancement_gates(baseline_metrics, model_metrics, sensor_wins, bootstrap)

    deployment_map = {
        sensor_id: select_sensor_spec(records[sensor_id], days, specs)
        for sensor_id in sorted(records)
    }
    passed = all(gates.values())
    return {
        "candidate_count": len(specs),
        "cross_validation": "leave_one_day_out_with_fold_internal_sensor_selection",
        "day_blocks": len(days),
        "measurement_count": len(model_errors),
        "metrics": {
            "baseline_local_idw_k3_p2": baseline_metrics,
            "tail_safe_sensor_map_v1": model_metrics,
        },
        "sensor_wins": sensor_wins,
        "sensor_count": len(per_sensor),
        "per_sensor_mae": per_sensor,
        "day_mae_improvement_c": day_improvements,
        "bootstrap": bootstrap,
        "gates": gates,
        "fold_selection_counts": dict(sorted(fold_selection_counts.items())),
        "fold_maps": fold_maps,
        "deployment_map": deployment_map,
        "development_decision": "candidate_forwarded_to_e11f" if passed else "no_candidate_forwarded",
    }
