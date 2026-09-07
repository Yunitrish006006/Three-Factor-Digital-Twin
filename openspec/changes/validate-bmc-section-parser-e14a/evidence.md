# E14A Post-Run Evidence

## Outcome

`h_data_01_not_supported`. The section-aware parser achieved exact oracle agreement on all 31 files, accepted 4,038 BMC rows, accepted no non-BMC source tags, and excluded the known host row. The preregistered temperature sanity gate nevertheless failed.

## Gate Results

- Exact manifest and all 31 raw hashes: pass.
- Production/oracle row-count agreement: 31/31 pass.
- At least one BMC row per file: pass.
- Accepted source violations: 0, pass.
- Known host timestamp `2024-01-04T16:07:43Z`: excluded, pass.
- All mapped temperatures below 1,000 degrees C: fail.

## Observed Extrema

Accepted inlet, outlet, CPU1, and target maxima were 47,000, 45,000, 59,500, and 59,500 raw units. Summed PSU power reached 326,000,000 raw units. These values occurred in three selection files and remained within correctly identified `sdgp/bmc` sections.

## Evidence Decision

The cross-section host leakage is corrected, but H-DATA-01 remains unsupported because source-aware selection alone does not recover physical units. The three files form a coherent millidegree-Celsius and microwatt regime consistent with Linux hwmon and OpenBMC scale conventions. Any unit conversion requires a separately preregistered study.

## Artifacts

- Result: `outputs/data/enclosure/bmc_section_parser_e14a_result.json`
- Result SHA-256: `348d6525a7f495302a7e076f38f4705c5d3214a62d13546961cf8e1546e94833`
