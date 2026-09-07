"""Preregistered hierarchical role-local development models for E11E."""

from __future__ import annotations

import math
from collections import defaultdict

from digital_twin.enclosure.aau_role import (
    ROLES,
    bootstrap_day_improvement,
    classify_sensor_role,
    summarize,
)


def extract_frozen_sensor_metadata(document: dict[str, object]) -> dict[str, dict[str, object]]:
    try:
        per_sensor = document["evaluation"]["per_sensor"]
    except (KeyError, TypeError) as exc:
        raise ValueError("missing E11C evaluation.per_sensor metadata") from exc
    metadata: dict[str, dict[str, object]] = {}
    for sensor_id, item in per_sensor.items():
        role = classify_sensor_role(sensor_id)
        if role not in ROLES or not isinstance(item, dict):
            continue
        column = item.get("csv_column")
        position = item.get("position_m")
        if not isinstance(column, str) or not isinstance(position, dict):
            raise ValueError(f"incomplete frozen metadata for {sensor_id}")

        def coordinate(axis: str) -> float:
            for key in (axis, f"{axis}_m"):
                if key in position:
                    return float(position[key])
            raise ValueError(f"missing {axis} coordinate for {sensor_id}")

        metadata[column] = {
            "sensor_id": sensor_id,
            "role": role,
            "position_m": (coordinate("x"), coordinate("y"), coordinate("z")),
        }
    return metadata


def build_neighbor_orders(
    metadata: dict[str, dict[str, object]], same_role: bool
) -> dict[str, list[tuple[str, float]]]:
    orders: dict[str, list[tuple[str, float]]] = {}
    for target, target_meta in metadata.items():
        tx, ty, tz = target_meta["position_m"]
        peers = []
        for sensor, sensor_meta in metadata.items():
            if sensor == target:
                continue
            if same_role and sensor_meta["role"] != target_meta["role"]:
                continue
            sx, sy, sz = sensor_meta["position_m"]
            distance = math.sqrt((tx - sx) ** 2 + (ty - sy) ** 2 + (tz - sz) ** 2)
            peers.append((sensor, distance))
        peers.sort(key=lambda item: (item[1], metadata[item[0]]["sensor_id"]))
        if not peers:
            raise ValueError(f"no eligible peers for {target}")
        orders[target] = peers
    return orders


def idw_prediction(
    values: dict[str, float], ordered_peers: list[tuple[str, float]], k: int, power: float
) -> float:
    selected = ordered_peers[: min(k, len(ordered_peers))]
    zero_distance = [values[sensor] for sensor, distance in selected if distance == 0]
    if zero_distance:
        return sum(zero_distance) / len(zero_distance)
    weighted = [(values[sensor], 1.0 / (distance**power)) for sensor, distance in selected]
    return sum(value * weight for value, weight in weighted) / sum(weight for _, weight in weighted)


def candidate_specs() -> dict[str, dict[str, object]]:
    specs: dict[str, dict[str, object]] = {}
    for k in (1, 3, 5):
        for power in (1, 2):
            role_local_id = f"role_local_k{k}_p{power}"
            specs[role_local_id] = {"kind": "role_local", "k": k, "power": power}
            for alpha, alpha_id in ((0.25, "025"), (0.50, "050"), (0.75, "075")):
                specs[f"blend_a{alpha_id}_k{k}_p{power}"] = {
                    "kind": "blend",
                    "k": k,
                    "power": power,
                    "alpha": alpha,
                }
    return specs


