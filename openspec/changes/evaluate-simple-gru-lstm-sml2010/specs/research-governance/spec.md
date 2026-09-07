# Gated Recurrent Research Governance

## ADDED Requirements

### Requirement: RGV-009 Bounded gated-model interpretation

The project SHALL not generalize a single-seed SML2010 GRU/LSTM comparison to
all recurrent architectures, dense spatial fields, enclosures, or control.

#### Scenario: A gated model satisfies the forwarding gate

- **WHEN** GRU or LSTM meets H-RNNGATE-01
- **THEN** it may be called a candidate for a separately registered full 3-D comparison
- **AND** it SHALL NOT be called universally superior or deployment-ready

#### Scenario: Neither gated model satisfies the gate

- **WHEN** neither model reaches the preregistered case-win and median-reduction thresholds
- **THEN** the adverse result remains visible and GRU/LSTM are not forwarded from this task
