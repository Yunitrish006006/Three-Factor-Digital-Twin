# Research Direction Design

## Role Separation

```text
field estimation: Base / Pure RNN / GRU / LSTM / Hybrid
control:          no-action / PID / future model-based controller
application:      room evidence -> new enclosure transfer protocol
```

- GRU and LSTM extend the estimator-comparator branch.
- PID belongs to the controller branch and consumes an estimated/measured state; it does not replace the spatial estimator.
- The enclosure is a new application geometry, not another label for the current 6 m × 4 m × 3 m room.

## Traceability

| Direction | Research ID | Requirement |
| --- | --- | --- |
| GRU/LSTM | `EQ-RNNGATE-01` | `RGV-008` |
| PID | `EQ-PID-01` | `RGV-008` |
| enclosure | `EQ-ENC-01` | `RGV-008` |
| synchronized wording | all | `SYN-011` |

## Failure Handling

- A comparator row, fold, or target mismatch makes the ranking `NOT_EVALUATED`.
- Missing plant or actuator constraints prevent PID execution.
- Any required temperature outside 20–30°C marks the enclosure case out of current scope.
- Missing airflow, heat-source, geometry, or reference data prevents an enclosure applicability claim.
