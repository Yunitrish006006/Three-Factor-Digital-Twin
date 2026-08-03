from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from digital_twin.core.public_dataset_benchmark import (
    _build_sml2010_response_samples,
    _load_sml2010_records,
    _metric_summary,
    _read_csv_rows,
)
from digital_twin.core.public_dataset_model_comparison import (
    MappedHybridPublicPredictor,
    _fit_regularized_linear_readout,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_DIR = ROOT / "outputs" / "data" / "normalized_public" / "sml2010"
DEFAULT_OUTPUT_PATH = ROOT / "outputs" / "data" / "public_benchmarks" / "rnn_sml2010_comparison.json"
DEFAULT_HORIZONS = (15, 60, 1440)
TARGET_NAMES = (
    "dining_temperature",
    "room_temperature",
    "dining_humidity",
    "room_humidity",
)
RAW_FEATURE_NAMES = (
    "dining_temperature",
    "room_temperature",
    "dining_humidity",
    "room_humidity",
    "outdoor_temperature",
    "outdoor_humidity",
    "sunlight_illuminance",
    "rain_ratio",
    "wind_speed",
    "forecast_temperature",
    "enthalpic_motor_1",
    "enthalpic_motor_2",
    "enthalpic_motor_turbo",
)
PHYSICS_FEATURE_INDICES = (0, 1, 2, 3, 8, 9, 10, 11)
PHYSICS_FEATURE_NAMES = (
    "physics_dining_temperature",
    "physics_room_temperature",
    "physics_dining_humidity",
    "physics_room_humidity",
    "boundary_activation",
    "motor_level",
    "outdoor_temperature_gap",
    "outdoor_humidity_gap",
)
METHOD_NAMES = (
    "persistence",
    "sequence_linear_regression",
    "physics_structured_readout",
    "vanilla_rnn",
)


@dataclass(frozen=True)
class RNNConfig:
    sequence_length: int = 4
    hidden_units: int = 6
    epochs: int = 30
    batch_size: int = 32
    learning_rate: float = 0.01
    gradient_clip: float = 1.0
    seed: int = 42


class VanillaElmanRNN:
    """Small deterministic sequence-to-one Elman RNN with Adam training."""

    def __init__(self, input_size: int, output_size: int, config: RNNConfig) -> None:
        if input_size <= 0 or output_size <= 0:
            raise ValueError("RNN input and output sizes must be positive.")
        if config.sequence_length < 2 or config.hidden_units <= 0:
            raise ValueError("RNN sequence length must be at least two and hidden units must be positive.")
        self.input_size = int(input_size)
        self.output_size = int(output_size)
        self.config = config
        rng = random.Random(config.seed)
        input_limit = 1.0 / math.sqrt(float(self.input_size))
        hidden_limit = 1.0 / math.sqrt(float(config.hidden_units))
        self.params: Dict[str, object] = {
            "w_xh": [
                [rng.uniform(-input_limit, input_limit) for _ in range(self.input_size)]
                for _ in range(config.hidden_units)
            ],
            "w_hh": [
                [rng.uniform(-hidden_limit, hidden_limit) for _ in range(config.hidden_units)]
                for _ in range(config.hidden_units)
            ],
            "b_h": [0.0 for _ in range(config.hidden_units)],
            "w_hy": [
                [rng.uniform(-hidden_limit, hidden_limit) for _ in range(config.hidden_units)]
                for _ in range(self.output_size)
            ],
            "b_y": [0.0 for _ in range(self.output_size)],
        }
        self._first_moment = _zeros_like(self.params)
        self._second_moment = _zeros_like(self.params)
        self._step = 0

    def fit(
        self,
        sequences: Sequence[Sequence[Sequence[float]]],
        targets: Sequence[Sequence[float]],
    ) -> Dict[str, object]:
        if not sequences or len(sequences) != len(targets):
            raise ValueError("RNN training sequences and targets must have the same non-zero length.")
        for sequence, target in zip(sequences, targets):
            self._validate_sequence(sequence)
            if len(target) != self.output_size:
                raise ValueError("RNN target width mismatch.")

        epoch_losses: List[float] = []
        for _ in range(self.config.epochs):
            gradients = _zeros_like(self.params)
            batch_count = 0
            squared_error_sum = 0.0
            value_count = 0
            for sequence, target in zip(sequences, targets):
                prediction, hidden_states = self._forward(sequence)
                squared_error_sum += sum(
                    (float(prediction[index]) - float(target[index])) ** 2
                    for index in range(self.output_size)
                )
                value_count += self.output_size
                self._accumulate_gradients(sequence, target, prediction, hidden_states, gradients)
                batch_count += 1
                if batch_count == self.config.batch_size:
                    self._apply_adam(gradients, batch_count)
                    gradients = _zeros_like(self.params)
                    batch_count = 0
            if batch_count:
                self._apply_adam(gradients, batch_count)
            epoch_losses.append(squared_error_sum / float(max(value_count, 1)))

        return {
            "epochs": self.config.epochs,
            "samples": len(sequences),
            "initial_standardized_mse": round(epoch_losses[0], 8),
            "final_standardized_mse": round(epoch_losses[-1], 8),
            "all_epoch_losses_finite": all(math.isfinite(value) for value in epoch_losses),
        }

    def predict(self, sequence: Sequence[Sequence[float]]) -> List[float]:
        self._validate_sequence(sequence)
        prediction, _ = self._forward(sequence)
        if not all(math.isfinite(value) for value in prediction):
            raise ValueError("RNN produced a non-finite prediction.")
        return prediction

    def _validate_sequence(self, sequence: Sequence[Sequence[float]]) -> None:
        if len(sequence) != self.config.sequence_length:
            raise ValueError("RNN sequence length mismatch.")
        if any(len(row) != self.input_size for row in sequence):
            raise ValueError("RNN input width mismatch.")
        if any(not math.isfinite(float(value)) for row in sequence for value in row):
            raise ValueError("RNN inputs must be finite.")

    def _forward(
        self,
        sequence: Sequence[Sequence[float]],
    ) -> Tuple[List[float], List[List[float]]]:
        w_xh = self.params["w_xh"]
        w_hh = self.params["w_hh"]
        b_h = self.params["b_h"]
        w_hy = self.params["w_hy"]
        b_y = self.params["b_y"]
        hidden_states: List[List[float]] = [[0.0 for _ in range(self.config.hidden_units)]]
        for row in sequence:
            previous = hidden_states[-1]
            current = []
            for hidden_index in range(self.config.hidden_units):
                value = float(b_h[hidden_index])
                value += sum(
                    float(w_xh[hidden_index][input_index]) * float(row[input_index])
                    for input_index in range(self.input_size)
                )
                value += sum(
                    float(w_hh[hidden_index][prior_index]) * float(previous[prior_index])
                    for prior_index in range(self.config.hidden_units)
                )
                current.append(math.tanh(value))
            hidden_states.append(current)
        final_hidden = hidden_states[-1]
        prediction = [
            float(b_y[output_index])
            + sum(
                float(w_hy[output_index][hidden_index]) * float(final_hidden[hidden_index])
                for hidden_index in range(self.config.hidden_units)
            )
            for output_index in range(self.output_size)
        ]
        return prediction, hidden_states

    def _accumulate_gradients(
        self,
        sequence: Sequence[Sequence[float]],
        target: Sequence[float],
        prediction: Sequence[float],
        hidden_states: Sequence[Sequence[float]],
        gradients: Dict[str, object],
    ) -> None:
        w_hh = self.params["w_hh"]
        w_hy = self.params["w_hy"]
        final_hidden = hidden_states[-1]
        output_gradient = [
            2.0 * (float(prediction[index]) - float(target[index])) / float(self.output_size)
            for index in range(self.output_size)
        ]
        for output_index in range(self.output_size):
            gradients["b_y"][output_index] += output_gradient[output_index]
            for hidden_index in range(self.config.hidden_units):
                gradients["w_hy"][output_index][hidden_index] += (
                    output_gradient[output_index] * float(final_hidden[hidden_index])
                )

        hidden_gradient = [
            sum(
                float(w_hy[output_index][hidden_index]) * output_gradient[output_index]
                for output_index in range(self.output_size)
            )
            for hidden_index in range(self.config.hidden_units)
        ]
        for sequence_index in range(len(sequence) - 1, -1, -1):
            current_hidden = hidden_states[sequence_index + 1]
            previous_hidden = hidden_states[sequence_index]
            tanh_gradient = [
                hidden_gradient[hidden_index] * (1.0 - float(current_hidden[hidden_index]) ** 2)
                for hidden_index in range(self.config.hidden_units)
            ]
            for hidden_index in range(self.config.hidden_units):
                gradients["b_h"][hidden_index] += tanh_gradient[hidden_index]
                for input_index in range(self.input_size):
                    gradients["w_xh"][hidden_index][input_index] += (
                        tanh_gradient[hidden_index] * float(sequence[sequence_index][input_index])
                    )
                for prior_index in range(self.config.hidden_units):
                    gradients["w_hh"][hidden_index][prior_index] += (
                        tanh_gradient[hidden_index] * float(previous_hidden[prior_index])
                    )
            hidden_gradient = [
                sum(
                    float(w_hh[hidden_index][prior_index]) * tanh_gradient[hidden_index]
                    for hidden_index in range(self.config.hidden_units)
                )
                for prior_index in range(self.config.hidden_units)
            ]

    def _apply_adam(self, gradients: Dict[str, object], batch_count: int) -> None:
        self._step += 1
        beta1 = 0.9
        beta2 = 0.999
        epsilon = 1e-8
        learning_rate = self.config.learning_rate
        clip = self.config.gradient_clip
        for name in self.params:
            _adam_update(
                parameter=self.params[name],
                gradient=gradients[name],
                first_moment=self._first_moment[name],
                second_moment=self._second_moment[name],
                batch_count=batch_count,
                learning_rate=learning_rate,
                beta1=beta1,
                beta2=beta2,
                epsilon=epsilon,
                step=self._step,
                clip=clip,
            )


def run_rnn_public_comparison(
    input_dir: Path = DEFAULT_INPUT_DIR,
    horizons: Sequence[int] = DEFAULT_HORIZONS,
    config: RNNConfig = RNNConfig(),
    cadence_minutes: int = 15,
) -> Dict[str, object]:
    input_dir = Path(input_dir)
    normalized_horizons = tuple(sorted({int(value) for value in horizons if int(value) > 0}))
    if not normalized_horizons:
        raise ValueError("At least one positive horizon is required.")
    required_inputs = (
        input_dir / "corner_sensor_timeseries.csv",
        input_dir / "outdoor_environment.csv",
        input_dir / "auxiliary_features.csv",
    )
    missing = [str(path) for path in required_inputs if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing normalized SML2010 inputs: {', '.join(missing)}")

    records = _load_sml2010_records(
        _read_csv_rows(required_inputs[0]),
        _read_csv_rows(required_inputs[1]),
        _read_csv_rows(required_inputs[2]),
    )
    disabled_checkpoint = input_dir / ".same_data_rnn_comparison_no_pretrained_checkpoint.json"
    if disabled_checkpoint.exists():
        raise ValueError(f"Reserved disabled-checkpoint path unexpectedly exists: {disabled_checkpoint}")
    predictor = MappedHybridPublicPredictor(checkpoint_path=disabled_checkpoint)

    cases: List[Dict[str, object]] = []
    horizon_audits: List[Dict[str, object]] = []
    for horizon in normalized_horizons:
        horizon_result = _evaluate_horizon(
            records=records,
            horizon_minutes=horizon,
            predictor=predictor,
            config=config,
            cadence_minutes=cadence_minutes,
        )
        horizon_audits.append(horizon_result["audit"])
        cases.extend(horizon_result["cases"])

    evaluated_cases = [case for case in cases if case["status"] == "ok"]
    lowest_mae_counts = {method: 0 for method in METHOD_NAMES}
    rnn_wins = {method: 0 for method in METHOD_NAMES if method != "vanilla_rnn"}
    for case in evaluated_cases:
        lowest_mae_counts[str(case["lowest_mae_method"])] += 1
        rnn_mae = float(case["metrics"]["vanilla_rnn"]["mae"])
        for method in rnn_wins:
            if rnn_mae < float(case["metrics"][method]["mae"]):
                rnn_wins[method] += 1

    expected_cases = len(normalized_horizons) * len(TARGET_NAMES)
    parity_passed = bool(horizon_audits) and all(bool(audit["parity_passed"]) for audit in horizon_audits)
    complete = len(evaluated_cases) == expected_cases and parity_passed
    return {
        "study_id": "E9-RNN-SAME-DATA-COMPARISON",
        "dataset": "SML2010",
        "task_id": "S2",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "COMPLETE" if complete else ("PARTIAL" if evaluated_cases else "NOT_EVALUATED"),
        "input_dir": str(input_dir),
        "input_provenance": {
            str(path.relative_to(input_dir)): {"sha256": _sha256(path), "bytes": path.stat().st_size}
            for path in required_inputs
        },
        "protocol": {
            "horizons_minutes": list(normalized_horizons),
            "targets": list(TARGET_NAMES),
            "split": "chronological_70_30",
            "cadence_minutes": cadence_minutes,
            "shared_history_records": config.sequence_length,
            "comparators": list(METHOD_NAMES),
            "rnn": asdict(config),
            "learned_synthetic_checkpoint_loaded": False,
            "decision_rule": "Descriptive comparison; CLM-RNN-01 requires all cases and endpoint-parity audits, not RNN superiority.",
        },
        "data_parity": {
            "primary_rule": "All comparators use identical eligible endpoints, four-record origin histories, split, targets, and test rows.",
            "raw_history_shared_by": ["sequence_linear_regression", "vanilla_rnn"],
            "physics_feature_provenance": "Derived only from the same four origin records; no learned synthetic checkpoint is loaded.",
            "horizon_audits": horizon_audits,
            "all_horizons_passed": parity_passed,
        },
        "cases": cases,
        "summary": {
            "evaluated_cases": len(evaluated_cases),
            "expected_cases": expected_cases,
            "lowest_mae_counts": lowest_mae_counts,
            "rnn_wins_vs": rnn_wins,
        },
        "decisions": {
            "RQ-RNN-01": "evaluated" if complete else "not_evaluated",
            "CLM-RNN-01": "supported" if complete else "not_supported",
        },
        "claim_boundary": (
            "Same-data SML2010 S2 public-task comparison only. It is not full 3-D validation, "
            "cross-domain evidence, or proof that RNN or the project method is universally superior."
        ),
    }


def write_rnn_public_comparison(
    summary: Dict[str, object],
    output_path: Path = DEFAULT_OUTPUT_PATH,
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output_path


def _evaluate_horizon(
    records: Sequence[Dict[str, float]],
    horizon_minutes: int,
    predictor: MappedHybridPublicPredictor,
    config: RNNConfig,
    cadence_minutes: int,
) -> Dict[str, object]:
    samples = _build_sml2010_response_samples(records, horizon_minutes, task_id="S2")
    endpoints = _shared_sequence_endpoints(samples, config.sequence_length, cadence_minutes)
    if len(endpoints) < 8:
        cases = [
            {
                "target": target,
                "horizon_minutes": horizon_minutes,
                "status": "insufficient_samples",
                "eligible_endpoints": len(endpoints),
                "minimum_required": 8,
            }
            for target in TARGET_NAMES
        ]
        return {
            "audit": {
                "horizon_minutes": horizon_minutes,
                "parity_passed": False,
                "eligible_endpoints": len(endpoints),
                "reason": "insufficient_samples",
            },
            "cases": cases,
        }

    split_index = max(1, min(len(endpoints) - 1, int(len(endpoints) * 0.7)))
    train_endpoints = endpoints[:split_index]
    test_endpoints = endpoints[split_index:]
    raw_rows = [[float(value) for value in sample["features"]] for sample in samples]
    mapped_rows = [
        predictor.build_features("sml2010", "S2", sample, horizon_minutes)
        for sample in samples
    ]
    physics_rows = [
        [float(row[index]) for index in PHYSICS_FEATURE_INDICES]
        for row in mapped_rows
    ]

    training_history_indices = sorted(
        {
            index
            for endpoint in train_endpoints
            for index in range(endpoint - config.sequence_length + 1, endpoint + 1)
        }
    )
    raw_means, raw_scales = _fit_standardizer(
        [raw_rows[index] for index in training_history_indices]
    )
    raw_standardized = [_transform_row(row, raw_means, raw_scales) for row in raw_rows]
    raw_sequences = {
        endpoint: raw_standardized[endpoint - config.sequence_length + 1 : endpoint + 1]
        for endpoint in endpoints
    }
    flattened_raw = {endpoint: _flatten(raw_sequences[endpoint]) for endpoint in endpoints}

    physics_means, physics_scales = _fit_standardizer(
        [physics_rows[index] for index in training_history_indices]
    )
    physics_standardized = [_transform_row(row, physics_means, physics_scales) for row in physics_rows]
    flattened_physics = {
        endpoint: _flatten(
            physics_standardized[endpoint - config.sequence_length + 1 : endpoint + 1]
        )
        for endpoint in endpoints
    }

    target_matrix = [
        [float(samples[endpoint]["targets"][target]) for target in TARGET_NAMES]
        for endpoint in train_endpoints
    ]
    target_means, target_scales = _fit_standardizer(target_matrix)
    standardized_targets = [
        _transform_row(row, target_means, target_scales)
        for row in target_matrix
    ]
    rnn = VanillaElmanRNN(len(RAW_FEATURE_NAMES), len(TARGET_NAMES), config)
    training = rnn.fit(
        [raw_sequences[endpoint] for endpoint in train_endpoints],
        standardized_targets,
    )
    if not training["all_epoch_losses_finite"]:
        raise ValueError("RNN training produced non-finite losses.")
    rnn_predictions_matrix = [
        _inverse_transform_row(rnn.predict(raw_sequences[endpoint]), target_means, target_scales)
        for endpoint in test_endpoints
    ]

    endpoint_ids = [_endpoint_id(samples[endpoint]) for endpoint in endpoints]
    train_ids = endpoint_ids[:split_index]
    test_ids = endpoint_ids[split_index:]
    endpoint_hash = _hash_strings(endpoint_ids)
    train_hash = _hash_strings(train_ids)
    test_hash = _hash_strings(test_ids)
    train_input_hash = _hash_strings(
        [_shared_input_record(samples, endpoint, config.sequence_length) for endpoint in train_endpoints]
    )
    test_input_hash = _hash_strings(
        [_shared_input_record(samples, endpoint, config.sequence_length) for endpoint in test_endpoints]
    )
    method_data_contracts = {
        method: {
            "shared_train_endpoint_hash": train_hash,
            "shared_test_endpoint_hash": test_hash,
            "shared_train_input_hash": train_input_hash,
            "shared_test_input_hash": test_input_hash,
        }
        for method in METHOD_NAMES
    }

    cases: List[Dict[str, object]] = []
    for target_index, target in enumerate(TARGET_NAMES):
        train_actual = [float(samples[endpoint]["targets"][target]) for endpoint in train_endpoints]
        test_actual = [float(samples[endpoint]["targets"][target]) for endpoint in test_endpoints]
        persistence = [float(samples[endpoint]["persistence"][target]) for endpoint in test_endpoints]

        linear_coefficients = _fit_regularized_linear_readout(
            [flattened_raw[endpoint] for endpoint in train_endpoints],
            train_actual,
            ridge=1e-3,
        )
        linear_predictions = [
            _predict_linear(linear_coefficients, flattened_raw[endpoint])
            for endpoint in test_endpoints
        ]
        physics_coefficients = _fit_regularized_linear_readout(
            [flattened_physics[endpoint] for endpoint in train_endpoints],
            train_actual,
            ridge=1e-3,
        )
        physics_predictions = [
            _predict_linear(physics_coefficients, flattened_physics[endpoint])
            for endpoint in test_endpoints
        ]
        rnn_predictions = [row[target_index] for row in rnn_predictions_matrix]
        predictions = {
            "persistence": persistence,
            "sequence_linear_regression": linear_predictions,
            "physics_structured_readout": physics_predictions,
            "vanilla_rnn": rnn_predictions,
        }
        metrics = {
            method: _metric_summary(test_actual, values)
            for method, values in predictions.items()
        }
        lowest_method = min(METHOD_NAMES, key=lambda method: (float(metrics[method]["mae"]), method))
        rnn_mae = float(metrics["vanilla_rnn"]["mae"])
        cases.append(
            {
                "target": target,
                "horizon_minutes": horizon_minutes,
                "status": "ok",
                "eligible_endpoints": len(endpoints),
                "train_samples": len(train_endpoints),
                "test_samples": len(test_endpoints),
                "shared_endpoint_hash": endpoint_hash,
                "shared_train_endpoint_hash": train_hash,
                "shared_test_endpoint_hash": test_hash,
                "shared_train_input_hash": train_input_hash,
                "shared_test_input_hash": test_input_hash,
                "metrics": metrics,
                "rnn_mae_difference_vs": {
                    method: round(float(metrics[method]["mae"]) - rnn_mae, 6)
                    for method in METHOD_NAMES
                    if method != "vanilla_rnn"
                },
                "lowest_mae_method": lowest_method,
            }
        )

    parity_passed = all(
        case["shared_test_endpoint_hash"] == test_hash
        and case["shared_test_input_hash"] == test_input_hash
        and case["test_samples"] == len(test_endpoints)
        for case in cases
    ) and all(
        contract["shared_train_endpoint_hash"] == train_hash
        and contract["shared_test_endpoint_hash"] == test_hash
        and contract["shared_train_input_hash"] == train_input_hash
        and contract["shared_test_input_hash"] == test_input_hash
        for contract in method_data_contracts.values()
    )
    return {
        "audit": {
            "horizon_minutes": horizon_minutes,
            "parity_passed": parity_passed,
            "eligible_endpoints": len(endpoints),
            "excluded_for_sequence_history_or_gap": len(samples) - len(endpoints),
            "train_samples": len(train_endpoints),
            "test_samples": len(test_endpoints),
            "endpoint_hash": endpoint_hash,
            "train_endpoint_hash": train_hash,
            "test_endpoint_hash": test_hash,
            "train_input_hash": train_input_hash,
            "test_input_hash": test_input_hash,
            "method_data_contracts": method_data_contracts,
            "first_endpoint": endpoint_ids[0],
            "last_endpoint": endpoint_ids[-1],
            "first_test_endpoint": test_ids[0],
            "last_test_endpoint": test_ids[-1],
            "rnn_training": training,
        },
        "cases": cases,
    }


def _shared_sequence_endpoints(
    samples: Sequence[Dict[str, object]],
    sequence_length: int,
    cadence_minutes: int,
) -> List[int]:
    if sequence_length < 2:
        raise ValueError("Sequence length must be at least two.")
    endpoints: List[int] = []
    for endpoint in range(sequence_length - 1, len(samples)):
        window = samples[endpoint - sequence_length + 1 : endpoint + 1]
        origins = [sample["context"]["origin"]["timestamp_dt"] for sample in window]
        if any(
            int((current - previous).total_seconds()) != cadence_minutes * 60
            for previous, current in zip(origins, origins[1:])
        ):
            continue
        values = [
            float(value)
            for sample in window
            for value in sample["features"]
        ]
        values.extend(
            float(sample["targets"][target])
            for sample in window
            for target in TARGET_NAMES
        )
        if all(math.isfinite(value) for value in values):
            endpoints.append(endpoint)
    return endpoints


def _fit_standardizer(rows: Sequence[Sequence[float]]) -> Tuple[List[float], List[float]]:
    if not rows:
        raise ValueError("Rows are required for standardization.")
    width = len(rows[0])
    if width == 0 or any(len(row) != width for row in rows):
        raise ValueError("Standardization rows must have one consistent positive width.")
    means = [sum(float(row[index]) for row in rows) / float(len(rows)) for index in range(width)]
    scales = [
        max(
            math.sqrt(
                sum((float(row[index]) - means[index]) ** 2 for row in rows)
                / float(len(rows))
            ),
            1e-6,
        )
        for index in range(width)
    ]
    return means, scales


def _transform_row(row: Sequence[float], means: Sequence[float], scales: Sequence[float]) -> List[float]:
    if len(row) != len(means) or len(row) != len(scales):
        raise ValueError("Standardization width mismatch.")
    return [
        (float(value) - float(means[index])) / float(scales[index])
        for index, value in enumerate(row)
    ]


def _inverse_transform_row(row: Sequence[float], means: Sequence[float], scales: Sequence[float]) -> List[float]:
    if len(row) != len(means) or len(row) != len(scales):
        raise ValueError("Inverse-standardization width mismatch.")
    return [
        float(value) * float(scales[index]) + float(means[index])
        for index, value in enumerate(row)
    ]


def _flatten(rows: Sequence[Sequence[float]]) -> List[float]:
    return [float(value) for row in rows for value in row]


def _predict_linear(coefficients: Sequence[float], row: Sequence[float]) -> float:
    return float(coefficients[0] + sum(weight * value for weight, value in zip(coefficients[1:], row)))


def _endpoint_id(sample: Dict[str, object]) -> str:
    origin = sample["context"]["origin"]["timestamp_dt"].isoformat()
    future = sample["context"]["future"]["timestamp_dt"].isoformat()
    return f"{origin}|{future}"


def _shared_input_record(
    samples: Sequence[Dict[str, object]],
    endpoint: int,
    sequence_length: int,
) -> str:
    window = samples[endpoint - sequence_length + 1 : endpoint + 1]
    payload = {
        "history": [
            {
                "timestamp": sample["context"]["origin"]["timestamp_dt"].isoformat(),
                "features": [float(value) for value in sample["features"]],
            }
            for sample in window
        ],
        "future_timestamp": samples[endpoint]["context"]["future"]["timestamp_dt"].isoformat(),
        "targets": {
            target: float(samples[endpoint]["targets"][target])
            for target in TARGET_NAMES
        },
    }
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def _hash_strings(values: Sequence[str]) -> str:
    digest = hashlib.sha256()
    for value in values:
        digest.update(value.encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _zeros_like(value: object) -> object:
    if isinstance(value, dict):
        return {key: _zeros_like(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_zeros_like(item) for item in value]
    return 0.0


def _adam_update(
    parameter: object,
    gradient: object,
    first_moment: object,
    second_moment: object,
    batch_count: int,
    learning_rate: float,
    beta1: float,
    beta2: float,
    epsilon: float,
    step: int,
    clip: float,
) -> None:
    if isinstance(parameter, list):
        for index in range(len(parameter)):
            if isinstance(parameter[index], list):
                _adam_update(
                    parameter[index],
                    gradient[index],
                    first_moment[index],
                    second_moment[index],
                    batch_count,
                    learning_rate,
                    beta1,
                    beta2,
                    epsilon,
                    step,
                    clip,
                )
            else:
                averaged = float(gradient[index]) / float(batch_count)
                averaged = max(-clip, min(clip, averaged))
                first_moment[index] = beta1 * float(first_moment[index]) + (1.0 - beta1) * averaged
                second_moment[index] = beta2 * float(second_moment[index]) + (1.0 - beta2) * averaged * averaged
                corrected_first = float(first_moment[index]) / (1.0 - beta1 ** step)
                corrected_second = float(second_moment[index]) / (1.0 - beta2 ** step)
                parameter[index] = float(parameter[index]) - learning_rate * corrected_first / (
                    math.sqrt(corrected_second) + epsilon
                )
        return
    raise TypeError("Adam parameters must be represented as nested lists.")
