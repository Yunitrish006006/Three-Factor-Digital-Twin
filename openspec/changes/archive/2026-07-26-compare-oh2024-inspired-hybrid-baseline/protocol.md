# Pre-Registered Protocol

## Protocol Identity

- Change: `compare-oh2024-inspired-hybrid-baseline`
- Protocol version: `1.0`
- Registration date: `2026-07-26`
- Related IDs: `RQ-PHB-01`, `EQ-PHB-01`, `H-PHB-01`, `CLM-PHB-01`, `E9`
- Status: `EXECUTED`

## Experimental Design

- Study type: deterministic public-task method-transfer comparison
- Unit of analysis: one target timestamp for one SML2010 indoor temperature point
- Experimental unit: target--horizon case
- Number of runs or samples: six cases = two targets x three horizons; sample counts determined before fitting from available aligned rows
- Conditions and controls: identical normalized records, target rows, horizons, chronological split, and metric functions for every comparator
- Randomization or chronological ordering: no shuffle; earliest 70% training and latest 30% testing
- Blinding, if applicable: not applicable

## Variables

| Role | Variable | Definition | Unit | Collection source |
| --- | --- | --- | --- | --- |
| independent | comparator | persistence, direct linear, raw physics, project mapped readout, paper-inspired additive residual | category | evaluator |
| dependent | forecast error | MAE and RMSE on identical test rows | °C | computed |
| dependent | association/fit | Pearson correlation and R2 | dimensionless | computed |
| dependent | normalized error | RMSE divided by test target mean | % | computed CVRMSE |
| control | horizon | forecast lead | minutes | `15`, `60`, `1440` |
| control | split | chronological training/test assignment | fraction | `70/30` |
| confounder | dataset shift | late test period may differ seasonally from early training period | descriptive | timestamps/weather |

## Inputs, Sampling, and Provenance

- Room/scenario: SML2010 two-point pseudo-room alignment, task `S2`
- Sensor topology: dining-room and room indoor temperature points
- Sampling cadence: 15 minutes
- Settling interval: not applicable
- Dataset source and license: existing normalized SML2010 provenance in repository
- Inclusion criteria: origin and exact target timestamp exist for the requested horizon; both temperature targets and required input features are finite
- Exclusion criteria: missing exact horizon row or non-finite required value
- Missing-data handling: exclude before split and record counts
- Outlier policy: no post-hoc outlier deletion

## Leakage and Contamination Controls

- Train/test split: earliest `floor(0.7*n)` valid samples, with at least one training and one test row
- Time ordering: strictly chronological
- Repeated-measure handling: timestamps remain ordered; no random redistribution across split
- Hyperparameter selection: ridge fixed at `1e-3`; no test-set selection
- Prohibited post-outcome adjustments: no feature, ridge, threshold, target, or horizon changes after first result execution without protocol version change; target-time observations are excluded from model inputs

## Baselines and Ablations

| ID | Comparator | Purpose |
| --- | --- | --- |
| `B-PHB-01` | persistence | strong short-horizon time-series baseline |
| `B-PHB-02` | direct ridge linear regression | data-only low-capacity baseline |
| `B-PHB-03` | raw physics prior | isolates residual-correction benefit |
| `B-PHB-04` | project hybrid digital-twin readout | current E9 mapped method |
| `B-PHB-05` | Oh2024-inspired additive residual readout | tested transfer method |

## Metrics and Decision Criteria

| Hypothesis / claim | Metric | Success / interpretation rule | Failure rule |
| --- | --- | --- | --- |
| `H-PHB-01` | test MAE reduction vs raw physics | positive in at least 4 of 6 cases | positive in fewer than 4 |
| `CLM-PHB-01` | parity audit plus complete metrics | all comparators use identical test rows and output contains all five metrics | missing comparator, split mismatch, or leakage |
| `EQ-PHB-01` | lowest-MAE count and pairwise MAE reductions | descriptive only | no directional threshold |

## Analysis

- Aggregation: report each target--horizon separately plus win counts; do not average metrics across targets without keeping case-level rows.
- Uncertainty or interval estimate: not planned; timestamps are autocorrelated and one dataset is not an independent-building sample.
- Statistical test, if justified: none.
- Multiple-comparison handling: no inferential p-values.
- Sensitivity analysis: horizons span 15 minutes, 60 minutes, and the paper-aligned next-day lead of 1440 minutes.

## Execution and Evidence Contract

| Step | Command | Expected machine-readable output |
| --- | --- | --- |
| 1 | `python3 scripts/run_oh2024_inspired_comparison.py` | `outputs/data/public_benchmarks/oh2024_inspired_sml2010_comparison.json` |
| 2 | `python3 scripts/verify_thesis_results.py` | `outputs/data/thesis_result_verification_report.json` |

## Deviations and Failure Reporting

- All deviations SHALL be recorded in `evidence.md`.
- Failed, missing, or contradictory results SHALL remain visible.
- A threshold change after observing results SHALL create a new protocol version.
