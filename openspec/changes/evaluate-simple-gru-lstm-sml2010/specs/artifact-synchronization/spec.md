# Gated Recurrent Result Synchronization

## ADDED Requirements

### Requirement: SYN-012 Synchronize GRU/LSTM evidence status

The Chinese thesis, IEEE manuscript, presentation, and professor HTML report
SHALL report the same SML2010 GRU/LSTM configuration, metrics, decision, and
claim boundary after the experiment runs.

#### Scenario: Rendering the completed comparison

- **WHEN** any synchronized artifact discusses GRU or LSTM status
- **THEN** it reports the same 12-case lowest-MAE counts, pairwise vanilla-RNN wins, median relative reductions, and H-RNNGATE-01 decision
- **AND** PID remains `NOT_EVALUATED`
- **AND** the existing vanilla RNN 0/12 and pure RNN 0/24 adverse results remain visible
