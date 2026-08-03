# Research Governance Delta

## ADDED Requirements

### Requirement: RGV-007 Application relevance and operating-domain discipline

The project SHALL separate numerical estimator precision from demonstrated application need and SHALL keep application claims within the current `20–30 °C` temperature domain.

#### Scenario: Discussing human comfort

- **WHEN** human comfort is used as a motivating or recommendation target
- **THEN** it SHALL be represented with explicit target bands or tolerances
- **AND** lower model MAE SHALL not be described by itself as evidence that humans require equally precise actuation

#### Scenario: Proposing a precision-critical application

- **WHEN** a closed cultivation, laboratory, or other controlled environment is proposed
- **THEN** its need for dynamic rather than merely constant environmental control SHALL be stated
- **AND** every intended temperature SHALL lie within `20–30 °C` for current-scope alignment
- **AND** missing application variables and outcome evidence SHALL be disclosed

#### Scenario: An application exceeds the current range

- **WHEN** any required operating temperature is below `20 °C` or above `30 °C`
- **THEN** the application SHALL be labeled out of current model scope
- **AND** it SHALL require new modeling, calibration, and validation before any applicability claim

## MODIFIED Requirements

## REMOVED Requirements