def evaluate_hierarchical_grid(
    snapshots: list[tuple[str, dict[str, float]]], metadata: dict[str, dict[str, object]]
) -> dict[str, object]:
    all_orders = build_neighbor_orders(metadata, same_role=False)
    role_orders = build_neighbor_orders(metadata, same_role=True)
    candidates = candidate_specs()
    model_ids = ["baseline_local_idw_k3_p2", "baseline_role_mean", *sorted(candidates)]
    all_errors: dict[str, list[float]] = {model: [] for model in model_ids}
    role_errors = {
        model: {role: [] for role in ROLES} for model in model_ids
    }
    sensor_sums = {model: defaultdict(float) for model in model_ids}
    sensor_counts = {model: defaultdict(int) for model in model_ids}
    day_sums = {model: defaultdict(float) for model in model_ids}
    day_counts = {model: defaultdict(int) for model in model_ids}

    for minute, values in snapshots:
        day = minute[:10]
        for target, actual in values.items():
            role = metadata[target]["role"]
            role_peer_values = [
                values[sensor]
                for sensor in values
                if sensor != target and metadata[sensor]["role"] == role
            ]
            role_mean = sum(role_peer_values) / len(role_peer_values)
            predictions = {
                "baseline_local_idw_k3_p2": idw_prediction(values, all_orders[target], 3, 2),
                "baseline_role_mean": role_mean,
            }
            for model_id, spec in candidates.items():
                role_local = idw_prediction(
                    values, role_orders[target], int(spec["k"]), float(spec["power"])
                )
                predictions[model_id] = (
                    role_local
                    if spec["kind"] == "role_local"
                    else float(spec["alpha"]) * role_local + (1.0 - float(spec["alpha"])) * role_mean
                )
            for model_id, prediction in predictions.items():
                error = abs(actual - prediction)
                all_errors[model_id].append(error)
                role_errors[model_id][role].append(error)
                sensor_sums[model_id][target] += error
                sensor_counts[model_id][target] += 1
                day_sums[model_id][day] += error
                day_counts[model_id][day] += 1

    metrics = {model: summarize(errors) for model, errors in all_errors.items()}
    per_role = {
        model: {role: summarize(errors) for role, errors in roles.items()}
        for model, roles in role_errors.items()
    }
    per_sensor_mae = {
        model: {
            sensor: sensor_sums[model][sensor] / sensor_counts[model][sensor]
            for sensor in sorted(metadata)
        }
        for model in model_ids
    }
    baselines = ("baseline_local_idw_k3_p2", "baseline_role_mean")
    stronger = min(
        baselines,
        key=lambda model: (
            metrics[model]["mae_c"],
            metrics[model]["p95_absolute_error_c"],
            model,
        ),
    )
    gates = {}
    passing = []
    baseline_days = {
        day: day_sums[stronger][day] / day_counts[stronger][day] for day in day_sums[stronger]
    }
    for model_id in sorted(candidates):
        candidate_days = {
            day: day_sums[model_id][day] / day_counts[model_id][day] for day in day_sums[model_id]
        }
        improvements = {
            day: baseline_days[day] - candidate_days[day] for day in sorted(baseline_days)
        }
        bootstrap = bootstrap_day_improvement(improvements)
        wins = sum(
            per_sensor_mae[model_id][sensor] < per_sensor_mae[stronger][sensor]
            for sensor in metadata
        )
        ties = sum(
            per_sensor_mae[model_id][sensor] == per_sensor_mae[stronger][sensor]
            for sensor in metadata
        )
        conditions = {
            "mae_lower_than_stronger_baseline": metrics[model_id]["mae_c"] < metrics[stronger]["mae_c"],
            "rmse_lower_than_stronger_baseline": metrics[model_id]["rmse_c"] < metrics[stronger]["rmse_c"],
            "p95_lower_than_stronger_baseline": metrics[model_id]["p95_absolute_error_c"]
            < metrics[stronger]["p95_absolute_error_c"],
            "sensor_wins_at_least_26_of_42": wins >= 26,
            "bootstrap_ci_lower_above_zero": bootstrap["ci_95_lower_c"] > 0,
            "absolute_mae_at_most_1_25_c": metrics[model_id]["mae_c"] <= 1.25,
            "absolute_rmse_at_most_1_90_c": metrics[model_id]["rmse_c"] <= 1.90,
            "absolute_p95_at_most_4_00_c": metrics[model_id]["p95_absolute_error_c"] <= 4.00,
        }
        passed = all(conditions.values())
        gates[model_id] = {
            "passed": passed,
            "sensor_wins": wins,
            "sensor_ties": ties,
            "bootstrap": bootstrap,
            "conditions": conditions,
        }
        if passed:
            passing.append(model_id)
    selected = (
        min(
            passing,
            key=lambda model: (
                metrics[model]["mae_c"],
                metrics[model]["p95_absolute_error_c"],
                metrics[model]["rmse_c"],
                model,
            ),
        )
        if passing
        else None
    )
    return {
        "model_count": len(model_ids),
        "candidate_count": len(candidates),
        "stronger_baseline": stronger,
        "metrics": metrics,
        "per_role": per_role,
        "per_sensor_mae": per_sensor_mae,
        "candidate_gates": gates,
        "passing_candidates": passing,
        "selected_candidate": selected,
        "development_decision": "candidate_forwarded" if selected else "no_candidate_forwarded",
        "selected_spec": candidates.get(selected) if selected else None,
    }

