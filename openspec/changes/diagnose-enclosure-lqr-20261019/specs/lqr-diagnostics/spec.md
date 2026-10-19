# LQR diagnostics

## ADDED Requirements

### Requirement: LDA-901 Fixed factorial information intervention

The diagnostic SHALL independently replace controller state and controller model while retaining a fixed measured-input observer and shared constraints.

#### Scenario: Oracle information is used

- **WHEN** true state or exact parameters enter a controller
- **THEN** the arm SHALL be explicitly labeled simulation-only and SHALL not be presented as deployable sparse control

### Requirement: LDA-902 Complete immutable evidence

The study SHALL retain all forty episodes, independent verification and frozen historical evidence.

#### Scenario: A negative result occurs

- **WHEN** an oracle arm fails a preregistered gate
- **THEN** its result SHALL remain visible without retuning or reusing consumed evaluation data

### Requirement: LDA-903 Synchronized bounded explanation

Research artifacts SHALL agree on diagnostic outcomes and physical limits.

#### Scenario: Results are delivered

- **WHEN** the professor report is updated
- **THEN** it SHALL distinguish current simulation interventions from causes of old studies and from physical evidence
