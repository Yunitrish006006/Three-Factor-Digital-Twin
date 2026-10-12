# Research questions

- RQ-ENC-51: Can the canonical package process time-ordered plate/air/fan/inlet/power observations without source-truth input, while rejecting invalid or stale observations?
- RQ-ENC-52: Does the same bounded four-parameter calibration improve source estimation across capacity/fan-delay variants and a misspecified heat-path family?
- RQ-ENC-53: How do fixed, PI, PID, LQR, linear MPC and one/six-step ranking compare with identical sparse observations and command protections?
- H-ENC-51 (exploratory): on synthetic holdout, corrected source MAE is at most 90% of calibrated open-loop MAE, with improvement in at least 3/4 rig-seed pairs.
- H-ENC-52 (exploratory): six-step ranking reduces tracking MAE by at least 5% versus one-step ranking, without greater sampled overtemperature or over 20% extra fan proxy energy.

These are predeclared exploratory assumed-model criteria, not population hypotheses or physical efficacy. The out-of-family plant has a direct source-air heat path absent from the estimator. Alternative explanations include low excitation, common-scale capacity misspecification, and finite fan cooling capacity. No personal data is used; raw reference temperatures are quarantined from calibration and control. No claim of humidity/light or full spatial-field transfer follows.
