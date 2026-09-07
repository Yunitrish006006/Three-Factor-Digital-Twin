# E13 Protocol

## Frozen Inputs

- Reuse `outputs/data/enclosure/bmc_cross_run_e12_manifest.json` only when its SHA-256 is `9f0ef4e25805af89ac1f59ae1e13f39bf036a510dcbe07f4a2d3ccd4f78cad74`.
- Reuse the exact E12 split of 12 training, 5 selection, and 14 final-test complete files.
- The final-test files were not opened by E12 and SHALL remain unopened until the E13 frozen model is persisted.

## Only Protocol Change

- A complete file is evaluable with at least 10 valid rows rather than E12's 30.
- The threshold is justified by the development-only audit, whose minimum observed count was 13.
- Parsing, target, features, lambdas, baseline selection, model selection, refit, bootstrap seed, metrics, and accuracy gates remain identical to E12.

## Execution Order

1. Verify manifest hash and raw hashes for training and selection files.
2. Parse training and selection files and enforce 10 valid rows per file.
3. Select the offset baseline and ridge candidate, refit on development rows, and write the frozen-model JSON.
4. Record the frozen-model SHA-256.
5. Only then verify and parse final-test files.
6. Write all gates, per-run results, parse counts, and limitations.

## Decision

Support H-ENC-07 only if all 14 files are evaluable and every unchanged E12 accuracy gate passes.
