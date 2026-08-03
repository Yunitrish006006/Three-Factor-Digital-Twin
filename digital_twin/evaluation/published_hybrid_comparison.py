from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
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


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_DIR = ROOT / "outputs" / "data" / "normalized_public" / "sml2010"
DEFAULT_OUTPUT_PATH = ROOT / "outputs" / "data" / "public_benchmarks" / "oh2024_inspired_sml2010_comparison.json"
DEFAULT_HORIZONS = (15, 60, 1440)
TARGETS = ("dining_temperature", "room_temperature")
RIDGE = 1e-3
METHOD_NAMES = (
    "persistence",
    "direct_linear_regression",
    "raw_physics_prior",
    "hybrid_digital_twin_readout",
    "oh2024_inspired_additive_residual",
)


def run_oh2024_inspired_comparison(
    input_dir: Path = DEFAULT_INPUT_DIR,
    horizons: Sequence[int] = DEFAULT_HORIZONS,
    checkpoint_path: Optional[Path] = None,
) -> Dict[str, object]:
    input_dir = Path(input_dir)
    normalized_horizons = tuple(sorted({int(value) for value in horizons if int(value) > 0}))
    if not normalized_horizons:
        raise ValueError("At least one positive forecast horizon is required.")

    required_inputs = (
        input_dir / "corner_sensor_timeseries.csv",
        input_dir / "outdoor_environment.csv",
        input_dir / "auxiliary_features.csv",
    )
    missing_inputs = [str(path) for path in required_inputs if not path.exists()]
    if missing_inputs:
        raise FileNotFoundError(f"Missing normalized SML2010 inputs: {', '.join(missing_inputs)}")

    sensor_rows = _read_csv_rows(required_inputs[0])
    outdoor_rows = _read_csv_rows(required_inputs[1])
    auxiliary_rows = _read_csv_rows(required_inputs[2])
    records = _load_sml2010_records(sensor_rows, outdoor_rows, auxiliary_rows)
    selected_checkpoint = Path(checkpoint_path) if checkpoint_path is not None else DEFAULT_CHECKPOINT_PATH
    predictor = MappedHybridPublicPredictor(checkpoint_path=selected_checkpoint)

    cases: List[Dict[str, object]] = []
    for horizon in normalized_horizons:
        samples = _build_sml2010_response_samples(records, horizon, task_id="S2")
        cases.extend(_evaluate_horizon(samples, horizon, predictor))

    evaluated_cases = [case for case in cases if case["status"] == "ok"]
    improvement_count = sum(
        1
        for case in evaluated_cases
        if float(case["mae_reductions"]["oh2024_inspired_vs_raw_physics"]) > 0.0
    )
    lowest_mae_counts = {method: 0 for method in METHOD_NAMES}
    for case in evaluated_cases:
        lowest_mae_counts[str(case["lowest_mae_method"])] += 1

    complete_default_design = (
        normalized_horizons == DEFAULT_HORIZONS
        and len(evaluated_cases) == len(DEFAULT_HORIZONS) * len(TARGETS)
    )
    if complete_default_design:
        hypothesis_decision = "supported" if improvement_count >= 4 else "not_supported"
        claim_decision = "supported"
    else:
        hypothesis_decision = "not_evaluated"
        claim_decision = "partial" if evaluated_cases else "not_evaluated"

    return {
        "study_id": "E9-OH2024-TRANSFER",
        "dataset": "SML2010",
        "benchmark_mode": "two-point temperature response method transfer",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "COMPLETE" if complete_default_design else ("PARTIAL" if evaluated_cases else "NOT_EVALUATED"),
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
            "task_id": "S2",
            "targets": list(TARGETS),
            "horizons_minutes": list(normalized_horizons),
            "split": "chronological_70_30",
            "ridge": RIDGE,
            "metrics": ["mae", "rmse", "correlation", "r2", "cvrmse_pct"],
            "decision_rule": "H-PHB-01 is supported when the transfer MAE is lower than raw physics in at least 4 of 6 default target-horizon cases.",
        },
        "method_fidelity": {
            "label": "Oh et al. (2024)-inspired additive residual transfer",
            "equation": "y_hat_transfer(t+h|I_t) = y_hat_physics(t+h|I_t) + r_hat_linear(t+h|I_t)",
            "shared_concepts": [
                "physical or simulation prediction is an explicit target-time baseline",
                "origin-time measurements and operating or boundary variables inform a learned discrepancy",
                "the final prediction adds the learned discrepancy to the physical baseline",
            ],
            "known_differences": [
                "ridge-linear residual head replaces the paper's CNN-LSTM structure",
                "project pseudo-room physics replaces TRNSYS Type 56 and the calibrated RC model",
                "SML2010 two-point temperatures replace confidential commercial-building return-air data",
            ],
            "reproduction_status": "METHOD_TRANSFER_NOT_PAPER_REPRODUCTION",
            "paper_data_availability": "confidential",
        },
        "published_context_not_directly_comparable": {
            "citation": "Oh, Sfarra, and Kim, Energy and Buildings 324 (2024) 114898",
            "december": {"black_box_r2": 0.72, "black_box_cvrmse_pct": 3.58, "hybrid_rc_r2": 0.93, "hybrid_rc_cvrmse_pct": 1.73},
            "january": {"black_box_r2": -2.79, "black_box_cvrmse_pct": 19.82, "hybrid_rc_r2": 0.88, "hybrid_rc_cvrmse_pct": 3.55},
            "february": {"black_box_r2": -4.60, "black_box_cvrmse_pct": 18.83, "hybrid_rc_r2": 0.83, "hybrid_rc_cvrmse_pct": 3.27},
            "comparison_boundary": "These published values use another building, return-air target, training regime, physical model, and data source; they are literature context, not pooled head-to-head evidence.",
        },
        "cases": cases,
        "summary": {
            "evaluated_cases": len(evaluated_cases),
            "default_cases_expected": len(DEFAULT_HORIZONS) * len(TARGETS),
            "oh2024_inspired_wins_vs_raw_physics": improvement_count,
            "lowest_mae_counts": lowest_mae_counts,
        },
        "decisions": {
            "H-PHB-01": hypothesis_decision,
            "CLM-PHB-01": claim_decision,
        },
        "claim_boundary": (
            "This output supports only a public-task method-transfer comparison. "
            "It does not reproduce the paper's confidential data, CNN-LSTM, TRNSYS/RC models, "
            "published numerical results, or a full 3-D spatial field evaluation."
        ),
    }


