# E14A Research Questions and Hypotheses

## Research Question

Can a source-aware parser reproduce independently counted BMC rows across every frozen E12/E13 source file while rejecting all host and non-BMC sections?

## Hypothesis H-DATA-01

The corrected parser will achieve exact parser-oracle row-count agreement on 31 of 31 files, accept zero rows whose `_measurement` or `device_id` differs from `sdgp` and `bmc`, reject the known host row at `2024-01-04T16:07:43Z` in `202401050043.csv`, and produce no mapped temperature at or above 1,000 degrees C.

## Null and Adverse Outcomes

- Any count disagreement or non-BMC acceptance leaves H-DATA-01 unsupported.
- A file with no valid BMC section is retained as a failed file, not silently excluded.
- Values that remain extreme after semantic correction are reported without clipping or model-based deletion.
