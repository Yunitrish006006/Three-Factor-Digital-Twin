# Evidence

## Execution Status

- Experiment: E11D
- Hypothesis: H-ENC-04
- Decision: `supported`
- Dataset: AAU Server Room v4, DOI `10.5281/zenodo.19398358`
- Manifest: `outputs/data/enclosure/aau_temperature_ranges_e11d_manifest.json`
- Manifest SHA-256: `3c030b7765f73fce878dd584faefd436f29e47203ef8ca95c923d4b56dc54f4e`
- Result: `outputs/data/enclosure/aau_role_conditioned_confirmation.json`
- Result SHA-256: `1a7750cfaba8d87916ac96066d783cc8c335746dcf77d34d84c60516b5c4a747`
- Frozen E11C role metadata SHA-256: `0b667ca8bb959e332aeff0155b9dceb1318dca3f91a26c1aa5552fb6bfef7055`

## Data Accounting

- 11 independent 4 MiB observation fragments; all returned HTTP `206` with exact byte counts.
- 22 boundary records discarded by the registered policy.
- 89,584 rows seen and accepted; 0 malformed rows and 0 non-finite values.
- 1,505 complete one-minute snapshots across 13 calendar-day blocks.
- 42 sensors: 9 `rack_front`, 28 `rack_back`, and 5 `gradient`.

## Registered Results

| Model | MAE (C) | RMSE (C) | P95 absolute error (C) |
|---|---:|---:|---:|
| Global leave-one-out mean | 2.3972 | 2.9748 | 5.7232 |
| Role-conditioned leave-one-out mean | 1.6517 | 2.3648 | 5.4886 |

- Paired MAE improvement: `0.7455 C`.
- Per-sensor MAE wins: role-conditioned `30/42`; global `12/42`; ties `0`.
- Day-block bootstrap: 20,000 replicates, seed `20260823`, 95% CI `[0.6867, 0.8124] C`.
- Per-role MAE changed from `2.4095` to `0.5737 C` for gradient sensors, `2.8986` to `1.0510 C` for rack-front sensors, and `2.2338` to `2.0372 C` for rack-back sensors.

## Decision Trace

- Role-conditioned MAE lower: true.
- Role-conditioned RMSE lower: true.
- Role-conditioned per-sensor wins at least 26/42: true (`30/42`).
- Bootstrap confidence lower bound above zero: true (`0.6867 C`).
- H-ENC-04 decision: `supported` because every preregistered condition passed.

## Interpretation and Limits

This confirms that categorical sensor semantics carry transferable information that a role-agnostic room mean discards. It does not establish an airflow mechanism, and the global mean is a deliberately simple baseline. E11D uses a different byte split from E11C, so cross-experiment MAE values must not be treated as a paired model ranking. No model or threshold was changed after E11D observations were read.

## Difficulties Preserved

RDL-024 through RDL-028 record sandbox DNS restrictions, a missing XLSX dependency, OpenSpec heading validation, network-execution rejection, and the implicit E11C role-map schema. Each failure occurred before a scientific decision or changed only the data interface, not the registered analysis.

