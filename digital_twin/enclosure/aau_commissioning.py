"""Commissioning-calibrated virtual sensing for E11H."""

from __future__ import annotations

import math
import statistics
from collections import Counter, defaultdict

from .aau_hierarchical import (
    bootstrap_day_improvement,
    build_neighbor_orders,
    idw_prediction,
    summarize,
)
from .aau_tail_safe import advancement_gates, gated_prediction, tail_safe_specs


Record = tuple[float, float, float]


def commissioning_specs() -> dict[str, dict[str, float | str]]:
    specs: dict[str, dict[str, float | str]] = {}
    for base in ("local", "e11g"):
        for shrinkage in (0.50, 0.75, 1.00):
            specs[f"{base}_median_l{int(shrinkage * 100):03d}"] = {
                "base": base,
                "calibration": "median_offset",
                "shrinkage": shrinkage,
            }
        specs[f"{base}_huber_affine"] = {
            "base": base,
            "calibration": "huber_affine",
        }
    return specs


def _base_prediction(record: Record, base: str, e11g_spec: dict[str, float | str] | None) -> float:
    _, local, role = record
    if base == "local" or e11g_spec is None:
        return local
    return gated_prediction(local, role, e11g_spec)


def huber_affine(x_values: list[float], y_values: list[float]) -> tuple[float, float]:
    if len(x_values) != len(y_values) or not x_values:
        raise ValueError("Huber calibration requires paired non-empty values")
    weights = [1.0] * len(x_values)
    slope = 1.0
    intercept = statistics.median(y - x for x, y in zip(x_values, y_values))
    for _ in range(20):
        weight_sum = sum(weights)
        mean_x = sum(w * x for w, x in zip(weights, x_values)) / weight_sum
        mean_y = sum(w * y for w, y in zip(weights, y_values)) / weight_sum
        denominator = sum(w * (x - mean_x) ** 2 for w, x in zip(weights, x_values)) + 1e-12
        slope = sum(
            w * (x - mean_x) * (y - mean_y)
            for w, x, y in zip(weights, x_values, y_values)
        ) / denominator
        slope = max(0.5, min(1.5, slope))
        intercept = mean_y - slope * mean_x
        residuals = [y - (slope * x + intercept) for x, y in zip(x_values, y_values)]
        center = statistics.median(residuals)
        mad = statistics.median(abs(value - center) for value in residuals)
        scale = max(1e-6, 1.4826 * mad)
        cutoff = 1.345 * scale
        weights = [1.0 if abs(value) <= cutoff else cutoff / abs(value) for value in residuals]
    return slope, intercept


def fit_candidate(
    records: list[Record],
    spec: dict[str, float | str],
    e11g_spec: dict[str, float | str] | None,
) -> dict[str, float | str]:
    base_values = [_base_prediction(record, str(spec["base"]), e11g_spec) for record in records]
    truths = [record[0] for record in records]
    fitted = dict(spec)
    if spec["calibration"] == "median_offset":
        residual = statistics.median(truth - base for truth, base in zip(truths, base_values))
        fitted["offset_c"] = float(spec["shrinkage"]) * residual
    else:
        slope, intercept = huber_affine(base_values, truths)
        fitted["slope"] = slope
        fitted["intercept_c"] = intercept
    return fitted


def calibrated_prediction(
    record: Record,
    model: dict[str, float | str],
    e11g_spec: dict[str, float | str] | None,
) -> float:
    base = _base_prediction(record, str(model["base"]), e11g_spec)
    if model["calibration"] == "median_offset":
        return base + float(model["offset_c"])
    return float(model["slope"]) * base + float(model["intercept_c"])


def _errors(
    records: list[Record],
    model: dict[str, float | str] | None,
    e11g_spec: dict[str, float | str] | None,
) -> list[float]:
    if model is None:
        return [abs(record[1] - record[0]) for record in records]
    return [abs(calibrated_prediction(record, model, e11g_spec) - record[0]) for record in records]


