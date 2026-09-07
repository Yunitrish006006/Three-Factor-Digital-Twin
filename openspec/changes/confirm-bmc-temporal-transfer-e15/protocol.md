# Protocol

## Frozen inputs

- Model: `outputs/data/enclosure/bmc_corrected_e14c_frozen_model.json`
- Required model SHA-256: `609048167f2a7e261bee45e2d935c650be7a55184cdce3966b014e6cd1e5ba84`
- Parser and normalization: frozen E14B section-aware implementation
- Baseline: inlet temperature plus 8.0 degrees C
- Candidate: load-aware ridge, lambda 1.0, coefficients from the frozen file

## Confirmation files

Use exactly these previously unused complete exports:

`202308022155.csv`, `202308022222.csv`, `202308051737.csv`,
`202308051757.csv`, `202308051827.csv`, `202308052003.csv`,
`202309212229.csv`, `202309221110.csv`, `202309222035.csv`,
`202310252044.csv`, `202310252102.csv`, `202310252230.csv`,
`202405241724.csv`, and `202405241940.csv`.

## Data-quality gates

- All 14 files download and match manifest SHA-256 values.
- Every file yields at least 10 complete BMC rows.
- Every accepted row and BMC section has a concordant unit regime.
- Both models produce finite predictions within [-50, 200] degrees C.

## Accuracy gates

- Aggregate MAE, RMSE, and P95 gains are each at least 0.2 degrees C.
- Macro per-run MAE gain is at least 0.2 degrees C.
- The 20,000-resample run-block bootstrap 95% interval has lower bound above 0.
- The candidate wins at least 9 of 14 individual runs.

## Sequential rule

Write the manifest after download, then execute the evaluator once. No model
changes, threshold changes, or file substitutions are allowed after outcomes
are loaded. Preserve null, adverse, failed, and missing results.
