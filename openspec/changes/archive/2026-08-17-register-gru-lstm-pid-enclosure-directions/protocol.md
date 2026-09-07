# Pre-Registered Direction Protocol

## Status

- Registration date: `2026-08-17`
- Current execution status: `NOT_EVALUATED`
- This protocol registers comparison gates only; it does not register result thresholds or report expected wins.

## GRU/LSTM Gate

- Compare vanilla RNN, GRU, and LSTM only on identical tasks, inputs, preprocessing, folds, targets, and test rows.
- Register hidden size, parameter-budget rule, epochs, optimizer, seed set, early-stopping rule, and tuning budget before the first result.
- Preserve the existing pure RNN 3-D and SML2010 RNN results as separate completed baselines.
- Report per-case metrics, failures, training cost, and adverse results; do not select the architecture after inspecting the test set.

## PID Gate

- Define the controlled variable, reference trajectory, plant or physical testbed, sampling period, actuator, delay, saturation, disturbances, and safety cutoff before execution.
- Minimum comparators: open-loop or no-action baseline, PID, and the proposed model-based/learned controller if one exists.
- Minimum metrics: tracking MAE, settling time, overshoot, control effort/energy proxy, constraint violations, and failure count.
- Use identical plant states, disturbances, observation streams, reference trajectories, and actuator limits for all controllers.

## Equipment-Enclosure Transfer Gate

- All intended air-state targets must remain inside 20–30°C for current-scope alignment.
- Provide enclosure dimensions, sensor coordinates, fan/vent geometry, component heat-source locations and power profiles, and an independent reference measurement plan.
- Test dynamic load transitions and spatial hotspots rather than only a constant setpoint.
- Label the study as a new transfer scenario; do not reuse room-level results as enclosure evidence.

## Future Evidence Paths

- GRU/LSTM comparison: `outputs/data/future/gru_lstm_comparison.json`
- PID comparison: `outputs/data/future/pid_closed_loop_comparison.json`
- Enclosure transfer: `outputs/data/future/enclosure_transfer_summary.json`

These paths are reservations only and SHALL remain absent until the respective experiment is implemented and executed.
