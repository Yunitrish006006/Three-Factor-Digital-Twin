# Spatial Field Estimation Delta

## ADDED Requirements

### Requirement: SFE-007 Validated temperature operating range

Current indoor field-estimation, target-state, and recommendation claims SHALL remain bounded to temperatures from `20 °C` through `30 °C`, inclusive. Outdoor boundary inputs MAY lie outside this interval, but SHALL NOT expand the claimed indoor operating range.

#### Scenario: Evaluating an in-range case

- **WHEN** every indoor baseline, target, and expected indoor field state is within `20–30 °C`
- **THEN** the case MAY be evaluated under the current model contract
- **AND** other evidence-class and application-specific boundaries SHALL still apply

#### Scenario: Evaluating an out-of-range case

- **WHEN** any required indoor operating, target, or expected field temperature is below `20 °C` or above `30 °C`
- **THEN** the current evidence SHALL not be used to claim valid performance
- **AND** a new range-specific calibration and validation change SHALL be required

## MODIFIED Requirements

## REMOVED Requirements
