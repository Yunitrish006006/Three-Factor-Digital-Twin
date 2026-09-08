# Startup PI boundary
## ADDED Requirements
### Requirement: SPB-001 Startup gains require subsequent PI-quality retention
Startup assistance SHALL use identical bounded selection and irreversible bumpless handover rules across devices.
#### Scenario: A candidate improves early response but harms subsequent PI performance
- **WHEN** late quality or acquisition constraints fail
- **THEN** selection SHALL reject that candidate and preserve the adverse evidence
- **AND** purePI fallback SHALL not count as startup improvement
