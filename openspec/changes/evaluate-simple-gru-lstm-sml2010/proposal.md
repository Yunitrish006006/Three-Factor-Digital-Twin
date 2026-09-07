# Proposal: Simple GRU/LSTM Same-Data Comparison

## Research gap

The registered vanilla Elman RNN was lowest-MAE in 0 of 12 SML2010 cases.
That adverse result does not establish whether gated recurrence helps because
GRU and LSTM remain unevaluated.

## Proposed change

Run one lightweight, fixed-budget comparison of vanilla RNN, GRU, and LSTM on
the existing SML2010 S2 endpoint contract. Keep the same four-record history,
targets, horizons, chronological split, test rows, preprocessing, metrics, and
non-recurrent comparators. Match recurrent parameter counts within about 15%
and prohibit tuning after test outcomes are loaded.

## Claim impact

The run may change GRU and LSTM from `NOT_EVALUATED` to `EVALUATED` for this
one public temporal task. It cannot replace the existing 3-D RNN result,
establish recurrent superiority, support a computer-enclosure claim, or imply
that PID has been evaluated.

## Affected synchronized artifacts

- Chinese thesis source, build source, DOCX, and PDF outputs
- English IEEE source, references if needed, and PDF output
- Presentation source, both outlines, and PPTX outputs
- Professor HTML progress report
- Canonical OpenSpec governance, evidence, and synchronization capabilities
