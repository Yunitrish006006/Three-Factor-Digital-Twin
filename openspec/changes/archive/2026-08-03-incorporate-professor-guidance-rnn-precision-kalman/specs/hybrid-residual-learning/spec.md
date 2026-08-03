# Hybrid Residual Learning Delta

## ADDED Requirements

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

## MODIFIED Requirements

## REMOVED Requirements
