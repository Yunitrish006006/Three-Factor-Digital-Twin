# Change: Evaluate Cross-Run BMC Virtual Sensing

## Why

E11F confirms frozen calibration only on unseen byte ranges from the same AAU campaign. A non-physical follow-up is needed to test whether sparse thermal inference survives complete, date-disjoint measurement runs and unseen workload or fan-control conditions.

## What Changes

- Add E12, a public-data evaluation using complete BMC exports from one dual-socket server.
- Predict the higher of `Cpu1_Temp` and `Cpu2_Temp` from sparse environmental, fan, and PSU measurements.
- Separate model fitting, candidate selection, and final testing by complete source files and dates.
- Preserve null or adverse results and limit any positive claim to this server and dataset.

## Impact

This change affects evaluation evidence and data reproducibility. It does not constitute a physical PC-chassis or NTC-sensor experiment.
