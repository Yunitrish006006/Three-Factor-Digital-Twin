# Protocol

## Dataset and E11E Development Split

- Dataset: AAU Server Room v4 `AAU_temperature_and_power_use.csv`, DOI `10.5281/zenodo.19398358`.
- Eleven observation ranges, each 4,194,304 bytes.
- Fixed E11E starts: `47861335`, `111676448`, `175491561`, `239306674`, `303121787`, `366936900`, `430752013`, `494567126`, `558382239`, `622197352`, `686012465`.
- Abort if any E11E range overlaps E11B, E11C, E11D, another E11E range, or the reserved E11F ranges.
- Reuse the E11D schema-only byte-zero request policy and discard two boundary records per fragment.
- Aggregate accepted values to complete one-minute snapshots over the frozen 42 sensors.

## Untouched E11F Reservation

- Reserved starts: `55838224`, `119653337`, `183468450`, `247283563`, `311098676`, `374913789`, `438728902`, `502544015`, `566359128`, `630174241`, `693989354`.
- E11F bytes SHALL NOT be downloaded or inspected during E11E.

## Frozen Metadata and Baselines

- Sensor names, roles, and coordinates come from E11C result SHA-256 `0b667ca8bb959e332aeff0155b9dceb1318dca3f91a26c1aa5552fb6bfef7055`.
- Baseline B1: unstratified local IDW, `k=3`, `p=2`.
- Baseline B2: same-role leave-one-sensor-out arithmetic mean.
- The stronger baseline is the one with lower E11E MAE, then lower P95, then lexical model ID.

## Frozen Candidate Grid

- Same-role local IDW: `k in {1,3,5}`, `p in {1,2}`.
- Hierarchical blend: `alpha * role_local_idw + (1-alpha) * role_mean`, where `alpha in {0.25,0.50,0.75}` for every registered `k,p` pair.
- When a role has fewer than `k` eligible peers, use all available same-role peers; this applies to `k=5` for the five-sensor gradient role.
- Distance is 3D Euclidean distance in meters. Ties use sensor ID lexical order.
- No candidate, parameter, sensor exclusion, role reassignment, metric, or threshold may be added after E11E observations are read.

## Metrics and Forwarding Gate

- Report MAE, RMSE, P95 absolute error, per-sensor MAE, per-role metrics, and calendar-day paired bootstrap uncertainty.
- Bootstrap: 20,000 replicates, seed `20260823`.
- A candidate passes only if, versus the stronger baseline: MAE, RMSE, and P95 are all lower; at least 26/42 sensors have lower MAE; and the paired MAE-improvement 95% CI lower bound is above zero.
- It must also meet MAE <= 1.25 C, RMSE <= 1.90 C, and P95 <= 4.00 C.
- If multiple candidates pass, select lowest MAE, then P95, then RMSE, then lexical model ID.
- If none pass, record `no_candidate_forwarded` and do not run E11F.
