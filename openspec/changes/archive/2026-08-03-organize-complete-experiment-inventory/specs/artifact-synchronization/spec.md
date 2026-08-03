# Artifact Synchronization Delta

## ADDED Requirements

### Requirement: SYN-008 Master experiment overview synchronization

The master experiment overview SHALL agree with the current thesis sources and machine-readable evidence without introducing a separate progress level.

#### Scenario: Updating a reconciled metric

- **WHEN** reconciliation changes a metric shown in a synchronized source
- **THEN** its build source and generated outputs SHALL be rebuilt
- **AND** all applicable occurrences of the superseded value SHALL be removed or clearly labeled as legacy

#### Scenario: Reporting an unexecuted experiment

- **WHEN** E8, Kalman filtering, or another future protocol is listed
- **THEN** its status SHALL remain `NOT_EVALUATED` or protocol-only
- **AND** it SHALL not be grouped with completed empirical results

## MODIFIED Requirements

## REMOVED Requirements
