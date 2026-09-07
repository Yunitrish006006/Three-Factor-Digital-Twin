# Evidence

## Run Identity

- Experiment: E11H commissioning-calibrated development.
- Result: `outputs/data/enclosure/aau_commissioning_development.json`.
- Result SHA-256: `b76ecfe3e597d0641515df60b0d6636ed9a0ff1e23ebcb2852a225d4eee490e9`.
- Manifest SHA-256: `79a46e8f0df311292864d2c155597416af4ae4320d631f1dbd8a0b4206d012f0`.
- E11F accessed: false.

## Observations

- Parse: 89,589 accepted rows, 1,502 minute snapshots, 42 sensors, and no malformed or nonfinite values.
- Chronology: two calibration days, one selection day, and nine frozen test days.
- Frozen test measurements: 45,864 sensor-minutes.
- Baseline MAE/RMSE/P95: 1.0958/1.7435/3.5061 degrees Celsius.
- Commissioning map MAE/RMSE/P95: 0.4039/0.6830/1.2900 degrees Celsius.
- Sensor wins: 39 of 42.
- Day-block MAE improvement 95% CI: [0.4854, 0.9271] degrees Celsius.

## Gate Decision

All preregistered aggregate, tail, sensor-coverage, bootstrap, and absolute-error gates passed. The frozen model map is `candidate_forwarded_to_e11f`.

## Limitations

E11H is development evidence with target-location observations during commissioning. Its byte ranges are new, but some calendar dates overlap E11G dates. Several Huber models reach the slope clamp, indicating limited affine identifiability over a narrow temperature range. E11F must use the exact frozen map and remains a same-campaign confirmation.

