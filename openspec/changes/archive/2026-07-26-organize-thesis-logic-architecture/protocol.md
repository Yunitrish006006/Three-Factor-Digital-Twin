# Pre-Registered Protocol

## Protocol Identity

- Change: `organize-thesis-logic-architecture`
- Protocol version: `1`
- Registration date: `2026-07-26`
- Related IDs: `RQ1`--`RQ4`, `E1`--`E9`, `SYN-007`
- Status: `PLANNED`

## Experimental Design

- Study type: artifact consistency and visual communication validation
- Unit of analysis: one logical mapping edge or one rendered placement
- Experimental unit: source diagram, thesis page, IEEE page, or slide
- Number of runs or samples: all affected generated artifacts
- Conditions and controls: compare diagram labels against current OpenSpec and manuscript wording
- Randomization or chronological ordering: not applicable
- Blinding, if applicable: not applicable

## Variables

| Role | Variable | Definition | Unit | Collection source |
| --- | --- | --- | --- | --- |
| independent | diagram organization | problem/RQ/method/evidence/claim layout | version | source Markdown/Python |
| dependent | consistency | label and relationship agreement | pass/fail | source audit |
| dependent | legibility | no clipping, overlap, or unreadable scaling | pass/fail | PNG render |
| control | research content | existing RQ, E1--E9, metrics, boundaries | fixed | current specs |
| confounder | renderer | Word, LibreOffice, PowerPoint, Tectonic differences | renderer | QA logs |

## Inputs, Sampling, and Provenance

- Room/scenario: not applicable
- Sensor topology: existing eight-corner topology only as a method label
- Sampling cadence: not applicable
- Settling interval: not applicable
- Dataset source and license: no new dataset
- Inclusion criteria: every affected thesis/IEEE/presentation placement
- Exclusion criteria: repository structure diagrams and non-research admin files
- Missing-data handling: absent builders or outputs are failures
- Outlier policy: not applicable

## Leakage and Contamination Controls

- Train/test split: not applicable
- Time ordering: not applicable
- Repeated-measure handling: inspect both short and 30-minute decks
- Hyperparameter selection: not applicable
- Prohibited post-outcome adjustments: do not change RQ, metric, or evidence status to make the diagram easier to draw

## Baselines and Ablations

| ID | Comparator | Purpose |
| --- | --- | --- |
| `B-ARCH-01` | existing system abstraction tree | verify that the new figure adds argument logic rather than duplicates system layers |

## Metrics and Decision Criteria

| Hypothesis / claim | Metric | Success / interpretation rule | Failure rule |
| --- | --- | --- | --- |
| `CLM-ARCH-01` | mapping coverage | RQ1--RQ4, method core, E1--E9 classes and limits are visible | missing or misleading relationship |
| `CLM-ARCH-01` | visual QA | no overlap, clipping, broken glyph, or unreadable placement | any unresolved defect |
| `SYN-007` | synchronization | thesis, IEEE and both decks use equivalent logic | contradictory labels or stale diagram |

## Analysis

- Aggregation: pass only if every required placement passes.
- Uncertainty or interval estimate: not applicable.
- Statistical test, if justified: not applicable.
- Multiple-comparison handling: not applicable.
- Sensitivity analysis: inspect full-width paper placement and slide placement.

## Execution and Evidence Contract

| Step | Command | Expected machine-readable output |
| --- | --- | --- |
| 1 | `python3 scripts/build_architecture_diagrams.py` | architecture SVGs |
| 2 | `python3 scripts/build_thesis_docx.py` | thesis DOCX + PNG assets |
| 3 | `python3 scripts/build_thesis_pdf.py` | thesis PDF |
| 4 | `python3 scripts/build_thesis_pptx.py` | two PPTX files |
| 5 | `tectonic --keep-logs --keep-intermediates paper.tex` | IEEE PDF |
| 6 | `python3 scripts/validate_research_openspec.py` | validation pass |

## Deviations and Failure Reporting

- All deviations SHALL be recorded in `evidence.md`.
- Failed, missing, or contradictory results SHALL remain visible.
- Any change to research content requires a separate OpenSpec change.
