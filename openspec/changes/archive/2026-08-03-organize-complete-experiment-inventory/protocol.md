# Pre-Registered Reconciliation Protocol

## Identity

- Change: `organize-complete-experiment-inventory`
- Version: `1.0`
- Registration date: `2026-08-03`
- Related IDs: `RQ-INV-01`, `EQ-E5-RANGE-01`, `CLM-INV-01`, `EVD-016`, `SYN-008`
- Status: `PLANNED`

## Inventory Units

1. E1 canonical full-field reconstruction.
2. E2 IDW comparison.
3. E3 ablation and reproducibility.
4. E4 appliance impact-learning check.
5. E5 window matrix and direct-input sensitivity.
6. E6 hybrid residual robustness.
7. E7 real-bedroom sparse calibration, bootstrap, and leave-one-date-out sensitivity.
8. E8 real before/after intervention readiness.
9. E9 public benchmark plus baseline, project mapped comparison, Oh-inspired transfer, next-day follow-up, and RNN same-data comparison.

## Canonical Evidence Rule

- Current machine-readable JSON is authoritative for numeric values.
- Existing prose is authoritative only when it agrees with the JSON or describes a boundary not encoded numerically.
- A stale prose number SHALL be replaced, not averaged with the current number.
- No experiment is rerun merely to obtain a more favorable value during this reconciliation.

## E5 Range Audit

- Unit: each of the 48 rows in `outputs/data/window_matrix_summary.json`.
- Variable: `target_zone_estimated.temperature`.
- In-domain rule: `20.0 <= temperature <= 30.0`.
- Out-of-domain rule: temperature below `20.0` or above `30.0`.
- Outdoor temperature may be outside this interval and is not used for the classification.
- The result is descriptive and SHALL NOT be used as a model-accuracy success threshold.

## Completeness Decision

`CLM-INV-01` is accepted only if every inventory unit has: purpose, evidence class, inputs/data, comparison or control, metrics, current result/status, evidence path, producer command, and boundary. Missing or contradictory items must be marked rather than inferred.

## Verification

```text
python3 scripts/verify_thesis_results.py
python3 scripts/validate_research_openspec.py
python3 -m unittest discover -s tests
git diff --check
```

