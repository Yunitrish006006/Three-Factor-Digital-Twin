# Generality audit
## ADDED Requirements
### Requirement: BGA-001 Separate frozen-date evidence from generality
Reports SHALL distinguish absence of per-date retuning from absence of benchmark-specific development.
#### Scenario: A user requests generality assurance
- **WHEN** all evaluations use the same FMU and coefficients were selected on its development cases
- **THEN** generality SHALL remain unverified even if within-round source hashes match
- **AND** selected hyperparameters and cross-round reuse SHALL be disclosed
