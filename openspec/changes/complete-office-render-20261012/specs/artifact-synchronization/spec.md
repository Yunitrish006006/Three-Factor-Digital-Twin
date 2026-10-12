# Office Rendering Delta

## ADDED Requirements

### Requirement: SYN-601 Observed Office acceptance

Office visual acceptance SHALL require actual rendering and observed complete page coverage tied to exact source and evidence hashes.

#### Scenario: Missing or stale observation

- **WHEN** source bytes change or page coverage/render evidence is missing
- **THEN** acceptance SHALL remain incomplete or stale
- **AND** automatic rendering or structural checks SHALL not manufacture visual acceptance

### Requirement: SYN-602 Source-level layout repairs

Observed layout defects SHALL be repaired in canonical builders and reflected in every affected synchronized output while retaining research metrics and boundaries.

#### Scenario: Repairing a slide

- **WHEN** actual rendering reveals clipping or overlap
- **THEN** the responsible source layout SHALL be repaired and re-rendered
- **AND** no frozen scientific evidence SHALL be rerun or overwritten

### Requirement: SYN-603 Completed E15 status consistency

Artifact status SHALL distinguish the historical E15 protocol from its already completed same-server confirmation.

#### Scenario: Reporting completed confirmation

- **WHEN** current artifacts describe E15
- **THEN** they SHALL retain the executed 14-file/3112-row result and same-server temporal/workload boundary
- **AND** they SHALL not call it unopened, rerun it, or expand it to hardware/control evidence
