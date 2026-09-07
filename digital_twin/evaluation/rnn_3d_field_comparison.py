from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from digital_twin.core.demo import compare_fields, synthesize_sensor_observations
from digital_twin.core.entities import Vector3
from digital_twin.core.scenarios import Scenario, build_validation_scenarios
from digital_twin.evaluation.rnn_public_comparison import RNNConfig, VanillaElmanRNN
from digital_twin.neural.hybrid_residual import (
    SpectralDenoisingConfig,
    _field_point_from_index,
    _selected_field_indices,
    _truth_and_estimated_results,
    build_residual_dataset,
    evaluate_hybrid_model_on_scenario,
    train_hybrid_residual_model,
)
from digital_twin.physics.baselines import build_idw_field
from digital_twin.physics.model import FieldGrid, METRICS


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_PATH = ROOT / "outputs" / "data" / "rnn_3d_field_comparison.json"
METHOD_NAMES = ("idw", "base_model", "pure_rnn", "loo_hybrid")
DEVICE_ORDER = ("ac_main", "window_main", "light_main")
DEFAULT_RNN_CONFIG = RNNConfig(
    sequence_length=8,
    hidden_units=8,
    epochs=40,
    batch_size=32,
    learning_rate=0.01,
    gradient_clip=1.0,
    seed=42,
)
INPUT_FEATURE_NAMES = (
    "sensor_x_norm",
    "sensor_y_norm",
    "sensor_z_norm",
    "sensor_temperature",
    "sensor_humidity",
    "sensor_illuminance",
    "query_x_norm",
    "query_y_norm",
    "query_z_norm",
    "room_base_temperature",
    "room_base_humidity",
    "room_base_illuminance",
    "outdoor_temperature",
    "outdoor_humidity",
    "sunlight_illuminance",
    "daylight_factor",
    "elapsed_norm",
    "ac_main_activation",
    "ac_main_power",
    "window_main_activation",
    "window_main_power",
    "light_main_activation",
    "light_main_power",
)
FORBIDDEN_INPUT_TERMS = ("estimated", "physics", "residual", "truth", "idw")


@dataclass(frozen=True)
class PureRNNFieldDataset:
    feature_names: Tuple[str, ...]
    sensor_names: Tuple[str, ...]
    sequences: List[List[List[float]]]
    targets: List[List[float]]
    query_ids: List[str]
    scenario_names: List[str]


@dataclass
class PureRNNFieldModel:
    network: VanillaElmanRNN
    feature_names: Tuple[str, ...]
    sensor_names: Tuple[str, ...]
    input_means: List[float]
    input_scales: List[float]
    target_means: List[float]
    target_scales: List[float]

    def predict(self, sequence: Sequence[Sequence[float]]) -> List[float]:
        transformed = [
            _transform_row(row, self.input_means, self.input_scales)
            for row in sequence
        ]
        standardized = self.network.predict(transformed)
        return _inverse_transform_row(standardized, self.target_means, self.target_scales)


def build_pure_rnn_field_dataset(
    scenarios: Sequence[Scenario],
    max_points_per_scenario: Optional[int] = 96,
) -> PureRNNFieldDataset:
    sequences: List[List[List[float]]] = []
    targets: List[List[float]] = []
    query_ids: List[str] = []
    scenario_names: List[str] = []
    expected_sensor_names: Optional[Tuple[str, ...]] = None

    for scenario in scenarios:
        truth_result, _estimated_result = _truth_and_estimated_results_for_scenario(scenario)
        observed_sensors = synthesize_sensor_observations(
            truth_result.sensor_predictions,
            scenario.sensors,
        )
        total_points = len(truth_result.field.values["temperature"])
        if max_points_per_scenario is None:
            selected_indices = list(range(total_points))
        else:
            selected_indices = _selected_field_indices(
                truth_result.field,
                max_points_per_scenario,
            )
        dataset = _dataset_from_precomputed(
            scenario=scenario,
            truth_field=truth_result.field,
            observed_sensors=observed_sensors,
            selected_indices=selected_indices,
        )
        if expected_sensor_names is None:
            expected_sensor_names = dataset.sensor_names
        elif dataset.sensor_names != expected_sensor_names:
            raise ValueError("All pure RNN scenarios must use the same ordered sensor names.")
        sequences.extend(dataset.sequences)
        targets.extend(dataset.targets)
        query_ids.extend(dataset.query_ids)
        scenario_names.extend(dataset.scenario_names)

    return PureRNNFieldDataset(
        feature_names=INPUT_FEATURE_NAMES,
        sensor_names=expected_sensor_names or tuple(),
        sequences=sequences,
        targets=targets,
        query_ids=query_ids,
        scenario_names=scenario_names,
    )


