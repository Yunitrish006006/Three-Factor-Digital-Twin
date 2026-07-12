from dataclasses import dataclass
import math
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from digital_twin.core.entities import (
    SENSOR_ROLE_INPUT,
    SENSOR_ROLE_PSEUDO,
    SENSOR_ROLE_TARGET,
    SENSOR_ROLE_VALIDATION,
    Sensor,
    Vector3,
    select_sensors_by_role,
)
from digital_twin.core.scenarios import Scenario, apply_truth_adjustments
from digital_twin.physics.model import DigitalTwinModel, METRICS


@dataclass(frozen=True)
class SensorLayout:
    """Role-aware spatial nodes used by a research evaluation.

    Input and validation sensors are measured locations. Target and pseudo
    nodes are non-measured query/support locations and must not be treated as
    ground truth.
    """

    nodes: List[Sensor]

    def __post_init__(self) -> None:
        names = [node.name for node in self.nodes]
        if len(names) != len(set(names)):
            raise ValueError("Sensor layout names must be unique across all roles.")

        measured_positions: Dict[Tuple[float, float, float], str] = {}
        for node in self.measured_sensors:
            key = _position_key(node.position)
            if key in measured_positions:
                raise ValueError(
                    "Measured input and validation sensors must not share a position: "
                    f"{measured_positions[key]} and {node.name}."
                )
            measured_positions[key] = node.name

    @property
    def input_sensors(self) -> List[Sensor]:
        return select_sensors_by_role(self.nodes, SENSOR_ROLE_INPUT)

    @property
    def validation_sensors(self) -> List[Sensor]:
        return select_sensors_by_role(self.nodes, SENSOR_ROLE_VALIDATION)

    @property
    def target_points(self) -> List[Sensor]:
        return select_sensors_by_role(self.nodes, SENSOR_ROLE_TARGET)

    @property
    def pseudo_nodes(self) -> List[Sensor]:
        return select_sensors_by_role(self.nodes, SENSOR_ROLE_PSEUDO)

    @property
    def measured_sensors(self) -> List[Sensor]:
        return self.input_sensors + self.validation_sensors

    def to_dict(self) -> Dict[str, object]:
        return {
            "input_sensors": [_node_dict(node) for node in self.input_sensors],
            "validation_sensors": [_node_dict(node) for node in self.validation_sensors],
            "target_points": [_node_dict(node) for node in self.target_points],
            "pseudo_nodes": [_node_dict(node) for node in self.pseudo_nodes],
        }


def build_sensor_layout(
    input_sensors: Sequence[Sensor],
    validation_sensors: Optional[Sequence[Sensor]] = None,
    target_points: Optional[Sequence[Sensor]] = None,
    pseudo_nodes: Optional[Sequence[Sensor]] = None,
) -> SensorLayout:
    nodes: List[Sensor] = []
    nodes.extend(_with_role(sensor, SENSOR_ROLE_INPUT) for sensor in input_sensors)
    nodes.extend(_with_role(sensor, SENSOR_ROLE_VALIDATION) for sensor in (validation_sensors or []))
    nodes.extend(_with_role(sensor, SENSOR_ROLE_TARGET) for sensor in (target_points or []))
    nodes.extend(_with_role(sensor, SENSOR_ROLE_PSEUDO) for sensor in (pseudo_nodes or []))
    return SensorLayout(nodes=nodes)


def build_standard_holdout_layout(scenario: Scenario) -> SensorLayout:
    """Create a reproducible synthetic holdout layout for standard scenarios.

    These targets are validation examples for the controlled simulation suite;
    they are not real-room ground truth and must be reported as synthetic
    target-point evidence.
    """

    room = scenario.room
    validation = [
        Sensor(
            name="validation_center",
            position=Vector3(room.width * 0.50, room.length * 0.50, room.height * 0.40),
            role=SENSOR_ROLE_VALIDATION,
            metadata={"target_class": "room_center", "evidence": "synthetic_holdout"},
        ),
        Sensor(
            name="validation_window_side",
            position=Vector3(room.width * 0.26, room.length * 0.78, room.height * 0.40),
            role=SENSOR_ROLE_VALIDATION,
            metadata={"target_class": "window_side", "evidence": "synthetic_holdout"},
        ),
        Sensor(
            name="validation_furniture_boundary",
            position=Vector3(room.width * 0.225, room.length * 0.50, room.height * 0.40),
            role=SENSOR_ROLE_VALIDATION,
            metadata={"target_class": "near_furniture", "evidence": "synthetic_holdout"},
        ),
        Sensor(
            name="validation_door_side",
            position=Vector3(room.width * 0.84, room.length * 0.75, room.height * 0.40),
            role=SENSOR_ROLE_VALIDATION,
            metadata={"target_class": "door_side", "evidence": "synthetic_holdout"},
        ),
    ]
    return build_sensor_layout(
        input_sensors=scenario.sensors,
        validation_sensors=validation,
    )


