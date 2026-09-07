# E14C Protocol

## Frozen Inputs

- E12 manifest SHA-256: `9f0ef4e25805af89ac1f59ae1e13f39bf036a510dcbe07f4a2d3ccd4f78cad74`.
- E14B result SHA-256: `db1525cf0dc11d5c84342415e3658f6905ef27e379b2be85c56fe5f914dd7ef4`.
- Reuse the exact 12 training, 5 selection, and 14 retrospective-test files.
- Require at least 10 normalized BMC rows per file.

## Frozen Pipeline

- Reuse inlet-offset and outlet-offset baselines selected by validation MAE.
- Reuse `thermal_pair`, `load_aware`, and `load_aware_interactions` ridge feature sets.
- Reuse lambdas `0.01`, `0.1`, `1.0`, and `10.0`.
- Refit selected baseline and ridge on training plus selection rows.
- Persist the corrected frozen model before loading retrospective-test rows.
- Reuse the 10,000-run bootstrap with seed `20260824`.

## Original Accuracy Gates

- Pooled MAE, RMSE, and P95 gains each at least 0.20 degrees C.
- Macro run MAE gain at least 0.20 degrees C.
- Run-bootstrap 95% confidence-interval lower bound above zero.
- Ridge wins at least 9 of 14 runs.
- All 14 runs evaluable.

## Added Plausibility Gate

- Every baseline and ridge prediction must be finite and in `[-50, 200]` degrees C.

## Decision

- All gates pass: `candidate_eligible_for_new_confirmation`.
- Any gate fails: `candidate_not_eligible_for_confirmation`.
- Neither decision constitutes confirmatory model evidence.
