# Evidence

## Run Identity

- Experiment: E11G adaptive tail-safe development.
- Result: `outputs/data/enclosure/aau_tail_safe_development.json`.
- Result SHA-256: `aef099fea6b37036fd32644f4897e2aea5e47922d525f072b7b01592928466ed`.
- E11E input SHA-256: `c345e1320bd7e1aed21fd67f04e661d555a18e6e0fd312f638bc350300eb732a`.
- E11E manifest SHA-256: `873e155bceaaac530f004b1ef14d1cceb8356af83f5a9ace1638ec54a34919d6`.
- E11F accessed: false.

## Observations

- 30 fixed candidates, 12 leave-one-day-out folds, 42 sensors, and 63,084 sensor-minute evaluations.
- Local-IDW baseline: MAE 1.1168 degrees Celsius, RMSE 1.7250, P95 3.4900.
- Tail-safe sensor map: MAE 0.8945 degrees Celsius, RMSE 1.5415, P95 3.1013.
- Day-block MAE improvement 95% bootstrap CI: [0.1847, 0.2620] degrees Celsius.
- Sensor outcomes: 21 lower-MAE wins, 20 exact fallback ties, and one loss.

## Gate Decision

The aggregate MAE, RMSE, P95, bootstrap, and all three absolute-error gates passed. The preregistered requirement of at least 26 strict sensor wins failed at 21 of 42. The decision is therefore `no_candidate_forwarded`; E11F remains untouched.

## Interpretation

Tail-safe gating resolves the E11E aggregate tail-error failure on adaptive out-of-fold development data, but it does not meet the prespecified spatial-coverage criterion. This is promising development evidence, not independent enclosure validation or a causal airflow result.

