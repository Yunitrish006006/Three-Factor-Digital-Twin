# Equipment-Enclosure Transfer Delta

## ADDED Requirements

### Requirement: ENC-001 Public BMC data contract

The enclosure-transfer experiment SHALL preserve source provenance and parse timestamped inlet temperature, outlet temperature, fan speed, and equipment power without inventing missing observations.

#### Scenario: Loading an eligible BMC trace

- **WHEN** an InfluxDB-style BMC CSV contains the required channels
- **THEN** comment metadata SHALL be ignored and observations SHALL be ordered within `device_id`
- **AND** source SHA-256, available channels, row counts, and exclusions SHALL be recorded

#### Scenario: Required telemetry is missing

- **WHEN** a row lacks a parseable timestamp, inlet, outlet, fan, or power value
- **THEN** the row SHALL not be interpolated or silently retained
- **AND** its exclusion SHALL contribute to the reported missing-data count

### Requirement: ENC-002 Fair temporal estimator comparison

Every `E11A` comparator SHALL use identical eligible examples, chronological splits, targets, and metrics.

#### Scenario: Evaluating one enclosure trace

- **WHEN** a trace has enough eligible adjacent pairs
- **THEN** persistence, linear readout, and thermal-balance readout SHALL share the same train, validation, and test endpoints
- **AND** ridge strength and split boundaries SHALL be fixed before test evaluation
- **AND** case output SHALL contain MAE, RMSE, split hashes, winner, and adverse results

#### Scenario: A trace has insufficient eligible pairs

- **WHEN** fewer than 30 eligible pairs remain
- **THEN** the case SHALL be labeled `insufficient_in_scope_samples`
- **AND** no model ranking SHALL be produced for that case

### Requirement: ENC-003 Enclosure operating-domain and claim boundary

The initial enclosure-transfer result SHALL remain a public task-aligned air-state claim inside 20–30 °C and SHALL not be described as spatial, component-level, causal, or closed-loop validation.

#### Scenario: An air state exceeds the registered range

- **WHEN** a current or next inlet/outlet air temperature is below 20 °C or above 30 °C
- **THEN** the affected pair SHALL be excluded as out of current scope
- **AND** the exclusion count and retained fraction SHALL remain visible

#### Scenario: Reporting a successful temporal comparison

- **WHEN** a thermal-balance readout beats persistence on eligible public traces
- **THEN** the claim SHALL name the dataset, target, range, split and evidence class
- **AND** it SHALL not imply CPU hotspot accuracy, 3-D field reconstruction, arbitrary enclosure transfer, or PID effectiveness

### Requirement: ENC-004 Dataset role separation

Candidate enclosure datasets SHALL be assigned to tasks that match their observable variables and geometry.

#### Scenario: Selecting data for E11A

- **WHEN** the BMC dataset is used
- **THEN** it SHALL support only temporal inlet/outlet, power, fan and workload analyses exposed by its channels
- **AND** absent spatial coordinates SHALL prevent a 3-D field claim

#### Scenario: Planning spatial follow-up

- **WHEN** the AAU high-resolution server-room dataset is selected for future work
- **THEN** its 3-D geometry, temperature, air-speed and power measurements SHALL be registered in a separate `E11B` protocol
- **AND** room-level and BMC temporal results SHALL not substitute for its spatial validation
