# Public scenes and practical LQR preparation delta

## ADDED Requirements

### Requirement: SCN-801 Evidence-bounded public scene discovery

Public scenario preparation SHALL distinguish documented capabilities, live-service checks, local model execution and recorded datasets with source/provenance and explicit limits.

#### Scenario: A service probe fails

- **WHEN** a valid-TLS request cannot reach a public endpoint
- **THEN** the actual error SHALL remain visible and SHALL not be generalized to permanent service unavailability

### Requirement: LQR-801 Practical source-faithful LQR guide

LQR preparation SHALL cover feasible equilibrium, model/state access, discrete Riccati/gain/stability checks, weights/scales and constrained/estimated-state limitations, distinguishing modern teaching equations from original Kalman formulas.

#### Scenario: The fan command is limited

- **WHEN** unconstrained LQR output is saturated or slew-limited
- **THEN** the guide SHALL not retain an unconditional unconstrained optimality or hardware safety claim

### Requirement: SYN-801 Observed HTML preparation delivery

New candidate and teaching content SHALL use the existing professor HTML with first-person talk, primary links and exact hash-bound observed responsive/interaction/offline/print QA.

#### Scenario: A previous QA record exists

- **WHEN** report bytes change
- **THEN** new observation evidence SHALL be produced in a new stage without rewriting older frozen QA
