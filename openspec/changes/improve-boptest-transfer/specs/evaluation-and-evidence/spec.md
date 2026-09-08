# BOPTEST transfer improvement
## ADDED Requirements
### Requirement: BPT-001 Development selection and transfer isolation
The experiment SHALL select only on prior development dates and freeze its controller before new transfer cases.
#### Scenario: Evaluating improvement
- **WHEN** transfer results are opened
- **THEN** controller sources and selected parameters SHALL match the recorded pre-transfer hashes
- **AND** every noise sequence SHALL be shared by comparators and metrics SHALL use simulator truth
- **AND** negative results, generic baseline handover improvements and same-plant limitations SHALL remain visible
