# Evaluation and Evidence Delta

## ADDED Requirements

### Requirement: EVD-023 Development-Confirmation Separation for Hierarchical Enclosure Models

The project SHALL develop role-local and hierarchical reconstruction candidates on E11E without accessing the reserved E11F confirmation ranges.

#### Scenario: One or more candidates pass every gate

- **WHEN** candidates are scored on the preregistered E11E grid
- **AND** one or more candidates pass all relative, uncertainty, coverage, and absolute thresholds
- **THEN** exactly one candidate is selected by the registered deterministic ordering
- **AND** its complete formula is frozen before E11F retrieval

#### Scenario: No candidate passes every gate

- **WHEN** every candidate fails at least one registered gate
- **THEN** E11E records `no_candidate_forwarded`
- **AND** E11F is not downloaded or executed

#### Scenario: Confirmation bytes remain untouched

- **WHEN** E11E completes or fails
- **THEN** the evidence records that no reserved E11F range was requested

