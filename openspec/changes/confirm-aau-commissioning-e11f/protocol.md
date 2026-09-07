# Protocol

## Frozen Inputs

- E11H result SHA-256: `b76ecfe3e597d0641515df60b0d6636ed9a0ff1e23ebcb2852a225d4eee490e9`.
- Frozen metadata SHA-256: `0b667ca8bb959e332aeff0155b9dceb1318dca3f91a26c1aa5552fb6bfef7055`.
- Eleven 4 MiB E11F starts: `55838224, 119653337, 183468450, 247283563, 311098676, 374913789, 438728902, 502544015, 566359128, 630174241, 693989354`.
- The downloader rejects overlap with every existing downloaded manifest.
- First and last partial records per fragment are discarded.

## Fixed Evaluation

- Baseline: local IDW, `k=3`, power `p=2`.
- Model: exact E11H `selected_models`, including baseline fallbacks, median offsets, Huber slopes, and intercepts.
- E11G base map: exact hash referenced by E11H.
- No calibration, model selection, coefficient update, clipping change, or sensor exclusion is permitted.

## Confirmation Gate

H-ENC-05 is supported only if all conditions hold on E11F:

- MAE, RMSE, and P95 are strictly lower than local IDW.
- At least 26 of 42 sensors have strictly lower MAE.
- The 20,000-replicate day-block bootstrap lower bound is above zero with seed `20260823`.
- Absolute MAE is at most 1.25 degrees Celsius, RMSE at most 1.90, and P95 at most 4.00.

Calendar-day overlap with E11E/E11H is a mandatory applicability diagnostic, not a post hoc exclusion criterion. All E11F records remain in the primary result.

