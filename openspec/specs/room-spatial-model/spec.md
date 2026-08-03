# Room and Spatial Data Specification

## Purpose

This capability defines the geometry, coordinate, sensor, zone, device,
furniture, environmental, and validation contracts for every room-specific
dataset used by the digital twin.

## Requirements

### Requirement: RMS-001 Room dimensions and coordinates

Every room design SHALL provide positive `width_m`, `length_m`, and `height_m`
values and SHALL use meters with the origin at the floor southwest corner.

#### Scenario: Interpreting a point

- **GIVEN** a room with dimensions `(width_m, length_m, height_m)`
- **WHEN** a point `{x, y, z}` is supplied
- **THEN** `x` SHALL be interpreted along width, `y` along length, and `z` along height
- **AND** each coordinate SHALL lie within its inclusive room boundary

#### Scenario: Rejecting an incomplete room

- **WHEN** any dimension is absent, non-numeric, or not greater than zero
- **THEN** room validation SHALL fail with the offending field identified

### Requirement: RMS-002 Standard sensor topology

The standard research topology SHALL contain eight three-factor sensors at the
four floor corners and four ceiling corners.

#### Scenario: Validating the standard topology

- **WHEN** a room declares the standard topology
- **THEN** sensors SHALL exist at all combinations of `x in {0,width}`, `y in {0,length}`, and `z in {0,height}`
- **AND** each sensor SHALL provide or represent temperature, humidity, and illuminance observations

#### Scenario: Declaring a non-standard topology

- **WHEN** a room uses positions other than the standard eight corners
- **THEN** `metadata.reason` SHALL explain the deviation
- **AND** results SHALL not be called equivalent to the current eight-parameter trilinear correction unless a separate validation establishes equivalence

### Requirement: RMS-003 Zones and furniture bounds

Zones and furniture SHALL use three-dimensional `min_corner` and `max_corner`
bounding boxes fully contained by the room.

#### Scenario: Accepting a bounding box

- **WHEN** a zone or furniture item is validated
- **THEN** every minimum coordinate SHALL be strictly less than the corresponding maximum coordinate
- **AND** both corners SHALL stay within the room dimensions

#### Scenario: Modeling an obstruction

- **WHEN** furniture participates in blocking or reflection
- **THEN** its effect strength SHALL be stored in metadata using the implemented parameter contract
- **AND** the geometry SHALL remain separable from the effect parameter

### Requirement: RMS-004 Supported device geometry

Room designs SHALL support `ac`, `window`, and `light` devices with a position,
orientation, activation, and an optional influence radius.

#### Scenario: Validating device state

- **WHEN** a device is loaded
- **THEN** its `kind` SHALL be one of the supported device types
- **AND** its position SHALL be within the room
- **AND** activation SHALL be in the inclusive range `[0.0, 1.0]`

#### Scenario: Applying a default influence radius

- **WHEN** `influence_radius_m` is omitted
- **THEN** the implementation SHALL use the project default for that device kind
- **AND** the resolved value SHALL be visible in scenario or service metadata where available

### Requirement: RMS-005 Environmental and target data

A runnable room scenario SHALL define indoor baseline conditions, outdoor
boundary conditions, a grid resolution, and complete comfort targets for all
three modeled factors when action ranking is requested.

#### Scenario: Building a field-estimation scenario

- **WHEN** a room scenario is evaluated
- **THEN** it SHALL provide indoor baseline temperature, humidity, and illuminance
- **AND** it SHALL provide outdoor temperature, outdoor humidity, sunlight illuminance, and daylight factor
- **AND** grid dimensions `nx`, `ny`, and `nz` SHALL be positive integers

#### Scenario: Requesting recommendation ranking

- **WHEN** action ranking is requested
- **THEN** target temperature, humidity, and illuminance SHALL all be present
- **AND** an incomplete target SHALL produce a validation error rather than a partial ranking

### Requirement: RMS-006 Canonical room-data format

New room-specific data SHALL conform to
`docs/requirements/room_design_format_requirements_zh.md` and use the canonical
template and validator.

#### Scenario: Adding a new room design

- **WHEN** a new JSON room design is added
- **THEN** it SHALL be derived from `docs/templates/room_design_template.json`
- **AND** it SHALL pass `python3 scripts/validate_room_design.py <path>`

#### Scenario: Publishing a room-specific result

- **WHEN** a room design or result appears in thesis, IEEE, presentation, or figures
- **THEN** geometry, units, captions, and scenario counts SHALL agree across all synchronized artifacts
