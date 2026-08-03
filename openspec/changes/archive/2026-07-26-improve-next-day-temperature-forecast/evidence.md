# Evidence

## Outcome

The registered next-day advantage was not supported. All negative and unstable
results remain in the machine-readable output and synchronized thesis
artifacts.

## Primary Result

- Dataset/task: SML2010 `S2`, dining and room temperature, `h=1440 min`
- Split: chronological 60% train, 10% validation, 30% final test; selected
  candidate refitted on the first 70%
- Validation selection: `damped_daily_trend`, `alpha=0.25`, for both targets
- Dining final MAE: selected `1.628868` versus persistence `1.517486`;
  relative change `-7.339903%`
- Room final MAE: selected `1.624972` versus persistence `1.499639`;
  relative change `-8.357545%`
- Mean relative change: `-7.848724%`
- Dining paired date-block MAE-reduction interval:
  `[-0.262278, 0.029453] degC`
- Room paired date-block MAE-reduction interval:
  `[-0.278769, 0.019744] degC`
- Bootstrap: 10,000 replicates, seed `20260726` for both targets
- Decisions: `H-ND-01=not_supported`,
  `H-ND-ROB-01=not_supported`, `CLM-ND-01=not_supported`

The registered bias-corrected persistence candidate was not selected by
validation. Its final-test MAE was `1.501763` and `1.488394`, approximately
`1.04%` and `0.75%` better than persistence. This is preserved as a descriptive
unselected-candidate observation and is not promoted to the main method.

## Post-Primary Exploratory Result

Protocol 2.0 was written after the primary decisions were known but before the
adaptive predictions were computed. Validation selected
`same_slot_median_14d` for both targets. It worsened dining and room MAE to
`1.651511` and `1.645603`, relative changes of `-8.832042%` and
`-9.733276%`; mean relative change was `-9.282659%`. The exploratory signal was
therefore not supported and cannot replace the primary decision.

## Leakage and Deviation Record

The first protocol execution stopped before candidate fitting or metric
production because `579` final-test rows lacked an exact `t-7d` timestamp at a
source-file boundary. Protocol amendment 1.1 then registered an
origin-or-past-only fallback with explicit availability flags, applied
identically to development and test rows. Candidate families, grids, split,
metrics, hypotheses, and thresholds were unchanged.

The final leakage audit records validation-only selection, no target-time
measurements or actual target-time weather, origin/past-only history fallback,
availability flags, and identical final-test rows for both targets.

During final reproducibility audit, the implementation was corrected so both
primary target bootstraps use the registered seed `20260726`; the room interval
was regenerated and synchronized before archive.

## Verification

- `python3 -m unittest discover -s tests`: 136 tests passed
- `python3 scripts/verify_thesis_results.py`: 59 PASS, 0 FAIL, 0 MISSING
- Research OpenSpec validation: 69 requirements, 148 scenarios, 0 active changes
- Presentation structural tests: both decks passed with no overflow
- Visual QA: Chinese thesis page 54, IEEE page 7, short-deck slide 12, and
  30-minute-deck slide 23 were inspected after rebuild; no clipping or overlap
- IEEE output: 7 A4 pages
- Chinese thesis output: 77 A4 pages

## Evidence Artifact

- Path:
  `outputs/data/public_benchmarks/next_day_temperature_improvement.json`
- SHA-256:
  `8ce43f4e00da4880a3d1ea9b9825dfbb8da6cc79a09613e5e74687b626df4129`
- Inputs and checkpoint hashes are embedded in the JSON.
