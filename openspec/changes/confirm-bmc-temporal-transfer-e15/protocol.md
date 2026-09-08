# Protocol

## Frozen inputs

- Model: `outputs/data/enclosure/bmc_corrected_e14c_frozen_model.json`
- Historical E14C container SHA-256: `609048167f2a7e261bee45e2d935c650be7a55184cdce3966b014e6cd1e5ba84`
- Required canonical `frozen_models` content SHA-256: `cff6dfbf05fa0f81bff5ebf5cd4d812575b4ec89c5946e8eb1c15384aa8c7935`
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

## Pre-execution integrity amendment (2026-09-07)

The full E14C JSON container could not be reconstructed byte-for-byte because it includes serialization-sensitive surrounding evidence. Before any E15 file was downloaded or outcome loaded, the gate was narrowed to a canonical hash of the actual baseline and ridge model objects. The model family, coefficients, means, scales, feature order, thresholds, filenames, and decision rules are unchanged. E15 remains `NOT_EVALUATED`.

## Pre-outcome execution-record amendment (2026-09-07)

After downloading the fixed files, but before parsing any confirmation outcomes,
read-only methodology review identified that a parser exception or empty dataset
could terminate the evaluator before writing its result. An external execution
wrapper now creates an exclusive attempt receipt before invoking the unchanged
evaluator, captures its complete output, and records success or failure with
input and result hashes. A failed or interrupted attempt must not be rerun.
This wrapper changes only failure preservation.

The same review also found that the evaluator's row-concordance flag merely
repeated the section-median flag. Before outcome access, the evaluator was
corrected to independently apply the existing E14B cutoffs (raw CPU temperature
>= 1000 and raw summed power >= 100000) to every accepted row and require its
regime to agree with the section's applied scales. This enforces the already
registered every-row gate; it does not rescale, exclude, or replace any row.
No model, parser, numerical threshold, file, metric, bootstrap, or hypothesis
rule is changed. P95 retains E15's tested linear interpolation convention.
