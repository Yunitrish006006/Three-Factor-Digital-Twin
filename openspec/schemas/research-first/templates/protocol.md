# Pre-Registered Protocol

## Protocol Identity

- Change:
- Protocol version:
- Registration date:
- Related IDs:
- Status: `PLANNED`

## Experimental Design

- Study type:
- Unit of analysis:
- Experimental unit:
- Number of runs or samples:
- Conditions and controls:
- Randomization or chronological ordering:
- Blinding, if applicable:

## Variables

| Role | Variable | Definition | Unit | Collection source |
| --- | --- | --- | --- | --- |
| independent | <!-- --> | <!-- --> | <!-- --> | <!-- --> |
| dependent | <!-- --> | <!-- --> | <!-- --> | <!-- --> |
| control | <!-- --> | <!-- --> | <!-- --> | <!-- --> |
| confounder | <!-- --> | <!-- --> | <!-- --> | <!-- --> |

## Inputs, Sampling, and Provenance

- Room/scenario:
- Sensor topology:
- Sampling cadence:
- Settling interval:
- Dataset source and license:
- Inclusion criteria:
- Exclusion criteria:
- Missing-data handling:
- Outlier policy:

## Leakage and Contamination Controls

- Train/test split:
- Time ordering:
- Repeated-measure handling:
- Hyperparameter selection:
- Prohibited post-outcome adjustments:

## Baselines and Ablations

| ID | Comparator | Purpose |
| --- | --- | --- |
| `B?` | <!-- baseline or ablation --> | <!-- what it tests --> |

## Metrics and Decision Criteria

| Hypothesis / claim | Metric | Success / interpretation rule | Failure rule |
| --- | --- | --- | --- |
| `H?` / `CLM-?` | <!-- --> | <!-- pre-specified threshold --> | <!-- --> |

## Analysis

- Aggregation:
- Uncertainty or interval estimate:
- Statistical test, if justified:
- Multiple-comparison handling:
- Sensitivity analysis:

## Execution and Evidence Contract

| Step | Command | Expected machine-readable output |
| --- | --- | --- |
| 1 | `python3 ...` | `outputs/...json` |

## Deviations and Failure Reporting

- All deviations SHALL be recorded in `evidence.md`.
- Failed, missing, or contradictory results SHALL remain visible.
- A threshold change after observing results SHALL create a new protocol version.
