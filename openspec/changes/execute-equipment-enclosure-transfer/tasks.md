# Tasks

## 1. Specification and Data Contracts

- [x] 1.1 Register `E11A`, `RQ-ENC-01` through `RQ-ENC-03`, `H-ENC-01`, and `CLM-ENC-01` (`ENC-001`–`ENC-004`).
- [x] 1.2 Fix the BMC input, chronological split, 20–30 °C domain, output and failure contracts.
- [x] 1.3 Record primary papers and candidate public datasets without treating literature metrics as project evidence.

## 2. Implementation or Experiment Setup

- [x] 2.1 Add the InfluxDB-style BMC parser and deterministic case builder (`ENC-001`).
- [x] 2.2 Add persistence, linear and thermal-balance comparators on identical rows (`ENC-002`).
- [x] 2.3 Add positive, domain-boundary and insufficient-data tests.

## 3. Execution and Evidence

- [x] 3.1 Acquire selected BMC traces and record exact source commit/license/checksums.
- [x] 3.2 Execute at least three eligible traces without changing registered thresholds.
- [x] 3.3 Preserve machine-readable output and populate `evidence.md` from the actual run.
- [x] 3.4 Record every adverse, missing, failed and out-of-scope case.

## 4. Claim Review

- [x] 4.1 Decide `H-ENC-01` and `CLM-ENC-01` from actual evidence.
- [x] 4.2 Mark `H-ENC-01` not supported while keeping spatial enclosure applicability `NOT_EVALUATED`.

## 5. Synchronized Research Artifacts

- [x] 5.1 Update Chinese thesis source and DOCX builder for the negative result.
- [x] 5.2 Update IEEE source and references for the negative result.
- [x] 5.3 Update presentation source and outlines for the negative result.
- [x] 5.4 Rebuild affected DOCX, PDF, PPTX, IEEE PDF and figures.
- [x] 5.5 Search for stale `NOT_EVALUATED`, metrics, captions and scope wording.

## 6. Final Verification

- [ ] 6.1 Run enclosure tests and the full unit-test suite after empirical execution.
- [ ] 6.2 Run thesis-result verification after synchronized edits.
- [ ] 6.3 Run research OpenSpec validation.
- [ ] 6.4 Confirm every completion criterion before archive.
