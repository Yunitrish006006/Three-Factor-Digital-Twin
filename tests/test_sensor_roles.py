import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
root_str = str(ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)

from digital_twin.core.entities import (
    SENSOR_ROLE_INPUT,
    SENSOR_ROLE_PSEUDO,
    SENSOR_ROLE_TARGET,
    SENSOR_ROLE_VALIDATION,
    Furniture,
    Sensor,
    Vector3,
    create_adaptive_corner_sensors,
    input_sensors,
    validation_sensors,
)
from digital_twin.core.scenarios import build_standard_devices, build_standard_room, build_validation_scenarios
from digital_twin.core.validation import (
    SensorLayout,
    build_sensor_layout,
    build_standard_holdout_layout,
    run_synthetic_holdout_validation,
)
from digital_twin.physics.learning import learn_device_impact_from_sensor_delta
from digital_twin.physics.model import DigitalTwinModel


class SensorRoleTests(unittest.TestCase):
    def test_sensor_defaults_to_input_for_backward_compatibility(self) -> None:
        sensor = Sensor(name="legacy", position=Vector3(1.0, 1.0, 1.0))
        self.assertEqual(sensor.role, SENSOR_ROLE_INPUT)
        self.assertTrue(sensor.can_fit)
        self.assertTrue(sensor.is_measured)

    def test_sensor_rejects_unknown_role(self) -> None:
        with self.assertRaises(ValueError):
            Sensor(name="bad", position=Vector3(0.0, 0.0, 0.0), role="ground_truth")

    def test_target_and_pseudo_nodes_are_not_measured(self) -> None:
        target = Sensor(name="target", position=Vector3(1.0, 1.0, 1.0), role=SENSOR_ROLE_TARGET)
        pseudo = Sensor(name="pseudo", position=Vector3(1.5, 1.0, 1.0), role=SENSOR_ROLE_PSEUDO)
        self.assertFalse(target.is_measured)
        self.assertFalse(pseudo.is_measured)
        self.assertFalse(target.can_fit)
        self.assertFalse(pseudo.can_fit)

    def test_role_selection_helpers_are_disjoint(self) -> None:
        nodes = [
            Sensor(name="input", position=Vector3(0.0, 0.0, 0.0)),
            Sensor(
                name="validation",
                position=Vector3(1.0, 0.0, 0.0),
                role=SENSOR_ROLE_VALIDATION,
            ),
        ]
        self.assertEqual([sensor.name for sensor in input_sensors(nodes)], ["input"])
        self.assertEqual([sensor.name for sensor in validation_sensors(nodes)], ["validation"])

    def test_adaptive_layout_preserves_validation_role(self) -> None:
        room = build_standard_room()
        furniture = [
            Furniture(
                name="corner_block",
                kind="cabinet",
                min_corner=Vector3(0.0, 0.0, 0.0),
                max_corner=Vector3(0.5, 0.5, 0.8),
                activation=1.0,
            )
        ]
        sensors = create_adaptive_corner_sensors(
            room=room,
            furniture=furniture,
            validation_target_points=[("holdout", Vector3(3.0, 2.0, 1.2))],
            compensation_per_blocked_corner=2,
        )
        holdout = next(sensor for sensor in sensors if sensor.name == "holdout")
        compensation = [sensor for sensor in sensors if sensor.name.startswith("floor_sw_comp_")]
        self.assertEqual(holdout.role, SENSOR_ROLE_VALIDATION)
        self.assertEqual(holdout.metadata["layout_kind"], "target_validation")
        self.assertEqual(len(compensation), 2)
        self.assertTrue(all(sensor.role == SENSOR_ROLE_INPUT for sensor in compensation))
        self.assertTrue(all(sensor.metadata["source_sensor"] == "floor_sw" for sensor in compensation))

    def test_sensor_layout_rejects_duplicate_measured_positions(self) -> None:
        with self.assertRaises(ValueError):
            SensorLayout(
                nodes=[
                    Sensor(name="input", position=Vector3(1.0, 1.0, 1.0)),
                    Sensor(
                        name="validation",
                        position=Vector3(1.0, 1.0, 1.0),
                        role=SENSOR_ROLE_VALIDATION,
                    ),
                ]
            )

    def test_build_sensor_layout_normalizes_roles(self) -> None:
        layout = build_sensor_layout(
            input_sensors=[Sensor(name="a", position=Vector3(0.0, 0.0, 0.0), role=SENSOR_ROLE_TARGET)],
            validation_sensors=[Sensor(name="b", position=Vector3(1.0, 0.0, 0.0))],
            target_points=[Sensor(name="c", position=Vector3(2.0, 0.0, 0.0))],
            pseudo_nodes=[Sensor(name="d", position=Vector3(3.0, 0.0, 0.0))],
        )
        self.assertEqual([node.role for node in layout.input_sensors], [SENSOR_ROLE_INPUT])
        self.assertEqual([node.role for node in layout.validation_sensors], [SENSOR_ROLE_VALIDATION])
        self.assertEqual([node.role for node in layout.target_points], [SENSOR_ROLE_TARGET])
        self.assertEqual([node.role for node in layout.pseudo_nodes], [SENSOR_ROLE_PSEUDO])

    def test_standard_holdout_layout_has_disjoint_input_and_validation_names(self) -> None:
        scenario = build_validation_scenarios()[0]
        layout = build_standard_holdout_layout(scenario)
        input_names = {sensor.name for sensor in layout.input_sensors}
        validation_names = {sensor.name for sensor in layout.validation_sensors}
        self.assertTrue(input_names)
        self.assertEqual(len(validation_names), 4)
        self.assertFalse(input_names & validation_names)

    def test_holdout_validation_never_passes_validation_truth_into_fitting(self) -> None:
        scenario = build_validation_scenarios()[1]
        result = run_synthetic_holdout_validation(scenario, observation_noise=False)
        input_names = set(result["input_observation_names"])
        validation_names = set(result["validation_truth_names"])
        self.assertFalse(result["leakage_detected"])
        self.assertFalse(input_names & validation_names)
        self.assertEqual(set(result["metrics"]), {"temperature", "humidity", "illuminance"})
        for metric in result["metrics"].values():
            self.assertGreaterEqual(metric["mae"], 0.0)
            self.assertGreaterEqual(metric["rmse"], metric["mae"] - 1e-9)
            self.assertGreaterEqual(metric["max_error"], metric["mae"] - 1e-9)

    def test_device_impact_learning_ignores_validation_observations(self) -> None:
        room = build_standard_room()
        model = DigitalTwinModel()
        device = next(device for device in build_standard_devices() if device.name == "ac_main")
        device.activation = 0.85
        input_sensor = Sensor(name="fit", position=Vector3(4.0, 2.0, 1.4))
        validation_sensor = Sensor(
            name="holdout",
            position=Vector3(2.0, 2.0, 1.4),
            role=SENSOR_ROLE_VALIDATION,
        )
        before = {
            "fit": {"temperature": 28.0, "humidity": 65.0, "illuminance": 100.0},
            "holdout": {"temperature": 28.0, "humidity": 65.0, "illuminance": 100.0},
        }
        after = {
            "fit": {"temperature": 26.5, "humidity": 63.0, "illuminance": 100.0},
            "holdout": {"temperature": 80.0, "humidity": 5.0, "illuminance": 9000.0},
        }
        input_only = learn_device_impact_from_sensor_delta(
            model=model,
            device=device,
            room=room,
            furniture=[],
            sensors=[input_sensor],
            before_observations=before,
            after_observations=after,
            elapsed_minutes=18.0,
        )
        mixed_roles = learn_device_impact_from_sensor_delta(
            model=model,
            device=device,
            room=room,
            furniture=[],
            sensors=[input_sensor, validation_sensor],
            before_observations=before,
            after_observations=after,
            elapsed_minutes=18.0,
        )
        self.assertEqual(mixed_roles.metric_coefficients, input_only.metric_coefficients)
        self.assertEqual(mixed_roles.sensor_observation_delta, input_only.sensor_observation_delta)


if __name__ == "__main__":
    unittest.main()