def build_sensor_token_sequence(
    scenario: Scenario,
    observed_sensors: Mapping[str, Mapping[str, float]],
    query_point: Vector3,
) -> List[List[float]]:
    sensors = [sensor for sensor in scenario.sensors if sensor.role == "input"]
    if len(sensors) != 8:
        raise ValueError(f"Pure RNN requires exactly eight input sensors, found {len(sensors)}.")
    devices = {device.name: device for device in scenario.devices}
    room = scenario.room
    environment = scenario.environment
    query_context = [
        query_point.x / max(room.width, 1e-9),
        query_point.y / max(room.length, 1e-9),
        query_point.z / max(room.height, 1e-9),
        room.base_temperature,
        room.base_humidity,
        room.base_illuminance,
        environment.outdoor_temperature,
        environment.outdoor_humidity,
        environment.sunlight_illuminance,
        environment.daylight_factor,
        min(max(scenario.elapsed_minutes / 120.0, 0.0), 1.5),
    ]
    for device_name in DEVICE_ORDER:
        device = devices.get(device_name)
        query_context.extend(
            [
                0.0 if device is None else float(device.activation),
                0.0 if device is None else float(device.power),
            ]
        )

    sequence = []
    for sensor in sensors:
        if sensor.name not in observed_sensors:
            raise ValueError(f"Missing pure RNN observation for sensor {sensor.name}.")
        observation = observed_sensors[sensor.name]
        sequence.append(
            [
                sensor.position.x / max(room.width, 1e-9),
                sensor.position.y / max(room.length, 1e-9),
                sensor.position.z / max(room.height, 1e-9),
                float(observation["temperature"]),
                float(observation["humidity"]),
                float(observation["illuminance"]),
            ]
            + query_context
        )
    if any(len(row) != len(INPUT_FEATURE_NAMES) for row in sequence):
        raise ValueError("Pure RNN input feature width mismatch.")
    return sequence


def train_pure_rnn_field_model(
    dataset: PureRNNFieldDataset,
    config: RNNConfig = DEFAULT_RNN_CONFIG,
) -> Tuple[PureRNNFieldModel, Dict[str, object]]:
    if not dataset.sequences or len(dataset.sequences) != len(dataset.targets):
        raise ValueError("Pure RNN field training requires aligned non-empty sequences and targets.")
    if len(dataset.sensor_names) != config.sequence_length:
        raise ValueError("Pure RNN sequence length must match the ordered sensor count.")
    if any(term in name.lower() for name in dataset.feature_names for term in FORBIDDEN_INPUT_TERMS):
        raise ValueError("Pure RNN input contract contains a forbidden physics/truth feature.")

    token_rows = [row for sequence in dataset.sequences for row in sequence]
    input_means, input_scales = _fit_standardizer(token_rows)
    target_means, target_scales = _fit_standardizer(dataset.targets)
    standardized_sequences = [
        [_transform_row(row, input_means, input_scales) for row in sequence]
        for sequence in dataset.sequences
    ]
    standardized_targets = [
        _transform_row(row, target_means, target_scales)
        for row in dataset.targets
    ]
    network = VanillaElmanRNN(
        input_size=len(dataset.feature_names),
        output_size=len(METRICS),
        config=config,
    )
    training = network.fit(standardized_sequences, standardized_targets)
    model = PureRNNFieldModel(
        network=network,
        feature_names=dataset.feature_names,
        sensor_names=dataset.sensor_names,
        input_means=input_means,
        input_scales=input_scales,
        target_means=target_means,
        target_scales=target_scales,
    )
    return model, training


