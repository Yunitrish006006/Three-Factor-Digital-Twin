# Action Recommendation Delta Specification

## ADDED Requirements

### Requirement: ACT-006 Preregistered intervention trial records

Real E8 action trials SHALL follow a versioned machine-readable record contract
that preserves the recommendation, executed action, target, observations,
settling interval, controls, and deviations.

#### Scenario: Recording a completed top-ranked trial

- **WHEN** a trial is labeled `COMPLETED` with condition `top_ranked`
- **THEN** the executed action SHALL equal the action with predicted rank 1
- **AND** before and after observations SHALL contain temperature, humidity, and illuminance
- **AND** the full predicted ranking and target definition SHALL be preserved

#### Scenario: Rejecting an incomplete completed trial

- **WHEN** a completed trial omits a required observation, target factor, action, or settling interval
- **THEN** the analyzer SHALL reject the record
- **AND** the record SHALL not contribute to any efficacy metric

#### Scenario: Evaluating matched action arms

- **WHEN** one environmental block contains comparable completed action arms
- **THEN** top-1 regret and rank correlation MAY be computed from the measured outcomes
- **AND** unavailable matched-arm metrics SHALL remain null rather than be inferred

