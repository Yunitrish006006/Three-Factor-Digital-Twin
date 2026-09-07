# Protocol

## Dataset and Independent Confirmation Sample

- Dataset: AAU Server Room v4, DOI `10.5281/zenodo.19398358`.
- Source object size: 706,160,545 bytes.
- Range size: 4,194,304 bytes.
- Confirmation offsets, fixed before successful download: `31907556`, `95722669`, `159537782`, `223352894`, `287168007`, `350983120`, `414798233`, `478613346`, `542428459`, `606243571`, `670058684`.
- Each offset is the integer midpoint of two adjacent E11B start offsets. This places one 4 MiB range at the center of each of the 11 inter-range gaps.
- Every interval is checked against all E11B intervals; any overlap makes the run invalid. The initial 12-offset formula was rejected by this guard before network retrieval and is retained as `RDL-017`, not as confirmation data.
- Fragment boundary repair, one-minute median aggregation, 42 included PT100 locations, and six excluded ambiguous channels remain identical to E11B.
- The source byte-zero CSV header is used only as a fixed column schema. No byte-zero observation row or E11B fragment contributes to E11C metrics.

## Unit of Analysis and Exclusions

- Primary unit: one held-out sensor at one eligible one-minute snapshot.
- Per-sensor unit: MAE over all eligible confirmation snapshots.
- The run is not evaluable if the sensor count is not 42, fewer than 120 snapshots remain, a confirmation interval overlaps E11B, or any offset changes after retrieval starts.

## Fixed Methods

- One-nearest-neighbor baseline using 3-D Euclidean distance.
- Local IDW using exactly the three nearest observed sensors, distance power `p=2`.
- Global IDW using all observed sensors and `p=2`, reported as secondary context.
- Distance ties are ordered by stable sensor name; no geometry, sensor, `k`, or `p` tuning is allowed from E11C results.

## Metrics and Uncertainty

- Macro MAE, RMSE, and P95 absolute error over all sensor-minute predictions.
- Per-sensor MAE and strict pairwise local-IDW wins, losses, and ties against nearest neighbor.
- Paired improvement is `abs_error_nearest - abs_error_local`.
- A 20,000-replicate calendar-day block bootstrap uses seed `20260823`; its percentile 95% interval is reported.

## Decision Rule

H-ENC-03 is supported only if all conditions hold:

1. Local IDW macro MAE is lower than nearest neighbor.
2. Local IDW macro RMSE is lower than nearest neighbor.
3. Local IDW has lower per-sensor MAE for at least 26 of 42 sensors.
4. The lower bound of the paired day-block-bootstrap 95% interval is greater than zero.

Otherwise H-ENC-03 is `not_supported`; failed acquisition or minimum-data conditions produce `not_evaluable`.
