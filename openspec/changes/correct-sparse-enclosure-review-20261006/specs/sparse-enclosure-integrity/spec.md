# Corrective requirements

## ADDED Requirements

### Requirement: ENC-401 Raw-sensor warning contract

The corrected controller SHALL require original plate/air observations and trigger common warning from estimated source or either original thermal observation.

#### Scenario: Filter suppresses an observed threshold crossing

- **WHEN** raw plate or air is above warning while posterior is below
- **THEN** corrected control SHALL request maximum PWM before applying the shared slew limiter
- **AND** hidden-source truth SHALL never be passed as an observation

### Requirement: ENC-402 Independent scoring provenance

The integrity audit SHALL check timestamps, truth continuity, initial conditions, exogenous inputs, plant dynamics and archived bytes separately from source-blind algorithm replay.

#### Scenario: Wrongly paired scoring truth

- **WHEN** CSV truth is reordered or time shifted with metrics recomputed
- **THEN** the added scorer audit SHALL reject the corrupted record
- **AND** original frozen study bytes SHALL remain unchanged

### Requirement: SYN-401 Content-bound observed QA

Automatic synchronization SHALL report observed QA only from explicit dated records bound to identical artifact hashes.

#### Scenario: Content changed after visual observation

- **WHEN** current artifact bytes differ from the observed artifact hash
- **THEN** current QA SHALL be STALE and cannot satisfy visual delivery acceptance
- **AND** the original observation date and checks SHALL remain unchanged

### Requirement: ENC-403 Capacity interpretation stays retrospective

Capacity diagnostics SHALL distinguish held-input steady reachability from actual finite-time overtemperature and SHALL not alter original hypotheses.

#### Scenario: Maximum fan cannot attain a steady temperature limit

- **WHEN** the assumed network has maximum-fan equilibrium above the limit
- **THEN** reports SHALL identify the physical-capacity restriction
- **AND** count actual sampled overtemperature separately
