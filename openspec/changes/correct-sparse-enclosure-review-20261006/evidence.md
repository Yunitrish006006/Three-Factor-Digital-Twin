# Corrective evidence (2026-10-06)

## Execution and evidence class

The research-first correction protocol was committed/pushed before implementation (`3947780`). Reference original evidence is commit `ebb40f96731f8956880b8e1ad2921ded8ac8a4ea`. This is corrective regression and retrospective assumed-network capacity analysis. No original study, criterion, frozen source or holdout is overwritten; E15 was not rerun. Unit-test E15 stdout comes from temporary/mock guard fixtures, not the consumed real confirmation.

| ID | Executed check | Result |
| --- | --- | --- |
| E-ENC-41 | v2 required raw plate/air warnings, six control methods, sensor/estimated-source crossing and malformed input tests | PASS; raw input cannot be silently replaced by posterior plate/air |
| E-ENC-41 | `replay_sparse_enclosure_v2.py` under archived actions | 72 episodes / 12,960 steps; zero command/warning/prediction differences; input-only opened-data regression |
| E-ENC-42 | `verify_sparse_enclosure_integrity.py` | PASS 108 episodes / 19,440 steps; original score checks plus timestamp, continuity, exogenous/noise and independent thermal/fan dynamics |
| E-ENC-42 | high-accuracy independent ODE versus original RK4 | max source difference 0.000573904475°C, observed temperature difference 0.000512878256°C, fan 2.22e-16; source/observation tolerances 0.01°C preregistered |
| E-ENC-42 | frozen reference manifest | 115 original artifact files compared with original Git bytes; original frozen source hashes covered by original verifier |
| E-ENC-42 | mutation-negative cases | reordered truth with recomputed legacy metrics rejected; coordinated truth shift, timestamps, power/inlet/noise/fan tampering and missing CSV rejected |
| E-ENC-43 | explicit observed QA | HTML three widths and Q/R interaction; Chinese PDF file pages 89/90, IEEE file page 7 only; artifact and evidence SHA256 bound to recorded observations |
| E-ENC-43 | actual isolated `verify_sync` broken-HTML probe | baseline PASS; changed HTML still passes 18 content checks but delivery NOT_ACCEPTED and observed QA STALE; see `artifacts/sync_negative_probe.json` |
| E-ENC-43 | missing/stale/malformed/incomplete QA tests | PASS; no automatic refresh of observation date/hash; Browser Z timestamps also accepted on Python 3.9 |
| E-ENC-44 | capacity diagnostic | contact-poor 22°C / 3.35W / full fan equilibrium 32.399861674°C; H6 holdout held-input equilibria above 30°C 150/360 versus actual sampled overtemperature 124 steps |

## Native checks and synchronized artifacts

- `.venv-mpc/bin/python -m unittest discover -s tests -p test_sparse_enclosure_corrections.py -v`: **18 passed**, 3.271 s.
- `.venv-mpc/bin/python -m unittest discover -s tests`: **332 passed**, 32.385 s.
- `.venv-mpc/bin/python scripts/validate_research_openspec.py`: PASS, 14 spec files / 130 requirements / 251 scenarios / 35 active changes.
- `.venv/bin/python scripts/verify_thesis_results.py`: 110 PASS / 0 FAIL / 0 MISSING.
- `.venv/bin/python scripts/verify_sparse_enclosure_sync.py`: 18 content checks PASS; current HTML delivery PASS; complete Office QA NOT_EVALUATED.
- `git diff --check`: PASS.

Rebuilt via existing `build_thesis_docx.py`, `build_thesis_pptx.py`, `build_thesis_pdf.py`, IEEE `tectonic --keep-logs --keep-intermediates paper.tex`, and `build_sparse_enclosure_report.py`. Chinese Markdown / DOCX / PDF, IEEE source / PDF, existing slide sources / PPTX / notes and output copies preserve the same corrections and capacity boundary. PDF/font warnings and IEEE underfull/rerun warnings did not prevent builds. No bibliography entries were changed because no new literature claims were introduced.

Current content checks, output hashes, page/slide counts and actual observation scopes are in `artifacts/artifact_sync_verification.json`. QA evidence screenshots and selected rendered pages are stored with `visual_qa_observations.json`; the synchronization checker only reads that store. Rebuilding/changing observed artifacts requires new actual inspection, not an updated hash on an old PASS.

## Independent re-review

A separate `correction_rereviewer` role completed actual read-only adversarial checks of implementation checkpoint `0ba6d194410b55533ef94fcd34de1a37e78f0f8e`. It confirmed R1/R2/R3 resolved with no newly confirmed P1/P2 in the corrective scope. It independently ran 18 focused tests, raw-threshold boundary probes (two channels × six methods), timestamp/coordinated-truth/fan mutations, actual broken/missing-HTML-QA probes, 115 original Git-byte comparisons, replay and capacity recalculation. It did not rerun the full suite or perform fresh Browser/PDF observation. Full findings and retained limits are in `docs/reviews/independent_research_rereview_2026-10-06_zh.md`.

The implementation checkpoint was pushed to origin/main; the following documentation checkpoint preserves the independent review and completion status. Git remote verification is performed after publishing that checkpoint; no CI or physical acceptance is inferred from successful push.

## Remaining scope

Complete DOCX/PPTX Office visual rendering, HTML print, IEEE 6–7-page target (currently 8), real enclosure identification/actuation, complete three-factor transfer and new closed-loop confirmation are not completed by these corrections. PDF visual acceptance covers only the recorded changed pages. Steady capacity is not finite-horizon infeasibility; archived input-only replay is not unseen/controller efficacy confirmation. OpenSpec remains active with these boundaries explicit.
