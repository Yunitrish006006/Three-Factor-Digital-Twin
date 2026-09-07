# Pre-Registered Protocol

## Identity

- Change: `compare-pure-rnn-3d-field`
- Protocol version: `1.0`
- Registration date: `2026-08-17`
- Status before execution: `REGISTERED_NOT_RUN`
- Related IDs: `RQ-RNN3D-01`, `CLM-RNN3D-01`, `EVD-018`, `HRL-011`, `SYN-010`

## Dataset and Units

- Dataset: eight canonical controlled scenarios from `build_validation_scenarios()`.
- Sparse input: the same eight synthesized corner-sensor observations used by IDW and base calibration.
- Truth: the same synthetic dense 16 × 12 × 6 field used by existing full-field evaluation.
- Folds: eight leave-one-scenario-out folds; no scenario is removed after seeing results.
- RNN training points: deterministic 96-point subsample per training scenario, identical to the LOO hybrid sampling rule.
- Test points: all 1,152 grid points in every held-out scenario.

## Fixed Pure RNN

- Architecture: vanilla Elman RNN, one recurrent hidden layer, linear three-output head.
- Sequence length: 8 sensor tokens in scenario sensor order.
- Hidden units: 8.
- Epochs: 40.
- Batch size: 32.
- Learning rate: 0.01.
- Gradient clip: 1.0.
- Seed: 42 plus `97 × fold_index`.
- Inputs: sensor coordinates and observed metrics plus query coordinates and current scenario context described in `research.md`.
- Forbidden inputs: physics/base estimates, residual targets, IDW values, target-point truth, held-out dense truth, or other test targets.
- Standardization: fit input and target means/scales using training-fold samples only; minimum scale `1e-6`.

## Fixed Comparison

- Methods: `idw`, `base_model`, `pure_rnn`, `loo_hybrid`.
- IDW and base use the same held-out sparse observations already registered by the canonical experiment.
- Pure RNN and hybrid train only on the same seven training scenarios and deterministic 96 points per scenario.
- Hybrid retains its registered hidden dimension, epochs, learning rate, L2, Fourier configuration, and fold seed.
- Metric: per-factor full-field MAE, averaged equally across eight held-out scenario folds.
- Per-fold MAE, averages, pairwise reductions, training diagnostics, input hashes, and non-winning methods remain visible.

## Decision Rules

- Status is `COMPLETE` only when eight folds exist, all four methods have finite MAE for all three factors, shared fold/input hashes pass, and RNN training losses remain finite.
- `CLM-RNN3D-01` is supported by complete parity-audited execution, regardless of rank.
- No model size, epoch, input feature, sensor order, or seed change is allowed after the first full run without a new protocol version.
- A poor RNN result SHALL be retained and SHALL NOT be replaced by post-outcome tuning.

## Expected Command and Evidence

| Command | Output |
| --- | --- |
| `python3 scripts/run_rnn_3d_field_comparison.py` | `outputs/data/rnn_3d_field_comparison.json` |

## Failure Handling

Missing methods, mismatched hashes, non-finite values, training failure, or incomplete folds produce `PARTIAL` or `NOT_EVALUATED`. Failed and adverse folds remain in evidence.
