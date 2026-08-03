# Action Recommendation Delta

## ADDED Requirements

### Requirement: ACT-007 Application-specific precision targets

Recommendation targets SHALL reflect application-specific tolerance bands and SHALL not infer control value from estimator precision alone.

#### Scenario: Ranking for human comfort

- **WHEN** the target application is human comfort
- **THEN** temperature, humidity, and illuminance targets SHALL include explicit tolerances or acceptable ranges
- **AND** recommendations SHALL not optimize unnecessary sub-tolerance changes as if they were demonstrated user benefits

#### Scenario: Ranking for a precision-critical process

- **WHEN** a cultivation or laboratory process is proposed
- **THEN** its dynamic setpoint schedule, tolerance, temperature-domain fit, missing variables, and process endpoint SHALL be defined before action efficacy is evaluated
- **AND** the current comfort penalty SHALL not be relabeled as a biological or laboratory quality metric

## MODIFIED Requirements

## REMOVED Requirements
