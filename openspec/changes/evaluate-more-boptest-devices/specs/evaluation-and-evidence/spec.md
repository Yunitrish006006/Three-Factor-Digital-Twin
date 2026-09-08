# Additional device confirmation
## ADDED Requirements
### Requirement: MDV-001 Frozen additional-device evaluation
Additional devices SHALL use frozen shared identification and control with declared native interfaces and equal adaptation budgets.
#### Scenario: A new device fails identification or control
- **WHEN** its model is rejected or its paired control gate fails
- **THEN** evidence SHALL retain the failure without device-specific repair or replacement
- **AND** incomplete evaluations SHALL not count as successful generalization
