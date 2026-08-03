# Spatial Field Estimation Specification

## Purpose

This capability defines observable behavior for estimating temperature,
humidity, and illuminance fields from room geometry, device states, boundary
conditions, elapsed time, and sparse sensor observations.

## Requirements

### Requirement: SFE-001 Three-factor continuous-field contract

The estimator SHALL represent temperature, humidity, and illuminance as spatial
and temporal fields that can be sampled at valid room coordinates.

#### Scenario: Sampling a valid point

- **WHEN** a caller supplies a point inside the room and an elapsed-time or steady-state setting
- **THEN** the estimator SHALL return temperature in degrees Celsius, humidity in percent, and illuminance in lux
- **AND** the response SHALL identify the estimator actually used

#### Scenario: Rejecting an invalid point

- **WHEN** any requested coordinate is outside the room
- **THEN** the request SHALL fail with a boundary validation error
- **AND** the estimator SHALL not silently clamp the point

### Requirement: SFE-002 Reduced-order field composition

The primary estimator SHALL compose an indoor background or bulk field, local
device influence fields, sparse-sensor calibration, and an optional additive
residual correction.

#### Scenario: Running the primary estimator

- **WHEN** hybrid residual correction is not requested
- **THEN** the result SHALL be generated from the reduced-order physics and calibration layers
- **AND** device and boundary-condition effects SHALL remain interpretable in the output metadata or evaluation artifacts

#### Scenario: Running the optional hybrid estimator

- **WHEN** hybrid residual correction is requested and a compatible checkpoint is available
- **THEN** the residual prediction SHALL be added to the primary estimate
- **AND** the primary physics estimate SHALL remain recoverable for comparison

### Requirement: SFE-003 Time-response semantics

Device and boundary effects SHALL be evaluated using explicit elapsed-time or
steady-state semantics.

#### Scenario: Evaluating elapsed time

- **WHEN** `elapsed_minutes` is supplied
- **THEN** time-response functions SHALL use that value
- **AND** the response SHALL report the effective elapsed time

#### Scenario: Evaluating steady state

- **WHEN** steady-state evaluation is requested
- **THEN** the service SHALL use its declared steady-state duration or mode
- **AND** the response SHALL distinguish steady state from an explicitly timed sample

### Requirement: SFE-004 Sparse calibration

Sparse calibration SHALL use sensor residuals to correct the field without
relabeling sensor points as dense ground truth.

#### Scenario: Applying eight-corner correction

- **GIVEN** complete observations at the standard eight corners
- **WHEN** calibration is applied
- **THEN** active-device scale calibration and trilinear residual correction MAY update the estimated field
- **AND** the correction SHALL remain defined over the room bounds

#### Scenario: Evaluating an unseen point

- **WHEN** a reference point is used to evaluate calibration generalization
- **THEN** that reference point SHALL not also be used as a calibration sensor for the same evaluation
- **AND** before/after errors SHALL be preserved in machine-readable evidence

### Requirement: SFE-005 Multi-resolution outputs

The same estimator state SHALL support point, zone, volume, dashboard, timeline,
JSON, CSV, and visualization-oriented outputs without changing the underlying
research model.

#### Scenario: Comparing interfaces

- **WHEN** two interfaces evaluate the same scenario, point, time, device overrides, and estimator setting
- **THEN** their numerical field values SHALL agree within declared serialization precision

#### Scenario: Computing a zone summary

- **WHEN** a target zone is evaluated
- **THEN** the result SHALL aggregate samples inside the zone bounds
- **AND** it SHALL report all three modeled factors

### Requirement: SFE-006 Estimator transparency and fallback

Requests for optional model components SHALL expose whether the requested
component was loaded, used, or unavailable.

#### Scenario: Missing residual checkpoint

- **WHEN** hybrid residual correction is requested but a compatible checkpoint is unavailable
- **THEN** the system SHALL either return a clear unavailable status with the physics result or fail explicitly
- **AND** it SHALL not label an uncorrected physics result as hybrid

#### Scenario: Reporting calibration state

- **WHEN** calibration or learned power scaling affects a result
- **THEN** the response or evidence artifact SHALL expose the applicable calibration metadata

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
