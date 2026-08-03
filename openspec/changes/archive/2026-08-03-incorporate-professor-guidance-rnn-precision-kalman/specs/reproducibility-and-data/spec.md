# Reproducibility and Data Delta

## ADDED Requirements

### Requirement: RPD-007 Comparator data-parity audit

Model rankings SHALL be reproducible from a shared endpoint index and SHALL disclose any non-data structural prior.

#### Scenario: Comparing RNN and project methods

- **WHEN** a public-task model comparison is produced
- **THEN** endpoint IDs or a deterministic endpoint hash, train/test counts, timestamp ranges, history length, feature availability, and exclusions SHALL be recorded
- **AND** every ranked comparator SHALL use the same test endpoint IDs

#### Scenario: A method has extra learned data

- **WHEN** a comparator uses pretrained weights learned from another dataset
- **THEN** that additional data source SHALL be disclosed
- **AND** the method SHALL be excluded from the primary same-data ranking unless every compared data-driven method receives an equivalent training-data contract

## MODIFIED Requirements

## REMOVED Requirements
