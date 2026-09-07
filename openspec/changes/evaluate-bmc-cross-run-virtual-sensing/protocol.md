# E12 Protocol

## Frozen Data Source

- Repository: `https://github.com/arealuser/bmcdata`
- License: MIT
- Retrieval date: 2026-08-24
- Unit of separation: one complete CSV export file
- Every downloaded file SHALL be recorded with URL, byte count, and SHA-256.

## Frozen Split

Training files (12):

`202304252143`, `202304252201`, `202304252221`, `202304261725`, `202304281100`, `202304281732`, `202306172153`, `202306181509`, `202306181534`, `202306181653`, `202306191023`, `202306191544`.

Selection files (5):

`202307052240`, `202307052309`, `202307191620`, `202307201552`, `202307211550`.

Final-test files (14):

`202307301643`, `202307301734`, `202307301819`, `202307301853`, `202307302018`, `202307311829`, `202308011635`, `202308011759`, `202308051600`, `202308051718`, `202401042141`, `202401042237`, `202401042338`, `202401050043`.

## Rows and Target

- Ignore InfluxDB metadata lines beginning with `#`.
- Parse the first non-comment header and tolerate additional columns.
- Require finite `Inlet_Temp`, `Outlet_Temp`, `Cpu1_Temp`, `Cpu2_Temp`, `FAN1` through `FAN4`, `PSU1_Total_Power`, and `PSU2_Total_Power`.
- Target: `max(Cpu1_Temp, Cpu2_Temp)` in degrees C.
- A file is evaluable with at least 30 valid rows.

## Baseline and Candidates

- Fit inlet-offset and outlet-offset baselines on training rows using the median target-minus-source offset.
- Select the lower validation-MAE baseline; test files remain inaccessible.
- Ridge candidates use standardized training features, an unpenalized intercept, feature sets `thermal_pair`, `load_aware`, and `load_aware_interactions`, and lambdas `0.01`, `0.1`, `1.0`, and `10.0`.
- Select the lowest validation MAE; break ties by fewer features and then smaller lambda.
- Refit the selected structure on training plus selection rows exactly once, then freeze it before final testing.

## Metrics and Decision

- Report pooled MAE, RMSE, and P95 absolute error for baseline and model.
- Report macro run MAE, per-run wins, valid-row coverage, and coefficient values.
- Bootstrap the 14 run-level MAE improvements 10,000 times with seed `20260824`.
- Support H-ENC-06 only when every preregistered gate passes.
