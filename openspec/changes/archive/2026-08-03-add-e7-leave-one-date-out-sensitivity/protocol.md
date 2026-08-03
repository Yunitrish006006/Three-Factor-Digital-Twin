# Pre-Registered Protocol

## Protocol Identity

- Change: `add-e7-leave-one-date-out-sensitivity`
- Protocol version: `1.0`
- Registration date: `2026-08-03`
- Related IDs: `RQ-E7-LODO-01`, `H-E7-LODO-01`, `CLM-E7-LODO-01`, `EVD-014`
- Status: `COMPLETED`

## Experimental Design

- Study type: deterministic secondary sensitivity analysis of existing E7 snapshots.
- Observed sample: 7 dates, 4 snapshots per date, 28 snapshots total.
- Fold: remove all snapshots from exactly one date; compute on the remaining 24 snapshots.
- Fold count: exactly 7, sorted by omitted date.
- Metrics: raw MAE, calibrated MAE, absolute MAE reduction, relative reduction percentage.
- Randomness: none.

## Inputs and Inclusion

- Input: snapshot rows produced from `docs/requirements/bedroom_01_combined_room_and_weekly_simulation.json`.
- Include every row with a non-empty date and complete raw/calibrated absolute error values for all three metrics.
- Missing fields, fewer than two dates, or a deletion leaving zero rows SHALL fail visibly.
- No trimming, weighting, outlier removal, or fold exclusion is allowed.

## Decision Criteria

| ID | Success rule | Failure rule |
| --- | --- | --- |
| `H-E7-LODO-01` | minimum absolute MAE reduction across 7 folds is > 0 for all three metrics | any metric minimum <= 0 |
| `CLM-E7-LODO-01` | exact folds and extrema are reported with one-room boundary | any missing/adverse fold is hidden or wording implies external validity |

## Analysis

For each sorted date, remove all rows with that date. For each metric, compute mean raw absolute error and mean calibrated absolute error on the remaining rows. Store their difference and relative percentage. Summarize the minimum and maximum absolute reduction across the seven folds and the omitted date associated with each extreme.

## Execution and Evidence Contract

| Step | Command | Expected output |
| --- | --- | --- |
| 1 | `python3 scripts/run_bedroom_weekly_simulation.py` | `aggregate.leave_one_date_out_sensitivity` |
| 2 | `python3 -m unittest tests.test_bedroom_uncertainty` | deterministic positive and adverse tests |
| 3 | `python3 scripts/verify_thesis_results.py` | registered extrema PASS |
| 4 | rebuild commands in `AGENTS.md` | synchronized DOCX/PDF/PPTX/IEEE outputs |

## Deviations and Failure Reporting

- Any change to fold definition, included dates, endpoint, weighting, or decision rule SHALL be recorded.
- Zero, negative, or inconsistent folds SHALL remain visible and shall weaken the claim.
