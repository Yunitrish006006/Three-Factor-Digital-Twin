# Evidence Record

## Outcome

The E8 intervention-validation workflow is now executable and preregistered,
but recommendation efficacy remains untested.

- `RQ-E8-PREP-01`: answered for method readiness.
- `H-E8-PREP-01`: accepted.
- `CLM-E8-PREP-01`: accepted only as an execution-readiness claim.
- Current real completed trial count: `0`.
- Current evidence status: `NOT_EVALUATED`.
- Current efficacy estimates: all null.

No synthetic record was written into `outputs/data/` as E8 efficacy evidence.

## Implemented Data and Analysis Path

- Versioned schema:
  `docs/requirements/e8_intervention_trial_schema.json`
- Empty field template:
  `docs/templates/e8_intervention_trials_template.json`
- Analysis module:
  `digital_twin/evaluation/intervention.py`
- Command:
  `scripts/analyze_e8_intervention_trials.py`
- Machine-readable status:
  `outputs/data/e8_intervention_summary.json`
- Human-readable status:
  `outputs/data/e8_intervention_summary.md`

The analyzer independently recomputes three-factor comfort penalty, actual
improvement, prediction error, and per-factor direction agreement. It computes
top-1 regret and Spearman correlation only when a matched block contains enough
comparable action arms. Missing design support produces null rather than an
inferred value.

## Verification Results

- Focused E8 tests: 8 passed.
- Full unit suite: 121 passed.
- Thesis result verifier: 45 PASS, 0 FAIL, 0 MISSING.
- OpenSpec after main-spec synchronization and before archival:
  10 spec files, 67 requirements, 140 scenarios, 1 active change.
- OpenSpec after archival:
  10 spec files, 67 requirements, 140 scenarios, 0 active changes.
- Both PowerPoint files passed structural overflow testing.
- Content search confirmed the same `0` trial, `NOT_EVALUATED`, null-estimate,
  and execution-kit boundary in the Chinese thesis/build source, IEEE source,
  presentation source, outlines, speaker notes, and standalone E8 protocol.

## Build and Visual QA

- Chinese thesis PDF: 75 A4 pages; all-page montage inspected and affected
  pages 57-58 inspected at full size without clipping or overlap.
- IEEE manuscript: 7 A4 pages; all pages and affected page 6 inspected without
  clipping or overlap.
- Short presentation: 42 slides; all-slide montage and affected slide 9
  inspected.
- 30-minute presentation: 54 slides; all-slide montage and affected slide 20
  inspected.
- DOCX: 61 rendered pages; all-page montage and affected pages 47-48 inspected
  for layout. The LibreOffice preview environment continues to omit some CJK
  glyphs, so the rebuilt Chinese PDF is the authoritative CJK visual check.
- Existing non-blocking build warnings remain: system-font/ToUnicode warnings
  in the Chinese PDF build, LaTeX underfull boxes, and a 1.5117 pt overfull
  equation in the IEEE build. No material visual defect was found.

## Current Summary

```json
{
  "evidence_status": "NOT_EVALUATED",
  "completed_trials": 0,
  "excluded_trials": 0,
  "efficacy_estimates": null
}
```

## Checksums

| Artifact | SHA-256 |
| --- | --- |
| E8 JSON Schema | `7e0fcbe831a0149cdd2f46b2cb44f15a80b534c74f926724f3d74a68840f85c2` |
| E8 empty template | `1d1331f20cc34e1f8943fb2f51a97666cacca94ad310af2a6eeedaa2326bb4a0` |
| E8 current summary | `2fa66eafc11b2e5648807d733f67b5cb3fc905bc95fd899ade716325e8f07e44` |
| Chinese thesis DOCX | `2f53d4058e2e8b61636f68c88278e341503287e495982836ff8f824f62bd061e` |
| Chinese thesis PDF | `d4c1bf7257e04a3d2c32ccef4eb7f41ca293f31c6f656ba30cf97bdf117d6872` |
| short presentation | `7d60608f9518a3a80b4a36cd7652be8dc90bbfe67c2441610084bfaff127bda8` |
| 30-minute presentation | `4dda290c4ba5fb704a231fcd2e56a8952de874584709d23880de5e7a90fed075` |
| IEEE paper PDF | `bbe79d82cca00cb09cd77a833e858eb9f6f8801a17fbb02e018faa2f7d620818` |

## Claim Boundary

This change supports only the claim that E8 data collection and analysis are
ready to execute. It does not support success rate, measured benefit, rank
superiority, control efficacy, or a causal recommendation claim. Those require
completed real before/after trials and a separate evidence-review change.
