# Evaluation and Evidence Delta

## ADDED Requirements

### Requirement: EVD-022 Independent role-conditioned enclosure confirmation

The project SHALL evaluate H-ENC-04 on observation byte ranges disjoint from E11B and E11C, using sensor roles, models, metrics, and thresholds fixed before E11D retrieval.

#### Scenario: Role-conditioned model meets every threshold

- **WHEN** role-conditioned MAE and RMSE are lower than global-mean errors
- **AND** at least 26 of 42 sensors have lower role-conditioned MAE
- **AND** the paired day-block bootstrap 95% confidence interval has a lower bound above zero
- **THEN** H-ENC-04 is recorded as `supported`

#### Scenario: Any threshold fails

- **WHEN** one or more registered decision conditions are false
- **THEN** H-ENC-04 is recorded as `not_supported`
- **AND** aggregate, per-role, per-sensor, and uncertainty results remain in the evidence artifact

#### Scenario: Protocol integrity fails

- **WHEN** a range overlaps prior observations, a response is not HTTP `206`, the role map is incomplete, or the schema cannot be resolved
- **THEN** the run aborts without a hypothesis decision
- **AND** the failure is recorded in the research difficulty log
