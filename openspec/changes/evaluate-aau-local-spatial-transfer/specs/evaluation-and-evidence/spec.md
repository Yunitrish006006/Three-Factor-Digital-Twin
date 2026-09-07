# E11C Evaluation and Evidence Delta

## ADDED Requirements

### Requirement: EVD-021 Independent local spatial-transfer confirmation

The project SHALL evaluate E11C on the 11 preregistered gap-centered AAU byte ranges that do not overlap E11B and SHALL compare fixed three-neighbor IDW with one-nearest-neighbor on identical held-out sensor-minute targets.

#### Scenario: Executing E11C

- **WHEN** all confirmation fragments pass range and provenance checks
- **THEN** the evaluator SHALL use 42 high-confidence sensors, `k=3`, `p=2`, seed `20260823`, and 20,000 day-block-bootstrap replicates
- **AND** it SHALL preserve aggregate, per-sensor, uncertainty, adverse, and decision fields
- **AND** it SHALL not choose interpolation settings from E11C metrics

#### Scenario: Deciding H-ENC-03

- **WHEN** E11C is evaluable
- **THEN** support SHALL require lower local-IDW macro MAE and RMSE, at least 26/42 per-sensor wins, and a positive bootstrap lower bound
- **AND** failure of any condition SHALL produce `not_supported`
