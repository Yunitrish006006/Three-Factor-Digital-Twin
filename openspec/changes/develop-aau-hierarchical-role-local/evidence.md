# Evidence

## Execution Status

- Experiment: E11E
- Purpose: development only
- Decision: `no_candidate_forwarded`
- E11F accessed: false
- Manifest: `outputs/data/enclosure/aau_temperature_ranges_e11e_manifest.json`
- Manifest SHA-256: `873e155bceaaac530f004b1ef14d1cceb8356af83f5a9ace1638ec54a34919d6`
- Result: `outputs/data/enclosure/aau_hierarchical_development.json`
- Result SHA-256: `c345e1320bd7e1aed21fd67f04e661d555a18e6e0fd312f638bc350300eb732a`

## Data Accounting

- 11 independent 4 MiB E11E fragments; all validated as HTTP `206` with exact byte counts and SHA-256 hashes.
- 22 boundary records discarded.
- 89,606 rows seen and accepted; 0 malformed and 0 non-finite values.
- 1,502 complete one-minute snapshots over 12 calendar-day blocks and 42 sensors.
- The manifest records all reserved E11F starts as not requested.

## Baselines

| Model | MAE (C) | RMSE (C) | P95 absolute error (C) |
|---|---:|---:|---:|
| Unstratified local IDW k3 p2 | 1.1168 | 1.7250 | 3.4900 |
| Role-conditioned mean | 1.5625 | 2.2357 | 5.1315 |

The unstratified local IDW was the registered stronger baseline.

## Best Development Candidate

`role_local_k5_p2` had MAE `1.0187 C`, RMSE `1.6792 C`, and P95 `3.7699 C`. Relative to the stronger baseline, aggregate MAE improved by `0.0981 C` and the 20,000-replicate day-block bootstrap 95% CI was `[0.0708, 0.1292] C`. It met all three absolute-accuracy thresholds.

However, P95 worsened by `0.2799 C`, and per-sensor MAE improved for only `25/42` sensors rather than the required 26. The candidate therefore failed two registered forwarding conditions.

## Grid-Level Decision

- Candidates evaluated: 24.
- Candidates with lower P95 than the stronger baseline: 0/24.
- Candidates meeting the 26/42 sensor-win threshold: 0/24.
- Candidates passing every gate: 0/24.
- Development decision: `no_candidate_forwarded`.
- E11F action: do not download or execute.

## Interpretation

Same-role locality can improve average error, but the registered grid trades that gain for worse tail behavior and incomplete sensor coverage. This is not evidence that hierarchical role-local reconstruction generalizes. E11E may motivate a new tail-aware development study, but E11F remains reserved until a separately preregistered candidate passes a development gate.