def run_synthetic_holdout_validation(
    scenario: Scenario,
    layout: Optional[SensorLayout] = None,
    observation_noise: bool = True,
) -> Dict[str, object]:
    """Evaluate held-out target points without exposing their values to fitting.

    The function intentionally passes only input observations to power
    calibration and trilinear correction. Validation truth is read only after
    the corrected model has produced predictions.
    """

    layout = layout or build_standard_holdout_layout(scenario)
    input_nodes = layout.input_sensors
    validation_nodes = layout.validation_sensors
    if not input_nodes:
        raise ValueError("Holdout validation requires at least one input sensor.")
    if not validation_nodes:
        raise ValueError("Holdout validation requires at least one validation sensor.")

    input_names = {sensor.name for sensor in input_nodes}
    validation_names = {sensor.name for sensor in validation_nodes}
    overlap = input_names & validation_names
    if overlap:
        raise ValueError(f"Input and validation sensors must be disjoint: {sorted(overlap)}")

    model = DigitalTwinModel()
    truth_devices = apply_truth_adjustments(scenario.devices, scenario.truth_adjustments)
    truth_result = model.simulate(
        room=scenario.room,
        environment=scenario.environment,
        devices=truth_devices,
        furniture=scenario.furniture,
        sensors=layout.measured_sensors,
        zones=scenario.zones,
        elapsed_minutes=scenario.elapsed_minutes,
        resolution=scenario.resolution,
    )

    input_truth = _prediction_subset(truth_result.sensor_predictions, input_nodes)
    input_observations = _synthesize_observations(input_truth, input_nodes) if observation_noise else input_truth

    estimated_result = model.simulate(
        room=scenario.room,
        environment=scenario.environment,
        devices=scenario.devices,
        furniture=scenario.furniture,
        sensors=input_nodes,
        zones=scenario.zones,
        elapsed_minutes=scenario.elapsed_minutes,
        resolution=scenario.resolution,
        observed_sensors=input_observations,
    )

    validation_predictions = model.predict_sensors(
        room=scenario.room,
        environment=scenario.environment,
        devices=estimated_result.calibrated_devices,
        furniture=scenario.furniture,
        sensors=validation_nodes,
        elapsed_minutes=scenario.elapsed_minutes,
        corrections=estimated_result.corrections,
    )
    validation_truth = _prediction_subset(truth_result.sensor_predictions, validation_nodes)
    metrics = _error_metrics(validation_predictions, validation_truth)

    return {
        "scenario": scenario.name,
        "evidence_scope": "synthetic_target_point_holdout",
        "truth_provenance": "controlled_simulation_truth",
        "layout": layout.to_dict(),
        "input_observation_names": sorted(input_observations),
        "validation_truth_names": sorted(validation_truth),
        "leakage_detected": bool(set(input_observations) & set(validation_truth)),
        "metrics": metrics,
        "validation_points": [
            {
                "name": sensor.name,
                "position": _vector_dict(sensor.position),
                "metadata": dict(sensor.metadata),
                "truth": _round_metrics(validation_truth[sensor.name]),
                "prediction": _round_metrics(validation_predictions[sensor.name]),
                "absolute_error": {
                    metric: round(
                        abs(validation_predictions[sensor.name][metric] - validation_truth[sensor.name][metric]),
                        6,
                    )
                    for metric in METRICS
                },
            }
            for sensor in validation_nodes
        ],
    }


def _with_role(sensor: Sensor, role: str) -> Sensor:
    return Sensor(
        name=sensor.name,
        position=sensor.position,
        role=role,
        metadata=dict(sensor.metadata),
    )


def _position_key(position: Vector3) -> Tuple[float, float, float]:
    return (round(position.x, 6), round(position.y, 6), round(position.z, 6))


def _prediction_subset(
    predictions: Dict[str, Dict[str, float]],
    sensors: Iterable[Sensor],
) -> Dict[str, Dict[str, float]]:
    return {
        sensor.name: dict(predictions[sensor.name])
        for sensor in sensors
    }


def _synthesize_observations(
    truth_predictions: Dict[str, Dict[str, float]],
    sensors: Sequence[Sensor],
) -> Dict[str, Dict[str, float]]:
    observations: Dict[str, Dict[str, float]] = {}
    for index, sensor in enumerate(sensors):
        pattern = (index % 4) - 1.5
        observations[sensor.name] = {
            "temperature": truth_predictions[sensor.name]["temperature"] + 0.08 * pattern,
            "humidity": truth_predictions[sensor.name]["humidity"] + 0.3 * pattern,
            "illuminance": truth_predictions[sensor.name]["illuminance"] + 3.0 * pattern,
        }
    return observations


def _error_metrics(
    predictions: Dict[str, Dict[str, float]],
    truth: Dict[str, Dict[str, float]],
) -> Dict[str, Dict[str, float]]:
    output: Dict[str, Dict[str, float]] = {}
    for metric in METRICS:
        errors = [
            predictions[name][metric] - truth[name][metric]
            for name in sorted(truth)
        ]
        if not errors:
            output[metric] = {"mae": 0.0, "rmse": 0.0, "max_error": 0.0, "bias": 0.0}
            continue
        output[metric] = {
            "mae": round(sum(abs(error) for error in errors) / len(errors), 6),
            "rmse": round(math.sqrt(sum(error * error for error in errors) / len(errors)), 6),
            "max_error": round(max(abs(error) for error in errors), 6),
            "bias": round(sum(errors) / len(errors), 6),
        }
    return output


def _node_dict(node: Sensor) -> Dict[str, object]:
    return {
        "name": node.name,
        "role": node.role,
        "position": _vector_dict(node.position),
        "metadata": dict(node.metadata),
    }


def _vector_dict(point: Vector3) -> Dict[str, float]:
    return {"x": point.x, "y": point.y, "z": point.z}


def _round_metrics(values: Dict[str, float]) -> Dict[str, float]:
    return {metric: round(float(values[metric]), 6) for metric in METRICS}
