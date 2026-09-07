#!/usr/bin/env python3
"""Run the preregistered E15 frozen-model BMC confirmation exactly once."""

from __future__ import annotations

import hashlib
import json
import math
import random
import sys
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from digital_twin.enclosure.bmc_virtual_sensor import parse_influx_bmc


RAW_DIR = ROOT / "outputs/data/enclosure/bmc_confirmation_e15/raw"
MANIFEST_PATH = ROOT / "outputs/data/enclosure/bmc_confirmation_e15_manifest.json"
MODEL_PATH = ROOT / "outputs/data/enclosure/bmc_corrected_e14c_frozen_model.json"
RESULT_PATH = ROOT / "outputs/data/enclosure/bmc_confirmation_e15_result.json"
EXPECTED_MODEL_SHA256 = "609048167f2a7e261bee45e2d935c650be7a55184cdce3966b014e6cd1e5ba84"
EXPECTED_FILENAMES = (
    "202308022155.csv", "202308022222.csv", "202308051737.csv",
    "202308051757.csv", "202308051827.csv", "202308052003.csv",
    "202309212229.csv", "202309221110.csv", "202309222035.csv",
    "202310252044.csv", "202310252102.csv", "202310252230.csv",
    "202405241724.csv", "202405241940.csv",
)
MIN_ROWS = 10
MIN_GAIN_C = 0.2
MIN_RUN_WINS = 9
BOOTSTRAP_REPLICATES = 20_000
BOOTSTRAP_SEED = 20_260_824


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def percentile(values: Iterable[float], probability: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("Cannot calculate a percentile of an empty sequence")
    position = probability * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def metrics(actual: list[float], predicted: list[float]) -> dict[str, float | int]:
    if len(actual) != len(predicted) or not actual:
        raise ValueError("Metrics require equal non-empty sequences")
    errors = [abs(a - p) for a, p in zip(actual, predicted)]
    squared = [(a - p) ** 2 for a, p in zip(actual, predicted)]
    return {
        "count": len(actual),
        "mae_c": sum(errors) / len(errors),
        "rmse_c": math.sqrt(sum(squared) / len(squared)),
        "p95_c": percentile(errors, 0.95),
    }


def predict_baseline(row: dict[str, float], model: dict) -> float:
    return float(row[model["source"]]) + float(model["offset_c"])


def predict_ridge(row: dict[str, float], model: dict) -> float:
    coefficients = model["coefficients"]
    prediction = float(coefficients[0])
    for name, mean, scale, coefficient in zip(
        model["feature_names"],
        model["means"],
        model["scales"],
        coefficients[1:],
    ):
        prediction += float(coefficient) * (
            (float(row[name]) - float(mean)) / float(scale)
        )
    return prediction


def bootstrap_macro_gain(gains: list[float]) -> dict[str, float | int]:
    randomizer = random.Random(BOOTSTRAP_SEED)
    samples = []
    for _ in range(BOOTSTRAP_REPLICATES):
        draw = [gains[randomizer.randrange(len(gains))] for _ in gains]
        samples.append(sum(draw) / len(draw))
    return {
        "seed": BOOTSTRAP_SEED,
        "replicates": BOOTSTRAP_REPLICATES,
        "lower_95_c": percentile(samples, 0.025),
        "upper_95_c": percentile(samples, 0.975),
    }


def main() -> None:
    if RESULT_PATH.exists():
        raise SystemExit(f"Refusing to overwrite existing E15 result: {RESULT_PATH}")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    frozen = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
    model_sha = sha256(MODEL_PATH)
    if model_sha != EXPECTED_MODEL_SHA256:
        raise SystemExit(f"Frozen model hash mismatch: {model_sha}")

    records = manifest.get("files", [])
    names = tuple(record.get("filename") for record in records)
    if names != EXPECTED_FILENAMES:
        raise SystemExit("Manifest filename set or order differs from preregistration")
    for record in records:
        path = RAW_DIR / record["filename"]
        if not path.exists() or sha256(path) != record["sha256"]:
            raise SystemExit(f"Downloaded file hash mismatch: {record['filename']}")

    baseline_model = frozen["frozen_models"]["baseline"]
    ridge_model = frozen["frozen_models"]["ridge"]
    all_actual: list[float] = []
    all_baseline: list[float] = []
    all_ridge: list[float] = []
    per_run = []
    parse_report = []

    for filename in EXPECTED_FILENAMES:
        parsed = parse_influx_bmc(RAW_DIR / filename)
        rows = parsed["rows"]
        unit_sections = parsed["unit_sections"]
        unit_ok = all(section["concordant"] for section in unit_sections) and all(
            row["unit_concordant"] for row in rows
        )
        actual = [float(row["target"]) for row in rows]
        baseline = [predict_baseline(row, baseline_model) for row in rows]
        ridge = [predict_ridge(row, ridge_model) for row in rows]
        finite = all(math.isfinite(value) for value in baseline + ridge)
        baseline_metrics = metrics(actual, baseline) if actual else None
        ridge_metrics = metrics(actual, ridge) if actual else None
        gain = (
            baseline_metrics["mae_c"] - ridge_metrics["mae_c"]
            if baseline_metrics and ridge_metrics
            else None
        )
        per_run.append(
            {
                "filename": filename,
                "row_count": len(rows),
                "unit_concordant": unit_ok,
                "predictions_finite": finite,
                "baseline": baseline_metrics,
                "ridge": ridge_metrics,
                "mae_gain_c": gain,
                "ridge_win": gain is not None and gain > 0.0,
            }
        )
        parse_report.append(
            {
                "filename": filename,
                "accepted_rows": len(rows),
                "total_data_rows": parsed["total_data_rows"],
                "invalid_rows": parsed["invalid_rows"],
                "rejected_non_bmc_rows": parsed["rejected_non_bmc_rows"],
                "section_count": parsed["section_count"],
                "bmc_section_count": parsed["bmc_section_count"],
                "unit_sections": unit_sections,
            }
        )
        all_actual.extend(actual)
        all_baseline.extend(baseline)
        all_ridge.extend(ridge)

    baseline_metrics = metrics(all_actual, all_baseline)
    ridge_metrics = metrics(all_actual, all_ridge)
    gains = [float(run["mae_gain_c"]) for run in per_run if run["mae_gain_c"] is not None]
    macro_gain = sum(gains) / len(gains)
    interval = bootstrap_macro_gain(gains)
    prediction_values = all_baseline + all_ridge
    prediction_extrema = {
        "minimum_c": min(prediction_values),
        "maximum_c": max(prediction_values),
    }
    gates = {
        "all_14_files_evaluable": len(per_run) == 14 and all(
            run["row_count"] >= MIN_ROWS for run in per_run
        ),
        "all_unit_regimes_concordant": all(run["unit_concordant"] for run in per_run),
        "all_predictions_finite": all(run["predictions_finite"] for run in per_run),
        "predictions_within_minus50_to_200_c": (
            prediction_extrema["minimum_c"] >= -50.0
            and prediction_extrema["maximum_c"] <= 200.0
        ),
        "aggregate_mae_gain_ge_0_2_c": (
            baseline_metrics["mae_c"] - ridge_metrics["mae_c"] >= MIN_GAIN_C
        ),
        "aggregate_rmse_gain_ge_0_2_c": (
            baseline_metrics["rmse_c"] - ridge_metrics["rmse_c"] >= MIN_GAIN_C
        ),
        "aggregate_p95_gain_ge_0_2_c": (
            baseline_metrics["p95_c"] - ridge_metrics["p95_c"] >= MIN_GAIN_C
        ),
        "macro_mae_gain_ge_0_2_c": macro_gain >= MIN_GAIN_C,
        "bootstrap_lower_bound_gt_0_c": interval["lower_95_c"] > 0.0,
        "ridge_wins_at_least_9_of_14_runs": sum(run["ridge_win"] for run in per_run)
        >= MIN_RUN_WINS,
    }
    supported = all(gates.values())
    result = {
        "study_id": "E15",
        "status": "completed",
        "hypothesis_decision": "h_enc_08_supported" if supported else "h_enc_08_not_supported",
        "manifest_sha256": sha256(MANIFEST_PATH),
        "frozen_model_sha256": model_sha,
        "confirmation_previously_unopened": True,
        "file_count": len(per_run),
        "row_count": len(all_actual),
        "aggregate": {
            "baseline": baseline_metrics,
            "ridge": ridge_metrics,
            "mae_gain_c": baseline_metrics["mae_c"] - ridge_metrics["mae_c"],
            "rmse_gain_c": baseline_metrics["rmse_c"] - ridge_metrics["rmse_c"],
            "p95_gain_c": baseline_metrics["p95_c"] - ridge_metrics["p95_c"],
        },
        "macro_run_mae_gain_c": macro_gain,
        "run_block_bootstrap": interval,
        "ridge_run_wins": sum(run["ridge_win"] for run in per_run),
        "prediction_extrema": prediction_extrema,
        "gates": gates,
        "per_run": per_run,
        "parse_report": parse_report,
        "claim_boundary": (
            "Same-server temporal/workload confirmation only; not cross-server, "
            "desktop-enclosure, NTC, spatial-field, or deployment evidence."
        ),
    }
    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(
        json.dumps(result, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "decision": result["hypothesis_decision"],
        "rows": result["row_count"],
        "baseline": baseline_metrics,
        "ridge": ridge_metrics,
        "macro_mae_gain_c": macro_gain,
        "bootstrap": interval,
        "ridge_run_wins": result["ridge_run_wins"],
        "gates": gates,
    }, indent=2))


if __name__ == "__main__":
    main()
