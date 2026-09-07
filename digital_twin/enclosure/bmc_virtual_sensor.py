"""Standard-library E12 sparse BMC virtual-sensor evaluation."""

from __future__ import annotations

import csv
import math
import random
import statistics
from pathlib import Path
from typing import Iterable


SOURCE_COLUMNS = ("_time", "_measurement", "device_id")
NUMERIC_COLUMNS = (
    "Inlet_Temp", "Outlet_Temp", "Cpu1_Temp", "Cpu2_Temp",
    "FAN1", "FAN2", "FAN3", "FAN4", "PSU1_Total_Power",
    "PSU2_Total_Power",
)
REQUIRED_COLUMNS = SOURCE_COLUMNS + NUMERIC_COLUMNS
FEATURE_SETS = {
    "thermal_pair": ("inlet", "outlet"),
    "load_aware": ("inlet", "outlet", "fan_krpm", "power_100w"),
    "load_aware_interactions": (
        "inlet", "outlet", "fan_krpm", "power_100w", "thermal_rise",
        "power_per_fan",
    ),
}
LAMBDAS = (0.01, 0.1, 1.0, 10.0)


def parse_influx_bmc(path: Path) -> dict:
    header = None
    section_is_bmc_capable = False
    raw_section_rows = []
    rows = []
    unit_sections = []
    total = 0
    invalid = 0
    rejected_non_bmc = 0
    section_count = 0
    bmc_section_count = 0
    current_section_index = -1
    saw_header = False

    def flush_section() -> None:
        nonlocal raw_section_rows
        if not raw_section_rows:
            return
        temperature_median = statistics.median(
            max(item["values"]["Cpu1_Temp"], item["values"]["Cpu2_Temp"])
            for item in raw_section_rows
        )
        power_median = statistics.median(
            item["values"]["PSU1_Total_Power"] + item["values"]["PSU2_Total_Power"]
            for item in raw_section_rows
        )
        temperature_raw = temperature_median >= 1000.0
        power_raw = power_median >= 100000.0
        temperature_scale = 0.001 if temperature_raw else 1.0
        power_scale = 0.000001 if power_raw else 1.0
        concordant = temperature_raw == power_raw
        unit_sections.append({
            "section_index": current_section_index,
            "accepted_rows": len(raw_section_rows),
            "temperature_raw_median": temperature_median,
            "summed_power_raw_median": power_median,
            "temperature_scale": temperature_scale,
            "power_scale": power_scale,
            "concordant": concordant,
            "regime": "raw_hwmon" if temperature_raw and power_raw else (
                "normalized" if not temperature_raw and not power_raw else "discordant"
            ),
        })
        for item in raw_section_rows:
            record = item["record"]
            values = item["values"]
            inlet = values["Inlet_Temp"] * temperature_scale
            outlet = values["Outlet_Temp"] * temperature_scale
            cpu1 = values["Cpu1_Temp"] * temperature_scale
            cpu2 = values["Cpu2_Temp"] * temperature_scale
            fan_mean = sum(values[f"FAN{i}"] for i in range(1, 5)) / 4.0
            power_w = (
                values["PSU1_Total_Power"] + values["PSU2_Total_Power"]
            ) * power_scale
            fan_krpm = fan_mean / 1000.0
            rows.append({
                "time": record["_time"],
                "measurement": record["_measurement"],
                "device_id": record["device_id"],
                "section_index": current_section_index,
                "temperature_scale": temperature_scale,
                "power_scale": power_scale,
                "unit_concordant": concordant,
                "inlet": inlet,
                "outlet": outlet,
                "cpu1": cpu1,
                "cpu2": cpu2,
                "fan_krpm": fan_krpm,
                "power_100w": power_w / 100.0,
                "thermal_rise": outlet - inlet,
                "power_per_fan": (power_w / 100.0) / max(fan_krpm, 0.1),
                "target": max(cpu1, cpu2),
            })
        raw_section_rows = []

    with path.open("r", encoding="utf-8", newline="") as handle:
        for raw in handle:
            if raw.startswith("#group"):
                flush_section()
                header = None
                section_is_bmc_capable = False
                section_count += 1
                current_section_index = section_count - 1
                continue
            if raw.startswith("#") or not raw.strip():
                continue
            parsed = next(csv.reader([raw]))
            if header is None:
                header = parsed
                saw_header = True
                missing = [name for name in REQUIRED_COLUMNS if name not in header]
                section_is_bmc_capable = not missing
                if section_is_bmc_capable:
                    bmc_section_count += 1
                continue
            total += 1
            if not section_is_bmc_capable:
                rejected_non_bmc += 1
                continue
            if len(parsed) != len(header):
                invalid += 1
                continue
            record = dict(zip(header, parsed))
            if record.get("_measurement") != "sdgp" or record.get("device_id") != "bmc":
                rejected_non_bmc += 1
                continue
            try:
                values = {name: float(record[name]) for name in NUMERIC_COLUMNS}
            except (KeyError, TypeError, ValueError):
                invalid += 1
                continue
            if not all(math.isfinite(value) for value in values.values()):
                invalid += 1
                continue
            raw_section_rows.append({"record": record, "values": values})
    flush_section()
    if not saw_header:
        raise ValueError(f"{path.name} has no CSV header")
    return {
        "rows": rows,
        "total_data_rows": total,
        "invalid_rows": invalid,
        "rejected_non_bmc_rows": rejected_non_bmc,
        "section_count": section_count,
        "bmc_section_count": bmc_section_count,
        "unit_sections": unit_sections,
    }


