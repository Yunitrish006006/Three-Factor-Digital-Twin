# Simple GRU/LSTM Same-Data Evidence

## ADDED Requirements

### Requirement: EVD-039 Fixed-budget gated recurrent comparison

The project SHALL compare vanilla RNN, GRU, and LSTM on the same SML2010 S2
temporal endpoints with preregistered, approximately matched parameter budgets.

#### Scenario: Building recurrent inputs

- **WHEN** the gated comparison is prepared
- **THEN** all recurrent models receive identical four-record standardized sequences, training endpoints, test endpoints, targets, and metric functions
- **AND** standardization is fitted only on training records

#### Scenario: Fitting recurrent models

- **WHEN** vanilla RNN, GRU, and LSTM are trained
- **THEN** hidden dimensions, epochs, batch size, optimizer settings, gradient clipping, and seed match the preregistered protocol
- **AND** no architecture or stopping decision is selected from test performance

### Requirement: EVD-040 Preserve complete gated-model outcomes

The project SHALL retain all 12 case outcomes, parity hashes, training
diagnostics, parameter counts, adverse results, and the bounded decision.

#### Scenario: A parity or finite-value check fails

- **WHEN** any comparator is missing, a shared hash differs, or training or prediction is non-finite
- **THEN** the study is `NOT_EVALUATED` and no partial ranking supports a claim

#### Scenario: The comparison completes

- **WHEN** all 12 cases and audits pass
- **THEN** GRU and LSTM become evaluated only for the SML2010 same-data temporal task
- **AND** candidate forwarding requires at least 8/12 MAE wins over vanilla RNN and positive median relative MAE reduction
