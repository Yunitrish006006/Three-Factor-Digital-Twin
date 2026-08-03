# Evidence Record

## Execution Summary

- Change: `compare-oh2024-inspired-hybrid-baseline`
- Requirement: `EVD-012`
- Research question: `RQ-PHB-01`
- Evaluation question: `EQ-PHB-01`
- Hypothesis: `H-PHB-01`
- Claim: `CLM-PHB-01`
- Execution date: 2026-07-26
- Dataset: SML2010 task S2, dining and room temperatures, 15-minute cadence
- Design: six target--horizon cases, chronological 70/30 split, ridge `1e-3`, no shuffle
- Comparators: persistence, direct linear regression, raw physics prior, project readout, and Oh2024-inspired additive residual

## Machine-Readable Result

Source: `outputs/data/public_benchmarks/oh2024_inspired_sml2010_comparison.json`

| Horizon | Persistence MAE | Direct LR MAE | Raw physics MAE | Project readout MAE | Oh2024-inspired MAE | Lowest MAE |
| --- | --- | --- | --- | --- | --- | --- |
| 15 min | 0.1182 / 0.1153 | 0.0426 / 0.0519 | 0.4332 / 0.1572 | 0.0728 / 0.0951 | 0.0422 / 0.0517 | Oh2024-inspired, both points |
| 60 min | 0.4698 / 0.4580 | 0.1925 / 0.2297 | 0.4209 / 0.4204 | 0.1562 / 0.2167 | 0.1925 / 0.2305 | project readout, both points |
| 1440 min | 1.5175 / 1.4996 | 1.7532 / 1.7686 | 1.5869 / 1.5092 | 1.7894 / 1.8010 | 1.7538 / 1.7723 | persistence, both points |

Pair order is dining / room and all MAEs are in degrees Celsius.

The Oh2024-inspired residual reduced MAE relative to raw physics in 4 of 6
registered cases. Therefore, `H-PHB-01` is supported exactly at its
pre-registered threshold. Lowest-MAE counts across the six cases were:
Oh2024-inspired 2, project readout 2, persistence 2, direct linear regression
0, and raw physics 0.

The adverse next-day result is retained. At 1440 minutes, the Oh2024-inspired
MAE exceeded raw physics by 0.1668 degrees Celsius for dining and 0.2630
degrees Celsius for room. The published next-day advantage did not transfer to
this SML2010 two-point task.

## Method Fidelity and Claim Boundary

The transfer preserves the cited paper's additive logic:

`target-time physical prediction + learned residual = corrected prediction`.

The residual head is fixed ridge-linear because the paper's BEMS data are
confidential and its CNN--LSTM, TRNSYS Type 56, and calibrated RC
implementations are unavailable. Project pseudo-room physics and SML2010
two-point temperatures replace the original commercial return-air task.

`CLM-PHB-01` is supported as a public-task method-transfer comparison. This is
not a reproduction of Oh et al.'s data, physical model, CNN--LSTM, or published
December/January/February results, and it is not a full 3-D field validation.

## Implementation Deviation and Resolution

The first official command attempt stopped before producing experimental
results with `ModuleNotFoundError: digital_twin` because the standalone runner
did not add the repository root to `sys.path`. The runner packaging was fixed,
and the same pre-registered command, features, ridge, targets, horizons,
chronological split, and thresholds were then executed. No result-dependent
protocol setting changed.

## Commands and Verification

```text
python3 scripts/run_oh2024_inspired_comparison.py
python3 scripts/build_thesis_docx.py
python3 scripts/build_thesis_pdf.py
python3 scripts/build_thesis_pptx.py
cd docs/papers/ieee && tectonic --keep-logs --keep-intermediates paper.tex
python3 -m unittest discover -s tests
python3 scripts/verify_thesis_results.py
python3 scripts/validate_research_openspec.py
```

- Unit tests: 131 tests, all passed.
- Thesis result verifier: 51 PASS, 0 FAIL, 0 MISSING.
- Research OpenSpec before archival: 10 spec files, 68 requirements, 143 scenarios, 1 active change.
- Research OpenSpec after archival: 10 spec files, 68 requirements, 143 scenarios, 0 active changes.
- Both PowerPoint decks passed structural QA with no overflow detected.
- `git diff --check` passed after removing generated-log trailing whitespace.
- Content search found only the explicit prohibition examples and method-transfer/reproduction boundary language; no stale section numbering or unsupported superiority claim remained.

## Build and Visual QA

- Chinese thesis PDF: 76 A4 pages; affected pages 61--63 and the DOCX all-page contact sheet were inspected without clipping or overlap.
- IEEE manuscript: 7 A4 pages; affected pages 6--7 and the all-page contact sheet were inspected without clipping or overlap.
- Short presentation: 42 slides; all-slide contact sheet and affected slide 12 inspected.
- 30-minute presentation: 54 slides; all-slide contact sheet and affected slide 23 inspected.
- The LibreOffice DOCX preview environment omitted some CJK glyphs because of its font setup; layout was inspected there, while the rebuilt Chinese PDF was used for authoritative CJK verification.
- Non-blocking build warnings remain: system-font/ToUnicode warnings in the Chinese PDF build, LaTeX underfull boxes, and a 1.5117 pt overfull equation in the IEEE build. Visual inspection found no material layout defect.

## Output Checksums

| Artifact | SHA-256 |
| --- | --- |
| focused transfer JSON | `ec7e9d2408e6764daba4647738b12e7a1cdcb9ee9835778748233103d274b272` |
| Chinese thesis DOCX | `a789155e668d632eec36e7dcd078b35fb35c1670a4bc38518f59cbc4eb435370` |
| Chinese thesis PDF | `d9faa7e3a03146f7e1a4a7b0c5c079bbbfcd05496d8bd953e61c84b1d5ce29cb` |
| short presentation PPTX | `3e196e92e7782523e148891f420ba5c4ce2e065943f845d03c22df4e89ec2577` |
| 30-minute presentation PPTX | `9da983b879e617d61d42294eac4950878a6bca22b27d8be8b5e25bea3b682c9b` |
| IEEE paper PDF | `61155829d77eb3b029b39c2e98b978f5eba94692ed41d76decf5afe903bea811` |

## Claim Decision

- `H-PHB-01`: supported exactly at 4 of 6 cases versus raw physics.
- `CLM-PHB-01`: supported as a method-transfer comparator with the stated data, architecture, target, and validation boundaries.
- The 1440-minute negative result remains visible and rules out a reproduced next-day-advantage claim.
