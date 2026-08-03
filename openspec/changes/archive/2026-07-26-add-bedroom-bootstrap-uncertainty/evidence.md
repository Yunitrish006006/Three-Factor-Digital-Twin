# Evidence Record

## Execution Summary

- Change: `add-bedroom-bootstrap-uncertainty`
- Requirement: `EVD-010`
- Research question: `RQ-E7-UNC-01`
- Hypothesis: `H-E7-UNC-01`
- Claim: `CLM-E7-UNC-01`
- Execution date: 2026-07-26
- Dataset: one real-bedroom scenario, one held-out pillow point, seven dates, four snapshots per date, 28 paired snapshots total
- Bootstrap: paired date-block percentile bootstrap, 20,000 replicates, seed `20260726`, 95% confidence level

## Machine-Readable Result

Source: `outputs/data/bedroom_01_weekly/weekly_simulation_summary.json`

| Metric | Raw MAE | Calibrated MAE | Mean reduction | 95% CI for reduction | Relative reduction | Improved snapshots |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| temperature | 0.8967 °C | 0.1676 °C | 0.7291 °C | [0.4582, 1.0232] | 81.31% | 26/28 |
| humidity | 4.1286 %RH | 0.3939 %RH | 3.7346 %RH | [3.2005, 4.2524] | 90.46% | 28/28 |
| illuminance | 309.0142 lux | 16.6450 lux | 292.3692 lux | [288.3083, 297.0237] | 94.61% | 28/28 |

All three absolute-reduction interval lower bounds are positive. Therefore,
`H-E7-UNC-01` is accepted for this registered dataset and endpoint.

The accepted claim is deliberately bounded: sparse calibration improves the
held-out pillow-point MAE under resampling of the seven observed dates. This is
not dense full-room truth, cross-room generalization, or an intervention
success rate.

## Implementation Deviation and Resolution

During execution, the weekly producer's adaptive deployment layout removed
furniture-blocked named corner sensors and introduced compensation or target
points that have no E7 observation records. That caused a missing
`floor_sw_comp_1` observation and also changed the topology used to reproduce
the registered E7 result.

The E7 evidence path was corrected to use the exact eight named corner sensors
that were actually observed. Adaptive compensation remains a deployment-design
feature, but it is not injected into this retrospective real-bedroom evidence
dataset. A regression test now confirms that unobserved compensation points are
ignored.

## Commands and Verification

```text
python3 scripts/run_bedroom_weekly_simulation.py
python3 scripts/build_thesis_docx.py
python3 scripts/build_thesis_pdf.py
python3 scripts/build_thesis_pptx.py
cd docs/papers/ieee && tectonic --keep-logs --keep-intermediates paper.tex
python3 -m unittest discover -s tests
python3 scripts/verify_thesis_results.py
python3 scripts/validate_research_openspec.py
```

- Unit tests: 113 tests, all passed.
- Thesis result verifier: 42 PASS, 0 FAIL, 0 MISSING.
- Research OpenSpec before archival: 10 spec files, 65 requirements, 134 scenarios, 1 active change.
- Research OpenSpec after archival: 10 spec files, 65 requirements, 134 scenarios, 0 active changes.
- PowerPoint structural QA: both decks passed with no overflow detected.
- Content consistency search found the registered interval values and bounded interpretation in the Chinese thesis/build source, IEEE source, presentation source, outlines, and 30-minute speaker notes.

## Build and Visual QA

- Chinese thesis PDF: 74 A4 pages; affected pages and all contact sheets inspected without clipping or overlap.
- IEEE manuscript: 7 A4 pages; affected pages and all-page contact sheet inspected without clipping or overlap.
- Short presentation: 42 slides; all contact sheets and affected slide 11 inspected.
- 30-minute presentation: 54 slides; all contact sheets and affected slides 19–20 inspected.
- The LibreOffice DOCX preview environment omitted some CJK glyphs because of
  its font setup; layout was inspected there, while the rebuilt Chinese PDF was
  used for authoritative CJK visual verification.
- Non-blocking build warnings remain: system-font/ToUnicode warnings in the
  Chinese PDF build, LaTeX underfull boxes, and a 1.5117 pt overfull equation in
  the IEEE build. Visual inspection found no material layout defect.

## Output Checksums

| Artifact | SHA-256 |
| --- | --- |
| weekly simulation summary | `16ea1c1355f074626908b29d4803f2a47644d82c4f7387e1fb42a0d07be94023` |
| Chinese thesis DOCX | `2172bbf46c47158c6038349f4458de78d2aa22296d182020924a61ddb7b19ea9` |
| Chinese thesis PDF | `c48d5c3dd6627887a05708249325eaba81bfe4895b931e27e7743bb2a6677126` |
| short presentation PPTX | `abcf091b310d0353ca6c4c3834ec2a730efd8a8205c9e406e879e22a0384c030` |
| 30-minute presentation PPTX | `7b4a7b4203bb70c42e2b08850d89a0c6ddf1752c80207017fc4334f0617f24a7` |
| IEEE paper PDF | `69dd475d8d90dfc874a5113d36fa8aad8453a066fa8b01c65c6598544f1c451e` |

## Claim Decision

- `H-E7-UNC-01`: accepted for the registered E7 data and paired mean-MAE-reduction endpoint.
- `CLM-E7-UNC-01`: accepted with the stated one-room, one-point, seven-date boundary.
- E8 before/after intervention evidence remains future work; no causal efficacy claim is introduced by this change.
