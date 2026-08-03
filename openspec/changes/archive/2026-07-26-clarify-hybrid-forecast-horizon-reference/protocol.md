# Pre-Registered Protocol

## Protocol Identity

- Change: `clarify-hybrid-forecast-horizon-reference`
- Protocol version: `1.0`
- Registration date: `2026-07-26`
- Related IDs: `RQ-HRL-TIME-01`, `CLM-HRL-TIME-01`, `HRL-007`
- Status: `PLANNED`

## Experimental Design

- Study type: literature and notation audit; no new performance experiment.
- Unit of analysis: each hybrid formula and its explanatory paragraph.
- Experimental unit: synchronized thesis, IEEE, model-note, and presentation sources.
- Number of runs or samples: not applicable.
- Conditions and controls: current-time spatial estimation (`h=0`) versus general `h`-step forecast notation.
- Randomization or chronological ordering: not applicable.
- Blinding, if applicable: not applicable.

## Variables

| Role | Variable | Definition | Unit | Collection source |
| --- | --- | --- | --- | --- |
| independent | `h` | forecast lead from origin `t` | time unit | formula |
| dependent | target time | time represented by both additive outputs | `t+h` | formula |
| control | `I_t` | information legally available at forecast origin | set | method prose |
| confounder | elapsed-time `t` | current scenario time in existing implementation | minutes | current model |

## Inputs, Sampling, and Provenance

- Room/scenario: existing canonical room; no new scenario.
- Sensor topology: existing eight-corner topology.
- Sampling cadence: not applicable.
- Settling interval: unchanged.
- Dataset source and license: no new dataset.
- Inclusion criteria: project sources describing hybrid residual learning.
- Exclusion criteria: generated caches and external PDF full-text copying.
- Missing-data handling: not applicable.
- Outlier policy: not applicable.

## Leakage and Contamination Controls

- Train/test split: unchanged.
- Time ordering: any forecast notation SHALL condition on `I_t`.
- Repeated-measure handling: unchanged.
- Hyperparameter selection: unchanged.
- Prohibited post-outcome adjustments: `I_t` SHALL NOT include observed `y(t+h)` or residual truth at `t+h`.

## Baselines and Ablations

| ID | Comparator | Purpose |
| --- | --- | --- |
| `B-HRL-TIME-01` | current-state `F(p,t)+R(p,t)` | distinguish implemented spatial estimation from forecast generalization |

## Metrics and Decision Criteria

| Hypothesis / claim | Metric | Success / interpretation rule | Failure rule |
| --- | --- | --- | --- |
| `CLM-HRL-TIME-01` | source consistency audit | all synchronized sources define same target time and leakage boundary | any source implies future observation is available |

## Analysis

- Aggregation: exact-text and semantic review across sources.
- Uncertainty or interval estimate: not applicable.
- Statistical test, if justified: not applicable.
- Multiple-comparison handling: not applicable.
- Sensitivity analysis: verify both `h=0` and `h>0` wording.

## Execution and Evidence Contract

| Step | Command | Expected machine-readable output |
| --- | --- | --- |
| 1 | `rg -n "10.1016/j.enbuild.2024.114898|mathcal\\{I\\}|h=0" ...` | matching synchronized source lines |
| 2 | `python3 -m unittest discover -s tests` | passing tests |
| 3 | `python3 scripts/verify_thesis_results.py` | zero failures |
| 4 | `python3 scripts/validate_research_openspec.py` | zero validation failures |

## Deviations and Failure Reporting

- All deviations SHALL be recorded in `evidence.md`.
- Build, citation, page-count, or visual-QA failures SHALL remain visible.
- No claim threshold is changed because this protocol adds no performance claim.
