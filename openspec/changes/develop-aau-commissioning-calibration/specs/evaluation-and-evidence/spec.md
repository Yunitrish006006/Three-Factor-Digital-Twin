# Evaluation and Evidence Delta

## ADDED Requirements

### Requirement: EVD-025 E11H shall separate commissioning from frozen chronological testing

The research workflow SHALL fit calibration parameters only on the first two days, select models only on the third day, and evaluate unchanged models on later days.

#### Scenario: A calibration candidate improves fitted data only

- **WHEN** the candidate fails any selection-day MAE, RMSE, or P95 margin
- **THEN** the target sensor uses local IDW during the frozen test period

#### Scenario: A test-period gate fails

- **WHEN** any aggregate, tail, coverage, bootstrap, or absolute-error gate fails
- **THEN** E11H records `no_candidate_forwarded` and leaves E11F untouched

#### Scenario: E11H passes every development gate

- **WHEN** all frozen-test gates pass
- **THEN** only the recorded model map and calibration parameters may enter a separately specified E11F confirmation