def select_commissioning_model(
    calibration_records: list[Record],
    selection_records: list[Record],
    e11g_spec: dict[str, float | str] | None,
    minimum_improvement_c: float = 0.02,
) -> tuple[str, dict[str, float | str] | None]:
    baseline = summarize(_errors(selection_records, None, e11g_spec))
    eligible: list[tuple[float, float, float, str, dict[str, float | str]]] = []
    for model_id, spec in commissioning_specs().items():
        model = fit_candidate(calibration_records, spec, e11g_spec)
        metrics = summarize(_errors(selection_records, model, e11g_spec))
        if float(baseline["mae_c"]) - float(metrics["mae_c"]) < minimum_improvement_c:
            continue
        if float(baseline["rmse_c"]) - float(metrics["rmse_c"]) < minimum_improvement_c:
            continue
        if (
            float(baseline["p95_absolute_error_c"])
            - float(metrics["p95_absolute_error_c"])
            < minimum_improvement_c
        ):
            continue
        eligible.append(
            (
                float(metrics["p95_absolute_error_c"]),
                float(metrics["mae_c"]),
                float(metrics["rmse_c"]),
                model_id,
                model,
            )
        )
    if not eligible:
        return "baseline_local_idw_k3_p2", None
    selected = min(eligible)
    return selected[3], selected[4]


def evaluate_commissioning(
    snapshots: list[tuple[str, dict[str, float]]],
    metadata: dict[str, dict[str, object]],
    e11g_map: dict[str, str],
) -> dict[str, object]:
    all_neighbors = build_neighbor_orders(metadata, same_role=False)
    role_neighbors = build_neighbor_orders(metadata, same_role=True)
    tail_specs = tail_safe_specs()
    records: dict[str, dict[str, list[Record]]] = defaultdict(lambda: defaultdict(list))
    for timestamp, values in snapshots:
        day = timestamp[:10]
        for sensor_id in sorted(metadata):
            if sensor_id not in values:
                continue
            local = idw_prediction(values, all_neighbors[sensor_id], k=3, power=2.0)
            role = idw_prediction(values, role_neighbors[sensor_id], k=5, power=2.0)
            records[sensor_id][day].append((values[sensor_id], local, role))

    days = sorted({day for sensor_days in records.values() for day in sensor_days})
    if len(days) < 5:
        raise ValueError("E11H requires at least five complete day blocks")
    calibration_days = days[:2]
    selection_day = days[2]
    test_days = days[3:]

    selected_models: dict[str, dict[str, object]] = {}
    selection_counts: Counter[str] = Counter()
    for sensor_id in sorted(records):
        calibration_records = [record for day in calibration_days for record in records[sensor_id][day]]
        selection_records = records[sensor_id][selection_day]
        e11g_id = e11g_map[sensor_id]
        e11g_spec = None if e11g_id == "baseline_local_idw_k3_p2" else tail_specs[e11g_id]
        model_id, model = select_commissioning_model(
            calibration_records, selection_records, e11g_spec
        )
        selected_models[sensor_id] = {"model_id": model_id, "parameters": model}
        selection_counts[model_id] += 1

    baseline_errors: list[float] = []
    model_errors: list[float] = []
    baseline_by_sensor: dict[str, list[float]] = defaultdict(list)
    model_by_sensor: dict[str, list[float]] = defaultdict(list)
    day_improvements: dict[str, float] = {}
    for day in test_days:
        day_baseline: list[float] = []
        day_model: list[float] = []
        for sensor_id in sorted(records):
            e11g_id = e11g_map[sensor_id]
            e11g_spec = None if e11g_id == "baseline_local_idw_k3_p2" else tail_specs[e11g_id]
            model = selected_models[sensor_id]["parameters"]
            for record in records[sensor_id][day]:
                baseline_error = abs(record[1] - record[0])
                prediction = record[1] if model is None else calibrated_prediction(record, model, e11g_spec)
                model_error = abs(prediction - record[0])
                baseline_errors.append(baseline_error)
                model_errors.append(model_error)
                baseline_by_sensor[sensor_id].append(baseline_error)
                model_by_sensor[sensor_id].append(model_error)
                day_baseline.append(baseline_error)
                day_model.append(model_error)
        day_improvements[day] = sum(day_baseline) / len(day_baseline) - sum(day_model) / len(day_model)

    baseline_metrics = summarize(baseline_errors)
    model_metrics = summarize(model_errors)
    per_sensor = {
        sensor_id: {
            "baseline_mae_c": sum(baseline_by_sensor[sensor_id]) / len(baseline_by_sensor[sensor_id]),
            "model_mae_c": sum(model_by_sensor[sensor_id]) / len(model_by_sensor[sensor_id]),
        }
        for sensor_id in sorted(baseline_by_sensor)
    }
    sensor_wins = sum(value["model_mae_c"] < value["baseline_mae_c"] for value in per_sensor.values())
    bootstrap = bootstrap_day_improvement(day_improvements, replicates=20000, seed=20260823)
    gates = advancement_gates(baseline_metrics, model_metrics, sensor_wins, bootstrap)
    passed = all(gates.values())
    return {
        "candidate_count": len(commissioning_specs()),
        "chronology": {
            "calibration_days": calibration_days,
            "selection_day": selection_day,
            "test_days": test_days,
        },
        "test_measurement_count": len(model_errors),
        "metrics": {
            "baseline_local_idw_k3_p2": baseline_metrics,
            "commissioning_sensor_map_v1": model_metrics,
        },
        "sensor_wins": sensor_wins,
        "sensor_count": len(per_sensor),
        "per_sensor_mae": per_sensor,
        "day_mae_improvement_c": day_improvements,
        "bootstrap": bootstrap,
        "gates": gates,
        "selection_counts": dict(sorted(selection_counts.items())),
        "selected_models": selected_models,
        "development_decision": "candidate_forwarded_to_e11f" if passed else "no_candidate_forwarded",
    }


