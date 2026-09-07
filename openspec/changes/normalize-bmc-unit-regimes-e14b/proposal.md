# Change: Normalize BMC Unit Regimes

## Why

E14A removed host-section leakage but found three valid BMC files whose temperatures and PSU powers use raw hwmon/OpenBMC scales. Official documentation identifies temperature inputs as millidegree Celsius and power inputs as microwatts.

## What Changes

- Add E14B as a unit-normalization correctness study with no model evaluation.
- Classify each complete BMC section once from its median temperature and power magnitudes.
- Apply fixed `10^-3` temperature and `10^-6` power scales only to preregistered raw-unit sections.
- Preserve row counts and report all post-normalization extrema.

## Impact

E14B may establish physically interpretable BMC rows. It does not rehabilitate E13 as unseen confirmation or establish virtual-sensor accuracy.
