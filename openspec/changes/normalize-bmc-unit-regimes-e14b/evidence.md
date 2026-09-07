# E14B Post-Run Evidence

## Outcome

`h_data_02_supported`. All eight preregistered unit-correctness gates passed.

## Results

- Preserved rows: 4,038, with exact E14A and oracle per-file counts.
- Raw-unit files: exactly `202307191620.csv`, `202307201552.csv`, and `202307211550.csv`.
- Unit-indicator disagreements: 0 sections.
- Other 28 files: scale factors remained 1.0.
- Normalized inlet/outlet/CPU target range: 29.0 to 77.5 degrees C.
- Normalized summed PSU power range: 136 to 513 W.
- Known example: 34.5/34.5/36.5/37.0 degrees C and 245 W, exact.

## Evidence Decision

E14B supports the section-level powers-of-ten normalization for this frozen dataset. It does not support model accuracy. E13 remains parser-invalidated and its original test files remain ineligible for a new confirmation claim.

## Artifacts

- Result: `outputs/data/enclosure/bmc_unit_regimes_e14b_result.json`
- Result SHA-256: `db1525cf0dc11d5c84342415e3658f6905ef27e379b2be85c56fe5f914dd7ef4`
