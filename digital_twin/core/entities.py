from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


SENSOR_ROLE_INPUT = "input"
SENSOR_ROLE_VALIDATION = "validation"
SENSOR_ROLE_TARGET = "target"
SENSOR_ROLE_PSEUDO = "pseudo"
SENSOR_ROLES = frozenset(
    {
        SENSOR_ROLE_INPUT,
        SENSOR_ROLE_VALIDATION,
        SENSOR_ROLE_TARGET,
        SENSOR_ROLE_PSEUDO,
    }
)


@dataclass(frozen=True)
class Vector3:
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class Room:
    name: str
    width: float
    length: float
    height: float
    base_temperature: float
    base_humidity: float
    base_illuminance: float


@dataclass(frozen=True)
class Environment:
    outdoor_temperature: float
    outdoor_humidity: float
    sunlight_illuminance: float
    daylight_factor: float = 1.0


@dataclass(frozen=True)
class Zone:
    name: str
    min_corner: Vector3
    max_corner: Vector3

    def contains(self, point: Vector3) -> bool:
        return (
            self.min_corner.x <= point.x <= self.max_corner.x
            and self.min_corner.y <= point.y <= self.max_corner.y
            and self.min_corner.z <= point.z <= self.max_corner.z
        )


@dataclass(frozen=True)
class Sensor:
    name: str
    position: Vector3
    role: str = SENSOR_ROLE_INPUT
    metadata: Dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        normalized_role = str(self.role).strip().lower()
        if normalized_role not in SENSOR_ROLES:
            valid = ", ".join(sorted(SENSOR_ROLES))
            raise ValueError(f"Unsupported sensor role '{self.role}'. Expected one of: {valid}.")
        object.__setattr__(self, "role", normalized_role)
        object.__setattr__(self, "metadata", dict(self.metadata))

    @property
    def can_fit(self) -> bool:
        """Whether this observation may participate in calibration or training."""
        return self.role == SENSOR_ROLE_INPUT

    @property
    def is_measured(self) -> bool:
        """Whether this node represents a physical observation location."""
        return self.role in {SENSOR_ROLE_INPUT, SENSOR_ROLE_VALIDATION}


@dataclass
class Device:
    name: str
    kind: str
    position: Vector3
    orientation: Vector3
    influence_radius: float
    power: float = 1.0
    activation: float = 0.0
    response_time_minutes: float = 5.0
    metadata: Dict[str, object] = field(default_factory=dict)


@dataclass
class Furniture:
    name: str
    kind: str
    min_corner: Vector3
    max_corner: Vector3
    activation: float = 0.0
    metadata: Dict[str, object] = field(default_factory=dict)

    @property
    def center(self) -> Vector3:
        return Vector3(
            x=(self.min_corner.x + self.max_corner.x) / 2.0,
            y=(self.min_corner.y + self.max_corner.y) / 2.0,
            z=(self.min_corner.z + self.max_corner.z) / 2.0,
        )

    @property
    def size(self) -> Vector3:
        return Vector3(
            x=max(0.0, self.max_corner.x - self.min_corner.x),
            y=max(0.0, self.max_corner.y - self.min_corner.y),
            z=max(0.0, self.max_corner.z - self.min_corner.z),
        )


@dataclass(frozen=True)
class GridResolution:
    nx: int
    ny: int
    nz: int


@dataclass(frozen=True)
class ComfortTarget:
    temperature: float
    temperature_tolerance: float
    humidity: float
    humidity_tolerance: float
    illuminance: float
    illuminance_tolerance: float
    temperature_weight: float = 1.0
    humidity_weight: float = 0.45
    illuminance_weight: float = 0.9


@dataclass(frozen=True)
class ActionEffect:
    device_name: str
    activation: Optional[float] = None
    power_scale: float = 1.0
    metadata_updates: Dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class Action:
    name: str
    description: str
    effects: List[ActionEffect]


def select_sensors_by_role(sensors: Sequence[Sensor], *roles: str) -> List[Sensor]:
    normalized_roles = {str(role).strip().lower() for role in roles}
    unknown = normalized_roles - SENSOR_ROLES
    if unknown:
        valid = ", ".join(sorted(SENSOR_ROLES))
        raise ValueError(f"Unsupported sensor role(s) {sorted(unknown)}. Expected one of: {valid}.")
    return [sensor for sensor in sensors if sensor.role in normalized_roles]


def input_sensors(sensors: Sequence[Sensor]) -> List[Sensor]:
    return select_sensors_by_role(sensors, SENSOR_ROLE_INPUT)


def validation_sensors(sensors: Sequence[Sensor]) -> List[Sensor]:
    return select_sensors_by_role(sensors, SENSOR_ROLE_VALIDATION)


def _corner_sensor_specs(room: Room) -> List[Tuple[str, Vector3]]:
    return [
        ("floor_sw", Vector3(0.0, 0.0, 0.0)),
        ("floor_se", Vector3(room.width, 0.0, 0.0)),
        ("floor_nw", Vector3(0.0, room.length, 0.0)),
        ("floor_ne", Vector3(room.width, room.length, 0.0)),
        ("ceiling_sw", Vector3(0.0, 0.0, room.height)),
        ("ceiling_se", Vector3(room.width, 0.0, room.height)),
        ("ceiling_nw", Vector3(0.0, room.length, room.height)),
        ("ceiling_ne", Vector3(room.width, room.length, room.height)),
    ]


def _is_point_in_box(point: Vector3, item: Furniture, eps: float = 1e-9) -> bool:
    return (
        item.min_corner.x - eps <= point.x <= item.max_corner.x + eps
        and item.min_corner.y - eps <= point.y <= item.max_corner.y + eps
        and item.min_corner.z - eps <= point.z <= item.max_corner.z + eps
    )


