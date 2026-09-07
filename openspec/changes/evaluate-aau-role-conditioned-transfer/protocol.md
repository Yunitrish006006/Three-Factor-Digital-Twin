# Protocol

## Dataset and Independent Split

- Dataset: AAU Server Room v4 `AAU_temperature_and_power_use.csv`, DOI `10.5281/zenodo.19398358`.
- Retrieve eleven HTTP byte ranges of 4,194,304 bytes each.
- Fixed starts: `15953778`, `79768891`, `143584004`, `207399117`, `271214230`, `335029343`, `398844456`, `462659569`, `526474682`, `590289795`, `654104908`.
- These quarter-gap offsets are disjoint from the E11B grid and E11C midpoint ranges. Abort before retrieval if any fixed observation range overlaps a forbidden range.
- A small byte-zero request may be used only to recover the CSV header; it is not an observation range.
- Discard boundary records cut by range starts or ends and aggregate accepted values to one-minute sensor means.

## Frozen Sensor Roles and Models

- Eligible roles: `rack_front`, `rack_back`, and `gradient`.
- Recover the frozen 42-sensor role map from E11C result SHA-256 `0b667ca8bb959e332aeff0155b9dceb1318dca3f91a26c1aa5552fb6bfef7055` before reading E11D observations.
- Global baseline: for each target sensor and minute, arithmetic mean of every other eligible sensor.
- Role-conditioned model: arithmetic mean of every other eligible sensor having the same frozen role.
- No E11D-based role reassignment, parameter search, fallback model, sensor exclusion, or threshold change is allowed.

## Metrics and Decision Rule

- Report aggregate MAE, RMSE, P95 absolute error, per-role metrics, and per-sensor MAE wins.
- Compute paired improvement as `global absolute error - role-conditioned absolute error`.
- Bootstrap calendar-day blocks 20,000 times with seed `20260823`.
- Mark H-ENC-04 `supported` only if role-conditioned MAE and RMSE are lower, at least 26/42 sensors have lower MAE, and the bootstrap 95% CI lower bound is greater than zero. Otherwise mark `not_supported`.

