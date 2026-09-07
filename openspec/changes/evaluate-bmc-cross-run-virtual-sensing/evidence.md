# E12 Post-Run Evidence

## Outcome

`h_enc_06_not_supported` due to `pretest_data_quality_failure`. No model was selected, no frozen model was written, and no final-test file was opened.

## Observed Failure

The preregistered minimum was 30 valid BMC rows per complete file. Two training files had 13 and 14 valid rows. Three selection files had 16, 25, and 27 valid rows. The runner stopped at the first failing training file; a subsequent diagnostic was restricted to training and selection files and confirmed all five failures.

## Evidence Decisions

- Preserve the 30-row gate and E12 null outcome; do not remove files or lower the threshold post hoc.
- Preserve all 14 final-test files as unopened.
- Permit a separately preregistered study to use a lower run-size gate only if it records that the decision came from development-split availability, not final-test performance.

## Artifacts

- Manifest SHA-256: `9f0ef4e25805af89ac1f59ae1e13f39bf036a510dcbe07f4a2d3ccd4f78cad74`
- Machine-readable outcome: `outputs/data/enclosure/bmc_cross_run_e12_result.json`
