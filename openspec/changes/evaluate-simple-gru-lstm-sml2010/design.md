# Design

## Implementation

Add a NumPy-based gated recurrent module beside the existing pure-Python Elman
implementation. Both GRU and LSTM use explicit sequence-to-one forward passes,
backpropagation through the four timesteps, Adam, deterministic initialization,
and one linear four-target output head.

## Shared data flow

The runner first executes the existing registered comparison to recover the
non-recurrent and vanilla metrics. It independently reconstructs the same
eligible endpoints and verifies their hashes before fitting GRU or LSTM. Only
training endpoints fit input and target standardizers. Gated predictions are
then merged into the same 12 case records.

## Leakage controls

- Model dimensions and training settings are fixed in `protocol.md` before run.
- Test labels do not affect standardization, fitting, stopping, or architecture.
- No result-dependent rerun or seed selection is permitted.
- The original vanilla RNN result remains visible even if a gated model wins.

## Compatibility

The new experiment writes a separate JSON and does not overwrite the canonical
vanilla RNN evidence. PID code and enclosure code are unchanged.
