from __future__ import annotations

import hashlib
import json
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from digital_twin.core.public_dataset_benchmark import (
    _build_sml2010_response_samples,
    _fit_linear_regression,
    _load_sml2010_records,
    _predict_linear_regression,
    _read_csv_rows,
)
from digital_twin.core.public_dataset_model_comparison import (
    DEFAULT_CHECKPOINT_PATH,
    MappedHybridPublicPredictor,
    _fit_regularized_linear_readout,
)
from digital_twin.evaluation.published_hybrid_comparison import (
    _metric_summary,
    _predict_coefficients,
    _standardize_split,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_DIR = ROOT / "outputs" / "data" / "normalized_public" / "sml2010"
DEFAULT_OUTPUT_PATH = (
    ROOT / "outputs" / "data" / "public_benchmarks" / "next_day_temperature_improvement.json"
)
HORIZON_MINUTES = 1440
TARGETS = ("dining_temperature", "room_temperature")
TRAIN_FRACTION = 0.60
DEVELOPMENT_FRACTION = 0.70
RIDGE_GRID = (1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0)
WEIGHT_GRID = (0.0, 0.25, 0.5, 0.75, 1.0)
BOOTSTRAP_REPLICATES = 10_000
BOOTSTRAP_SEED = 20_260_726
FEATURE_NAMES = (
    "current_target_temperature",
    "current_other_temperature",
    "lag_24h_target_temperature",
    "lag_24h_other_temperature",
    "lag_7d_target_temperature",
    "lag_7d_other_temperature",
    "daily_trend_target",
    "daily_trend_other",
    "weekly_difference_target",
    "dining_humidity_origin",
    "room_humidity_origin",
    "outdoor_temperature_origin",
    "outdoor_humidity_origin",
    "weather_forecast_temperature_origin",
    "forecast_minus_outdoor_temperature",
    "log1p_sunlight_origin",
    "rain_ratio_origin",
    "wind_speed_origin",
    "enthalpic_motor_1_origin",
    "enthalpic_motor_2_origin",
    "enthalpic_motor_turbo_origin",
    "hour_sin",
    "hour_cos",
    "day_of_week_sin",
    "day_of_week_cos",
    "lag_24h_available",
    "lag_7d_available",
    "origin_derived_physics_prediction",
    "physics_minus_current_target",
)
CANDIDATE_ORDER = (
    "seasonal_persistence",
    "bias_corrected_persistence",
    "damped_daily_trend",
    "persistence_physics_blend",
    "seasonal_residual_ridge",
)
ADAPTIVE_CANDIDATE_ORDER = (
    "seasonal_persistence",
    "same_slot_mean_3d",
    "same_slot_mean_7d",
    "same_slot_mean_14d",
    "same_slot_median_3d",
    "same_slot_median_7d",
    "same_slot_median_14d",
    "same_slot_ewma_0.25",
    "same_slot_ewma_0.50",
    "same_slot_ewma_0.75",
)


def run_next_day_temperature_comparison(
    input_dir: Path = DEFAULT_INPUT_DIR,
    checkpoint_path: Optional[Path] = None,
    bootstrap_replicates: int = BOOTSTRAP_REPLICATES,
    bootstrap_seed: int = BOOTSTRAP_SEED,
) -> Dict[str, object]:
    input_dir = Path(input_dir)
    required_inputs = (
        input_dir / "corner_sensor_timeseries.csv",
        input_dir / "outdoor_environment.csv",
        input_dir / "auxiliary_features.csv",
    )
    missing_inputs = [str(path) for path in required_inputs if not path.exists()]
    if missing_inputs:
        raise FileNotFoundError(f"Missing normalized SML2010 inputs: {', '.join(missing_inputs)}")
    if bootstrap_replicates <= 0:
        raise ValueError("bootstrap_replicates must be positive")

    records = _load_sml2010_records(
        _read_csv_rows(required_inputs[0]),
        _read_csv_rows(required_inputs[1]),
        _read_csv_rows(required_inputs[2]),
    )
    samples = _build_sml2010_response_samples(records, HORIZON_MINUTES, task_id="S2")
    if len(samples) < 20:
        return _not_evaluated_result(
            input_dir=input_dir,
            required_inputs=required_inputs,
            sample_count=len(samples),
            reason="at least 20 exact next-day samples are required",
        )

    train_end = int(len(samples) * TRAIN_FRACTION)
    development_end = int(len(samples) * DEVELOPMENT_FRACTION)
    if not (1 <= train_end < development_end < len(samples)):
        raise ValueError("Invalid chronological split for next-day samples")

    selected_checkpoint = Path(checkpoint_path) if checkpoint_path is not None else DEFAULT_CHECKPOINT_PATH
    predictor = MappedHybridPublicPredictor(checkpoint_path=selected_checkpoint)
    mapped_features = [
        predictor.build_features("sml2010", "S2", sample, HORIZON_MINUTES)
        for sample in samples
    ]
    physics_by_target = {
        "dining_temperature": [float(row[0]) for row in mapped_features],
        "room_temperature": [float(row[1]) for row in mapped_features],
    }
    record_lookup = {record["timestamp_dt"]: record for record in records}

    cases: List[Dict[str, object]] = []
    final_lag_audits: List[Dict[str, object]] = []
    for target_index, target in enumerate(TARGETS):
        feature_rows, components, lag_audit = _build_next_day_feature_rows(
            samples=samples,
            record_lookup=record_lookup,
            physics_predictions=physics_by_target[target],
            target=target,
        )
        lag_audit["test_missing_lag_24h"] = sum(
            1
            for index in range(development_end, len(samples))
            if not components["lag_24h_available"][index]
        )
        lag_audit["test_missing_lag_7d"] = sum(
            1
            for index in range(development_end, len(samples))
            if not components["lag_7d_available"][index]
        )

        actual = [float(sample["targets"][target]) for sample in samples]
        validation_records = _evaluate_validation_candidates(
            actual=actual,
            current=components["current"],
            lag_24h=components["lag_24h"],
            physics=physics_by_target[target],
            feature_rows=feature_rows,
            train_end=train_end,
            development_end=development_end,
        )
        best_by_candidate = _best_validation_record_by_candidate(validation_records)
        selected_validation = min(
            best_by_candidate.values(),
            key=lambda record: _selection_key(record),
        )

        final_candidate_metrics: Dict[str, Dict[str, object]] = {}
        final_candidate_predictions: Dict[str, List[float]] = {}
        for candidate in CANDIDATE_ORDER:
            selected_parameter = best_by_candidate[candidate]["parameter"]
            predictions = _fit_and_predict_candidate(
                candidate=candidate,
                parameter=selected_parameter,
                actual=actual,
                current=components["current"],
                lag_24h=components["lag_24h"],
                physics=physics_by_target[target],
                feature_rows=feature_rows,
                fit_start=0,
                fit_end=development_end,
                predict_start=development_end,
                predict_end=len(samples),
            )
            final_candidate_predictions[candidate] = predictions
            final_candidate_metrics[candidate] = {
                "selected_parameter": selected_parameter,
                "validation_mae": best_by_candidate[candidate]["metrics"]["mae"],
                "test_metrics": _metric_summary(actual[development_end:], predictions),
            }

        comparison_predictions, comparison_metrics = _comparison_baselines(
            target=target,
            target_index=target_index,
            actual=actual,
            samples=samples,
            mapped_features=mapped_features,
            physics_predictions=physics_by_target[target],
            development_end=development_end,
        )
        del comparison_predictions

        selected_candidate = str(selected_validation["candidate"])
        selected_predictions = final_candidate_predictions[selected_candidate]
        persistence_predictions = final_candidate_predictions["seasonal_persistence"]
        test_actual = actual[development_end:]
        test_dates = [
            sample["context"]["future"]["timestamp_dt"].date().isoformat()
            for sample in samples[development_end:]
        ]
        bootstrap = _paired_daily_block_bootstrap(
            actual=test_actual,
            persistence=persistence_predictions,
            selected=selected_predictions,
            dates=test_dates,
            replicates=bootstrap_replicates,
            seed=bootstrap_seed,
        )
        persistence_mae = float(
            final_candidate_metrics["seasonal_persistence"]["test_metrics"]["mae"]
        )
        selected_mae = float(final_candidate_metrics[selected_candidate]["test_metrics"]["mae"])
        relative_improvement_pct = (
            ((persistence_mae - selected_mae) / persistence_mae) * 100.0
            if persistence_mae > 1e-12
            else 0.0
        )

        final_lag_audits.append(lag_audit)
        cases.append(
            {
                "task_id": "S2",
                "target": target,
                "horizon_minutes": HORIZON_MINUTES,
                "status": "ok",
                "sample_count": len(samples),
                "train_samples": train_end,
                "validation_samples": development_end - train_end,
                "development_samples": development_end,
                "test_samples": len(samples) - development_end,
                "train_start": str(samples[0]["context"]["origin"]["timestamp_dt"]),
                "train_end": str(samples[train_end - 1]["context"]["origin"]["timestamp_dt"]),
                "validation_start": str(samples[train_end]["context"]["origin"]["timestamp_dt"]),
                "validation_end": str(
                    samples[development_end - 1]["context"]["origin"]["timestamp_dt"]
                ),
                "test_start": str(samples[development_end]["context"]["origin"]["timestamp_dt"]),
                "test_end": str(samples[-1]["context"]["origin"]["timestamp_dt"]),
                "feature_names": list(FEATURE_NAMES),
                "lag_audit": lag_audit,
                "validation_candidates": validation_records,
                "best_validation_record_by_candidate": best_by_candidate,
                "selected_candidate": selected_candidate,
                "selected_parameter": selected_validation["parameter"],
                "final_test_candidate_metrics": final_candidate_metrics,
                "same_row_comparison_metrics": comparison_metrics,
                "selected_vs_persistence": {
                    "mae_reduction_c": round(persistence_mae - selected_mae, 6),
                    "relative_mae_reduction_pct": round(relative_improvement_pct, 6),
                },
                "bootstrap": bootstrap,
            }
        )

    relative_improvements = [
        float(case["selected_vs_persistence"]["relative_mae_reduction_pct"])
        for case in cases
    ]
    beats_persistence_both = all(
        float(case["selected_vs_persistence"]["mae_reduction_c"]) > 0.0
        for case in cases
    )
    mean_relative_improvement = sum(relative_improvements) / float(len(relative_improvements))
    h_nd_supported = beats_persistence_both and mean_relative_improvement >= 5.0
    h_rob_supported = all(
        float(case["bootstrap"]["mae_reduction_ci95_c"][0]) > 0.0
        for case in cases
    )
    leakage_audit = {
        "selection_partition": "validation_only",
        "test_used_for_selection": False,
        "target_time_measurements_in_features": False,
        "target_time_actual_weather_in_features": False,
        "historical_fallback_uses_only_origin_or_past": True,
        "historical_availability_flags_in_features": (
            "lag_24h_available" in FEATURE_NAMES
            and "lag_7d_available" in FEATURE_NAMES
        ),
        "identical_final_test_rows": len({case["test_start"] for case in cases}) == 1
        and len({case["test_end"] for case in cases}) == 1
        and len({case["test_samples"] for case in cases}) == 1,
    }
    audit_supported = all(bool(value) for key, value in leakage_audit.items() if key != "selection_partition")
    claim_decision = (
        "supported"
        if h_nd_supported and audit_supported
        else "not_supported"
    )
    robustness_note = (
        "robust_daily_block_interval"
        if h_rob_supported
        else "daily_block_interval_includes_zero_for_at_least_one_target"
    )
    adaptive_cases = [
        _evaluate_adaptive_online_followup(
            samples=samples,
            record_lookup=record_lookup,
            target=target,
            train_end=train_end,
            development_end=development_end,
            bootstrap_replicates=bootstrap_replicates,
            bootstrap_seed=bootstrap_seed + 100 + target_index,
        )
        for target_index, target in enumerate(TARGETS)
    ]
    adaptive_relative_improvements = [
        float(case["selected_vs_persistence"]["relative_mae_reduction_pct"])
        for case in adaptive_cases
    ]
    adaptive_beats_both = all(
        float(case["selected_vs_persistence"]["mae_reduction_c"]) > 0.0
        for case in adaptive_cases
    )
    adaptive_mean_relative_improvement = (
        sum(adaptive_relative_improvements) / float(len(adaptive_relative_improvements))
    )
    adaptive_signal = adaptive_beats_both and adaptive_mean_relative_improvement >= 2.0

    return {
        "study_id": "E9-NEXTDAY-SEASONAL-DELTA",
        "dataset": "SML2010",
        "benchmark_mode": "two-point next-day temperature improvement",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "COMPLETE",
        "input_dir": str(input_dir),
        "input_provenance": {
            str(path.relative_to(input_dir)): {
                "sha256": _sha256(path),
                "bytes": path.stat().st_size,
            }
            for path in required_inputs
        },
        "checkpoint": {
            "path": str(selected_checkpoint),
            "available": selected_checkpoint.exists(),
            "sha256": _sha256(selected_checkpoint) if selected_checkpoint.exists() else "",
        },
        "protocol": {
            "version": "2.0",
            "horizon_minutes": HORIZON_MINUTES,
            "targets": list(TARGETS),
            "chronological_split": "60_train_10_validation_30_test_then_refit_first_70",
            "ridge_grid": list(RIDGE_GRID),
            "weight_grid": list(WEIGHT_GRID),
            "bootstrap_replicates": bootstrap_replicates,
            "bootstrap_seed": bootstrap_seed,
            "bootstrap_unit": "target_calendar_date",
            "hypothesis_rule": (
                "H-ND-01 requires lower final-test MAE than seasonal persistence for both targets "
                "and at least 5% mean relative MAE reduction."
            ),
        },
        "registered_candidates": list(CANDIDATE_ORDER),
        "feature_contract": {
            "allowed": list(FEATURE_NAMES),
            "forecast_temperature_semantics": "origin-time weather forecast feature from SML2010",
            "prohibited": [
                "target-time measured indoor state",
                "target-time actual outdoor weather",
                "target-time sunlight",
                "target-time device state",
                "final-test metrics for selection",
            ],
        },
        "leakage_audit": leakage_audit,
        "cases": cases,
        "summary": {
            "selected_candidates": {
                str(case["target"]): str(case["selected_candidate"])
                for case in cases
            },
            "beats_persistence_both_targets": beats_persistence_both,
            "mean_relative_mae_reduction_pct": round(mean_relative_improvement, 6),
            "bootstrap_positive_both_targets": h_rob_supported,
            "robustness_note": robustness_note,
        },
        "decisions": {
            "H-ND-01": "supported" if h_nd_supported else "not_supported",
            "H-ND-ROB-01": "supported" if h_rob_supported else "not_supported",
            "CLM-ND-01": claim_decision,
        },
        "adaptive_online_followup": {
            "evidence_level": "POST_PRIMARY_EXPLORATORY",
            "registered_after_primary_result": True,
            "supports_confirmatory_claim": False,
            "registered_candidates": list(ADAPTIVE_CANDIDATE_ORDER),
            "selection_partition": "validation_only",
            "test_mode": (
                "sequential online update; each origin may use only same-slot daily deltas "
                "completed at or before that origin"
            ),
            "cases": adaptive_cases,
            "summary": {
                "selected_candidates": {
                    str(case["target"]): str(case["selected_candidate"])
                    for case in adaptive_cases
                },
                "beats_persistence_both_targets": adaptive_beats_both,
                "mean_relative_mae_reduction_pct": round(
                    adaptive_mean_relative_improvement,
                    6,
                ),
            },
            "decision": (
                "exploratory_signal"
                if adaptive_signal
                else "not_supported"
            ),
            "decision_rule": (
                "exploratory signal requires lower MAE than persistence for both targets "
                "and at least 2% mean relative MAE reduction"
            ),
        },
        "claim_boundary": (
            "Any supported improvement is limited to the registered SML2010 two-point next-day "
            "split. It is not cross-building evidence, full 3-D field validation, or reproduction "
            "of Oh et al.'s confidential BEMS/CNN-LSTM result."
        ),
    }


def _evaluate_adaptive_online_followup(
    samples: Sequence[Dict[str, object]],
    record_lookup: Dict[datetime, Dict[str, float]],
    target: str,
    train_end: int,
    development_end: int,
    bootstrap_replicates: int,
    bootstrap_seed: int,
) -> Dict[str, object]:
    actual = [float(sample["targets"][target]) for sample in samples]
    predictions_by_candidate, history_counts = _adaptive_online_predictions(
        samples=samples,
        record_lookup=record_lookup,
        target=target,
    )
    validation_metrics = {
        candidate: _metric_summary(
            actual[train_end:development_end],
            predictions[train_end:development_end],
        )
        for candidate, predictions in predictions_by_candidate.items()
    }
    selected_candidate = min(
        ADAPTIVE_CANDIDATE_ORDER,
        key=lambda candidate: (
            float(validation_metrics[candidate]["mae"]),
            ADAPTIVE_CANDIDATE_ORDER.index(candidate),
        ),
    )
    test_actual = actual[development_end:]
    test_metrics = {
        candidate: _metric_summary(
            test_actual,
            predictions[development_end:],
        )
        for candidate, predictions in predictions_by_candidate.items()
    }
    selected_predictions = predictions_by_candidate[selected_candidate][development_end:]
    persistence_predictions = predictions_by_candidate["seasonal_persistence"][development_end:]
    persistence_mae = float(test_metrics["seasonal_persistence"]["mae"])
    selected_mae = float(test_metrics[selected_candidate]["mae"])
    relative_improvement = (
        ((persistence_mae - selected_mae) / persistence_mae) * 100.0
        if persistence_mae > 1e-12
        else 0.0
    )
    test_dates = [
        sample["context"]["future"]["timestamp_dt"].date().isoformat()
        for sample in samples[development_end:]
    ]
    return {
        "target": target,
        "horizon_minutes": HORIZON_MINUTES,
        "selected_candidate": selected_candidate,
        "validation_metrics": validation_metrics,
        "test_metrics": test_metrics,
        "selected_vs_persistence": {
            "mae_reduction_c": round(persistence_mae - selected_mae, 6),
            "relative_mae_reduction_pct": round(relative_improvement, 6),
        },
        "bootstrap": _paired_daily_block_bootstrap(
            actual=test_actual,
            persistence=persistence_predictions,
            selected=selected_predictions,
            dates=test_dates,
            replicates=bootstrap_replicates,
            seed=bootstrap_seed,
        ),
        "history_audit": {
            "minimum_available_same_slot_deltas": min(history_counts),
            "maximum_available_same_slot_deltas": max(history_counts),
            "test_minimum_available_same_slot_deltas": min(
                history_counts[development_end:]
            ),
            "target_or_future_values_used_for_correction": False,
        },
    }


def _adaptive_online_predictions(
    samples: Sequence[Dict[str, object]],
    record_lookup: Dict[datetime, Dict[str, float]],
    target: str,
) -> Tuple[Dict[str, List[float]], List[int]]:
    if target not in TARGETS:
        raise ValueError(f"Unsupported target: {target}")
    output = {candidate: [] for candidate in ADAPTIVE_CANDIDATE_ORDER}
    history_counts: List[int] = []
    for sample in samples:
        origin = sample["context"]["origin"]
        timestamp = origin["timestamp_dt"]
        current = float(origin.get(target) or 0.0)
        deltas: List[float] = []
        for day_offset in range(14):
            end_timestamp = timestamp - timedelta(days=day_offset)
            start_timestamp = end_timestamp - timedelta(days=1)
            end_record = record_lookup.get(end_timestamp)
            start_record = record_lookup.get(start_timestamp)
            if end_record is None or start_record is None:
                continue
            end_value = end_record.get(target)
            start_value = start_record.get(target)
            if end_value is None or start_value is None:
                continue
            deltas.append(float(end_value) - float(start_value))
        history_counts.append(len(deltas))
        output["seasonal_persistence"].append(current)
        for window in (3, 7, 14):
            selected_deltas = deltas[:window]
            mean_delta = (
                sum(selected_deltas) / float(len(selected_deltas))
                if selected_deltas
                else 0.0
            )
            output[f"same_slot_mean_{window}d"].append(current + mean_delta)
            median_delta = _median(selected_deltas) if selected_deltas else 0.0
            output[f"same_slot_median_{window}d"].append(current + median_delta)
        for alpha in (0.25, 0.50, 0.75):
            correction = _newest_weighted_average(deltas, alpha=alpha)
            output[f"same_slot_ewma_{alpha:.2f}"].append(current + correction)
    return output, history_counts


def _median(values: Sequence[float]) -> float:
    ordered = sorted(float(value) for value in values)
    midpoint = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[midpoint]
    return (ordered[midpoint - 1] + ordered[midpoint]) / 2.0


def _newest_weighted_average(
    newest_first_values: Sequence[float],
    alpha: float,
) -> float:
    if not newest_first_values:
        return 0.0
    weights = [
        alpha * ((1.0 - alpha) ** index)
        for index in range(len(newest_first_values))
    ]
    total_weight = sum(weights)
    return sum(
        weight * float(value)
        for weight, value in zip(weights, newest_first_values)
    ) / total_weight


def write_next_day_temperature_comparison(
    summary: Dict[str, object],
    output_path: Path = DEFAULT_OUTPUT_PATH,
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return output_path


def _build_next_day_feature_rows(
    samples: Sequence[Dict[str, object]],
    record_lookup: Dict[datetime, Dict[str, float]],
    physics_predictions: Sequence[float],
    target: str,
) -> Tuple[List[List[float]], Dict[str, List[float]], Dict[str, int]]:
    if target not in TARGETS:
        raise ValueError(f"Unsupported target: {target}")
    if len(samples) != len(physics_predictions):
        raise ValueError("Samples and physics predictions must have equal length")

    other_target = "room_temperature" if target == "dining_temperature" else "dining_temperature"
    rows: List[List[float]] = []
    current_values: List[float] = []
    lag_24h_values: List[float] = []
    lag_24h_available_values: List[float] = []
    lag_7d_available_values: List[float] = []
    missing_lag_24h = 0
    missing_lag_7d = 0

    for sample, physics in zip(samples, physics_predictions):
        origin = sample["context"]["origin"]
        timestamp = origin["timestamp_dt"]
        lag_24h_record = record_lookup.get(timestamp - timedelta(days=1))
        lag_7d_record = record_lookup.get(timestamp - timedelta(days=7))
        lag_24h_available = lag_24h_record is not None
        lag_7d_available = lag_7d_record is not None
        if not lag_24h_available:
            missing_lag_24h += 1
            lag_24h_record = origin
        if not lag_7d_available:
            missing_lag_7d += 1
            lag_7d_record = lag_24h_record

        current_target = float(origin.get(target) or 0.0)
        current_other = float(origin.get(other_target) or 0.0)
        lag_24h_target = float(lag_24h_record.get(target) or current_target)
        lag_24h_other = float(lag_24h_record.get(other_target) or current_other)
        lag_7d_target = float(lag_7d_record.get(target) or lag_24h_target)
        lag_7d_other = float(lag_7d_record.get(other_target) or lag_24h_other)
        outdoor_temperature = float(origin.get("outdoor_temperature") or 0.0)
        forecast_temperature = float(origin.get("forecast_temperature") or 0.0)
        hour = timestamp.hour + timestamp.minute / 60.0
        day_of_week = float(origin.get("day_of_week") or timestamp.weekday())
        hour_angle = 2.0 * math.pi * hour / 24.0
        week_angle = 2.0 * math.pi * day_of_week / 7.0
        row = [
            current_target,
            current_other,
            lag_24h_target,
            lag_24h_other,
            lag_7d_target,
            lag_7d_other,
            current_target - lag_24h_target,
            current_other - lag_24h_other,
            current_target - lag_7d_target,
            float(origin.get("dining_humidity") or 0.0),
            float(origin.get("room_humidity") or 0.0),
            outdoor_temperature,
            float(origin.get("outdoor_humidity") or 0.0),
            forecast_temperature,
            forecast_temperature - outdoor_temperature,
            math.log1p(max(float(origin.get("sunlight_illuminance") or 0.0), 0.0)),
            float(origin.get("rain_ratio") or 0.0),
            float(origin.get("wind_speed") or 0.0),
            float(origin.get("enthalpic_motor_1") or 0.0),
            float(origin.get("enthalpic_motor_2") or 0.0),
            float(origin.get("enthalpic_motor_turbo") or 0.0),
            math.sin(hour_angle),
            math.cos(hour_angle),
            math.sin(week_angle),
            math.cos(week_angle),
            1.0 if lag_24h_available else 0.0,
            1.0 if lag_7d_available else 0.0,
            float(physics),
            float(physics) - current_target,
        ]
        if len(row) != len(FEATURE_NAMES):
            raise AssertionError("Next-day feature width does not match feature names")
        rows.append(row)
        current_values.append(current_target)
        lag_24h_values.append(lag_24h_target)
        lag_24h_available_values.append(1.0 if lag_24h_available else 0.0)
        lag_7d_available_values.append(1.0 if lag_7d_available else 0.0)

    return (
        rows,
        {
            "current": current_values,
            "lag_24h": lag_24h_values,
            "lag_24h_available": lag_24h_available_values,
            "lag_7d_available": lag_7d_available_values,
        },
        {
            "all_missing_lag_24h": missing_lag_24h,
            "all_missing_lag_7d": missing_lag_7d,
            "test_missing_lag_24h": 0,
            "test_missing_lag_7d": 0,
        },
    )


def _evaluate_validation_candidates(
    actual: Sequence[float],
    current: Sequence[float],
    lag_24h: Sequence[float],
    physics: Sequence[float],
    feature_rows: Sequence[Sequence[float]],
    train_end: int,
    development_end: int,
) -> List[Dict[str, object]]:
    records: List[Dict[str, object]] = []
    grids = {
        "seasonal_persistence": (None,),
        "bias_corrected_persistence": (None,),
        "damped_daily_trend": WEIGHT_GRID,
        "persistence_physics_blend": WEIGHT_GRID,
        "seasonal_residual_ridge": RIDGE_GRID,
    }
    for candidate in CANDIDATE_ORDER:
        for parameter in grids[candidate]:
            predictions = _fit_and_predict_candidate(
                candidate=candidate,
                parameter=parameter,
                actual=actual,
                current=current,
                lag_24h=lag_24h,
                physics=physics,
                feature_rows=feature_rows,
                fit_start=0,
                fit_end=train_end,
                predict_start=train_end,
                predict_end=development_end,
            )
            records.append(
                {
                    "candidate": candidate,
                    "parameter": parameter,
                    "metrics": _metric_summary(actual[train_end:development_end], predictions),
                }
            )
    return records


def _best_validation_record_by_candidate(
    validation_records: Sequence[Dict[str, object]],
) -> Dict[str, Dict[str, object]]:
    output: Dict[str, Dict[str, object]] = {}
    for candidate in CANDIDATE_ORDER:
        candidate_records = [
            dict(record)
            for record in validation_records
            if record["candidate"] == candidate
        ]
        if not candidate_records:
            raise ValueError(f"Missing validation records for {candidate}")
        output[candidate] = min(candidate_records, key=lambda record: _selection_key(record))
    return output


def _selection_key(record: Dict[str, object]) -> Tuple[float, int, float]:
    parameter = record.get("parameter")
    numeric_parameter = -1.0 if parameter is None else float(parameter)
    return (
        float(record["metrics"]["mae"]),
        CANDIDATE_ORDER.index(str(record["candidate"])),
        numeric_parameter,
    )


def _fit_and_predict_candidate(
    candidate: str,
    parameter: object,
    actual: Sequence[float],
    current: Sequence[float],
    lag_24h: Sequence[float],
    physics: Sequence[float],
    feature_rows: Sequence[Sequence[float]],
    fit_start: int,
    fit_end: int,
    predict_start: int,
    predict_end: int,
) -> List[float]:
    if not (0 <= fit_start < fit_end <= predict_start < predict_end <= len(actual)):
        raise ValueError("Candidate fit/predict ranges must be ordered and non-empty")
    if candidate == "seasonal_persistence":
        return [float(value) for value in current[predict_start:predict_end]]
    if candidate == "bias_corrected_persistence":
        correction = sum(
            float(actual[index]) - float(current[index])
            for index in range(fit_start, fit_end)
        ) / float(fit_end - fit_start)
        return [
            float(current[index]) + correction
            for index in range(predict_start, predict_end)
        ]
    if candidate == "damped_daily_trend":
        alpha = float(parameter)
        return [
            float(current[index])
            + alpha * (float(current[index]) - float(lag_24h[index]))
            for index in range(predict_start, predict_end)
        ]
    if candidate == "persistence_physics_blend":
        weight = float(parameter)
        return [
            (1.0 - weight) * float(current[index]) + weight * float(physics[index])
            for index in range(predict_start, predict_end)
        ]
    if candidate == "seasonal_residual_ridge":
        fit_rows = feature_rows[fit_start:fit_end]
        predict_rows = feature_rows[predict_start:predict_end]
        standardized_fit, standardized_predict = _standardize_split(fit_rows, predict_rows)
        residual_targets = [
            float(actual[index]) - float(current[index])
            for index in range(fit_start, fit_end)
        ]
        coefficients = _fit_regularized_linear_readout(
            standardized_fit,
            residual_targets,
            ridge=float(parameter),
        )
        residual_predictions = [
            _predict_coefficients(coefficients, row)
            for row in standardized_predict
        ]
        return [
            float(current[index]) + residual
            for index, residual in zip(
                range(predict_start, predict_end),
                residual_predictions,
            )
        ]
    raise ValueError(f"Unsupported candidate: {candidate}")


def _comparison_baselines(
    target: str,
    target_index: int,
    actual: Sequence[float],
    samples: Sequence[Dict[str, object]],
    mapped_features: Sequence[Sequence[float]],
    physics_predictions: Sequence[float],
    development_end: int,
) -> Tuple[Dict[str, List[float]], Dict[str, Dict[str, float]]]:
    source_features = [
        [float(value) for value in sample["features"]]
        for sample in samples
    ]
    direct_coefficients = _fit_linear_regression(
        source_features[:development_end],
        actual[:development_end],
    )
    direct_predictions = [
        _predict_linear_regression(direct_coefficients, row)
        for row in source_features[development_end:]
    ]

    mapped_development, mapped_test = _standardize_split(
        mapped_features[:development_end],
        mapped_features[development_end:],
    )
    mapped_coefficients = _fit_regularized_linear_readout(
        mapped_development,
        actual[:development_end],
        ridge=1e-3,
    )
    mapped_predictions = [
        _predict_coefficients(mapped_coefficients, row)
        for row in mapped_test
    ]

    paper_features = [
        source + [float(mapped[0]), float(mapped[1])]
        for source, mapped in zip(source_features, mapped_features)
    ]
    paper_development, paper_test = _standardize_split(
        paper_features[:development_end],
        paper_features[development_end:],
    )
    residual_targets = [
        float(actual[index]) - float(physics_predictions[index])
        for index in range(development_end)
    ]
    residual_coefficients = _fit_regularized_linear_readout(
        paper_development,
        residual_targets,
        ridge=1e-3,
    )
    residual_predictions = [
        _predict_coefficients(residual_coefficients, row)
        for row in paper_test
    ]
    transfer_predictions = [
        float(physics) + residual
        for physics, residual in zip(
            physics_predictions[development_end:],
            residual_predictions,
        )
    ]
    predictions = {
        "direct_linear_regression": direct_predictions,
        "raw_physics_prior": [
            float(value) for value in physics_predictions[development_end:]
        ],
        "hybrid_digital_twin_readout": mapped_predictions,
        "oh2024_inspired_additive_residual": transfer_predictions,
    }
    del target, target_index
    return (
        predictions,
        {
            name: _metric_summary(actual[development_end:], values)
            for name, values in predictions.items()
        },
    )


def _paired_daily_block_bootstrap(
    actual: Sequence[float],
    persistence: Sequence[float],
    selected: Sequence[float],
    dates: Sequence[str],
    replicates: int,
    seed: int,
) -> Dict[str, object]:
    if not (len(actual) == len(persistence) == len(selected) == len(dates)):
        raise ValueError("Bootstrap inputs must have equal length")
    grouped: Dict[str, List[int]] = {}
    for index, date in enumerate(dates):
        grouped.setdefault(str(date), []).append(index)
    ordered_dates = sorted(grouped)
    if not ordered_dates:
        raise ValueError("Bootstrap requires at least one date block")
    rng = random.Random(seed)
    reductions: List[float] = []
    for _ in range(replicates):
        sampled_dates = [
            ordered_dates[rng.randrange(len(ordered_dates))]
            for _ in ordered_dates
        ]
        sampled_indices = [
            index
            for date in sampled_dates
            for index in grouped[date]
        ]
        persistence_mae = sum(
            abs(float(persistence[index]) - float(actual[index]))
            for index in sampled_indices
        ) / float(len(sampled_indices))
        selected_mae = sum(
            abs(float(selected[index]) - float(actual[index]))
            for index in sampled_indices
        ) / float(len(sampled_indices))
        reductions.append(persistence_mae - selected_mae)
    reductions.sort()
    observed_persistence_mae = sum(
        abs(float(prediction) - float(observation))
        for observation, prediction in zip(actual, persistence)
    ) / float(len(actual))
    observed_selected_mae = sum(
        abs(float(prediction) - float(observation))
        for observation, prediction in zip(actual, selected)
    ) / float(len(actual))
    return {
        "unit": "target_calendar_date",
        "date_blocks": len(ordered_dates),
        "replicates": replicates,
        "seed": seed,
        "observed_mae_reduction_c": round(
            observed_persistence_mae - observed_selected_mae,
            6,
        ),
        "mae_reduction_ci95_c": [
            round(_percentile(reductions, 0.025), 6),
            round(_percentile(reductions, 0.975), 6),
        ],
    }


def _percentile(sorted_values: Sequence[float], quantile: float) -> float:
    if not sorted_values:
        raise ValueError("Percentile requires non-empty values")
    if not 0.0 <= quantile <= 1.0:
        raise ValueError("quantile must be within [0, 1]")
    position = (len(sorted_values) - 1) * quantile
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return float(sorted_values[lower])
    fraction = position - lower
    return float(sorted_values[lower]) * (1.0 - fraction) + float(sorted_values[upper]) * fraction


def _not_evaluated_result(
    input_dir: Path,
    required_inputs: Sequence[Path],
    sample_count: int,
    reason: str,
) -> Dict[str, object]:
    return {
        "study_id": "E9-NEXTDAY-SEASONAL-DELTA",
        "dataset": "SML2010",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "NOT_EVALUATED",
        "input_dir": str(input_dir),
        "input_provenance": {
            str(path.relative_to(input_dir)): {
                "sha256": _sha256(path),
                "bytes": path.stat().st_size,
            }
            for path in required_inputs
        },
        "sample_count": sample_count,
        "reason": reason,
        "cases": [],
        "decisions": {
            "H-ND-01": "not_evaluated",
            "H-ND-ROB-01": "not_evaluated",
            "CLM-ND-01": "not_evaluated",
        },
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()
