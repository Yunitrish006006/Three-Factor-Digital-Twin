# Delta specifications
## ADDED Requirements
### Requirement: UFC-001 Common enclosure comparison environment
The study SHALL compare five methods with identical plant, seed schedules, observations and constraints within each paired episode.
#### Scenario: Formal comparison
- **WHEN** a split/seed is evaluated
- **THEN** fixed PWM, PI, PID, LQR and MPC SHALL use identical exogenous input and initial state
- **AND** report full-state assumed-model evidence only
### Requirement: UFC-002 Equal candidate trial budget
Each method SHALL receive three candidates and three calibration seeds, selected before evaluation.
#### Scenario: Selecting gains
- **WHEN** calibration finishes
- **THEN** a shared score and deterministic tie-break SHALL freeze selected parameters
### Requirement: UFC-003 Preserved evidence and independent audit
All results SHALL retain source/config freeze, attempts, CSV and independent metric/dynamics verification.
#### Scenario: Evidence corruption
- **WHEN** stored data or result metrics are modified
- **THEN** verification SHALL fail without modifying frozen evidence
### Requirement: UFC-004 Result and artifact consistency
The report and applicable canonical artifacts SHALL contain matching settings, metrics and evidence boundaries.
#### Scenario: Result publication
- **WHEN** a report is generated
- **THEN** the five-method ranking SHALL retain energy, overtemperature and failed results

