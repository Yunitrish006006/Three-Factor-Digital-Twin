# Evidence Record

## Execution Summary

- Change: `add-e7-leave-one-date-out-sensitivity`
- Requirement: `EVD-014`
- Research question: `RQ-E7-LODO-01`
- Hypothesis: `H-E7-LODO-01`
- Claim: `CLM-E7-LODO-01`
- Execution date: 2026-08-03
- Dataset: one real-bedroom scenario, one held-out pillow point, seven dates, four snapshots per date, 28 paired snapshots total
- Analysis: deterministic seven-fold leave-one-date-out sensitivity; each fold omits one complete date and retains 24 snapshots

## Machine-Readable Result

Source: `outputs/data/bedroom_01_weekly/weekly_simulation_summary.json`

| Omitted date | Temperature reduction (°C) | Humidity reduction (%RH) | Illuminance reduction (lux) |
| --- | ---: | ---: | ---: |
| 2026-04-14 | 0.8124 | 3.5551 | 293.4640 |
| 2026-04-15 | 0.7351 | 3.6707 | 292.6852 |
| 2026-04-16 | 0.6964 | 3.7789 | 292.3901 |
| 2026-04-17 | 0.7543 | 3.7328 | 292.8230 |
| 2026-04-18 | 0.6123 | 3.9245 | 290.5716 |
| 2026-04-19 | 0.6903 | 3.8576 | 291.2726 |
| 2026-04-20 | 0.8033 | 3.6229 | 293.3777 |

| Metric | Minimum reduction | Omitted date at minimum | Maximum reduction | Omitted date at maximum |
| --- | ---: | --- | ---: | --- |
| temperature | 0.6123 °C | 2026-04-18 | 0.8124 °C | 2026-04-14 |
| humidity | 3.5551 %RH | 2026-04-14 | 3.9245 %RH | 2026-04-18 |
| illuminance | 290.5716 lux | 2026-04-18 | 293.4640 lux | 2026-04-14 |

Every fold-level reduction is positive for every metric. Therefore,
`H-E7-LODO-01` is supported under the registered decision rule.

The accepted claim is bounded to the observed seven dates in `bedroom_01`, one
held-out pillow point, and the current sparse-calibration pipeline. The folds
overlap and are not independent replications. This result does not establish
dense-field accuracy, cross-room generalization, or causal intervention
efficacy.

## Commands and Verification

```text
python3 scripts/run_bedroom_weekly_simulation.py
python3 scripts/build_architecture_diagrams.py
python3 scripts/build_thesis_docx.py
python3 scripts/build_thesis_pdf.py
python3 scripts/build_thesis_pptx.py
cd docs/papers/ieee && tectonic --keep-logs --keep-intermediates paper.tex
python3 -m unittest discover -s tests
python3 scripts/verify_thesis_results.py
python3 scripts/validate_research_openspec.py
```

- Unit tests: 141 tests, all passed.
- Thesis result verifier: 63 PASS, 0 FAIL, 0 MISSING.
- Research OpenSpec before archival: 10 spec files, 69 requirements, 148 scenarios, 1 active change.
- Research OpenSpec after archival: 10 spec files, 70 requirements, 151 scenarios, 0 active changes.
- Content consistency search found the three registered minima in the Chinese thesis/build source, IEEE source, presentation source, both outlines, speaker notes, and professor weekly report.
- `git diff --check` passed after trimming trailing whitespace emitted in the generated IEEE log.

## Build and Visual QA

- Chinese thesis PDF: 77 A4 pages; affected pages 57 and 71 rendered and inspected without clipping or overlap.
- IEEE manuscript: 7 A4 pages; affected pages 6 and 7 rendered and inspected without clipping or overlap.
- Short presentation: 42 slides; affected slide 11 rendered and inspected, with no shape outside slide bounds.
- 30-minute presentation: 54 slides; affected slides 19 and 20 rendered and inspected, with no shape outside slide bounds.
- DOCX and both PPTX files were also parsed by macOS Quick Look; the registered values were present in the generated previews.
- Non-blocking build warnings remain: system-font/ToUnicode warnings in the Chinese PDF build, LaTeX underfull boxes, and a 1.5117 pt overfull equation in the IEEE build. Visual inspection found no material layout defect.
- An extra `py_compile` check could not write the macOS system-Python cache outside the workspace. This was an environment permission deviation, not a source failure; module execution and the full unit-test suite passed.

## Output Checksums

| Artifact | SHA-256 |
| --- | --- |
| weekly simulation summary | `ad34b7743b5b1bb4c23459724193826e73c9ccc23a824a4fbc28ca90b0f075d7` |
| Chinese thesis DOCX | `cc7280aa61eba81889c121ac33d59b28d69a28810d34fb433e0ae212f32b7c97` |
| Chinese thesis PDF | `2d8ca3484e2ef9bfb3f0689002808a6683d3af9805ea7bde43c3c1075243f19f` |
| short presentation PPTX | `c611d7af56f19d072f3353d5fb9ad9745698d3bd0a7e54122dc444a7a076575c` |
| 30-minute presentation PPTX | `7a23c2e029c90a07a6a32bbddb0b2bdf4de566ec8b43733e8f78755c7f759034` |
| IEEE paper PDF | `5602b1bb05cc0fc66a3b9fbab872cc87785cdab90370036941d818323e5f9ae2` |

## Claim Decision

- `H-E7-LODO-01`: supported for the registered E7 data and fold-level mean-MAE-reduction endpoint.
- `CLM-E7-LODO-01`: accepted with the one-room, one-point, seven-date boundary.
- No E8 causal efficacy or cross-room claim is introduced by this change.
