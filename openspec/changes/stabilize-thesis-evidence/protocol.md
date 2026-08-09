# Pre-Registered Protocol

## Protocol Identity

- Change: `stabilize-thesis-evidence`
- Protocol version: `1.0-merge-normalized`
- Registration date: `2026-08-09`
- Related IDs: `RQ-STAB-01`--`03`, `H-STAB-01`--`02`, `CLM-STAB-01`--`03`
- Status: `PLANNED_WITH_PARTIAL_IMPLEMENTATION`

## Experimental Design

- Study type: controlled synthetic target holdout followed by planned real target-point validation.
- Unit of analysis: scenario × validation target × environmental metric.
- Experimental unit: one scenario execution with a frozen input/validation role split.
- Number of runs or samples: runner-defined scenarios; actual count is recorded in output rather than assumed here.
- Conditions and controls: same room/scenario, same input observations, same targets, same metrics for all comparators.
- Randomization or chronological ordering: deterministic controlled runs; real data uses blocked or leave-one-day-out ordering.
- Blinding: validation truth is inaccessible to fitting and is read only by the evaluator.

## Variables

| Role | Variable | Definition | Unit | Collection source |
| --- | --- | --- | --- | --- |
| independent | estimator | BasePhysics, IDW, implemented free-space estimator, optional residual | categorical | method configuration |
| dependent | target error | prediction minus held-out truth | °C, %RH, lux | evaluator |
| control | sensor split | frozen `S_input` and `S_validation` membership | node IDs | scenario/layout |
| confounder | device, fan, outdoor and furniture state | boundary conditions affecting the field | mixed | scenario/event metadata |

## Inputs, Sampling, and Provenance

- Room/scenario: canonical single-room scenarios; real bedroom coordinates must follow the room-design contract.
- Sensor topology: input and validation roles are disjoint; pseudo nodes are not measured.
- Sampling cadence: recorded per dataset; no cross-cadence pooling without alignment.
- Settling interval: recorded for real before/after data; absent values remain missing.
- Dataset source and license: controlled generator, user-collected bedroom data, or separately disclosed public dataset.
- Inclusion criteria: valid coordinates, complete role, supported metric, and declared boundary conditions.
- Exclusion criteria: occupied query point, invalid reading, unknown critical state in primary analysis, or leakage detection.
- Missing-data handling: retain missing status; do not impute validation truth for primary metrics.
- Outlier policy: report quality flag and sensitivity result; do not silently remove worst cases.

## Leakage and Contamination Controls

- Train/test split: fitting uses only `S_input`; evaluation uses `S_validation` after prediction.
- Time ordering: real data uses blocked or leave-one-day-out splits.
- Repeated-measure handling: aggregate and inspect by day/target; do not treat adjacent timestamps as independent rooms.
- Hyperparameter selection: validation truth is unavailable to model selection.
- Prohibited post-outcome adjustments: comparator input rows, targets, metric definitions and exclusions cannot change after results are observed without a new protocol version.

## Baselines and Ablations

| ID | Comparator | Purpose |
| --- | --- | --- |
| `B-STAB-01` | BasePhysics without target truth | primary interpretable estimator |
| `B-STAB-02` | sensor-level IDW | distance-only baseline |
| `B-STAB-03` | uncorrected nominal field | calibration ablation |
| `B-STAB-04` | residual off/on | additive residual contribution |

## Metrics and Decision Criteria

| Hypothesis / claim | Metric | Success / interpretation rule | Failure rule |
| --- | --- | --- | --- |
| `H-STAB-01` | leakage flag and audited role intersection | zero validation observations used in fitting | any leakage rejects the run |
| `H-STAB-02` | parity metadata | identical split, targets and truth lookup for comparators | mismatched parity makes comparison invalid |
| `CLM-STAB-01` | MAE/RMSE/MaxErr/bias | report descriptively under controlled simulation | must not be promoted to real-room truth |

No estimator-superiority threshold is preregistered in this version; negative and ranking-reversal results remain visible.

## Analysis

- Aggregation: per scenario, target, metric and method; then macro summary without hiding groups.
- Uncertainty: real repeated measurements require day/cluster-aware intervals where sample size permits.
- Statistical test: descriptive comparison unless independence and sample size justify a named test.
- Multiple comparisons: method/metric family is reported explicitly; no selective best-case reporting.
- Sensitivity: fan state, occlusion, residual on/off, and leave-one-day-out where data exists.

## Execution and Evidence Contract

| Step | Command | Expected machine-readable output |
| --- | --- | --- |
| 1 | `python3 scripts/run_target_holdout_validation.py` | `outputs/data/target_holdout_validation_summary.json` |
| 2 | `python3 -m unittest discover -s tests` | test process result |
| 3 | `python3 scripts/verify_thesis_results.py` | `outputs/data/thesis_result_verification_report.json` |
| 4 | `python3 scripts/validate_research_openspec.py` | structural validation result |

## Deviations and Failure Reporting

- All deviations SHALL be recorded in `evidence.md` after actual execution.
- Failed, missing or contradictory results SHALL remain visible.
- A threshold change after observing results SHALL create a new protocol version.