def _is_blocked(point: Vector3, furniture: Optional[Sequence[Furniture]]) -> bool:
    if not furniture:
        return False
    return any(_is_point_in_box(point, item) for item in furniture)


def _clamp_point(point: Vector3, room: Room) -> Vector3:
    return Vector3(
        x=min(max(point.x, 0.0), room.width),
        y=min(max(point.y, 0.0), room.length),
        z=min(max(point.z, 0.0), room.height),
    )


def _sensor_position_key(position: Vector3) -> Tuple[float, float, float]:
    return (round(position.x, 6), round(position.y, 6), round(position.z, 6))


def _compensation_candidates(sensor: Sensor, room: Room, step: float) -> List[Vector3]:
    sx = 1.0 if sensor.position.x <= room.width / 2.0 else -1.0
    sy = 1.0 if sensor.position.y <= room.length / 2.0 else -1.0
    sz = 1.0 if sensor.position.z <= room.height / 2.0 else -1.0
    p = sensor.position
    return [
        _clamp_point(Vector3(p.x + sx * step, p.y, p.z), room),
        _clamp_point(Vector3(p.x, p.y + sy * step, p.z), room),
        _clamp_point(Vector3(p.x, p.y, p.z + sz * step), room),
        _clamp_point(Vector3(p.x + sx * step, p.y + sy * step, p.z + sz * step * 0.5), room),
    ]


def create_adaptive_sensor_layout(
    room: Room,
    base_sensors: Sequence[Sensor],
    furniture: Optional[Sequence[Furniture]] = None,
    target_sensors: Optional[Sequence[Sensor]] = None,
    compensation_per_blocked_sensor: int = 4,
    compensation_step: float = 0.35,
) -> List[Sensor]:
    sensors: List[Sensor] = []
    blocked: List[Sensor] = []
    used_names = set()
    used_positions = set()

    for sensor in base_sensors:
        if _is_blocked(sensor.position, furniture):
            blocked.append(sensor)
            continue
        key = _sensor_position_key(sensor.position)
        if key in used_positions or sensor.name in used_names:
            continue
        sensors.append(sensor)
        used_names.add(sensor.name)
        used_positions.add(key)

    compensation_target = max(0, int(compensation_per_blocked_sensor))
    for sensor in blocked:
        added = 0
        for scale in (1.0, 1.6, 2.2, 2.8):
            for index, candidate in enumerate(_compensation_candidates(sensor, room, compensation_step * scale), start=1):
                if added >= compensation_target:
                    break
                if _is_blocked(candidate, furniture):
                    continue
                key = _sensor_position_key(candidate)
                if key in used_positions:
                    continue
                name = f"{sensor.name}_comp_{added + 1}"
                while name in used_names:
                    name = f"{sensor.name}_comp_{added + 1}_{index}"
                metadata = dict(sensor.metadata)
                metadata.update(
                    {
                        "layout_kind": "compensation",
                        "source_sensor": sensor.name,
                        "source_role": sensor.role,
                        "blocked_reason": "furniture_occupied",
                    }
                )
                sensors.append(
                    Sensor(
                        name=name,
                        position=candidate,
                        role=sensor.role,
                        metadata=metadata,
                    )
                )
                used_names.add(name)
                used_positions.add(key)
                added += 1
            if added >= compensation_target:
                break

    for target in target_sensors or []:
        position = _clamp_point(target.position, room)
        key = _sensor_position_key(position)
        if key in used_positions:
            continue
        name = target.name
        if name in used_names:
            suffix = 1
            while f"{name}_{suffix}" in used_names:
                suffix += 1
            name = f"{name}_{suffix}"
        metadata = dict(target.metadata)
        metadata.setdefault("layout_kind", "target")
        sensors.append(
            Sensor(
                name=name,
                position=position,
                role=target.role,
                metadata=metadata,
            )
        )
        used_names.add(name)
        used_positions.add(key)

    return sensors


def create_adaptive_corner_sensors(
    room: Room,
    furniture: Optional[Sequence[Furniture]] = None,
    target_points: Optional[Iterable[Tuple[str, Vector3]]] = None,
    validation_target_points: Optional[Iterable[Tuple[str, Vector3]]] = None,
    compensation_per_blocked_corner: int = 4,
    compensation_step: float = 0.35,
) -> List[Sensor]:
    base = [
        Sensor(
            name=name,
            position=position,
            role=SENSOR_ROLE_INPUT,
            metadata={"layout_kind": "corner"},
        )
        for name, position in _corner_sensor_specs(room)
    ]
    targets = [
        Sensor(
            name=name,
            position=position,
            role=SENSOR_ROLE_INPUT,
            metadata={"layout_kind": "target_input"},
        )
        for name, position in (target_points or [])
    ]
    targets.extend(
        Sensor(
            name=name,
            position=position,
            role=SENSOR_ROLE_VALIDATION,
            metadata={"layout_kind": "target_validation"},
        )
        for name, position in (validation_target_points or [])
    )
    return create_adaptive_sensor_layout(
        room=room,
        base_sensors=base,
        furniture=furniture,
        target_sensors=targets,
        compensation_per_blocked_sensor=compensation_per_blocked_corner,
        compensation_step=compensation_step,
    )


def create_corner_sensors(room: Room) -> List[Sensor]:
    return [
        Sensor(
            name=name,
            position=position,
            role=SENSOR_ROLE_INPUT,
            metadata={"layout_kind": "corner"},
        )
        for name, position in _corner_sensor_specs(room)
    ]
