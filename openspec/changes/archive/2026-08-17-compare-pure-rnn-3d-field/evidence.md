# Evidence

## Execution Record

- Command: `PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_rnn_3d_field_comparison.py`
- Runtime environment: Python 3.9.6, repository-local standard-library implementation.
- Run type: first full registered run; no post-outcome architecture or parameter change.
- Created at: `2026-08-17T09:30:12.374802+00:00`.
- Output: `outputs/data/rnn_3d_field_comparison.json`.
- Output SHA-256: `80efe9db9f1f64455c538551845b890667cb75ef8234de51cbc90d4b0139e37b`.
- Output bytes: `40233`.
- Status: `COMPLETE`.
- Evidence class: `CONTROLLED_SYNTHETIC_FULL_FIELD`.

## Protocol Compliance

- 8/8 leave-one-scenario-out folds completed.
- Every fold used 672 training point samples per learned method and all 1,152 held-out grid points.
- Every fold used the registered eight sensor tokens, 8 hidden units, 40 epochs, batch size 32, learning rate 0.01, and fold seed `42 + 97 × fold_index`.
- 8/8 fold parity audits passed; sparse input, query grid, truth field, and training-point hashes were recorded for all methods.
- All RNN epoch losses were finite.
- Pure RNN input feature names contain no physics estimate, residual, truth, or IDW feature.
- No deviations or exclusions occurred.

## Average Full-Field MAE

| Method | Temperature (°C) | Humidity (%RH) | Illuminance (lux) |
| --- | ---: | ---: | ---: |
| IDW | 0.172312 | 0.463263 | 54.905175 |
| Base model | 0.047438 | 0.176487 | 2.026887 |
| Pure RNN | 0.209125 | 0.224112 | 48.142175 |
| LOO hybrid | 0.001650 | 0.005938 | 0.140725 |

LOO hybrid had the lowest MAE for all three average factors and all 24 fold-factor comparisons. Pure RNN was lowest in 0/24.

Relative to IDW, pure RNN temperature MAE was 21.36% higher, while humidity and illuminance MAE were 51.62% and 12.32% lower. Pure RNN was worse than the base model and LOO hybrid for all three average factors. This adverse result is retained without tuning.

## Decisions

| ID | Decision | Basis |
| --- | --- | --- |
| `RQ-RNN3D-01` | evaluated | all eight same-task folds completed with finite four-method metrics |
| `CLM-RNN3D-01` | supported | comparison completeness and parity were satisfied; superiority was not required |
| pure RNN superiority | not supported | pure RNN was lowest in 0/24 fold-factor comparisons |

## Claim Boundary

This result supports only a same-task leave-one-scenario-out comparison on eight canonical controlled synthetic scenarios. It does not provide measured dense 3-D truth, cross-room validation, production RNN integration, or evidence that recurrent models are generally inferior or superior. Sensor-token recurrence is a fixed spatial ordering convention rather than a physical time sequence.
