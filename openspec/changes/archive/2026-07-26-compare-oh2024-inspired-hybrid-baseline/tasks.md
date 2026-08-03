# Tasks

## 1. Specification and Data Contracts

- [x] 1.1 Register `RQ-PHB-01`, `EQ-PHB-01`, `H-PHB-01`, `CLM-PHB-01`, and `EVD-012`.
- [x] 1.2 Validate target, horizon, metric, method-fidelity, and missing-data contracts.

## 2. Implementation or Experiment Setup

- [x] 2.1 Implement the focused SML2010 five-comparator evaluator.
- [x] 2.2 Add the command-line producer and deterministic JSON writer.
- [x] 2.3 Add positive, split-parity, leakage-boundary, and insufficient-data tests.

## 3. Execution and Evidence

- [x] 3.1 Execute the pre-registered command without changing features, ridge, targets, horizons, or thresholds.
- [x] 3.2 Preserve machine-readable output and populate `evidence.md`.
- [x] 3.3 Extend result verification with method-fidelity and metric checks.

## 4. Claim Review

- [x] 4.1 Decide `H-PHB-01` and `CLM-PHB-01` from actual evidence.
- [x] 4.2 Preserve comparator losses and prohibit original-paper reproduction claims.

## 5. Synchronized Research Artifacts

- [x] 5.1 Update Chinese thesis source and build source.
- [x] 5.2 Update IEEE source.
- [x] 5.3 Update presentation source, outlines, and speaker notes.
- [x] 5.4 Rebuild affected DOCX, PDFs, PPTXs, and IEEE PDF.
- [x] 5.5 Search the repository for stale or overclaimed comparison language.

## 6. Final Verification

- [x] 6.1 Run `python3 -m unittest discover -s tests`.
- [x] 6.2 Run `python3 scripts/verify_thesis_results.py`.
- [x] 6.3 Run `python3 scripts/validate_research_openspec.py`.
- [x] 6.4 Confirm every task and completion criterion before archive.
