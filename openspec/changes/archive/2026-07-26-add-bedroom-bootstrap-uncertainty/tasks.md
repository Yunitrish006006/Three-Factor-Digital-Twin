# Tasks

## 1. Specification and Data Contracts

- [x] 1.1 Define the paired date-block bootstrap contract (`EVD-010`, `RQ-E7-UNC-01`).
- [x] 1.2 Validate required date, raw-error, calibrated-error, metric, and output metadata fields.

## 2. Implementation and Tests

- [x] 2.1 Add deterministic E7 bootstrap analysis to the weekly simulation producer.
- [x] 2.2 Add positive, boundary, invalid-input, and deterministic tests.
- [x] 2.3 Extend result verification with registered uncertainty values.

## 3. Execution and Evidence

- [x] 3.1 Execute 20,000 date-block replicates with seed 20260726.
- [x] 3.2 Preserve the machine-readable output and record every metric, interval, and improvement fraction.
- [x] 3.3 Decide `H-E7-UNC-01` without changing the registered threshold.

## 4. Claim Review

- [x] 4.1 Bound `CLM-E7-UNC-01` to one room, one pillow point, and seven dates.
- [x] 4.2 Confirm improvement fraction is not described as intervention success rate.

## 5. Synchronized Research Artifacts

- [x] 5.1 Update Chinese thesis source and build source.
- [x] 5.2 Update IEEE source.
- [x] 5.3 Update presentation source, both outlines, and speaker notes.
- [x] 5.4 Rebuild DOCX, PDFs, and both PPTX outputs.
- [x] 5.5 Search for stale E7 wording without uncertainty or with overclaim.

## 6. Final Verification

- [x] 6.1 Run `python3 -m unittest discover -s tests`.
- [x] 6.2 Run `python3 scripts/verify_thesis_results.py`.
- [x] 6.3 Run `python3 scripts/validate_research_openspec.py`.
- [x] 6.4 Sync `EVD-010` into the main spec and archive the completed change.
