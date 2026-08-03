# Tasks

## 1. Specification and Data Contracts

- [ ] 1.1 <!-- task --> (`CAP-???`, `RQ?`)
- [ ] 1.2 Validate input, output, unit, and missing-data contracts.

## 2. Implementation or Experiment Setup

- [ ] 2.1 <!-- implementation/protocol task --> (`H?`, `E?`)
- [ ] 2.2 Add positive, negative, boundary, and failure-case tests.

## 3. Execution and Evidence

- [ ] 3.1 Execute the pre-registered commands without silently changing thresholds.
- [ ] 3.2 Preserve machine-readable outputs and populate `evidence.md`.
- [ ] 3.3 Run result verification and record missing or contradictory evidence.

## 4. Claim Review

- [ ] 4.1 Decide every hypothesis and intended claim from actual evidence.
- [ ] 4.2 Weaken or remove unsupported claims across all synchronized artifacts.

## 5. Synchronized Research Artifacts

- [ ] 5.1 Update Chinese thesis source and build source where applicable.
- [ ] 5.2 Update IEEE source and references where applicable.
- [ ] 5.3 Update presentation source and outlines where applicable.
- [ ] 5.4 Rebuild affected figures, DOCX, PDF, PPTX, and IEEE PDF.
- [ ] 5.5 Search the repository for stale metrics, captions, names, and claims.

## 6. Final Verification

- [ ] 6.1 Run `python3 -m unittest discover -s tests`.
- [ ] 6.2 Run `python3 scripts/verify_thesis_results.py`.
- [ ] 6.3 Run `python3 scripts/validate_research_openspec.py`.
- [ ] 6.4 Confirm every task and completion criterion before archive.
