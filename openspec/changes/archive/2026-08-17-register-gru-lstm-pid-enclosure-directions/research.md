# Research Framing

## Questions

- `EQ-RNNGATE-01`: Under identical inputs, folds, training budgets, targets, and test points, do GRU or LSTM improve upon the registered vanilla RNN without unfair tuning?
- `EQ-PID-01`: Given the same plant, setpoint trajectory, disturbances, actuator limits, and observation stream, how does PID compare with model-based or learned closed-loop controllers?
- `EQ-ENC-01`: Can the sparse-sensing approach be transferred to a 20–30°C equipment enclosure after adding enclosure-scale geometry, forced-airflow, component heat-source, and reference-sensor contracts?

## Intended Bounded Claims

| ID | Claim | Status | Forbidden overclaim |
| --- | --- | --- | --- |
| `CLM-RNNGATE-01` | GRU and LSTM are registered future comparators that require a new fixed protocol. | `NOT_EVALUATED` | gated recurrence is superior; replacing the RNN result |
| `CLM-PID-01` | PID is a future closed-loop control baseline, not a field-estimation model. | `NOT_EVALUATED` | current system has automatic control; PID performance advantage |
| `CLM-ENC-01` | A 20–30°C equipment enclosure is a plausible dynamic thermal-control candidate requiring a new transfer study. | `NOT_EVALUATED` | present room results apply directly to cabinets or component hotspots |

## Competing Explanations and Threats

- GRU/LSTM gains may arise from parameter count, longer history, or extra tuning rather than gating; equal-data and controlled-budget comparisons are required.
- PID may appear strong or weak because of plant simplification, setpoint choice, sampling rate, delay, or actuator saturation.
- Enclosure behavior may be dominated by forced convection, fan curves, recirculation, component heat generation, and sub-room scale effects absent from the present model.
- Temperature targets above 30°C are outside the current research domain even if common inside electronics enclosures.
- Humidity and illuminance may be irrelevant to some enclosures, so a transfer cannot automatically preserve the current three-factor contribution.

## Safety and Ethics

- No physical controller or enclosure experiment is executed in this change.
- Any later PID or learned-controller test must define actuator saturation, emergency cutoff, rate limits, and a safe fallback.
- A real enclosure test must protect hardware against overheating, condensation, and fan failure.
