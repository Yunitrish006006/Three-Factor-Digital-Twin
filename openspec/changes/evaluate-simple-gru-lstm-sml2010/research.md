# Research Questions and Hypothesis

## EQ-RNNGATE-01

Under identical SML2010 inputs, endpoints, split, targets, training epochs, and
approximately matched parameter counts, do GRU or LSTM improve upon the
registered vanilla RNN?

## H-RNNGATE-01

At least one gated model will beat vanilla RNN MAE in at least 8 of 12 cases
and have a positive median per-case relative MAE reduction versus vanilla RNN.

## Intended bounded claim

If every parity and finite-training check passes, GRU and LSTM become evaluated
on the SML2010 S2 same-data temporal task. A model satisfying H-RNNGATE-01 may
be forwarded as a candidate for a separately registered full 3-D comparison.

## Competing explanations and threats

- A gain may come from parameter count rather than gating; recurrent parameter
  counts are therefore kept within about 15% of the vanilla RNN.
- One fixed seed can be unstable; this simplified run is preliminary and does
  not support architecture-wide superiority.
- A four-record history may be too short for gate advantages to emerge.
- Temperature and humidity cases have different units, so raw MAE values are
  not averaged across targets; case wins and relative reductions are used.
- SML2010 is a public building task, not measured dense 3-D truth, a computer
  enclosure, or a closed-loop control experiment.

## Ethics and safety

The experiment uses existing normalized public data and performs no physical
control or human intervention. PID remains outside this execution.
