# Sparse enclosure candidate delta

## ADDED Requirements

### Requirement: ENC-301 Explicit conductive and convective paths

The candidate SHALL expose separate heat-capacity, contact-conduction, air-exchange and fan-delay parameters and preserve internal heat exchange balance.

#### Scenario: Constructing the candidate

- **WHEN** a synthetic rig is evaluated
- **THEN** all parameter units, assumptions, measured inputs and excluded truth SHALL be recorded
- **AND** it SHALL not inherit room or physical-device validity

### Requirement: ENC-302 Source-blind calibration and correction

Identification and sparse updates SHALL receive only declared input observations, and SHALL never consume hidden-source truth.

#### Scenario: Changing truth used for scoring

- **WHEN** held-out truth values are changed without changing inputs
- **THEN** observer estimates and command choices SHALL remain unchanged
- **AND** only evaluation scores SHALL change

### Requirement: ENC-303 Frozen fair ablations

Every compared method SHALL share preregistered workloads, observations, command limits and scoring, with calibration and freeze preceding evaluation.

#### Scenario: Comparing horizons

- **WHEN** H=1 and H=6 are evaluated
- **THEN** settings other than horizon SHALL match
- **AND** uncertainty, degradation, command violations and out-of-domain samples SHALL remain visible

### Requirement: SYN-301 Candidate evidence synchronization

The candidate status, quantitative results and scope limits SHALL remain synchronized across research artifacts.

#### Scenario: Reporting synthetic results

- **WHEN** an output reports this candidate
- **THEN** it SHALL identify temperature-only synthetic evidence, sparse inputs and unevaluated physical actuation
- **AND** incomplete publication or visual checks SHALL remain explicit