def predict_pure_rnn_field(
    model: PureRNNFieldModel,
    dataset: PureRNNFieldDataset,
    template: FieldGrid,
) -> FieldGrid:
    expected_points = len(template.values["temperature"])
    if len(dataset.sequences) != expected_points:
        raise ValueError("Full-field RNN dataset must contain one sequence per grid point.")
    predictions = [model.predict(sequence) for sequence in dataset.sequences]
    return FieldGrid(
        resolution=template.resolution,
        x_coords=list(template.x_coords),
        y_coords=list(template.y_coords),
        z_coords=list(template.z_coords),
        values={
            metric: [float(row[index]) for row in predictions]
            for index, metric in enumerate(METRICS)
        },
    )


def run_rnn_3d_field_comparison(
    scenarios: Optional[Sequence[Scenario]] = None,
    max_points_per_scenario: int = 96,
    rnn_config: RNNConfig = DEFAULT_RNN_CONFIG,
    hybrid_hidden_dim: int = 10,
    hybrid_epochs: int = 80,
    hybrid_learning_rate: float = 0.018,
    hybrid_l2: float = 1e-5,
) -> Dict[str, object]:
    scenario_list = list(scenarios or build_validation_scenarios())
    if len(scenario_list) < 2:
        raise ValueError("Pure RNN LOO comparison requires at least two scenarios.")
    if rnn_config.sequence_length != 8:
        raise ValueError("Registered pure RNN sequence length is eight sensors.")

    prepared = {
        scenario.name: _prepare_scenario(scenario, max_points_per_scenario)
        for scenario in scenario_list
    }
    spectral_denoising = SpectralDenoisingConfig(
        enabled=True,
        timeline_steps=9,
        keep_frequency_ratio=0.35,
        min_keep_bins=1,
        metrics=("temperature", "humidity"),
    )
    folds: List[Dict[str, object]] = []

    for fold_index, holdout_scenario in enumerate(scenario_list):
        train_scenarios = [
            scenario for scenario in scenario_list if scenario.name != holdout_scenario.name
        ]
        training_dataset = _combine_datasets(
            [prepared[scenario.name]["training_dataset"] for scenario in train_scenarios]
        )
        test_dataset = prepared[holdout_scenario.name]["full_dataset"]
        fold_config = RNNConfig(
            sequence_length=rnn_config.sequence_length,
            hidden_units=rnn_config.hidden_units,
            epochs=rnn_config.epochs,
            batch_size=rnn_config.batch_size,
            learning_rate=rnn_config.learning_rate,
            gradient_clip=rnn_config.gradient_clip,
            seed=rnn_config.seed + fold_index * 97,
        )
        rnn_model, rnn_training = train_pure_rnn_field_model(training_dataset, fold_config)
        pure_rnn_field = predict_pure_rnn_field(
            rnn_model,
            test_dataset,
            prepared[holdout_scenario.name]["truth_field"],
        )

        hybrid_train_dataset = build_residual_dataset(
            train_scenarios,
            max_points_per_scenario=max_points_per_scenario,
            spectral_denoising=spectral_denoising,
        )
        hybrid_test_dataset = build_residual_dataset(
            [holdout_scenario],
            max_points_per_scenario=max_points_per_scenario,
        )
        hybrid_model, hybrid_training = train_hybrid_residual_model(
            train_dataset=hybrid_train_dataset,
            test_dataset=hybrid_test_dataset,
            hidden_dim=hybrid_hidden_dim,
            epochs=hybrid_epochs,
            learning_rate=hybrid_learning_rate,
            l2=hybrid_l2,
            seed=rnn_config.seed + fold_index * 97,
        )
        hybrid_evaluation = evaluate_hybrid_model_on_scenario(
            hybrid_model,
            holdout_scenario,
        )

        truth_field = prepared[holdout_scenario.name]["truth_field"]
        method_metrics = {
            "idw": compare_fields(prepared[holdout_scenario.name]["idw_field"], truth_field),
            "base_model": compare_fields(prepared[holdout_scenario.name]["base_field"], truth_field),
            "pure_rnn": compare_fields(pure_rnn_field, truth_field),
            "loo_hybrid": dict(hybrid_evaluation["hybrid_field_mae"]),
        }
        training_point_hash = _hash_strings(training_dataset.query_ids)
        parity_passed = (
            len(training_dataset.sequences)
            == len(hybrid_train_dataset.features)
            == len(train_scenarios) * min(max_points_per_scenario, len(truth_field.values["temperature"]))
            and len(test_dataset.sequences) == len(truth_field.values["temperature"])
            and all(
                math.isfinite(float(method_metrics[method][metric]))
                for method in METHOD_NAMES
                for metric in METRICS
            )
            and bool(rnn_training["all_epoch_losses_finite"])
        )
        lowest_by_metric = {
            metric: min(
                METHOD_NAMES,
                key=lambda method: (float(method_metrics[method][metric]), method),
            )
            for metric in METRICS
        }
        shared_contract = {
            "heldout_sparse_input_hash": prepared[holdout_scenario.name]["sparse_input_hash"],
            "heldout_query_grid_hash": prepared[holdout_scenario.name]["query_grid_hash"],
            "heldout_truth_field_hash": prepared[holdout_scenario.name]["truth_field_hash"],
            "training_point_hash": training_point_hash,
        }
        folds.append(
            {
                "holdout_scenario": holdout_scenario.name,
                "train_scenarios": [scenario.name for scenario in train_scenarios],
                "train_samples_per_learned_method": len(training_dataset.sequences),
                "test_grid_points": len(test_dataset.sequences),
                "sensor_names": list(training_dataset.sensor_names),
                "rnn_seed": fold_config.seed,
                "rnn_training": rnn_training,
                "hybrid_training": hybrid_training,
                "field_mae": method_metrics,
                "lowest_mae_method": lowest_by_metric,
                "data_parity": {
                    "passed": parity_passed,
                    "shared_contract": shared_contract,
                    "method_contracts": {
                        method: dict(shared_contract) for method in METHOD_NAMES
                    },
                },
            }
        )

    complete_folds = [fold for fold in folds if bool(fold["data_parity"]["passed"])]
    average_field_mae = {
        method: {
            metric: round(
                sum(float(fold["field_mae"][method][metric]) for fold in folds)
                / float(len(folds)),
                6,
            )
            for metric in METRICS
        }
        for method in METHOD_NAMES
    }
    lowest_mae_counts = {method: 0 for method in METHOD_NAMES}
    for fold in folds:
        for metric in METRICS:
            lowest_mae_counts[str(fold["lowest_mae_method"][metric])] += 1
    average_lowest_by_metric = {
        metric: min(
            METHOD_NAMES,
            key=lambda method: (float(average_field_mae[method][metric]), method),
        )
        for metric in METRICS
    }
    expected_fold_count = len(scenario_list)
    complete = len(complete_folds) == expected_fold_count
    return {
        "study_id": "E1-RNN-3D-FIELD-SAME-TASK",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "COMPLETE" if complete else ("PARTIAL" if complete_folds else "NOT_EVALUATED"),
        "evidence_class": "CONTROLLED_SYNTHETIC_FULL_FIELD",
        "protocol": {
            "scenario_names": [scenario.name for scenario in scenario_list],
            "fold_strategy": "leave_one_scenario_out",
            "expected_folds": expected_fold_count,
            "training_points_per_scenario": max_points_per_scenario,
            "test_grid_points_per_scenario": len(prepared[scenario_list[0].name]["full_dataset"].sequences),
            "comparators": list(METHOD_NAMES),
            "pure_rnn": asdict(rnn_config),
            "pure_rnn_input_feature_names": list(INPUT_FEATURE_NAMES),
            "pure_rnn_forbidden_input_terms": list(FORBIDDEN_INPUT_TERMS),
            "sensor_order": list(prepared[scenario_list[0].name]["training_dataset"].sensor_names),
            "hybrid": {
                "hidden_dim": hybrid_hidden_dim,
                "epochs": hybrid_epochs,
                "learning_rate": hybrid_learning_rate,
                "l2": hybrid_l2,
                "spectral_denoising": spectral_denoising.to_dict(),
            },
            "decision_rule": "Comparison completeness and parity, not pure RNN superiority.",
        },
        "data_parity": {
            "all_folds_passed": complete,
            "passed_folds": len(complete_folds),
            "expected_folds": expected_fold_count,
            "shared_rule": (
                "All methods use the same held-out scenario, eight sparse observations, query grid, "
                "dense synthetic truth, and field-MAE function; both learned methods use the same "
                "seven training scenarios and deterministic point-selection rule."
            ),
        },
        "folds": folds,
        "summary": {
            "average_field_mae": average_field_mae,
            "average_lowest_mae_method": average_lowest_by_metric,
            "lowest_mae_counts_over_24_fold_metrics": lowest_mae_counts,
            "pure_rnn_reduction_percent_vs": {
                method: {
                    metric: round(
                        _percent_reduction(
                            average_field_mae[method][metric],
                            average_field_mae["pure_rnn"][metric],
                        ),
                        2,
                    )
                    for metric in METRICS
                }
                for method in METHOD_NAMES
                if method != "pure_rnn"
            },
        },
        "decisions": {
            "RQ-RNN3D-01": "evaluated" if complete else "not_evaluated",
            "CLM-RNN3D-01": "supported" if complete else "not_supported",
        },
        "claim_boundary": (
            "Same-task leave-one-scenario-out comparison on eight canonical controlled synthetic "
            "scenarios only. It is not measured dense 3-D truth, cross-room validation, production "
            "RNN integration, or proof of recurrent-model superiority."
        ),
    }


