# Enclosure Session Delta

## ADDED Requirements

### Requirement: ENC-501 Source-blind session

The canonical package SHALL expose validated sparse observations and offline commands without receiving source reference truth or silently imputing missing sensors.

#### Scenario: Invalid or stale input

- **WHEN** an observation is nonfinite, outside input limits or has incorrect cadence
- **THEN** processing SHALL fail before updating session state or producing a command

### Requirement: ENC-502 Bounded commissioning transfer

Evaluation SHALL use the same declared calibration algorithm and budget across all rigs, retain out-of-family adverse results and separate measured evidence from synthetic commissioning.

#### Scenario: Reporting holdout

- **WHEN** new synthetic holdout is evaluated
- **THEN** source/config/calibration SHALL be frozen first and all samples retained
- **AND** historical opened studies and E15 SHALL remain untouched

### Requirement: ENC-503 Comparable source-blind decisions

Controllers SHALL share observation roles, target and command protections, with explicit optimizer fallbacks and timing cost.

#### Scenario: Comparing LQR and MPC

- **WHEN** command limiting or linearized constrained optimization is applied
- **THEN** the result SHALL not be described as unconstrained LQR optimality or full nonlinear MPC

### Requirement: SYN-501 Coupled reporting

Research reports SHALL derive metrics from executed evidence, preserve negative outcomes and match canonical synchronized sources.

#### Scenario: Delivering HTML

- **WHEN** final professor HTML is delivered
- **THEN** actual responsive and print QA SHALL be recorded for the exact final bytes
- **AND** physical measurement and oral presentation SHALL remain uncompleted without actual evidence
