# Research Questions and Hypotheses

## RQ-ENC-02

Can 3D inverse-distance weighting reconstruct a held-out temperature channel in a real server room more accurately than non-spatial global-mean and nearest-neighbor baselines?

## H-ENC-02

Across the 42 pre-registered high-confidence sensor locations, 3D IDW with fixed power `p=2` will have lower macro-averaged MAE than both global mean and nearest neighbor, and will achieve the lowest per-sensor MAE for at least 60% of held-out sensors.

## Decision Rule

- Supported: both aggregate comparisons and the 60% sensor-win threshold are satisfied.
- Not supported: any required condition fails.
- Not evaluable: fewer than 36 eligible sensors or fewer than 120 one-minute snapshots remain after parsing and completeness checks.

## Interpretation Boundary

Support would establish only task-aligned spatial reconstruction evidence for this AAU room. It would not validate CFD, generalize to arbitrary equipment enclosures, or demonstrate intervention effectiveness.
