# Model-consistent bounded compensation
## ADDED Requirements
### Requirement: MCC-001 Causal full-model compensation and honest fallback
The controller SHALL use the full identified ARX model and bounded regularized correction under identical cross-plant rules.
#### Scenario: Weak short-horizon actuation or failed identification
- **WHEN** compensation is disabled or the bank is rejected
- **THEN** evidence SHALL distinguish fallback equality, skipped controls and actual improvement
- **AND** all negative results SHALL remain visible in the report and typed 3D research graph
