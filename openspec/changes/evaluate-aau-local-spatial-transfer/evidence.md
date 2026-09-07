# E11C Post-Run Evidence

## Decision

- Hypothesis: `H-ENC-03`.
- Decision: `not_supported`.
- The fixed local IDW improved aggregate MAE, RMSE, and P95 error and had a positive day-block-bootstrap interval, but it won only 21 of 42 sensors rather than the required 26.
- No offset, sensor exclusion, neighborhood size, distance power, seed, bootstrap rule, or decision threshold was changed after confirmation metrics were observed.

## Provenance

- Dataset: *Data from the AAU Server Room* v4, DOI `10.5281/zenodo.19398358`.
- Confirmation sample: 11 gap-centered, E11B-disjoint ranges of 4 MiB each.
- Manifest: `outputs/data/enclosure/aau_temperature_ranges_e11c_manifest.json` (`sha256:3ff9dcaa9446b890bcaa3ffcefd0440c75ec0e3753dc6a591783349cbb2a54a6`).
- Result: `outputs/data/enclosure/aau_local_idw_confirmation.json` (`sha256:0b667ca8bb959e332aeff0155b9dceb1318dca3f91a26c1aa5552fb6bfef7055`).
- Raw fragments remain under `/tmp/aau_server_room_temperature_ranges_e11c` and are not redistributed.
- The byte-zero CSV header supplies schema only. No E11B observation row contributes to E11C metrics.

## Run Accounting

- Fragments: 11; overlap check: passed.
- Rows seen and accepted: 89,587; malformed or non-finite rows: 0.
- Boundary records discarded: 22.
- Eligible one-minute snapshots: 1,505.
- Eligible sensors: 42; six ambiguous cooling-unit channels remained excluded.
- Bootstrap: 11 calendar-day blocks, seed `20260823`, 20,000 replicates.

## Confirmatory Results

| Method | Macro MAE (deg C) | RMSE (deg C) | P95 absolute error (deg C) |
|---|---:|---:|---:|
| Nearest neighbor | 1.301 | 2.218 | 5.745 |
| Local IDW, `k=3, p=2` | **1.223** | **1.886** | **4.026** |
| Global IDW, `p=2` | 1.844 | 2.285 | 4.507 |

- Paired MAE improvement, nearest minus local: 0.0783 deg C.
- Day-block-bootstrap 95% interval: [0.0546, 0.1063] deg C.
- Per-sensor result: local IDW 21 wins, nearest neighbor 21 wins, zero ties.
- Conditions passed: lower MAE, lower RMSE, positive bootstrap lower bound.
- Condition failed: at least 26/42 local-IDW sensor wins.

The aggregate improvement is reproducible within the sampled days, but the preregistered breadth requirement failed. H-ENC-03 is therefore not supported.

## Exploratory Diagnostic

This diagnostic was not part of the confirmatory decision:

| Sensor label group | Local-IDW wins | Nearest-neighbor wins |
|---|---:|---:|
| Gradient | 0/5 | 5/5 |
| Rack back | 17/28 | 11/28 |
| Rack front | 4/9 | 5/9 |

The heterogeneity suggests that one Euclidean neighborhood rule does not fit every sensor role. It does not establish rack topology, airflow direction, or thermal stratification as the cause.

## Deviations and Failures Before Metrics

- The initial 12-offset formula failed the overlap guard before retrieval. It was replaced, before successful download, by one centered range in each of the 11 gaps between E11B ranges (RDL-017).
- The first runner attempt failed at package import (RDL-019).
- The second runner attempt failed because the parser coupled byte-zero header discovery with observation data (RDL-020).
- Both runner failures occurred before metric execution. The third attempt used the unchanged registered model and decision rule.

## Claim Boundary

E11C supports a bounded descriptive statement that local three-neighbor IDW lowered aggregate error on the disjoint sampled AAU task. It does not support H-ENC-03's sensor-coverage claim and does not validate CFD, causal cooling control, energy savings, component hotspots, explicit rack topology, or arbitrary data centers.

## Artifact and Validation Record

- Chinese thesis Markdown/DOCX/PDF, IEEE PDF, two presentation PPTX files, and presentation outlines rebuilt successfully.
- IEEE output: 7 pages, within the IoTaIS 6--7 page target after removing duplicated enclosure discussion; all registered E11B/E11C metrics remain.
- Full unit suite: 180 tests passed.
- Existing thesis result verification: 89 passed, zero failed, zero missing.
- E11B and E11C consistency verifiers: seven synchronized sources passed for each.
- Room design validation: passed.
- Research OpenSpec validation: 14 spec files, 117 requirements, 230 scenarios, five active changes.
- Current-source E11B/E11C stale-status search: no matches.
- Non-fatal PDF font and box warnings remain documented in RDL-013. E11C execution and submission-format difficulties are retained in RDL-015 through RDL-023.
