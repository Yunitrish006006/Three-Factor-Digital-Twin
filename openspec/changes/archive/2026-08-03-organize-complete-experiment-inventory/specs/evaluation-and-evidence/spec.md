# Evaluation and Evidence Delta

## ADDED Requirements

### Requirement: EVD-016 Canonical complete experiment inventory

The project SHALL maintain a consolidated E1–E9 inventory that is traceable to current machine-readable evidence and preserves adverse, missing, and out-of-domain outcomes.

#### Scenario: Rendering the inventory

- **WHEN** the complete experiment overview is generated
- **THEN** every E1–E9 item SHALL identify its evidence class, data, comparators, metrics, status, evidence path, producer command, and claim boundary
- **AND** E9 subexperiments SHALL remain distinguishable rather than being collapsed into one result

#### Scenario: Reconciling stale prose

- **WHEN** a prose number differs from the current canonical JSON
- **THEN** the prose SHALL be updated to the current value
- **AND** the mismatch SHALL not be hidden by averaging, selecting the favorable version, or leaving both versions unqualified

#### Scenario: Auditing the E5 temperature domain

- **WHEN** an E5 target-zone indoor temperature is outside `20–30 °C`
- **THEN** the row SHALL be retained as an out-of-domain stress case
- **AND** it SHALL not support current-domain applicability claims

## MODIFIED Requirements

## REMOVED Requirements

