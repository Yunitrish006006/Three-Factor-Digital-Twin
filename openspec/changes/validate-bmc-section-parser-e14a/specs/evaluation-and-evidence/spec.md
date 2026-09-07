# Evaluation and Evidence Delta

## ADDED Requirements

### Requirement: EVD-031 E14A shall validate source-aware BMC parsing independently

The research workflow SHALL compare a section-aware production parser against an independent raw-line oracle on all 31 frozen BMC source files.

#### Scenario: A new InfluxDB section begins

- **WHEN** the parser reads a `#group` line
- **THEN** it SHALL discard the previous section header and wait for the new local header

#### Scenario: A row belongs to host telemetry

- **WHEN** `_measurement` or `device_id` is not `sdgp` and `bmc`
- **THEN** the row SHALL not enter BMC thermal features or targets

#### Scenario: Correctness metrics are available

- **WHEN** all 31 files have been parsed and independently counted
- **THEN** H-DATA-01 SHALL be supported only with exact 31/31 count agreement, zero non-BMC acceptance, exclusion of the known host row, and no accepted mapped temperature at or above 1,000 degrees C

### Requirement: EVD-032 E14A shall preserve parser-invalidated model evidence

The research artifacts SHALL retain E13's executed outputs while preventing its schema-contaminated metrics from supporting model accuracy claims.

#### Scenario: E14A confirms schema contamination

- **WHEN** the corrected parser excludes rows previously mapped from host sections
- **THEN** E13 SHALL be labeled parser-invalidated rather than silently replaced
- **AND** corrected E13 test metrics SHALL not be described as unseen confirmation

#### Scenario: Further model evaluation is proposed

- **WHEN** parser correctness is supported
- **THEN** a new model study SHALL preregister unused complete files for final confirmation