def percentile95(values: Iterable[float]) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("cannot calculate percentile of no values")
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]


def metrics(actual: list[float], predicted: list[float]) -> dict:
    if len(actual) != len(predicted) or not actual:
        raise ValueError("metrics require equal non-empty vectors")
    errors = [abs(a - p) for a, p in zip(actual, predicted)]
    return {
        "count": len(errors),
        "mae_c": statistics.fmean(errors),
        "rmse_c": math.sqrt(statistics.fmean(error * error for error in errors)),
        "p95_c": percentile95(errors),
    }


def fit_offset(rows: list[dict], source: str) -> dict:
    return {
        "kind": "offset",
        "source": source,
        "offset_c": statistics.median(row["target"] - row[source] for row in rows),
    }


def solve_linear(matrix: list[list[float]], vector: list[float]) -> list[float]:
    size = len(vector)
    augmented = [matrix[i][:] + [vector[i]] for i in range(size)]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) < 1e-12:
            raise ValueError("singular ridge system")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        augmented[column] = [value / scale for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [
                current - factor * pivot_value
                for current, pivot_value in zip(augmented[row], augmented[column])
            ]
    return [augmented[row][-1] for row in range(size)]


def fit_ridge(rows: list[dict], feature_set: str, ridge_lambda: float) -> dict:
    names = FEATURE_SETS[feature_set]
    means = [statistics.fmean(row[name] for row in rows) for name in names]
    scales = []
    for name, mean in zip(names, means):
        variance = statistics.fmean((row[name] - mean) ** 2 for row in rows)
        scales.append(max(math.sqrt(variance), 1e-9))
    width = len(names) + 1
    matrix = [[0.0] * width for _ in range(width)]
    vector = [0.0] * width
    for row in rows:
        features = [1.0] + [
            (row[name] - mean) / scale
            for name, mean, scale in zip(names, means, scales)
        ]
        for i in range(width):
            vector[i] += features[i] * row["target"]
            for j in range(width):
                matrix[i][j] += features[i] * features[j]
    for index in range(1, width):
        matrix[index][index] += ridge_lambda
    return {
        "kind": "ridge",
        "feature_set": feature_set,
        "feature_names": list(names),
        "ridge_lambda": ridge_lambda,
        "means": means,
        "scales": scales,
        "coefficients": solve_linear(matrix, vector),
    }


def predict(model: dict, row: dict) -> float:
    if model["kind"] == "offset":
        return row[model["source"]] + model["offset_c"]
    features = [1.0] + [
        (row[name] - mean) / scale
        for name, mean, scale in zip(
            model["feature_names"], model["means"], model["scales"]
        )
    ]
    return sum(coefficient * value for coefficient, value in zip(
        model["coefficients"], features
    ))


def evaluate_rows(model: dict, rows: list[dict]) -> dict:
    return metrics(
        [row["target"] for row in rows],
        [predict(model, row) for row in rows],
    )


def evaluate_runs(model: dict, runs: dict[str, list[dict]]) -> dict:
    per_run = {}
    actual = []
    predicted = []
    for name, rows in runs.items():
        result = evaluate_rows(model, rows)
        per_run[name] = result
        actual.extend(row["target"] for row in rows)
        predicted.extend(predict(model, row) for row in rows)
    pooled = metrics(actual, predicted)
    return {
        "pooled": pooled,
        "macro_run_mae_c": statistics.fmean(item["mae_c"] for item in per_run.values()),
        "per_run": per_run,
    }


def bootstrap_mean_ci(values: list[float], samples: int = 10000, seed: int = 20260824) -> list[float]:
    generator = random.Random(seed)
    means = []
    for _ in range(samples):
        means.append(statistics.fmean(generator.choice(values) for _ in values))
    means.sort()
    return [means[int(0.025 * samples)], means[int(0.975 * samples) - 1]]


def select_and_refit(
    train_runs: dict[str, list[dict]],
    selection_runs: dict[str, list[dict]],
) -> dict:
    """Select and refit models without accepting any final-test argument."""
    train_rows = [row for rows in train_runs.values() for row in rows]
    selection_rows = [
        row for rows in selection_runs.values() for row in rows
    ]
    baseline_candidates = []
    for source in ("inlet", "outlet"):
        model = fit_offset(train_rows, source)
        baseline_candidates.append({
            "source": source,
            "validation": evaluate_rows(model, selection_rows),
        })
    baseline_choice = min(
        baseline_candidates, key=lambda item: (item["validation"]["mae_c"], item["source"])
    )
    model_candidates = []
    for feature_set in FEATURE_SETS:
        for ridge_lambda in LAMBDAS:
            model = fit_ridge(train_rows, feature_set, ridge_lambda)
            model_candidates.append({
                "feature_set": feature_set,
                "ridge_lambda": ridge_lambda,
                "feature_count": len(FEATURE_SETS[feature_set]),
                "validation": evaluate_rows(model, selection_rows),
            })
    model_choice = min(model_candidates, key=lambda item: (
        item["validation"]["mae_c"], item["feature_count"], item["ridge_lambda"]
    ))
    refit_rows = train_rows + selection_rows
    baseline = fit_offset(refit_rows, baseline_choice["source"])
    model = fit_ridge(
        refit_rows, model_choice["feature_set"], model_choice["ridge_lambda"]
    )
    return {
        "selection": {
            "baseline_candidates": baseline_candidates,
            "selected_baseline_source": baseline_choice["source"],
            "model_candidates": model_candidates,
            "selected_feature_set": model_choice["feature_set"],
            "selected_ridge_lambda": model_choice["ridge_lambda"],
        },
        "frozen_models": {"baseline": baseline, "ridge": model},
        "development_file_counts": {
            "train": len(train_runs),
            "selection": len(selection_runs),
        },
    }


def evaluate_frozen(frozen_models: dict, test_runs: dict[str, list[dict]]) -> dict:
    """Evaluate already-frozen models on final-test runs."""
    baseline_test = evaluate_runs(frozen_models["baseline"], test_runs)
    model_test = evaluate_runs(frozen_models["ridge"], test_runs)
    run_improvements = [
        baseline_test["per_run"][name]["mae_c"] - model_test["per_run"][name]["mae_c"]
        for name in test_runs
    ]
    wins = sum(value > 0 for value in run_improvements)
    pooled_gains = {
        metric: baseline_test["pooled"][metric] - model_test["pooled"][metric]
        for metric in ("mae_c", "rmse_c", "p95_c")
    }
    macro_gain = baseline_test["macro_run_mae_c"] - model_test["macro_run_mae_c"]
    confidence_interval = bootstrap_mean_ci(run_improvements)
    gates = {
        "all_14_test_runs_evaluable": len(test_runs) == 14,
        "pooled_mae_gain_ge_0_20_c": pooled_gains["mae_c"] >= 0.20,
        "pooled_rmse_gain_ge_0_20_c": pooled_gains["rmse_c"] >= 0.20,
        "pooled_p95_gain_ge_0_20_c": pooled_gains["p95_c"] >= 0.20,
        "macro_run_mae_gain_ge_0_20_c": macro_gain >= 0.20,
        "bootstrap_ci_lower_gt_zero": confidence_interval[0] > 0.0,
        "run_wins_ge_9_of_14": wins >= 9,
    }
    return {
        "test": {
            "baseline": baseline_test,
            "model": model_test,
            "pooled_gains_c": pooled_gains,
            "macro_run_mae_gain_c": macro_gain,
            "run_mae_improvements_c": run_improvements,
            "model_run_wins": wins,
            "run_bootstrap_95_ci_c": confidence_interval,
        },
        "gates": gates,
        "decision": (
            "h_enc_06_supported_within_server"
            if all(gates.values()) else "h_enc_06_not_supported"
        ),
    }


def run_experiment(runs_by_split: dict[str, dict[str, list[dict]]]) -> dict:
    """Convenience composition; production runner uses the two phases explicitly."""
    development = select_and_refit(
        runs_by_split["train"], runs_by_split["selection"]
    )
    final = evaluate_frozen(development["frozen_models"], runs_by_split["test"])
    return {**development, **final}
