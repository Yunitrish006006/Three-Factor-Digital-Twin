# Executed exploratory evidence

2026-10-06. Preregistration `69eea268569dfb2d84099f1948bb58ca87b0a8ae` was pushed before implementation/evaluation. Calibration and code/config/source snapshots were frozen at 2026-10-06T03:36:09.647348Z. Actual run: 108 episodes, 19,440 evaluation steps, plus 3×120 calibration steps; evaluation wall time 6.0705 s on this host. Config/CSV/source manifests are in artifacts/. No evaluation rerun or outcome-driven tuning.

## Results and decisions

Common open-loop holdout source MAE nominal/calibrated/sparse: 0.9609917/0.6580405/0.3352190°C. Sparse calibration correction improves 49.0580%, 6/6 designated rig-seed pairs. H-ENC-31 supported within the exploratory assumed-model criterion.

Closed-loop fixed/PI/PID/H1/H6/H6-no-correction tracking MAE: 1.5458075/1.2218796/1.2220839/1.3969206/1.2707565/1.3643980°C. H6 improves 9.0316% over H1; mean sampled overtemperature 103.3333 vs 120 s/episode; fan proxy .0747108 vs .0759570 Wh. H-ENC-32 supported within this design. H6 does not outperform PI; average PI tracking MAE is lower. Retain this adverse comparison.

All closed-loop commands satisfy shared limits; all 3 calibration fits converge (nfev 6/7/7). Capacity/other coefficients were known; local Jacobian condition is not a global identifiability proof. `max_nfev` excludes additional numerical-Jacobian evaluations, so it is not total CPU/call cost. Largest source temperature across all episodes is 32.072°C; out-of-domain counts retained. No physical thermal efficacy, hardware safety, population inference or full three-factor transfer claim.

## Actual verification

- `verify_sparse_enclosure.py`: all 108 CSVs / 19,440 rows, metrics, macro aggregates, decisions, design completeness, calibration budgets and frozen hashes PASS.
- `audit_sparse_enclosure.py`: replayed all 108 episodes using only declared plate/air/fan/inlet/power; estimates, predictions and commands match. No source truth input.
- 7 focused physics/observer/control tests PASS; 3 evidence tests include rejection of changed metrics, decision and calibration parameters.
- Full `.venv-mpc/bin/python -m unittest discover -s tests`: 314 tests / 29.578 s, OK. E15-looking logs are mock subprocess tests in temporary fixtures, not execution of the consumed E15 study.
- Existing v1/v2 evidence verifiers PASS; E15 not rerun.
- `validate_research_openspec.py`: 14 specs, 130 requirements, 251 scenarios, 34 active changes PASS.
- `verify_thesis_results.py`: 110 PASS, 0 FAIL, 0 MISSING.
- Existing thesis DOCX/PDF and presentation builders, plus IEEE tectonic build, succeeded. Designated DOCX/PDF copies match byte-for-byte. Final synchronization manifest is recorded separately.
- Offline HTML observed in Browser at widths 1440/820/390: source/model/results/LQR layouts, anchor navigation, details expansion and Q/R keyboard interaction checked. Mobile body overflow corrected; final 390 and820 widths have scrollWidth=clientWidth. Console error/warning list empty; no external runtime assets. Local source/evidence links checked from filesystem.
- Thesis PDF page89 and IEEE PDF pages7–8 rendered and visually inspected. Kalman source printed pages112–113 visually checked; reading does not claim all proofs rederived.
- `verify_sparse_enclosure_sync.py`: 18 synchronization checks PASS; DOCX/PDF/PPTX designated copies byte-equal, supplement text/slide notes match the evidence-derived summary, exactly one supplement slide per deck with shapes inside bounds. Hashes and counts recorded in `artifacts/artifact_sync_verification.json`. These structural checks do not replace Office rendering QA.

## GitHub checkpoints

Preregistration `69eea268569dfb2d84099f1948bb58ca87b0a8ae` and executed evidence/briefing checkpoint `f7fe825` were pushed to origin/main and remotely verified. The final synchronization checkpoint includes the already-verified 10/5 v1/v2 dependencies required by the coupled thesis builders; it preserves those prior studies and does not rerun them. Final commit identity is available in Git history rather than a self-referential file hash.

## Limits and remaining gates

LQZ→LQR clarification recorded in deviations.md after freeze; no study setting changed. Kalman1960 introduction and roughly five-minute script prepared; oral presentation NOT_EVALUATED.

Complete Office rendering QA remains pending: packaged render_docx.py fails before rendering because pdf2image is unavailable in the experiment runtime; the managed workspace dependency loader is not exposed. No substitute desktop Office rendering is claimed. PDF inspection does not establish DOCX/PPTX layout. IEEE research manuscript is now 8 pages; compression to the submission target 6–7 pages is separate unfinished editorial work, not claimed publication-ready. No HTML print/PDF export validation is claimed.

Physical rig, NTC accuracy, RPM/flow calibration, measured power, varying heat capacities/contact interfaces, sensor failures and out-of-family dynamics remain required future work. This change remains active and is not archived while full Office QA is pending.
