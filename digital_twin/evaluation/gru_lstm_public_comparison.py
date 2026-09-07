from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Dict, List, Sequence, Tuple

import numpy as np

from digital_twin.core.public_dataset_benchmark import (
    _build_sml2010_response_samples,
    _load_sml2010_records,
    _metric_summary,
    _read_csv_rows,
)
from digital_twin.evaluation.rnn_public_comparison import (
    DEFAULT_HORIZONS,
    DEFAULT_INPUT_DIR,
    RAW_FEATURE_NAMES,
    TARGET_NAMES,
    RNNConfig,
    _endpoint_id,
    _fit_standardizer,
    _hash_strings,
    _inverse_transform_row,
    _shared_input_record,
    _shared_sequence_endpoints,
    _transform_row,
    run_rnn_public_comparison,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_PATH = (
    ROOT / "outputs" / "data" / "public_benchmarks" / "gru_lstm_sml2010_comparison.json"
)
METHOD_NAMES = (
    "persistence",
    "sequence_linear_regression",
    "physics_structured_readout",
    "vanilla_rnn",
    "gru",
    "lstm",
)
GATED_METHODS = ("gru", "lstm")


@dataclass(frozen=True)
class GatedComparisonConfig:
    sequence_length: int = 4
    vanilla_hidden_units: int = 6
    gru_hidden_units: int = 3
    lstm_hidden_units: int = 2
    epochs: int = 30
    batch_size: int = 32
    learning_rate: float = 0.01
    gradient_clip: float = 1.0
    seed: int = 42


class _NumpyRecurrentBase:
    def __init__(
        self,
        input_size: int,
        output_size: int,
        hidden_units: int,
        config: GatedComparisonConfig,
    ) -> None:
        if input_size <= 0 or output_size <= 0 or hidden_units <= 0:
            raise ValueError("Recurrent dimensions must be positive.")
        if config.sequence_length < 2 or config.epochs <= 0 or config.batch_size <= 0:
            raise ValueError("Invalid recurrent training configuration.")
        self.input_size = int(input_size)
        self.output_size = int(output_size)
        self.hidden_units = int(hidden_units)
        self.config = config
        self.params: Dict[str, np.ndarray] = {}
        self._initialize(np.random.default_rng(config.seed))
        self._first_moment = {name: np.zeros_like(value) for name, value in self.params.items()}
        self._second_moment = {name: np.zeros_like(value) for name, value in self.params.items()}
        self._step = 0

    def _initialize(self, rng: np.random.Generator) -> None:
        raise NotImplementedError

    def _forward(self, values: np.ndarray):
        raise NotImplementedError

    def _backward(self, cache, target: np.ndarray) -> Dict[str, np.ndarray]:
        raise NotImplementedError

    @property
    def parameter_count(self) -> int:
        return int(sum(value.size for value in self.params.values()))

    def fit(
        self,
        sequences: Sequence[Sequence[Sequence[float]]],
        targets: Sequence[Sequence[float]],
    ) -> Dict[str, object]:
        x = np.asarray(sequences, dtype=np.float64)
        y = np.asarray(targets, dtype=np.float64)
        self._validate_arrays(x, y)
        epoch_losses: List[float] = []
        started = time.perf_counter()
        for _ in range(self.config.epochs):
            squared_error = 0.0
            value_count = 0
            for start in range(0, len(x), self.config.batch_size):
                batch_x = x[start : start + self.config.batch_size]
                batch_y = y[start : start + self.config.batch_size]
                prediction, cache = self._forward(batch_x)
                difference = prediction - batch_y
                squared_error += float(np.sum(difference * difference))
                value_count += int(difference.size)
                gradients = self._backward(cache, batch_y)
                self._apply_adam(gradients)
            epoch_losses.append(squared_error / float(max(value_count, 1)))
        elapsed = time.perf_counter() - started
        finite = all(math.isfinite(value) for value in epoch_losses) and all(
            bool(np.all(np.isfinite(value))) for value in self.params.values()
        )
        return {
            "epochs": self.config.epochs,
            "samples": len(x),
            "parameter_count": self.parameter_count,
            "initial_standardized_mse": round(epoch_losses[0], 8),
            "final_standardized_mse": round(epoch_losses[-1], 8),
            "all_epoch_losses_finite": finite,
            "training_seconds": round(elapsed, 6),
        }

    def predict(self, sequence: Sequence[Sequence[float]]) -> List[float]:
        values = np.asarray(sequence, dtype=np.float64)
        if values.shape != (self.config.sequence_length, self.input_size):
            raise ValueError("Recurrent prediction sequence shape mismatch.")
        prediction, _ = self._forward(values[np.newaxis, :, :])
        if not bool(np.all(np.isfinite(prediction))):
            raise ValueError("Recurrent model produced non-finite predictions.")
        return [float(value) for value in prediction[0]]

    def predict_many(
        self,
        sequences: Sequence[Sequence[Sequence[float]]],
    ) -> List[List[float]]:
        values = np.asarray(sequences, dtype=np.float64)
        if values.ndim != 3 or values.shape[1:] != (
            self.config.sequence_length,
            self.input_size,
        ):
            raise ValueError("Recurrent batch prediction shape mismatch.")
        prediction, _ = self._forward(values)
        if not bool(np.all(np.isfinite(prediction))):
            raise ValueError("Recurrent model produced non-finite predictions.")
        return prediction.tolist()

    def _validate_arrays(self, x: np.ndarray, y: np.ndarray) -> None:
        if x.ndim != 3 or x.shape[0] == 0:
            raise ValueError("Recurrent training sequences must be a non-empty rank-three array.")
        if x.shape[1:] != (self.config.sequence_length, self.input_size):
            raise ValueError("Recurrent training sequence shape mismatch.")
        if y.shape != (x.shape[0], self.output_size):
            raise ValueError("Recurrent training target shape mismatch.")
        if not bool(np.all(np.isfinite(x))) or not bool(np.all(np.isfinite(y))):
            raise ValueError("Recurrent training values must be finite.")

    def _apply_adam(self, gradients: Dict[str, np.ndarray]) -> None:
        if set(gradients) != set(self.params):
            raise ValueError("Gradient and parameter names differ.")
        total_norm = math.sqrt(
            sum(float(np.sum(value * value)) for value in gradients.values())
        )
        scale = min(1.0, self.config.gradient_clip / max(total_norm, 1e-12))
        self._step += 1
        beta1 = 0.9
        beta2 = 0.999
        for name, parameter in self.params.items():
            gradient = gradients[name] * scale
            self._first_moment[name] = beta1 * self._first_moment[name] + (1.0 - beta1) * gradient
            self._second_moment[name] = (
                beta2 * self._second_moment[name] + (1.0 - beta2) * gradient * gradient
            )
            first_hat = self._first_moment[name] / (1.0 - beta1**self._step)
            second_hat = self._second_moment[name] / (1.0 - beta2**self._step)
            parameter -= self.config.learning_rate * first_hat / (np.sqrt(second_hat) + 1e-8)


class SimpleGRU(_NumpyRecurrentBase):
    def _initialize(self, rng: np.random.Generator) -> None:
        input_limit = 1.0 / math.sqrt(float(self.input_size))
        hidden_limit = 1.0 / math.sqrt(float(self.hidden_units))
        for gate in ("z", "r", "n"):
            self.params[f"w_x{gate}"] = rng.uniform(
                -input_limit, input_limit, (self.hidden_units, self.input_size)
            )
            self.params[f"w_h{gate}"] = rng.uniform(
                -hidden_limit, hidden_limit, (self.hidden_units, self.hidden_units)
            )
            self.params[f"b_{gate}"] = np.zeros(self.hidden_units, dtype=np.float64)
        self.params["w_hy"] = rng.uniform(
            -hidden_limit, hidden_limit, (self.output_size, self.hidden_units)
        )
        self.params["b_y"] = np.zeros(self.output_size, dtype=np.float64)

    def _forward(self, values: np.ndarray):
        hidden = np.zeros((values.shape[0], self.hidden_units), dtype=np.float64)
        steps = []
        for index in range(values.shape[1]):
            x = values[:, index, :]
            previous = hidden
            z = _sigmoid(x @ self.params["w_xz"].T + previous @ self.params["w_hz"].T + self.params["b_z"])
            r = _sigmoid(x @ self.params["w_xr"].T + previous @ self.params["w_hr"].T + self.params["b_r"])
            n = np.tanh(
                x @ self.params["w_xn"].T
                + (r * previous) @ self.params["w_hn"].T
                + self.params["b_n"]
            )
            hidden = (1.0 - z) * n + z * previous
            steps.append((x, previous, z, r, n, hidden))
        prediction = hidden @ self.params["w_hy"].T + self.params["b_y"]
        return prediction, (steps, prediction)

    def _backward(self, cache, target: np.ndarray) -> Dict[str, np.ndarray]:
        steps, prediction = cache
        gradients = {name: np.zeros_like(value) for name, value in self.params.items()}
        output_gradient = 2.0 * (prediction - target) / float(prediction.size)
        final_hidden = steps[-1][-1]
        gradients["w_hy"] = output_gradient.T @ final_hidden
        gradients["b_y"] = np.sum(output_gradient, axis=0)
        hidden_gradient = output_gradient @ self.params["w_hy"]

        for x, previous, z, r, n, _ in reversed(steps):
            n_gradient = hidden_gradient * (1.0 - z)
            z_gradient = hidden_gradient * (previous - n)
            previous_gradient = hidden_gradient * z

            n_activation_gradient = n_gradient * (1.0 - n * n)
            gradients["w_xn"] += n_activation_gradient.T @ x
            gradients["w_hn"] += n_activation_gradient.T @ (r * previous)
            gradients["b_n"] += np.sum(n_activation_gradient, axis=0)
            reset_hidden_gradient = n_activation_gradient @ self.params["w_hn"]
            r_gradient = reset_hidden_gradient * previous
            previous_gradient += reset_hidden_gradient * r

            r_activation_gradient = r_gradient * r * (1.0 - r)
            gradients["w_xr"] += r_activation_gradient.T @ x
            gradients["w_hr"] += r_activation_gradient.T @ previous
            gradients["b_r"] += np.sum(r_activation_gradient, axis=0)
            previous_gradient += r_activation_gradient @ self.params["w_hr"]

            z_activation_gradient = z_gradient * z * (1.0 - z)
            gradients["w_xz"] += z_activation_gradient.T @ x
            gradients["w_hz"] += z_activation_gradient.T @ previous
            gradients["b_z"] += np.sum(z_activation_gradient, axis=0)
            previous_gradient += z_activation_gradient @ self.params["w_hz"]
            hidden_gradient = previous_gradient
        return gradients


class SimpleLSTM(_NumpyRecurrentBase):
    def _initialize(self, rng: np.random.Generator) -> None:
        input_limit = 1.0 / math.sqrt(float(self.input_size))
        hidden_limit = 1.0 / math.sqrt(float(self.hidden_units))
        for gate in ("i", "f", "o", "g"):
            self.params[f"w_x{gate}"] = rng.uniform(
                -input_limit, input_limit, (self.hidden_units, self.input_size)
            )
            self.params[f"w_h{gate}"] = rng.uniform(
                -hidden_limit, hidden_limit, (self.hidden_units, self.hidden_units)
            )
            self.params[f"b_{gate}"] = np.zeros(self.hidden_units, dtype=np.float64)
        self.params["b_f"].fill(1.0)
        self.params["w_hy"] = rng.uniform(
            -hidden_limit, hidden_limit, (self.output_size, self.hidden_units)
        )
        self.params["b_y"] = np.zeros(self.output_size, dtype=np.float64)

    def _forward(self, values: np.ndarray):
        hidden = np.zeros((values.shape[0], self.hidden_units), dtype=np.float64)
        cell = np.zeros_like(hidden)
        steps = []
        for index in range(values.shape[1]):
            x = values[:, index, :]
            previous_hidden = hidden
            previous_cell = cell
            input_gate = _sigmoid(
                x @ self.params["w_xi"].T + previous_hidden @ self.params["w_hi"].T + self.params["b_i"]
            )
            forget_gate = _sigmoid(
                x @ self.params["w_xf"].T + previous_hidden @ self.params["w_hf"].T + self.params["b_f"]
            )
            output_gate = _sigmoid(
                x @ self.params["w_xo"].T + previous_hidden @ self.params["w_ho"].T + self.params["b_o"]
            )
            candidate = np.tanh(
                x @ self.params["w_xg"].T + previous_hidden @ self.params["w_hg"].T + self.params["b_g"]
            )
            cell = forget_gate * previous_cell + input_gate * candidate
            hidden = output_gate * np.tanh(cell)
            steps.append(
                (
                    x,
                    previous_hidden,
                    previous_cell,
                    input_gate,
                    forget_gate,
                    output_gate,
                    candidate,
                    cell,
                    hidden,
                )
            )
        prediction = hidden @ self.params["w_hy"].T + self.params["b_y"]
        return prediction, (steps, prediction)

    def _backward(self, cache, target: np.ndarray) -> Dict[str, np.ndarray]:
        steps, prediction = cache
        gradients = {name: np.zeros_like(value) for name, value in self.params.items()}
        output_gradient = 2.0 * (prediction - target) / float(prediction.size)
        final_hidden = steps[-1][-1]
        gradients["w_hy"] = output_gradient.T @ final_hidden
        gradients["b_y"] = np.sum(output_gradient, axis=0)
        hidden_gradient = output_gradient @ self.params["w_hy"]
        cell_gradient = np.zeros_like(hidden_gradient)

        for (
            x,
            previous_hidden,
            previous_cell,
            input_gate,
            forget_gate,
            output_gate,
            candidate,
            cell,
            _,
        ) in reversed(steps):
            tanh_cell = np.tanh(cell)
            output_gate_gradient = hidden_gradient * tanh_cell
            total_cell_gradient = (
                cell_gradient + hidden_gradient * output_gate * (1.0 - tanh_cell * tanh_cell)
            )
            forget_gate_gradient = total_cell_gradient * previous_cell
            input_gate_gradient = total_cell_gradient * candidate
            candidate_gradient = total_cell_gradient * input_gate
            cell_gradient = total_cell_gradient * forget_gate

            activations = {
                "i": input_gate_gradient * input_gate * (1.0 - input_gate),
                "f": forget_gate_gradient * forget_gate * (1.0 - forget_gate),
                "o": output_gate_gradient * output_gate * (1.0 - output_gate),
                "g": candidate_gradient * (1.0 - candidate * candidate),
            }
            previous_hidden_gradient = np.zeros_like(previous_hidden)
            for gate, activation_gradient in activations.items():
                gradients[f"w_x{gate}"] += activation_gradient.T @ x
                gradients[f"w_h{gate}"] += activation_gradient.T @ previous_hidden
                gradients[f"b_{gate}"] += np.sum(activation_gradient, axis=0)
                previous_hidden_gradient += activation_gradient @ self.params[f"w_h{gate}"]
            hidden_gradient = previous_hidden_gradient
        return gradients


def run_gru_lstm_public_comparison(
    input_dir: Path = DEFAULT_INPUT_DIR,
    horizons: Sequence[int] = DEFAULT_HORIZONS,
    config: GatedComparisonConfig = GatedComparisonConfig(),
    cadence_minutes: int = 15,
) -> Dict[str, object]:
    input_dir = Path(input_dir)
    normalized_horizons = tuple(sorted({int(value) for value in horizons if int(value) > 0}))
    if not normalized_horizons:
        raise ValueError("At least one positive horizon is required.")
    vanilla_config = RNNConfig(
        sequence_length=config.sequence_length,
        hidden_units=config.vanilla_hidden_units,
        epochs=config.epochs,
        batch_size=config.batch_size,
        learning_rate=config.learning_rate,
        gradient_clip=config.gradient_clip,
        seed=config.seed,
    )
    baseline = run_rnn_public_comparison(
        input_dir=input_dir,
        horizons=normalized_horizons,
        config=vanilla_config,
        cadence_minutes=cadence_minutes,
    )
    required_inputs = (
        input_dir / "corner_sensor_timeseries.csv",
        input_dir / "outdoor_environment.csv",
        input_dir / "auxiliary_features.csv",
    )
    records = _load_sml2010_records(
        _read_csv_rows(required_inputs[0]),
        _read_csv_rows(required_inputs[1]),
        _read_csv_rows(required_inputs[2]),
    )
    baseline_cases = {
        (int(case["horizon_minutes"]), str(case["target"])): case
        for case in baseline["cases"]
        if case["status"] == "ok"
    }
    baseline_audits = {
        int(audit["horizon_minutes"]): audit
        for audit in baseline["data_parity"]["horizon_audits"]
    }

    cases: List[Dict[str, object]] = []
    horizon_audits: List[Dict[str, object]] = []
    for horizon in normalized_horizons:
        samples = _build_sml2010_response_samples(records, horizon, task_id="S2")
        endpoints = _shared_sequence_endpoints(samples, config.sequence_length, cadence_minutes)
        if len(endpoints) < 8:
            continue
        split_index = max(1, min(len(endpoints) - 1, int(len(endpoints) * 0.7)))
        train_endpoints = endpoints[:split_index]
        test_endpoints = endpoints[split_index:]
        raw_rows = [[float(value) for value in sample["features"]] for sample in samples]
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
        sequences = {
            endpoint: raw_standardized[endpoint - config.sequence_length + 1 : endpoint + 1]
            for endpoint in endpoints
        }
        target_matrix = [
            [float(samples[endpoint]["targets"][target]) for target in TARGET_NAMES]
            for endpoint in train_endpoints
        ]
        target_means, target_scales = _fit_standardizer(target_matrix)
        standardized_targets = [
            _transform_row(row, target_means, target_scales) for row in target_matrix
        ]

        gru = SimpleGRU(
            len(RAW_FEATURE_NAMES),
            len(TARGET_NAMES),
            config.gru_hidden_units,
            config,
        )
        lstm = SimpleLSTM(
            len(RAW_FEATURE_NAMES),
            len(TARGET_NAMES),
            config.lstm_hidden_units,
            config,
        )
        training_sequences = [sequences[endpoint] for endpoint in train_endpoints]
        gru_training = gru.fit(training_sequences, standardized_targets)
        lstm_training = lstm.fit(training_sequences, standardized_targets)
        test_sequences = [sequences[endpoint] for endpoint in test_endpoints]
        gru_matrix = [
            _inverse_transform_row(row, target_means, target_scales)
            for row in gru.predict_many(test_sequences)
        ]
        lstm_matrix = [
            _inverse_transform_row(row, target_means, target_scales)
            for row in lstm.predict_many(test_sequences)
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
        prior_audit = baseline_audits[horizon]
        parity_passed = (
            bool(prior_audit["parity_passed"])
            and prior_audit["endpoint_hash"] == endpoint_hash
            and prior_audit["train_endpoint_hash"] == train_hash
            and prior_audit["test_endpoint_hash"] == test_hash
            and prior_audit["train_input_hash"] == train_input_hash
            and prior_audit["test_input_hash"] == test_input_hash
            and bool(gru_training["all_epoch_losses_finite"])
            and bool(lstm_training["all_epoch_losses_finite"])
        )
        contracts = dict(prior_audit["method_data_contracts"])
        for method in GATED_METHODS:
            contracts[method] = {
                "shared_train_endpoint_hash": train_hash,
                "shared_test_endpoint_hash": test_hash,
                "shared_train_input_hash": train_input_hash,
                "shared_test_input_hash": test_input_hash,
            }
        horizon_audits.append(
            {
                "horizon_minutes": horizon,
                "parity_passed": parity_passed,
                "eligible_endpoints": len(endpoints),
                "train_samples": len(train_endpoints),
                "test_samples": len(test_endpoints),
                "endpoint_hash": endpoint_hash,
                "train_endpoint_hash": train_hash,
                "test_endpoint_hash": test_hash,
                "train_input_hash": train_input_hash,
                "test_input_hash": test_input_hash,
                "method_data_contracts": contracts,
                "training": {"gru": gru_training, "lstm": lstm_training},
            }
        )

        for target_index, target in enumerate(TARGET_NAMES):
            actual = [float(samples[endpoint]["targets"][target]) for endpoint in test_endpoints]
            prior_case = baseline_cases[(horizon, target)]
            metrics = dict(prior_case["metrics"])
            metrics["gru"] = _metric_summary(actual, [row[target_index] for row in gru_matrix])
            metrics["lstm"] = _metric_summary(actual, [row[target_index] for row in lstm_matrix])
            vanilla_mae = float(metrics["vanilla_rnn"]["mae"])
            relative_reduction = {
                method: _relative_reduction(vanilla_mae, float(metrics[method]["mae"]))
                for method in GATED_METHODS
            }
            cases.append(
                {
                    "target": target,
                    "horizon_minutes": horizon,
                    "status": "ok" if parity_passed else "parity_failure",
                    "eligible_endpoints": len(endpoints),
                    "train_samples": len(train_endpoints),
                    "test_samples": len(test_endpoints),
                    "shared_endpoint_hash": endpoint_hash,
                    "shared_train_endpoint_hash": train_hash,
                    "shared_test_endpoint_hash": test_hash,
                    "shared_train_input_hash": train_input_hash,
                    "shared_test_input_hash": test_input_hash,
                    "metrics": metrics,
                    "relative_mae_reduction_vs_vanilla_percent": relative_reduction,
                    "lowest_mae_method": min(
                        METHOD_NAMES,
                        key=lambda method: (float(metrics[method]["mae"]), method),
                    ),
                }
            )

    evaluated_cases = [case for case in cases if case["status"] == "ok"]
    expected_cases = len(normalized_horizons) * len(TARGET_NAMES)
    lowest_counts = {method: 0 for method in METHOD_NAMES}
    gated_wins = {method: 0 for method in GATED_METHODS}
    reductions = {method: [] for method in GATED_METHODS}
    for case in evaluated_cases:
        lowest_counts[str(case["lowest_mae_method"])] += 1
        vanilla_mae = float(case["metrics"]["vanilla_rnn"]["mae"])
        for method in GATED_METHODS:
            if float(case["metrics"][method]["mae"]) < vanilla_mae:
                gated_wins[method] += 1
            reductions[method].append(
                float(case["relative_mae_reduction_vs_vanilla_percent"][method])
            )
    median_reductions = {
        method: round(float(median(values)), 6) if values else None
        for method, values in reductions.items()
    }

    vanilla_parameters = (
        config.vanilla_hidden_units * len(RAW_FEATURE_NAMES)
        + config.vanilla_hidden_units * config.vanilla_hidden_units
        + config.vanilla_hidden_units
        + len(TARGET_NAMES) * config.vanilla_hidden_units
        + len(TARGET_NAMES)
    )
    gru_parameters = _gru_parameter_count(
        len(RAW_FEATURE_NAMES), config.gru_hidden_units, len(TARGET_NAMES)
    )
    lstm_parameters = _lstm_parameter_count(
        len(RAW_FEATURE_NAMES), config.lstm_hidden_units, len(TARGET_NAMES)
    )
    parameter_budget_passed = all(
        abs(count - vanilla_parameters) / float(vanilla_parameters) <= 0.15
        for count in (gru_parameters, lstm_parameters)
    )
    parity_passed = (
        len(horizon_audits) == len(normalized_horizons)
        and all(bool(audit["parity_passed"]) for audit in horizon_audits)
    )
    complete = (
        baseline["status"] == "COMPLETE"
        and len(evaluated_cases) == expected_cases
        and parity_passed
        and parameter_budget_passed
    )
    forwarded = [
        method
        for method in GATED_METHODS
        if complete
        and gated_wins[method] >= 8
        and median_reductions[method] is not None
        and float(median_reductions[method]) > 0.0
    ]
    return {
        "study_id": "E9-GRU-LSTM-SIMPLE-SAME-DATA",
        "dataset": "SML2010",
        "task_id": "S2",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "COMPLETE" if complete else "NOT_EVALUATED",
        "input_dir": str(input_dir),
        "input_provenance": baseline["input_provenance"],
        "protocol": {
            "horizons_minutes": list(normalized_horizons),
            "targets": list(TARGET_NAMES),
            "split": "chronological_70_30",
            "cadence_minutes": cadence_minutes,
            "shared_history_records": config.sequence_length,
            "comparators": list(METHOD_NAMES),
            "configuration": asdict(config),
            "parameter_counts": {
                "vanilla_rnn": vanilla_parameters,
                "gru": gru_parameters,
                "lstm": lstm_parameters,
            },
            "parameter_budget_within_15_percent": parameter_budget_passed,
            "candidate_gate": {
                "minimum_mae_wins_vs_vanilla_over_12": 8,
                "median_relative_mae_reduction_must_be_positive": True,
            },
            "test_based_tuning": False,
        },
        "data_parity": {
            "all_horizons_passed": parity_passed,
            "horizon_audits": horizon_audits,
        },
        "cases": cases,
        "summary": {
            "evaluated_cases": len(evaluated_cases),
            "expected_cases": expected_cases,
            "lowest_mae_counts": lowest_counts,
            "mae_wins_vs_vanilla_rnn": gated_wins,
            "median_relative_mae_reduction_vs_vanilla_percent": median_reductions,
            "forwarded_candidates": forwarded,
        },
        "decisions": {
            "EQ-RNNGATE-01": "evaluated" if complete else "not_evaluated",
            "H-RNNGATE-01": "supported" if forwarded else "not_supported",
        },
        "claim_boundary": (
            "Single-seed same-data SML2010 S2 temporal comparison only. It is not dense 3-D, "
            "cross-building, computer-enclosure, physical-sensor, PID-control, or general "
            "recurrent-architecture evidence."
        ),
    }


def write_gru_lstm_public_comparison(
    result: Dict[str, object],
    output_path: Path = DEFAULT_OUTPUT_PATH,
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return output_path


def _sigmoid(value: np.ndarray) -> np.ndarray:
    clipped = np.clip(value, -40.0, 40.0)
    return 1.0 / (1.0 + np.exp(-clipped))


def _relative_reduction(before: float, after: float) -> float:
    if abs(before) <= 1e-12:
        return 0.0 if abs(after) <= 1e-12 else -100.0
    return round((before - after) / before * 100.0, 6)


def _gru_parameter_count(input_size: int, hidden_units: int, output_size: int) -> int:
    return int(
        3 * (hidden_units * input_size + hidden_units * hidden_units + hidden_units)
        + output_size * hidden_units
        + output_size
    )


def _lstm_parameter_count(input_size: int, hidden_units: int, output_size: int) -> int:
    return int(
        4 * (hidden_units * input_size + hidden_units * hidden_units + hidden_units)
        + output_size * hidden_units
        + output_size
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
