# Design

ENC-501 adds a public digital_twin.enclosure.session module: validated Observation -> sparse observer -> versioned controller -> feasible PWM and diagnostics -> model prediction. A CSV runner exposes offline processing with JSON parameter manifests; it never sends heater/fan commands. Separate scoring columns cannot be converted into input observations. Room humidity/light code remains functional but is not duplicated into a thermal enclosure experiment.

ENC-502 fits a common capacity scale and fan delay in addition to contact and convection gain; the same bounded procedure is used on every rig. Independent plant evolution adds a direct source-air path on one holdout, allowing genuine model-family mismatch. Calibration state initialization is declared and must be measured for real deployment.

ENC-503 adds comparable sparse-state LQR and six-step linear MPC; shared raw warning/command limiting is applied last. Model-prediction and command-selection errors are reported separately. Optimization failure uses a documented shared fallback, without rig-specific exceptions.

SYN-501 derives all report numbers from result JSON, synchronizes candidate status across Chinese/IEEE/presentation and supplies an updated first-person HTML with LQR paper reading, device scenes, flow diagram, adverse results, hardware procedure and talk. Visual QA is hash-bound to the final bytes; no automatic script creates claims of observed acceptance.
