# Four Controller Delta

## ADDED Requirements

### Requirement: CTRL-201 Shared bounded control and solver health

Four methods SHALL use common protection and report numerical failures separately from sampled thermal violations.

#### Scenario: Numerical failure in overload

- **WHEN** a solution is invalid or exceeds the deadline
- **THEN** the same slew-limited fallback SHALL apply visibly
- **AND** soft thermal constraints SHALL not imply safety guarantees.

### Requirement: CTRL-202 Frozen calibration and LQR reference

The comparison SHALL use three candidates per method and a fixed equilibrium allocation for the shared fan.

#### Scenario: Assumed unseen plants

- **WHEN** plant_holdout begins
- **THEN** algorithms and selections SHALL remain frozen
- **AND** true variant parameters SHALL not be supplied to controllers.

### Requirement: EVD-201 Independent complete control audit

Evidence SHALL preserve exclusive attempts and validate metrics, decisions, candidates, scenarios and thermal integration independently.

#### Scenario: Interrupted or manipulated execution

- **WHEN** an attempt exists or evidence disagrees
- **THEN** explicit rejection SHALL remain active under Python optimization
- **AND** previous traces SHALL be preserved.

### Requirement: SYN-201 Four-method synchronization

Sources and applicable outputs SHALL distinguish historical v1, v2 simulation and unmeasured physical control.

#### Scenario: Missing render dependency

- **WHEN** Office rendering cannot run
- **THEN** its visual task SHALL remain incomplete with the dependency failure recorded.
