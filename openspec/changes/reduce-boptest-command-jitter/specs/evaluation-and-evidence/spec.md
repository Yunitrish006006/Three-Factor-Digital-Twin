# Jitter and delay evidence
## ADDED Requirements
### Requirement: BPJ-001 Applied-command and selection audit
The runner SHALL distinguish requested and applied actions and freeze candidates before unseen dates.
#### Scenario: Delay comparison
- **WHEN** an actuator delay is enabled
- **THEN** logged applied actions SHALL reproduce the delay queue
- **AND** all metrics SHALL use simulator truth, common noise and retained adverse cases
