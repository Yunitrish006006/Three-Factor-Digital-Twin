# Research Adaptive Orchestration Delta

## ADDED Requirements

### Requirement: RAO-001 Deterministic orchestration selection

The project SHALL map structured research-complexity inputs to a deterministic explainable orchestration score and one bounded orchestration mode.

#### Scenario: Route a trivial question
- **WHEN** a low-complexity task scores within the primary-only threshold
- **THEN** the plan SHALL contain Primary and no subagent

#### Scenario: Route a high-conflict task
- **WHEN** a task scores within the guarded-parallel threshold
- **THEN** the plan SHALL include bounded specialist roles subject to the configured subagent budget

### Requirement: RAO-002 Bounded role assignments

Every subagent assignment SHALL carry explicit scope, inclusion/exclusion rules, output schema, evidence requirements, forbidden assumptions, dependencies, and a no-recursive-spawn default.

#### Scenario: Assign evidence extraction
- **WHEN** an Evidence Extractor assignment is created
- **THEN** it SHALL be bounded to admitted paper identifiers and SHALL not participate in final synthesis

### Requirement: RAO-003 Independent reviewer ordering

The Independent Reviewer SHALL remain outside original synthesis and run only after Primary synthesis.

#### Scenario: Validate a review assignment
- **WHEN** a plan contains an Independent Reviewer
- **THEN** the reviewer SHALL depend on the Primary synthesis assignment and SHALL not participate in synthesis

### Requirement: RAO-004 Claim evidence integrity

Every research claim SHALL reference existing supporting evidence and SHALL preserve registered contradictory evidence.

#### Scenario: Validate an unsupported claim
- **WHEN** a claim contains no supporting evidence IDs
- **THEN** validation SHALL produce a blocking claim-without-evidence finding

#### Scenario: Validate contradiction retention
- **WHEN** a contradiction record names evidence that contradicts a claim
- **THEN** the claim SHALL retain those contradictory evidence IDs or validation SHALL fail

### Requirement: RAO-005 Durable research replay

Research replay SHALL be derived from append-only recorded research events rather than fabricated agent lifecycle traces.

#### Scenario: Replay research activity
- **WHEN** a research store replays its event history
- **THEN** events SHALL be returned in recorded sequence order and SHALL represent only actions that were actually appended
