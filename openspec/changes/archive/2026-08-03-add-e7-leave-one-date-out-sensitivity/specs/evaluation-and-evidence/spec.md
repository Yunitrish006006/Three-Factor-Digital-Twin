# Evaluation and Evidence Delta

## ADDED Requirements

### Requirement: EVD-014 Leave-one-date-out sensitivity for E7

The project SHALL report a deterministic date-deletion sensitivity analysis for the seven-day E7 pillow-point comparison.

#### Scenario: Computing date-deletion folds

- **WHEN** the E7 weekly summary is produced
- **THEN** each observed date SHALL be omitted exactly once
- **AND** raw and calibrated MAE SHALL be recomputed from every remaining snapshot for temperature, humidity, and illuminance
- **AND** no date-deletion fold SHALL be removed after its result is observed

#### Scenario: Accepting the robustness hypothesis

- **WHEN** `H-E7-LODO-01` is decided
- **THEN** the minimum absolute MAE reduction across all date-deletion folds SHALL be greater than zero for all three metrics
- **AND** any zero or negative minimum SHALL be reported as not supported

#### Scenario: Reporting the bounded result

- **WHEN** the sensitivity result appears in a thesis, paper, presentation, or report
- **THEN** the number of dates, omitted-date design, and minimum reductions SHALL remain traceable to machine-readable evidence
- **AND** the result SHALL remain bounded to one room, one held-out pillow point, and the observed seven dates