def write_rnn_3d_field_comparison(
    summary: Mapping[str, object],
    output_path: Path = DEFAULT_OUTPUT_PATH,
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return output_path


def _truth_and_estimated_results_for_scenario(scenario: Scenario):
    from digital_twin.physics.model import DigitalTwinModel

    return _truth_and_estimated_results(DigitalTwinModel(), scenario)


def _prepare_scenario(scenario: Scenario, max_points_per_scenario: int) -> Dict[str, object]:
    truth_result, estimated_result = _truth_and_estimated_results_for_scenario(scenario)
    observed_sensors = synthesize_sensor_observations(
        truth_result.sensor_predictions,
        scenario.sensors,
    )
    selected_indices = _selected_field_indices(
        truth_result.field,
        max_points_per_scenario,
    )
    training_dataset = _dataset_from_precomputed(
        scenario,
        truth_result.field,
        observed_sensors,
        selected_indices,
    )
    full_dataset = _dataset_from_precomputed(
        scenario,
        truth_result.field,
        observed_sensors,
        list(range(len(truth_result.field.values["temperature"]))),
    )
    idw_field = build_idw_field(
        room=scenario.room,
        sensors=scenario.sensors,
        observed_sensors=observed_sensors,
        resolution=scenario.resolution,
    )
    return {
        "truth_field": truth_result.field,
        "base_field": estimated_result.field,
        "idw_field": idw_field,
        "training_dataset": training_dataset,
        "full_dataset": full_dataset,
        "sparse_input_hash": _scenario_input_hash(scenario, observed_sensors),
        "query_grid_hash": _query_grid_hash(truth_result.field),
        "truth_field_hash": _truth_field_hash(truth_result.field),
    }


def _dataset_from_precomputed(
    scenario: Scenario,
    truth_field: FieldGrid,
    observed_sensors: Mapping[str, Mapping[str, float]],
    selected_indices: Sequence[int],
) -> PureRNNFieldDataset:
    sensors = tuple(sensor.name for sensor in scenario.sensors if sensor.role == "input")
    sequences: List[List[List[float]]] = []
    targets: List[List[float]] = []
    query_ids: List[str] = []
    for index in selected_indices:
        point = _field_point_from_index(truth_field, int(index))
        sequences.append(build_sensor_token_sequence(scenario, observed_sensors, point))
        targets.append([float(truth_field.values[metric][index]) for metric in METRICS])
        query_ids.append(f"{scenario.name}|{int(index)}")
    return PureRNNFieldDataset(
        feature_names=INPUT_FEATURE_NAMES,
        sensor_names=sensors,
        sequences=sequences,
        targets=targets,
        query_ids=query_ids,
        scenario_names=[scenario.name for _ in selected_indices],
    )


def _combine_datasets(datasets: Sequence[PureRNNFieldDataset]) -> PureRNNFieldDataset:
    if not datasets:
        raise ValueError("At least one pure RNN field dataset is required.")
    feature_names = datasets[0].feature_names
    sensor_names = datasets[0].sensor_names
    if any(
        dataset.feature_names != feature_names or dataset.sensor_names != sensor_names
        for dataset in datasets
    ):
        raise ValueError("Pure RNN field datasets have incompatible contracts.")
    return PureRNNFieldDataset(
        feature_names=feature_names,
        sensor_names=sensor_names,
        sequences=[sequence for dataset in datasets for sequence in dataset.sequences],
        targets=[target for dataset in datasets for target in dataset.targets],
        query_ids=[query_id for dataset in datasets for query_id in dataset.query_ids],
        scenario_names=[name for dataset in datasets for name in dataset.scenario_names],
    )


def _fit_standardizer(rows: Sequence[Sequence[float]]) -> Tuple[List[float], List[float]]:
    if not rows:
        raise ValueError("Rows are required for pure RNN standardization.")
    width = len(rows[0])
    if width <= 0 or any(len(row) != width for row in rows):
        raise ValueError("Pure RNN standardization rows require one consistent width.")
    means = [
        sum(float(row[index]) for row in rows) / float(len(rows))
        for index in range(width)
    ]
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


def _transform_row(
    row: Sequence[float],
    means: Sequence[float],
    scales: Sequence[float],
) -> List[float]:
    if len(row) != len(means) or len(row) != len(scales):
        raise ValueError("Pure RNN standardization width mismatch.")
    return [
        (float(value) - float(means[index])) / float(scales[index])
        for index, value in enumerate(row)
    ]


def _inverse_transform_row(
    row: Sequence[float],
    means: Sequence[float],
    scales: Sequence[float],
) -> List[float]:
    if len(row) != len(means) or len(row) != len(scales):
        raise ValueError("Pure RNN inverse-standardization width mismatch.")
    return [
        float(value) * float(scales[index]) + float(means[index])
        for index, value in enumerate(row)
    ]


def _scenario_input_hash(
    scenario: Scenario,
    observed_sensors: Mapping[str, Mapping[str, float]],
) -> str:
    payload = {
        "scenario": scenario.name,
        "room": {
            "width": scenario.room.width,
            "length": scenario.room.length,
            "height": scenario.room.height,
            "base_temperature": scenario.room.base_temperature,
            "base_humidity": scenario.room.base_humidity,
            "base_illuminance": scenario.room.base_illuminance,
        },
        "environment": {
            "outdoor_temperature": scenario.environment.outdoor_temperature,
            "outdoor_humidity": scenario.environment.outdoor_humidity,
            "sunlight_illuminance": scenario.environment.sunlight_illuminance,
            "daylight_factor": scenario.environment.daylight_factor,
        },
        "elapsed_minutes": scenario.elapsed_minutes,
        "devices": [
            {
                "name": device.name,
                "activation": device.activation,
                "power": device.power,
            }
            for device in scenario.devices
        ],
        "sensors": [
            {
                "name": sensor.name,
                "position": [sensor.position.x, sensor.position.y, sensor.position.z],
                "observation": {
                    metric: float(observed_sensors[sensor.name][metric])
                    for metric in METRICS
                },
            }
            for sensor in scenario.sensors
            if sensor.role == "input"
        ],
    }
    return _hash_json(payload)


def _query_grid_hash(field: FieldGrid) -> str:
    return _hash_json(
        {
            "resolution": [field.resolution.nx, field.resolution.ny, field.resolution.nz],
            "x": field.x_coords,
            "y": field.y_coords,
            "z": field.z_coords,
        }
    )


def _truth_field_hash(field: FieldGrid) -> str:
    return _hash_json({metric: field.values[metric] for metric in METRICS})


def _hash_json(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _hash_strings(values: Sequence[str]) -> str:
    digest = hashlib.sha256()
    for value in values:
        digest.update(value.encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def _percent_reduction(before: float, after: float) -> float:
    return 0.0 if abs(float(before)) <= 1e-12 else (float(before) - float(after)) / float(before) * 100.0
