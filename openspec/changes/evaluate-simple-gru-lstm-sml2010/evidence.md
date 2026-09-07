# Post-run Evidence

## Run identity

- Study: `E9-GRU-LSTM-SIMPLE-SAME-DATA`
- Result: `outputs/data/public_benchmarks/gru_lstm_sml2010_comparison.json`
- Result SHA-256: `129c939e59a43ec4c2e602e3627539616aa38af92a540118089e8650e6bff5e6`
- Execution status: `COMPLETE`
- Protocol deviations: none
- Focused tests before the full run: 9 passed

## Data and parity

All 12 preregistered SML2010 S2 target-horizon cases completed. The 15, 60,
and 1440 minute horizon audits all preserved the existing train/test endpoint
and input hashes. GRU, LSTM, vanilla RNN, persistence, sequence linear
regression, and the physics-structured readout used identical eligible test
rows. Parameter counts were 148, 169, and 140 for vanilla RNN, GRU, and LSTM,
respectively, satisfying the 15% budget rule. All losses and predictions were
finite.

## Observed results

- Lowest-MAE counts: sequence linear regression 7/12, persistence 5/12,
  physics readout 0/12, vanilla RNN 0/12, GRU 0/12, LSTM 0/12.
- GRU beat vanilla RNN in 2/12 cases, both 60-minute humidity targets. Its
  median per-case relative MAE reduction was -12.880146%.
- LSTM beat vanilla RNN in 0/12 cases. Its median per-case relative MAE
  reduction was -11.368865%.
- No gated model reached the preregistered 8/12 win requirement or a positive
  median relative reduction, so no candidate was forwarded.

Training standardized MSE decreased for every model and horizon. For example,
the 15-minute GRU decreased from 0.44204227 to 0.01323434 and LSTM from
0.69339437 to 0.02254791. The adverse test result is therefore not explained
by non-finite or wholly failed optimization.

## Decision

`EQ-RNNGATE-01` is evaluated. `H-RNNGATE-01` is **not supported**. GRU and
LSTM are now evaluated only for this single-seed, four-record-history SML2010
temporal comparison. The run does not support gated-model superiority, a full
3-D field claim, computer-enclosure transfer, physical sensing, or PID control.
Post-outcome changes to hidden size, history, epochs, or seed require a new
protocol and cannot replace this result.
