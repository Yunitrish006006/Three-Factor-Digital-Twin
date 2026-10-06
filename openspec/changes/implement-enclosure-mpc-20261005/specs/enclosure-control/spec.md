# Enclosure Control Delta

## ADDED Requirements

### Requirement: CTRL-101 Explicit resettable thermal model

The simulator SHALL expose CPU/GPU temperature, inlet temperature, workload W, normalized PWM and observed RPM with explicit units and assumed parameters.

#### Scenario: Repeating a simulation

- **WHEN** configuration, seed and controller are identical
- **THEN** numerical trace fields SHALL be deterministic independently of wall-clock timing
- **AND** evidence SHALL be labeled assumed-model simulation.

### Requirement: CTRL-102 Constrained receding horizon

MPC SHALL optimize finite-horizon commands using current observations, apply only the first command and replan after receiving the next observation.

#### Scenario: Solver failure or infeasible predicted temperatures

- **WHEN** a solver result fails validation or predicted safety requires soft slack
- **THEN** fallback or slack SHALL be visible in the trace
- **AND** no soft temperature limit SHALL be described as a hard safety guarantee.

### Requirement: CTRL-103 Common baseline limits

Fixed fan, PID and MPC SHALL use the same input bounds, slew limit, current disturbance observations and safety override.

#### Scenario: Evaluating holdout

- **WHEN** validation or holdout is evaluated
- **THEN** model settings and controller selections SHALL match the calibration freeze
- **AND** full future disturbance trajectories SHALL not be supplied to MPC.

### Requirement: EVD-101 Auditable control evidence

The comparison SHALL preserve all per-case traces, source hashes, settings, failure records, macro metrics and evidence boundaries.

#### Scenario: Claiming improvement

- **WHEN** the registered comparative criterion fails
- **THEN** the claim SHALL be not supported even if implementation checks pass
- **AND** hardware control SHALL remain NOT_EVALUATED.

### Requirement: SYN-101 Exploratory artifact parity

All applicable research sources and rebuilt outputs SHALL state the same simulation scope and result status.

#### Scenario: Missing a rebuild

- **WHEN** an applicable output cannot be rebuilt
- **THEN** its task SHALL remain incomplete with the specific failure recorded.
