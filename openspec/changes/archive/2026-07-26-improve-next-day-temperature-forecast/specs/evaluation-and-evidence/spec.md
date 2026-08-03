# Delta Spec: evaluation-and-evidence

## ADDED Requirements

### Requirement: EVD-013 Leakage-controlled next-day temperature improvement

The project SHALL evaluate next-day temperature improvements with a
chronological validation-only selection protocol and a final test partition
that is excluded from candidate and hyperparameter choice.

#### Scenario: Selecting a next-day candidate

- **GIVEN** exact SML2010 origin, lag, and target timestamps
- **WHEN** the next-day comparison is executed
- **THEN** candidate selection SHALL use only the earliest 60% training and next 10% validation rows
- **AND** the selected candidate SHALL be refitted only on the earliest 70%
- **AND** the latest 30% SHALL be used only for final metrics

#### Scenario: Auditing forecast-origin features

- **WHEN** the seasonal residual feature vector is constructed
- **THEN** it MAY use origin-time measurements, timestamp cycles, historical lags, origin-time weather forecast, and origin-derived physics
- **AND** it SHALL NOT use target-time measured indoor state, actual weather, sunlight, or device state

#### Scenario: A historical lag is unavailable

- **WHEN** an exact `t-24h` or `t-7d` lag is unavailable
- **THEN** the evaluator MAY use the nearest allowed origin/history fallback with an availability flag
- **AND** it SHALL preserve the original origin/target row and record the missing-lag count
- **AND** the fallback SHALL NOT use target-time measurements or actual target-time boundaries

#### Scenario: Reporting unsuccessful or unstable improvement

- **WHEN** either target fails to beat seasonal persistence or its daily-block bootstrap interval includes zero
- **THEN** the failure SHALL remain visible in machine-readable and synchronized research artifacts
- **AND** the project SHALL NOT claim a robust next-day advantage

#### Scenario: Running a post-primary adaptive analysis

- **WHEN** an online same-slot correction is designed after the primary test result is known
- **THEN** its candidates and validation rule SHALL be registered before its predictions are computed
- **AND** every correction at origin `t` SHALL use only daily deltas completed at or before `t`
- **AND** the result SHALL be labeled post-primary exploratory
- **AND** it SHALL NOT replace the primary hypothesis or support a confirmatory next-day claim