def evaluate_frozen_confirmation(
    snapshots: list[tuple[str, dict[str, float]]],
    metadata: dict[str, dict[str, object]],
    e11g_map: dict[str, str],
    selected_models: dict[str, dict[str, object]],
) -> dict[str, object]:
    all_neighbors = build_neighbor_orders(metadata, same_role=False)
    role_neighbors = build_neighbor_orders(metadata, same_role=True)
    tail_specs = tail_safe_specs()
    baseline_errors: list[float] = []
    model_errors: list[float] = []
    baseline_by_sensor: dict[str, list[float]] = defaultdict(list)
    model_by_sensor: dict[str, list[float]] = defaultdict(list)
    errors_by_day: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: {"baseline": [], "model": []}
    )

    for timestamp, values in snapshots:
        day = timestamp[:10]
        for sensor_id in sorted(metadata):
            if sensor_id not in values:
                continue
            local = idw_prediction(values, all_neighbors[sensor_id], k=3, power=2.0)
            role = idw_prediction(values, role_neighbors[sensor_id], k=5, power=2.0)
            record = (values[sensor_id], local, role)
            e11g_id = e11g_map[sensor_id]
            e11g_spec = None if e11g_id == "baseline_local_idw_k3_p2" else tail_specs[e11g_id]
            model = selected_models[sensor_id]["parameters"]
            prediction = local if model is None else calibrated_prediction(record, model, e11g_spec)
            baseline_error = abs(local - values[sensor_id])
            model_error = abs(prediction - values[sensor_id])
            baseline_errors.append(baseline_error)
            model_errors.append(model_error)
            baseline_by_sensor[sensor_id].append(baseline_error)
            model_by_sensor[sensor_id].append(model_error)
            errors_by_day[day]["baseline"].append(baseline_error)
            errors_by_day[day]["model"].append(model_error)

    baseline_metrics = summarize(baseline_errors)
    model_metrics = summarize(model_errors)
    per_sensor = {
        sensor_id: {
            "baseline_mae_c": sum(baseline_by_sensor[sensor_id]) / len(baseline_by_sensor[sensor_id]),
            "model_mae_c": sum(model_by_sensor[sensor_id]) / len(model_by_sensor[sensor_id]),
        }
        for sensor_id in sorted(baseline_by_sensor)
    }
    sensor_wins = sum(value["model_mae_c"] < value["baseline_mae_c"] for value in per_sensor.values())
    day_improvements = {
        day: sum(values["baseline"]) / len(values["baseline"])
        - sum(values["model"]) / len(values["model"])
        for day, values in sorted(errors_by_day.items())
    }
    bootstrap = bootstrap_day_improvement(day_improvements, replicates=20000, seed=20260823)
    gates = advancement_gates(baseline_metrics, model_metrics, sensor_wins, bootstrap)
    supported = all(gates.values())
    return {
        "frozen_model_count": len(selected_models),
        "day_blocks": len(day_improvements),
        "measurement_count": len(model_errors),
        "metrics": {
            "baseline_local_idw_k3_p2": baseline_metrics,
            "frozen_commissioning_sensor_map_v1": model_metrics,
        },
        "sensor_wins": sensor_wins,
        "sensor_count": len(per_sensor),
        "per_sensor_mae": per_sensor,
        "day_mae_improvement_c": day_improvements,
        "bootstrap": bootstrap,
        "gates": gates,
        "confirmation_decision": (
            "h_enc_05_supported_within_campaign" if supported else "h_enc_05_not_supported"
        ),
    }

