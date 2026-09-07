# Evidence

## Run Identity

- Experiment: E11F one-time frozen commissioning confirmation.
- Result: `outputs/data/enclosure/aau_commissioning_confirmation_e11f.json`.
- Result SHA-256: `14c606e26f4da454b96d1e8911189df65e498f64f6b7fd1fac2f567461db5c3a`.
- Manifest SHA-256: `d31e94a21124eeb789d1c2935ef7673781c7fddc2c3b31f447c70ffe739c214e`.
- Frozen E11H SHA-256: `b76ecfe3e597d0641515df60b0d6636ed9a0ff1e23ebcb2852a225d4eee490e9`.
- Refit performed: false.

## Observations

- Parse: 89,585 accepted rows, 1,505 minute snapshots, 42 sensors, and no malformed or nonfinite values.
- Confirmation measurements: 63,210 sensor-minutes across 13 calendar-day blocks.
- Local-IDW baseline MAE/RMSE/P95: 1.1399/1.7850/3.5735 degrees Celsius.
- Frozen commissioning map MAE/RMSE/P95: 0.3966/0.6723/1.2756 degrees Celsius.
- Strict sensor wins: 39 of 42; the other three retain frozen baseline fallbacks.
- Day-block MAE improvement 95% CI: [0.5851, 0.9274] degrees Celsius.
- All eight confirmation gates passed.

## Calendar Overlap

E11F has 13 dates. Eleven overlap E11G dates and eight overlap E11H dates, so `calendar_day_disjoint` is false. No records were excluded because overlap reporting was preregistered as a claim-limiting diagnostic.

## Decision

H-ENC-05 is `h_enc_05_supported_within_campaign`. This supports a calibration-assisted frozen virtual-sensor map on unseen AAU byte ranges within one campaign. It does not establish cross-date, cross-campaign, cross-enclosure, causal-airflow, or NTC-hardware validity.

