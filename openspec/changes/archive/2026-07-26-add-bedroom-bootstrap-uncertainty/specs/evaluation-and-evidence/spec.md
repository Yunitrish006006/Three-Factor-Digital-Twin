# Evaluation and Evidence Delta Specification

## ADDED Requirements

### Requirement: EVD-010 Cluster-aware uncertainty for repeated real-room snapshots

Real-bedroom snapshot comparisons SHALL report deterministic uncertainty that preserves the paired structure and the repeated snapshots within each date.

#### Scenario: Computing E7 uncertainty

- **WHEN** raw and calibrated pillow errors are compared across the seven-day E7 dataset
- **THEN** bootstrap resampling SHALL use calendar date as the block
- **AND** all snapshots from a sampled date SHALL move together
- **AND** the output SHALL record seed, replicate count, confidence level, and resampling unit

#### Scenario: Reporting the uncertainty result

- **WHEN** a confidence interval for calibration improvement is reported
- **THEN** it SHALL identify the endpoint as paired mean absolute-error reduction
- **AND** it SHALL remain bounded to one room, one held-out pillow point, and the observed seven-day period
- **AND** snapshot improvement fraction SHALL NOT be labeled as an intervention success rate

#### Scenario: Detecting unstable improvement

- **WHEN** any metric's interval includes or falls below zero
- **THEN** the all-metric robustness hypothesis SHALL not be accepted
- **AND** synchronized claims SHALL report the adverse or inconclusive metric
