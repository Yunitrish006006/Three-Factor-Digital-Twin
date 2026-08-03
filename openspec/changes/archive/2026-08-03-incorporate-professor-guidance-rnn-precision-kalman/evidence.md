# Evidence Record

## Execution Summary

- Change: `incorporate-professor-guidance-rnn-precision-kalman`
- Related requirements: `ACT-007`, `EVD-015`, `HRL-008`, `HRL-009`, `RPD-007`, `RGV-007`, `SFE-007`
- Related questions: `RQ-RNN-01`, `EQ-APP-01`, `EQ-KF-01`
- Related claims: `CLM-RNN-01`, `CLM-APP-01`, `CLM-KF-01`
- Execution date: 2026-08-03
- RNN dataset/task: normalized SML2010 S2
- RNN design: fixed vanilla Elman RNN, four-record history, hidden size 6, seed 42, 30 epochs, chronological 70/30 split
- Evidence status: RNN `COMPLETE`; application positioning `DOCUMENT_ONLY`; Kalman project performance `NOT_EVALUATED`

## Machine-Readable RNN Result

Source: `outputs/data/public_benchmarks/rnn_sml2010_comparison.json`

All four methods used the same eligible endpoints, four origin records, targets, chronological split, test rows, endpoint hashes, and input-content hashes. The primary comparison did not load a learned synthetic checkpoint.

| Horizon | Eligible endpoints | Train | Test | Parity | RNN loss finite |
| ---: | ---: | ---: | ---: | --- | --- |
| 15 min | 4,121 | 2,884 | 1,237 | passed | yes |
| 60 min | 4,110 | 2,877 | 1,233 | passed | yes |
| 1,440 min | 3,933 | 2,753 | 1,180 | passed | yes |

| Lowest-MAE method | Cases |
| --- | ---: |
| sequence linear regression | 7 / 12 |
| persistence | 5 / 12 |
| physics-structured readout | 0 / 12 |
| vanilla RNN | 0 / 12 |

The RNN beat persistence in 2 cases and the physics-structured readout in 2 cases, but it did not beat sequence linear regression in any of the 12 target-horizon cases. This adverse result was retained. No architecture, history, split, target, or threshold was changed after observing the formal result.

## Application-Scope Evidence

Source: `docs/research/professor_guidance_application_scope_zh.md`

- Human comfort is now a target-band and tolerance-based decision-support case; low estimator MAE is not treated as proof that people require equally narrow actuation.
- The current indoor operating and target-state claim is fixed to `20–30 °C`. Outdoor boundary inputs may be outside the interval but do not expand the indoor claim.
- A small dynamically programmed closed plant-growth environment is retained only as a candidate. The current model lacks PPFD/PAR, CO2, substrate/root-zone moisture, airflow, actuator logs, and biological endpoints.
- Literature treatments outside `20–30 °C` are explicitly `out_of_domain` rather than truncated into the project scope.

## Kalman Reference Evidence

Source: `docs/models/kalman_filter_research_direction_zh.md`

- The note defines possible roles in sensor denoising, latent-state estimation, sensor fusion, and online parameter adaptation.
- Both favorable EKF adaptation evidence and adverse greenhouse filtering evidence are retained.
- The future comparison contract requires identical rows and targets for unfiltered physics, moving average, linear Kalman filter, and any justified EKF.
- No project Kalman experiment was run in this change; `CLM-KF-01` remains `NOT_EVALUATED`.

## Commands and Verification

```text
python3 scripts/run_rnn_public_comparison.py
python3 -m unittest tests.test_rnn_public_comparison
python3 -m unittest discover -s tests
python3 scripts/verify_thesis_results.py
python3 scripts/validate_research_openspec.py
python3 scripts/build_architecture_diagrams.py
python3 scripts/build_thesis_docx.py
python3 scripts/build_thesis_pdf.py
python3 scripts/build_thesis_pptx.py
cd docs/papers/ieee && tectonic --keep-logs --keep-intermediates paper.tex
```

