# Research Governance Delta

## ADDED Requirements

### Requirement: RGV-008 Future recurrent, control, and enclosure directions

The project SHALL distinguish future gated-recurrent comparators, closed-loop control baselines, and application-transfer candidates from completed estimators and evidence.

#### Scenario: Proposing GRU or LSTM

- **WHEN** GRU or LSTM is listed as future work
- **THEN** it SHALL be labeled `NOT_EVALUATED` until a separately registered same-data protocol is executed
- **AND** the existing vanilla RNN adverse results SHALL remain visible
- **AND** architecture or tuning changes SHALL not be selected from held-out test performance

#### Scenario: Proposing PID

- **WHEN** PID is listed as future work
- **THEN** it SHALL be identified as a closed-loop control comparator rather than a 3-D field estimator
- **AND** its future evaluation SHALL share plant, trajectory, disturbance, observation, actuator, and safety constraints with competing controllers
- **AND** current counterfactual action ranking SHALL not be described as implemented PID control

#### Scenario: Proposing an equipment enclosure

- **WHEN** a machine or equipment enclosure is proposed as an application
- **THEN** it SHALL be labeled a transfer candidate requiring new scale, airflow, heat-source, sensor, and validation contracts
- **AND** every intended air-state target SHALL remain within `20–30 °C` for current-scope alignment
- **AND** room-level evidence SHALL not be reused as enclosure applicability evidence
