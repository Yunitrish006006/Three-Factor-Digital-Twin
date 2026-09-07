# Evaluation and Evidence Delta

## ADDED Requirements

### Requirement: EVD-024 E11G shall evaluate tail-safe gating without confirmation leakage

The research workflow SHALL evaluate all E11G choices with leave-one-day-out selection on E11E development data and SHALL leave E11F untouched.

#### Scenario: A sensor has no stable training-fold improvement

- **WHEN** no candidate improves MAE, RMSE, and P95 by the fixed margins and wins the required fraction of training days
- **THEN** that sensor uses the local-IDW baseline on the held-out day

#### Scenario: Aggregate MAE improves but a robustness gate fails

- **WHEN** any P95, RMSE, sensor-coverage, bootstrap, or absolute-error gate fails
- **THEN** the decision is `no_candidate_forwarded` and E11F is not accessed

#### Scenario: Every development gate passes

- **WHEN** all preregistered out-of-fold gates pass
- **THEN** the fixed deployment map may proceed only to a separately specified E11F confirmation change
