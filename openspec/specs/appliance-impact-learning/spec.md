# Non-Networked Appliance Impact Learning Specification

## Purpose

This capability defines how the project records before/after observations and
learns interpretable environmental impacts for appliances that do not expose a
network API or reliable self-reported state.

## Requirements

### Requirement: APL-001 Supported appliance effects

Impact learning SHALL support air conditioners, windows, and lights using
device-kind-specific parameters and three-factor environmental observations.

#### Scenario: Learning an air-conditioner effect

- **WHEN** an air-conditioner observation pair is learned
- **THEN** temperature SHALL be treated as a primary effect
- **AND** humidity and directional airflow parameters MAY be updated when supported by the record

#### Scenario: Learning a window or light effect

- **WHEN** a window or light observation pair is learned
- **THEN** window effects SHALL retain outdoor boundary and daylight context
- **AND** light effects SHALL retain activation, geometry, and illuminance context

### Requirement: APL-002 Complete before/after records

Each learning record SHALL preserve sufficient context to distinguish an
environmental change from an unqualified device delta.

#### Scenario: Starting a learning record

- **WHEN** a before observation is recorded
- **THEN** the record SHALL identify the device, device state and specifications, room baseline, outdoor boundary, furniture, elapsed-time semantics, and sensor readings
- **AND** it SHALL receive a stable record identifier

#### Scenario: Completing a learning record

- **WHEN** the after observation is submitted
- **THEN** it SHALL be linked to the same record identifier
- **AND** completeness and sensor compatibility SHALL be validated before learning

### Requirement: APL-003 Delta-based impact estimation

The learner SHALL estimate device impact from aligned after-minus-before
environmental changes rather than assuming an appliance API reports true effect.

#### Scenario: Fitting an impact parameter

- **WHEN** a complete record contains usable sensor deltas
- **THEN** the learner SHALL fit or update the supported device impact parameters
- **AND** it SHALL return the learned values and the observations used

#### Scenario: Insufficient evidence

- **WHEN** an observation pair is incomplete, mismatched, or provides insufficient variation
- **THEN** learning SHALL fail or report insufficient evidence
- **AND** default parameters SHALL not be presented as newly learned parameters

### Requirement: APL-004 Confounder preservation

Learning records SHALL preserve environmental and geometric conditions that can
confound attribution.

#### Scenario: Boundary conditions change

- **WHEN** outdoor temperature, humidity, sunlight, window state, or other active devices differ between before and after observations
- **THEN** the changed conditions SHALL remain visible in the record
- **AND** the resulting estimate SHALL not be described as isolated causal appliance impact without a controlled design

#### Scenario: Furniture changes

- **WHEN** furniture or obstruction configuration changes
- **THEN** the record SHALL preserve both configurations or reject the pair as incompatible

### Requirement: APL-005 Non-networked-device premise

The research model SHALL not require the studied appliance to provide a network
API, telemetry stream, or authoritative internal power report.

#### Scenario: Manually operated device

- **WHEN** a traditional device is operated manually or by an external controller
- **THEN** the model MAY use observer-supplied state and specifications
- **AND** its environmental impact SHALL be inferred from observations and model structure

#### Scenario: Available telemetry

- **WHEN** telemetry happens to be available
- **THEN** it MAY be recorded as auxiliary context
- **AND** the research contribution SHALL remain distinguishable from direct smart-device control

### Requirement: APL-006 Learning audit trail

Impact-learning operations SHALL produce an auditable, appendable record of
inputs, learned parameters, status, and failures.

#### Scenario: Persisting a learning result

- **WHEN** a learning operation finishes
- **THEN** the local service SHALL make the record serializable
- **AND** MCP-mediated learning SHALL append an entry to the configured local learning log

#### Scenario: Using learned impacts in claims

- **WHEN** learned parameters are reported in research artifacts
- **THEN** the originating records, evidence class, and limitations SHALL be identified
- **AND** controlled simulation learning SHALL not be represented as completed real-world causal identification
