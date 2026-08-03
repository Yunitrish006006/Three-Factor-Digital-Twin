# Hybrid Residual Learning Specification

## Purpose

This capability defines the optional data-driven correction layer that learns
residual error while preserving the reduced-order physics model as the primary
and interpretable estimator.

## Requirements

### Requirement: HRL-001 Additive residual architecture

The hybrid model SHALL compute final estimates as the primary physics estimate
plus a learned residual and SHALL not replace the primary estimator.

#### Scenario: Producing a corrected estimate

- **WHEN** a trained residual model evaluates a point
- **THEN** it SHALL predict residuals for temperature, humidity, and illuminance
- **AND** each residual SHALL be added to the corresponding physics estimate

#### Scenario: Comparing model layers

- **WHEN** hybrid performance is evaluated
- **THEN** physics-only and hybrid metrics SHALL be reported on the same held-out samples

### Requirement: HRL-002 Residual feature contract

Residual features SHALL include spatial, temporal, baseline, outdoor,
physics-estimate, and device-state information needed to interpret the remaining
structured error.

#### Scenario: Building a residual sample

- **WHEN** a training or inference feature vector is constructed
- **THEN** it SHALL encode normalized coordinates, elapsed time, indoor baselines, outdoor conditions, and primary estimates
- **AND** it SHALL encode supported device activation, power or influence envelopes, and air-conditioner mode where applicable

#### Scenario: Preventing target leakage

- **WHEN** a held-out sample is prepared
- **THEN** its truth residual SHALL be used only as an evaluation target
- **AND** it SHALL not be included in features or training data for that evaluation

### Requirement: HRL-003 Repeatable training and splits

Hybrid experiments SHALL record the random seed, scenario split, sample counts,
training configuration, and test scenarios.

#### Scenario: Running the default experiment

- **WHEN** the default hybrid experiment is executed
- **THEN** the default seed SHALL be `42` unless explicitly overridden
- **AND** output metadata SHALL record train and test scenario names and sample counts

#### Scenario: Running robustness evaluation

- **WHEN** submission-readiness evaluation is executed
- **THEN** it SHALL include leave-one-scenario-out folds
- **AND** it SHALL report fold-level and average held-out metrics

### Requirement: HRL-004 Fourier denoising boundary

Optional Fourier low-pass denoising SHALL operate on residual target traces and
SHALL preserve metric-specific configuration.

#### Scenario: Using the current default spectral metrics

- **WHEN** Fourier denoising is enabled without an explicit metric override
- **THEN** it SHALL apply to temperature and humidity residual targets
- **AND** it SHALL not apply to illuminance

#### Scenario: Comparing denoising choices

- **WHEN** denoising is used in a reported experiment
- **THEN** a no-Fourier comparison SHALL be retained in robustness evidence
- **AND** any metric-specific degradation SHALL be disclosed

### Requirement: HRL-005 Checkpoint transparency

A residual checkpoint SHALL preserve enough configuration and model state to
reconstruct compatible inference and SHALL not be silently applied to
incompatible features.

#### Scenario: Loading a compatible checkpoint

- **WHEN** a compatible checkpoint is found
- **THEN** the service MAY enable hybrid inference
- **AND** it SHALL identify the estimator as hybrid

#### Scenario: Loading fails

- **WHEN** checkpoint loading or compatibility validation fails
- **THEN** the service SHALL expose the unavailable state
- **AND** it SHALL not report physics-only output as residual-corrected output

### Requirement: HRL-006 Generalization claim boundary

Hybrid residual results SHALL be limited to the evaluated scenario families,
splits, data mappings, and evidence classes.

#### Scenario: Reporting low controlled-simulation error

- **WHEN** very low field MAE is observed on canonical synthetic scenarios
- **THEN** the claim SHALL state that synthetic truth is structurally related to the implemented model
- **AND** it SHALL not imply equal error in arbitrary real rooms

#### Scenario: Reporting public benchmark mapping

- **WHEN** the physics and residual model are used as a structured prior for public data
- **THEN** the fitted readout and shared chronological split SHALL be disclosed
- **AND** the result SHALL not be called zero-shot full spatial-twin validation

### Requirement: HRL-007 Time-aligned forecast notation

Any `h`-step additive hybrid forecast SHALL align the physics estimate and
learned residual to the same target time, SHALL define `h` as forecast lead,
and SHALL distinguish forecast-origin information from future observations.

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

### Requirement: HRL-008 Recurrent comparator boundary

A vanilla RNN SHALL be treated as a comparator unless separate evidence accepts it as a project model component.

#### Scenario: Running the RNN baseline

- **WHEN** the professor-requested RNN comparison is executed
- **THEN** the fixed pre-registered architecture and seed SHALL be used
- **AND** the RNN SHALL receive only the shared origin-history data
- **AND** its result SHALL not silently replace the primary reduced-order physics estimator

#### Scenario: RNN performance is favorable or adverse

- **WHEN** the RNN wins or loses a case
- **THEN** the case-level result SHALL be preserved
- **AND** no architecture or data-window change after outcome observation SHALL replace the registered result without a new protocol version

### Requirement: HRL-009 Kalman-family future research boundary

Kalman-family methods SHALL remain future state or parameter estimators until their transition, observation, noise, data, and comparator contracts are registered and executed.

#### Scenario: Describing Kalman filtering now

- **WHEN** Kalman filtering appears in a thesis, paper, presentation, or research note before project execution
- **THEN** it SHALL be labeled literature-grounded future work or `NOT_EVALUATED`
- **AND** it SHALL disclose dependence on model accuracy and process/measurement noise assumptions

#### Scenario: Executing a future Kalman comparison

- **WHEN** a Kalman experiment is started
- **THEN** unfiltered, moving-average, and Kalman-family methods SHALL use identical observed rows and targets
- **AND** adverse innovations, divergence, or lack of improvement SHALL remain visible
