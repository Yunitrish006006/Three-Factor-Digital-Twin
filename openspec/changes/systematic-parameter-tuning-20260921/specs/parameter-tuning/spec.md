# Parameter Tuning Delta

## ADDED Requirements

### Requirement: TUN-101 Frozen bounded search

Tuning SHALL fix candidate bounds, split definitions, selection rules and search budgets before evaluation.

#### Scenario: Locked validation

- **WHEN** a selected controller is evaluated on independent dates
- **THEN** parameters SHALL remain frozen and all baseline traces SHALL be preserved.

### Requirement: TUN-102 Preserve evidence boundaries

Contract tests, TCLab simulation, BOPTEST FMU and hardware intervention SHALL remain separate evidence classes.

#### Scenario: A simulation pilot passes

- **WHEN** hashes and split audits pass
- **THEN** the report SHALL describe only platform simulation feasibility
- **AND** E8 and physical enclosure SHALL remain NOT_EVALUATED.
