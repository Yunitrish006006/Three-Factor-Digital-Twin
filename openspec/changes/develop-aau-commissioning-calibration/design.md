# Design

## Deployment Interpretation

A low-cost NTC or traceable reference sensor may be temporarily placed at a target location during commissioning. The learned correction is then frozen and the physical target sensor can be removed. E11H emulates this sequence but does not evaluate NTC hardware uncertainty.

## Robust Calibration

Median residual offsets address stable location bias with low variance. Huber-affine calibration adds bounded scale correction while reducing sensitivity to transient outliers. Both remain interpretable and inexpensive enough for sparse IoT services.

## Leakage Controls

Calibration, selection, and test dates are chronological and disjoint. Candidate parameters use calibration days only. Candidate identity uses selection day only. No model update, threshold change, or sensor remapping is allowed after test metrics are read.

