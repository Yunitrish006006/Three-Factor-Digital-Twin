from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from digital_twin.core.public_dataset_benchmark import (
    _load_sml2010_records,
    _metric_summary,
    _read_csv_rows,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_DIR = ROOT / "outputs" / "data" / "normalized_public" / "sml2010"
DEFAULT_OUTPUT_PATH = (
    ROOT / "outputs" / "data" / "public_benchmarks" / "kalman_sml2010_filtering_comparison.json"
)
TARGETS: Mapping[str, Mapping[str, object]] = {
    "dining_temperature": {
        "unit": "degC",
        "noise_std": {"low": 0.5, "nominal": 1.0, "high": 2.0},
    },
    "room_temperature": {
        "unit": "degC",
        "noise_std": {"low": 0.5, "nominal": 1.0, "high": 2.0},
    },
    "dining_humidity": {
        "unit": "pctRH",
        "noise_std": {"low": 1.5, "nominal": 3.0, "high": 5.0},
    },
    "room_humidity": {
        "unit": "pctRH",
        "noise_std": {"low": 1.5, "nominal": 3.0, "high": 5.0},
    },
}
NOISE_PROFILES = ("low", "nominal", "high")
METHOD_NAMES = (
    "raw_noisy",
    "causal_moving_average_3",
    "linear_kalman_random_walk",
)


@dataclass(frozen=True)
class KalmanComparisonConfig:
    seed: int = 42
    split_ratio: float = 0.7
    moving_average_window: int = 3
    cadence_minutes: int = 15
    process_variance_floor: float = 1e-9


@dataclass
class ScalarRandomWalkKalman:
    process_variance: float
    measurement_variance: float
    state: float
    covariance: float

    def update(self, observation: float) -> Tuple[float, float, float]:
        predicted_state = float(self.state)
        predicted_covariance = float(self.covariance) + float(self.process_variance)
        denominator = predicted_covariance + float(self.measurement_variance)
        gain = 1.0 if denominator <= 0.0 else predicted_covariance / denominator
        innovation = float(observation) - predicted_state
        self.state = predicted_state + gain * innovation
        self.covariance = max((1.0 - gain) * predicted_covariance, 0.0)
        return self.state, innovation, gain


def run_kalman_filter_comparison(
    input_dir: Path = DEFAULT_INPUT_DIR,
    config: KalmanComparisonConfig = KalmanComparisonConfig(),
) -> Dict[str, object]:
    input_dir = Path(input_dir)
    _validate_config(config)
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
    timestamps = [row["timestamp_dt"] for row in records]
    cases: List[Dict[str, object]] = []
    for target, target_contract in TARGETS.items():
        clean_values = [float(row[target]) for row in records]
        for profile in NOISE_PROFILES:
            noise_std = float(target_contract["noise_std"][profile])
            cases.append(
                evaluate_controlled_filter_case(
                    timestamps=timestamps,
                    clean_values=clean_values,
                    target=target,
                    unit=str(target_contract["unit"]),
                    noise_profile=profile,
                    noise_std=noise_std,
                    config=config,
                )
            )

    evaluated_cases = [case for case in cases if case["status"] == "ok"]
    lowest_mae_counts = {method: 0 for method in METHOD_NAMES}
    kalman_wins_vs = {method: 0 for method in METHOD_NAMES if method != "linear_kalman_random_walk"}
    adverse_cases: List[Dict[str, object]] = []
    for case in evaluated_cases:
        winner = str(case["lowest_mae_method"])
        lowest_mae_counts[winner] += 1
        kalman_mae = float(case["metrics"]["linear_kalman_random_walk"]["mae"])
        for method in kalman_wins_vs:
            if kalman_mae < float(case["metrics"][method]["mae"]):
                kalman_wins_vs[method] += 1
        if winner != "linear_kalman_random_walk":
            adverse_cases.append(
                {
                    "target": case["target"],
                    "noise_profile": case["noise_profile"],
                    "winner": winner,
                    "winner_mae": case["metrics"][winner]["mae"],
                    "kalman_mae": case["metrics"]["linear_kalman_random_walk"]["mae"],
                }
            )

    expected_cases = len(TARGETS) * len(NOISE_PROFILES)
    parity_passed = bool(cases) and all(bool(case["data_parity"]["passed"]) for case in cases)
    complete = len(evaluated_cases) == expected_cases and parity_passed
    return {
        "study_id": "E10-KALMAN-CONTROLLED-FILTERING",
        "dataset": "SML2010",
        "evidence_class": "CONTROLLED_INJECTED_NOISE",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "COMPLETE" if complete else ("PARTIAL" if evaluated_cases else "NOT_EVALUATED"),
        "input_dir": str(input_dir),
        "input_provenance": {
            str(path.relative_to(input_dir)): {"sha256": _sha256(path), "bytes": path.stat().st_size}
            for path in required_inputs
        },
        "protocol": {
            "task": "current_time_filtering",
            "targets": list(TARGETS),
            "noise_profiles": {
                target: dict(contract["noise_std"])
                for target, contract in TARGETS.items()
            },
            "comparators": list(METHOD_NAMES),
            "state_transition": "x_k = x_(k-1) + w_k; F=1",
            "observation_model": "z_k = x_k + v_k; H=1",
            "measurement_covariance": "registered injected noise variance R=sigma^2",
            "process_covariance": "training-reference first-difference sample variance with registered floor",
            "config": asdict(config),
            "decision_rule": (
                "Completion and data parity support CLM-KF-02; Kalman superiority is not required."
            ),
        },
        "cases": cases,
        "summary": {
            "evaluated_cases": len(evaluated_cases),
            "expected_cases": expected_cases,
            "all_cases_data_parity_passed": parity_passed,
            "lowest_mae_counts": lowest_mae_counts,
            "kalman_wins_vs": kalman_wins_vs,
            "adverse_case_count": len(adverse_cases),
            "adverse_cases": adverse_cases,
        },
        "decisions": {
            "RQ-KF-01": "evaluated" if complete else "not_evaluated",
            "CLM-KF-02": "supported" if complete else "not_supported",
        },
        "claim_boundary": (
            "Fixed-seed controlled noise injected into normalized SML2010 current-time temperature and humidity records. "
            "This is not real-sensor denoising, forecasting, dense 3-D field, control, biological, or cross-site validation."
        ),
    }


def evaluate_controlled_filter_case(
    timestamps: Sequence[datetime],
    clean_values: Sequence[float],
    target: str,
    unit: str,
    noise_profile: str,
    noise_std: float,
    config: KalmanComparisonConfig = KalmanComparisonConfig(),
) -> Dict[str, object]:
    _validate_config(config)
    if len(timestamps) != len(clean_values) or len(timestamps) < 10:
        raise ValueError("Filtering comparison requires at least ten aligned timestamps and clean values.")
    if noise_std <= 0.0:
        raise ValueError("Injected noise standard deviation must be positive.")
    if any(not math.isfinite(float(value)) for value in clean_values):
        raise ValueError("Clean reference values must be finite.")
    if any(right <= left for left, right in zip(timestamps, timestamps[1:])):
        raise ValueError("Timestamps must be strictly increasing.")

    split_index = max(1, min(len(clean_values) - 1, int(len(clean_values) * config.split_ratio)))
    stream_seed = _stable_stream_seed(config.seed, target, noise_profile)
    rng = random.Random(stream_seed)
    noise = [rng.gauss(0.0, noise_std) for _ in clean_values]
    corrupted = [float(value) + delta for value, delta in zip(clean_values, noise)]
    process_variance = _training_process_variance(
        timestamps=timestamps[:split_index],
        clean_values=clean_values[:split_index],
        cadence_minutes=config.cadence_minutes,
        floor=config.process_variance_floor,
    )
    measurement_variance = noise_std * noise_std
    filtered = _run_shared_filters(
        timestamps=timestamps,
        corrupted=corrupted,
        process_variance=process_variance,
        measurement_variance=measurement_variance,
        config=config,
    )

    test_reference = [float(value) for value in clean_values[split_index:]]
    method_predictions = {
        method: [float(value) for value in filtered[method][split_index:]]
        for method in METHOD_NAMES
    }
    test_timestamps = [value.isoformat() for value in timestamps[split_index:]]
    timestamp_hash = _hash_strings(test_timestamps)
    corrupted_hash = _hash_strings(
        [f"{timestamp.isoformat()}|{value:.12g}" for timestamp, value in zip(timestamps[split_index:], corrupted[split_index:])]
    )
    reference_hash = _hash_strings(
        [f"{timestamp.isoformat()}|{value:.12g}" for timestamp, value in zip(timestamps[split_index:], test_reference)]
    )
    method_contracts = {
        method: {
            "test_timestamp_hash": timestamp_hash,
            "corrupted_observation_hash": corrupted_hash,
            "reference_target_hash": reference_hash,
            "test_samples": len(test_reference),
        }
        for method in METHOD_NAMES
    }
    parity_passed = (
        all(len(values) == len(test_reference) for values in method_predictions.values())
        and len({contract["test_timestamp_hash"] for contract in method_contracts.values()}) == 1
        and len({contract["corrupted_observation_hash"] for contract in method_contracts.values()}) == 1
        and len({contract["reference_target_hash"] for contract in method_contracts.values()}) == 1
    )
    metrics = {
        method: _metric_summary(test_reference, predictions)
        for method, predictions in method_predictions.items()
    }
    all_metrics_finite = all(
        math.isfinite(float(value))
        for method_metrics in metrics.values()
        for value in method_metrics.values()
    )
    winner = min(METHOD_NAMES, key=lambda method: float(metrics[method]["mae"]))
    innovations = [abs(float(value)) for value in filtered["innovations"][split_index:]]
    gains = [float(value) for value in filtered["gains"][split_index:]]
    actual_noise = [float(value) for value in noise[split_index:]]

    return {
        "target": target,
        "unit": unit,
        "noise_profile": noise_profile,
        "registered_noise_std": noise_std,
        "stream_seed": stream_seed,
        "status": "ok" if parity_passed and all_metrics_finite else "not_evaluated",
        "rows": {
            "total": len(clean_values),
            "train": split_index,
            "test": len(test_reference),
            "first_test_timestamp": test_timestamps[0],
            "last_test_timestamp": test_timestamps[-1],
        },
        "data_parity": {
            "passed": parity_passed,
            "method_contracts": method_contracts,
        },
        "covariance": {
            "process_variance_q": round(process_variance, 10),
            "measurement_variance_r": round(measurement_variance, 10),
        },
        "noise_diagnostics": {
            "test_mean": round(sum(actual_noise) / float(len(actual_noise)), 8),
            "test_rmse": round(math.sqrt(sum(value * value for value in actual_noise) / float(len(actual_noise))), 8),
        },
        "filter_diagnostics": {
            "segment_initializations": filtered["segment_initializations"],
            "cadence_gap_resets": filtered["cadence_gap_resets"],
            "mean_absolute_innovation": round(sum(innovations) / float(len(innovations)), 8),
            "max_absolute_innovation": round(max(innovations), 8),
            "mean_kalman_gain": round(sum(gains) / float(len(gains)), 8),
        },
        "metrics": metrics,
        "lowest_mae_method": winner,
        "kalman_mae_reduction_vs": {
            method: round(
                float(metrics[method]["mae"]) - float(metrics["linear_kalman_random_walk"]["mae"]),
                6,
            )
            for method in METHOD_NAMES
            if method != "linear_kalman_random_walk"
        },
        "preview": [
            {
                "timestamp": timestamps[index].isoformat(),
                "reference": round(float(clean_values[index]), 6),
                "corrupted": round(float(corrupted[index]), 6),
                "moving_average": round(float(filtered["causal_moving_average_3"][index]), 6),
                "kalman": round(float(filtered["linear_kalman_random_walk"][index]), 6),
            }
            for index in range(split_index, min(split_index + 12, len(clean_values)))
        ],
    }


def write_kalman_filter_comparison(
    summary: Dict[str, object],
    output_path: Path = DEFAULT_OUTPUT_PATH,
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output_path


def _run_shared_filters(
    timestamps: Sequence[datetime],
    corrupted: Sequence[float],
    process_variance: float,
    measurement_variance: float,
    config: KalmanComparisonConfig,
) -> Dict[str, object]:
    raw: List[float] = []
    moving_average: List[float] = []
    kalman_values: List[float] = []
    innovations: List[float] = []
    gains: List[float] = []
    window: List[float] = []
    filter_state: Optional[ScalarRandomWalkKalman] = None
    segment_initializations = 0
    cadence_gap_resets = 0
    expected_delta = timedelta(minutes=config.cadence_minutes)

    for index, (timestamp, observation) in enumerate(zip(timestamps, corrupted)):
        is_segment_start = index == 0 or timestamp - timestamps[index - 1] != expected_delta
        if is_segment_start:
            if index > 0:
                cadence_gap_resets += 1
            segment_initializations += 1
            window = []
            filter_state = ScalarRandomWalkKalman(
                process_variance=process_variance,
                measurement_variance=measurement_variance,
                state=float(observation),
                covariance=measurement_variance,
            )
            kalman_value = float(observation)
            innovation = 0.0
            gain = 1.0
        else:
            if filter_state is None:
                raise RuntimeError("Kalman state was not initialized.")
            kalman_value, innovation, gain = filter_state.update(float(observation))

        window.append(float(observation))
        if len(window) > config.moving_average_window:
            window.pop(0)
        raw.append(float(observation))
        moving_average.append(sum(window) / float(len(window)))
        kalman_values.append(kalman_value)
        innovations.append(innovation)
        gains.append(gain)

    return {
        "raw_noisy": raw,
        "causal_moving_average_3": moving_average,
        "linear_kalman_random_walk": kalman_values,
        "innovations": innovations,
        "gains": gains,
        "segment_initializations": segment_initializations,
        "cadence_gap_resets": cadence_gap_resets,
    }


def _training_process_variance(
    timestamps: Sequence[datetime],
    clean_values: Sequence[float],
    cadence_minutes: int,
    floor: float,
) -> float:
    expected_delta = timedelta(minutes=cadence_minutes)
    differences = [
        float(right_value) - float(left_value)
        for left_time, right_time, left_value, right_value in zip(
            timestamps,
            timestamps[1:],
            clean_values,
            clean_values[1:],
        )
        if right_time - left_time == expected_delta
    ]
    if len(differences) < 2:
        return float(floor)
    mean = sum(differences) / float(len(differences))
    variance = sum((value - mean) ** 2 for value in differences) / float(len(differences) - 1)
    return max(float(variance), float(floor))


def _validate_config(config: KalmanComparisonConfig) -> None:
    if not 0.0 < config.split_ratio < 1.0:
        raise ValueError("Split ratio must be between zero and one.")
    if config.moving_average_window != 3:
        raise ValueError("Protocol version 1.0 requires a three-record moving average window.")
    if config.cadence_minutes <= 0 or config.process_variance_floor <= 0.0:
        raise ValueError("Cadence and process variance floor must be positive.")


def _stable_stream_seed(base_seed: int, target: str, profile: str) -> int:
    digest = hashlib.sha256(f"{base_seed}|{target}|{profile}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def _hash_strings(values: Sequence[str]) -> str:
    digest = hashlib.sha256()
    for value in values:
        digest.update(value.encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
