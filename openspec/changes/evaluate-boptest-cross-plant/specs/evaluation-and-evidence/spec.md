# Shared cross-plant adaptation
## ADDED Requirements
### Requirement: BCP-001 Bounded portable adaptation
The controller SHALL use the same code and bounded adaptation rule on both plants with explicit device-only configuration.
#### Scenario: A new plant is evaluated
- **WHEN** the plant changes
- **THEN** no name-dependent controller branch or manual fit repair SHALL occur
- **AND** data budgets,trial counts,selection order,invalid fits and non-equivalent sensors SHALL be reported