- Focused RNN tests: 10 tests, all passed.
- Full test suite: 151 tests, all passed.
- Thesis result verifier: 69 PASS, 0 FAIL, 0 MISSING.
- Research OpenSpec before archival: 10 spec files, 77 requirements, 167 scenarios, 1 active change.
- Research OpenSpec after archival: 10 spec files, 77 requirements, 167 scenarios, 0 active changes.
- Comparator audits: all three horizon audits and all 12 case statuses passed.
- Content searches found RNN parity, the `20–30 °C` indoor boundary, tolerance-based human comfort, plant-data gaps, and Kalman `NOT_EVALUATED` wording across the applicable synchronized sources.
- The professor weekly report contains no submission-target or personal-development section.

## Build and Visual QA

- Chinese thesis: 81 A4 pages; all pages rendered from the synchronized PDF and inspected as four contact sheets. Affected pages 8–9, 57–58, and 65–67 were additionally inspected at high resolution without clipping or overlap.
- DOCX: the skill renderer could not run because LibreOffice/`soffice` is absent. macOS Quick Look successfully parsed the DOCX to a full HTML preview with all embedded attachments; the source-synchronized thesis PDF was used for page-by-page visual QA.
- IEEE manuscript: rebuilt to 7 A4 pages after removing repeated narrative without changing results or claim boundaries; every page was rendered and inspected without clipping or overlap. Non-blocking warnings remain for underfull boxes and one 1.5117 pt overfull equation.
- Short presentation: 42 slides rendered; all slides inspected as contact sheets, with affected slides 12–14 also inspected individually.
- 30-minute presentation: 54 slides rendered; all slides inspected as contact sheets, with affected slides 23–25 also inspected individually.
- Chinese PDF build retains non-blocking system-font/ToUnicode and underfull warnings; visual inspection found no material layout defect.
- The thesis DOCX/PDF copies under `docs/papers/thesis/` and `outputs/papers/` have identical SHA-256 values.

## Output Checksums

| Artifact | SHA-256 |
| --- | --- |
| RNN comparison JSON | `c22e2b89d56d0367102c91afb940296126172dbfe976c4a25df20ddaae1e4913` |
| professor weekly report | `1882fee4b193e2b5b9dd9b908447f09d2e70274c7a1ca2c279e1ae9efdbe3022` |
| Chinese thesis DOCX | `13dd2aca50e70168f9279e5208993d5ec6d807c5966f7213e370ba0a6caf61bc` |
| Chinese thesis PDF | `145b3d9245f4f7b6f0fd039792429cb4d64a902c05084db01de476c57fd83e9b` |
| short presentation PPTX | `1bfecb3db380691be1181868afdbf115d303c1fc277c9046166e3559a73f28d5` |
| 30-minute presentation PPTX | `0b80340a91bd46148795a915fc02c7c3930846c31eade412dc2d89ec1d646c67` |
| IEEE paper PDF | `c9bd3ca4e957abe413f0c9ce4a8371ea0a94212e80149684564edb785db310ce` |

## Deviations and Adverse Results

- The formal RNN configuration and comparison contract were not changed after result observation.
- Unit fixtures use their actual one-minute cadence to exercise generic endpoint construction; the formal SML2010 experiment remains at the registered 15-minute cadence.
- The DOCX-specific renderer was unavailable because `soffice` is not installed; this is recorded above rather than represented as a successful DOCX-to-PDF render.
- The standalone slide overflow checker could not start because its optional NumPy dependency is absent. Both decks still rendered successfully, and all slide images were visually inspected.
- RNN obtained zero lowest-MAE cases; this result remains visible in JSON and every synchronized narrative.
- Kalman-family project performance is not evaluated, and the negative greenhouse filtering study remains in the note and synchronized discussion.

## Claim Decisions

- `CLM-RNN-01`: accepted as a bounded descriptive claim. The same-data comparison is complete, but no RNN or project-method superiority claim is supported.
- `CLM-APP-01`: accepted only as a candidate-direction claim. Dynamic closed plant growth may motivate time-varying precision inside `20–30 °C`, but current evidence does not establish cultivation efficacy or application completeness.
- `CLM-KF-01`: retained as future work with status `NOT_EVALUATED`.
- No claim outside `20–30 °C`, no general human need for ultra-narrow control, and no causal recommendation efficacy claim is introduced.
