# Hybrid Residual Learning Delta Specification

## ADDED Requirements

### Requirement: HRL-007 Time-aligned forecast notation

Any `h`-step additive hybrid forecast SHALL align the physics estimate and learned residual to the same target time, SHALL define `h` as forecast lead, and SHALL distinguish forecast-origin information from future observations.

#### Scenario: Writing an h-step hybrid forecast

- **WHEN** an artifact expresses the additive model with forecast horizon `h`
- **THEN** the physics term and residual term SHALL both target `t+h`
- **AND** the formula SHALL condition on information available at forecast origin `t`

#### Scenario: Preventing future-observation leakage

- **WHEN** the information set for an `h`-step forecast is described
- **THEN** it SHALL exclude observed truth and truth residuals from target time `t+h`
- **AND** forecast boundary or control inputs SHALL be identified as forecasts or planned inputs rather than future observations

#### Scenario: Describing the current implementation

- **WHEN** the current spatial estimator is described without a forecasting experiment
- **THEN** it SHALL retain the current-time form `F(p,t)+R(p,t)`
- **AND** any comparison with `h`-step notation SHALL identify the current form as the `h=0` case
