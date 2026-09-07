# Proposal: Develop AAU Commissioning Calibration

## Why

E11G improves aggregate and tail error but strictly improves only 21 of 42 sensors because its safety policy leaves 20 locations unchanged. Literature on virtual sensing and in-situ calibration suggests that a short commissioning period can estimate location-specific systematic residuals before a physical sensor is removed.

## What Changes

- Acquire a new, non-overlapping E11H AAU development split.
- Use two chronological days for temporary-reference calibration and one day for model selection.
- Freeze sensor-specific robust calibration models before evaluating all later days.
- Preserve E11F as untouched confirmation data.

## Scope

E11H evaluates calibration-assisted virtual sensing. It does not support zero-shot transfer, NTC metrological accuracy, causal airflow claims, or external enclosure confirmation.

