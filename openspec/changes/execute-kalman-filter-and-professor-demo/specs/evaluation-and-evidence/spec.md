# Evaluation and Evidence Delta Specification

## Purpose

This delta registers a same-data controlled Kalman filtering comparison with explicit input parity and claim boundaries.

## Requirements

### Requirement: EVD-017 Same-data controlled Kalman filtering comparison

The project SHALL compare raw observations, a causal moving average, and a registered linear Kalman filter on identical fixed-seed corrupted SML2010 current-time rows.

#### Scenario: Building one corrupted input

- **WHEN** a target and registered noise profile are evaluated
- **THEN** one corrupted observation sequence SHALL be generated before any method is run
- **AND** every method SHALL use the same chronological split, timestamps, corrupted values, reference targets, and metric functions
- **AND** the timestamp and corrupted-value hashes SHALL be preserved in evidence

#### Scenario: Running the registered filter

- **WHEN** the scalar Kalman filter is executed
- **THEN** its transition, observation, process covariance, measurement covariance, initialization, and gap-reset rules SHALL match the registered protocol
- **AND** innovations, gains, resets, and every method loss SHALL remain visible

#### Scenario: Reporting bounded results

- **WHEN** the comparison is reported
- **THEN** it SHALL be labeled controlled injected-noise current-time filtering
- **AND** it SHALL NOT be described as real-sensor, forecasting, dense 3-D field, control, or cross-site validation
- **AND** non-Kalman winners and adverse cases SHALL not be removed