def write_oh2024_inspired_comparison(
    summary: Dict[str, object],
    output_path: Path = DEFAULT_OUTPUT_PATH,
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output_path


def _evaluate_horizon(
    samples: Sequence[Dict[str, object]],
    horizon_minutes: int,
    predictor: MappedHybridPublicPredictor,
) -> List[Dict[str, object]]:
    if len(samples) < 4:
        return [
            {
                "task_id": "S2",
                "target": target,
                "horizon_minutes": horizon_minutes,
                "status": "insufficient_samples",
                "sample_count": len(samples),
                "min_samples_required": 4,
            }
            for target in TARGETS
        ]

    split_index = max(1, min(len(samples) - 1, int(len(samples) * 0.7)))
    train_samples = list(samples[:split_index])
    test_samples = list(samples[split_index:])

    mapped_features = [
        predictor.build_features("sml2010", "S2", sample, horizon_minutes)
        for sample in samples
    ]
    source_features = [[float(value) for value in sample["features"]] for sample in samples]
    paper_features = [
        source + [float(mapped[0]), float(mapped[1])]
        for source, mapped in zip(source_features, mapped_features)
    ]
    mapped_train, mapped_test = _standardize_split(mapped_features[:split_index], mapped_features[split_index:])
    paper_train, paper_test = _standardize_split(paper_features[:split_index], paper_features[split_index:])

    output: List[Dict[str, object]] = []
    physics_indices = {"dining_temperature": 0, "room_temperature": 1}
    for target in TARGETS:
        train_actual = [float(sample["targets"][target]) for sample in train_samples]
        test_actual = [float(sample["targets"][target]) for sample in test_samples]
        persistence_predictions = [float(sample["persistence"][target]) for sample in test_samples]

        direct_coefficients = _fit_linear_regression(source_features[:split_index], train_actual)
        direct_predictions = [
            _predict_linear_regression(direct_coefficients, features)
            for features in source_features[split_index:]
        ]

        physics_index = physics_indices[target]
        train_physics = [float(row[physics_index]) for row in mapped_features[:split_index]]
        test_physics = [float(row[physics_index]) for row in mapped_features[split_index:]]

        mapped_coefficients = _fit_regularized_linear_readout(mapped_train, train_actual, ridge=RIDGE)
        mapped_predictions = [_predict_coefficients(mapped_coefficients, row) for row in mapped_test]

        train_residuals = [
            actual - physics
            for actual, physics in zip(train_actual, train_physics)
        ]
        residual_coefficients = _fit_regularized_linear_readout(paper_train, train_residuals, ridge=RIDGE)
        residual_predictions = [_predict_coefficients(residual_coefficients, row) for row in paper_test]
        transfer_predictions = [
            physics + residual
            for physics, residual in zip(test_physics, residual_predictions)
        ]

        predictions_by_method = {
            "persistence": persistence_predictions,
            "direct_linear_regression": direct_predictions,
            "raw_physics_prior": test_physics,
            "hybrid_digital_twin_readout": mapped_predictions,
            "oh2024_inspired_additive_residual": transfer_predictions,
        }
        metrics = {
            method: _metric_summary(test_actual, predictions)
            for method, predictions in predictions_by_method.items()
        }
        lowest_method = min(METHOD_NAMES, key=lambda name: (float(metrics[name]["mae"]), name))
        transfer_mae = float(metrics["oh2024_inspired_additive_residual"]["mae"])
        output.append(
            {
                "task_id": "S2",
                "target": target,
                "horizon_minutes": horizon_minutes,
                "status": "ok",
                "sample_count": len(samples),
                "train_samples": len(train_samples),
                "test_samples": len(test_samples),
                "train_start": str(train_samples[0]["context"]["origin"]["timestamp_dt"]),
                "train_end": str(train_samples[-1]["context"]["origin"]["timestamp_dt"]),
                "test_start": str(test_samples[0]["context"]["origin"]["timestamp_dt"]),
                "test_end": str(test_samples[-1]["context"]["origin"]["timestamp_dt"]),
                "method_feature_contract": {
                    "direct_linear_regression": "13 origin-time SML2010 S2 features",
                    "raw_physics_prior": f"mapped physics target index {physics_index}",
                    "hybrid_digital_twin_readout": predictor.feature_names("sml2010", "S2"),
                    "oh2024_inspired_additive_residual": (
                        "13 origin-time SML2010 S2 features plus the two target-time physics temperature estimates; "
                        "all standardization parameters are fitted on training rows only"
                    ),
                },
                "metrics": metrics,
                "mae_reductions": {
                    "oh2024_inspired_vs_raw_physics": round(
                        float(metrics["raw_physics_prior"]["mae"]) - transfer_mae,
                        6,
                    ),
                    "oh2024_inspired_vs_persistence": round(
                        float(metrics["persistence"]["mae"]) - transfer_mae,
                        6,
                    ),
                    "oh2024_inspired_vs_direct_linear": round(
                        float(metrics["direct_linear_regression"]["mae"]) - transfer_mae,
                        6,
                    ),
                    "oh2024_inspired_vs_project_readout": round(
                        float(metrics["hybrid_digital_twin_readout"]["mae"]) - transfer_mae,
                        6,
                    ),
                },
                "lowest_mae_method": lowest_method,
            }
        )
    return output


def _standardize_split(
    train_rows: Sequence[Sequence[float]],
    test_rows: Sequence[Sequence[float]],
) -> Tuple[List[List[float]], List[List[float]]]:
    if not train_rows:
        raise ValueError("Training rows are required for standardization.")
    width = len(train_rows[0])
    if any(len(row) != width for row in list(train_rows) + list(test_rows)):
        raise ValueError("All feature rows must have equal width.")
    means = [
        sum(float(row[index]) for row in train_rows) / float(len(train_rows))
        for index in range(width)
    ]
    scales = [
        max(
            math.sqrt(
                sum((float(row[index]) - means[index]) ** 2 for row in train_rows)
                / float(len(train_rows))
            ),
            1e-6,
        )
        for index in range(width)
    ]

    def transform(rows: Sequence[Sequence[float]]) -> List[List[float]]:
        return [
            [
                (float(value) - means[index]) / scales[index]
                for index, value in enumerate(row)
            ]
            for row in rows
        ]

    return transform(train_rows), transform(test_rows)


def _predict_coefficients(coefficients: Sequence[float], row: Sequence[float]) -> float:
    return float(coefficients[0] + sum(weight * value for weight, value in zip(coefficients[1:], row)))


def _metric_summary(actual: Sequence[float], predicted: Sequence[float]) -> Dict[str, float]:
    if not actual or len(actual) != len(predicted):
        raise ValueError("Actual and predicted vectors must have the same non-zero length.")
    count = float(len(actual))
    errors = [float(prediction) - float(observation) for observation, prediction in zip(actual, predicted)]
    squared_errors = [error * error for error in errors]
    absolute_errors = [abs(error) for error in errors]
    mean_actual = sum(float(value) for value in actual) / count
    mean_predicted = sum(float(value) for value in predicted) / count
    sst = sum((float(value) - mean_actual) ** 2 for value in actual)
    covariance = sum(
        (float(observation) - mean_actual) * (float(prediction) - mean_predicted)
        for observation, prediction in zip(actual, predicted)
    )
    actual_variance = sum((float(value) - mean_actual) ** 2 for value in actual)
    predicted_variance = sum((float(value) - mean_predicted) ** 2 for value in predicted)
    correlation_denominator = math.sqrt(actual_variance * predicted_variance)
    rmse = math.sqrt(sum(squared_errors) / count)
    return {
        "mae": round(sum(absolute_errors) / count, 6),
        "rmse": round(rmse, 6),
        "correlation": round(covariance / correlation_denominator if correlation_denominator > 1e-12 else 0.0, 6),
        "r2": round(1.0 - (sum(squared_errors) / sst) if sst > 1e-12 else 0.0, 6),
        "cvrmse_pct": round((rmse / abs(mean_actual)) * 100.0 if abs(mean_actual) > 1e-12 else 0.0, 6),
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()
