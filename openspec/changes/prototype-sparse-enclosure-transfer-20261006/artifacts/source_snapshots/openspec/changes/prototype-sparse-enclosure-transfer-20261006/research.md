# Research questions and decisions

- RQ-ENC-31: Can identical finite calibration using plate/air observations recover a useful hidden-source temperature predictor across designated synthetic rigs?
- RQ-ENC-32: Does six-step candidate ranking improve closed-loop tracking over its H=1 ablation and PI/PID comparators?
- H-ENC-31: sparse-corrected source estimate reduces macro source MAE by at least 10% against calibrated physics-only on the common open-loop holdout, with improvements in at least 4 of 6 rig-seed pairs.
- H-ENC-32: H=6 reduces macro tracking MAE by at least 5% against H=1, with no greater sampled overtemperature, and fan-energy proxy no more than 20% higher, on the 6 holdout pairs.

These are exploratory predeclared decision rules, not confirmatory real-device hypotheses. Truth exists only inside synthetic simulator and scorer. Observers/controllers never receive source truth. Known capacities and fixed air-exchange coefficients may create optimistic identifiability. Shared equation family, synthetic seeds and assigned variants are not independent hardware evidence. No privacy-sensitive data; no actuation. LQZ unresolved.
