# Evaluation and Evidence Delta Specification

## ADDED Requirements

### Requirement: EVD-012 Published hybrid-method transfer comparison

The project SHALL distinguish a reproducible, paper-inspired method transfer from reproduction of the cited paper's confidential data, physical model, and CNN--LSTM implementation.

#### Scenario: Running the transfer comparison

- **GIVEN** normalized SML2010 records and a compatible project model checkpoint
- **WHEN** `python3 scripts/run_oh2024_inspired_comparison.py` is executed
- **THEN** it SHALL compare persistence, direct linear regression, raw physics prior, the project mapped readout, and an Oh et al. (2024)-inspired additive residual readout
- **AND** every comparator SHALL use the same temperature targets, horizons, samples, chronological `70/30` split, and metric definitions
- **AND** the machine-readable output SHALL include `15`, `60`, and `1440` minute horizons

#### Scenario: Describing method fidelity

- **WHEN** the transfer result is presented in research artifacts
- **THEN** it SHALL state that the transferred residual learner is a fixed ridge-linear surrogate rather than the paper's CNN--LSTM
- **AND** it SHALL state that the paper's BEMS data are confidential
- **AND** it SHALL not claim reproduction of the published numerical results or direct superiority over the published model

#### Scenario: Preserving adverse results

- **WHEN** the transferred method loses to any comparator or fails the pre-registered physics-improvement threshold
- **THEN** the loss SHALL remain in the JSON evidence and synchronized narrative
- **AND** no horizon, target, feature set, or threshold SHALL be removed after observing the result without a new protocol version

## MODIFIED Requirements

## REMOVED Requirements
