# Pre-Registered Protocol

## Protocol Identity

- Change: `add-bedroom-bootstrap-uncertainty`
- Protocol version: `1.0`
- Registration date: `2026-07-26`
- Related IDs: `RQ-E7-UNC-01`, `H-E7-UNC-01`, `CLM-E7-UNC-01`, `EVD-010`
- Status: `PLANNED`

## Experimental Design

- Study type: secondary paired uncertainty analysis of existing E7 snapshots.
- Unit of analysis: pillow-point absolute error for each metric.
- Resampling unit: calendar date block containing all available snapshots from that date.
- Observed sample: 7 dates and 28 snapshots.
- Bootstrap replicates: 20,000.
- Random seed: 20260726.
- Confidence level: 95%, percentile method.

## Variables

| Role | Variable | Definition | Unit | Collection source |
| --- | --- | --- | --- | --- |
| paired baseline | raw pillow absolute error | error before sparse calibration | °C, %RH, lux | weekly summary snapshot |
| paired outcome | estimated pillow absolute error | error after calibration | °C, %RH, lux | weekly summary snapshot |
| primary endpoint | mean absolute-error reduction | raw minus calibrated | °C, %RH, lux | paired computation |
| secondary endpoint | improved snapshot fraction | proportion where calibrated error is smaller | 0--1 | paired computation |

## Inputs, Sampling, and Provenance

- Input: `docs/requirements/bedroom_01_combined_room_and_weekly_simulation.json`.
- Producer: `python3 scripts/run_bedroom_weekly_simulation.py`.
- Inclusion: every snapshot containing date, raw error, and calibrated error for all three metrics.
- Exclusion: none planned; missing required fields SHALL fail visibly.
- Outlier policy: no trimming or winsorization.

## Leakage and Contamination Controls

- Raw and calibrated errors SHALL come from the same snapshot.
- The pillow observation remains held out from eight-corner residual fitting.
- Whole dates SHALL be resampled; individual snapshots SHALL NOT be independently resampled for the primary interval.
- Seed and replicate count SHALL be written into the output.

## Metrics and Decision Criteria

| Hypothesis / claim | Metric | Success / interpretation rule | Failure rule |
| --- | --- | --- | --- |
| `H-E7-UNC-01` | 95% CI of paired MAE reduction | all three lower bounds > 0 | any lower bound <= 0 |
| `CLM-E7-UNC-01` | observed reduction + CI + improvement fraction | bounded to this room, period, and held-out point | any wording implies dense truth or cross-room efficacy |

## Analysis

For each replicate, sample seven date labels with replacement, include every snapshot belonging to each sampled date, and compute mean raw MAE, mean calibrated MAE, their difference, relative reduction, and improved fraction. Sort replicate values and use deterministic linear interpolation for the 2.5th and 97.5th percentiles.

## Execution and Evidence Contract

| Step | Command | Expected machine-readable output |
| --- | --- | --- |
| 1 | `python3 scripts/run_bedroom_weekly_simulation.py` | `aggregate.paired_day_block_bootstrap` in weekly summary |
| 2 | `python3 -m unittest discover -s tests` | deterministic bootstrap tests pass |
| 3 | `python3 scripts/verify_thesis_results.py` | uncertainty values receive PASS |
| 4 | `python3 scripts/validate_research_openspec.py` | no structural failures |

## Deviations and Failure Reporting

- Any change to seed, replicates, resampling unit, percentile definition, metric, or missing-data policy SHALL be recorded.
- Null, negative, or wide intervals SHALL be reported without changing the decision rule.
