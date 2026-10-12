# E-ENC-71 actual evidence and HTML delivery

The research-first proposal/protocol was committed and pushed as `dafc9f5` before implementation. Source/configuration/calibration snapshots were frozen before opening evaluation. The exclusive execution receipt and result timestamps are retained; the study was executed once. This is exploratory assumed-model temperature evidence following earlier opened negative findings, not a confirmatory physical study.

## What was implemented

`digital_twin/enclosure/calibrated_session.py` adds energy-conserving direct source–air heat exchange, separately fitted thermal capacities, the corresponding local observer transition and otherwise unchanged PI/six-step ranking gains/costs/limits. Earlier model/controller/study files were left frozen. The new offline CSV interface accepts only declared observations; the independent source-reference scorer remains separate. Its hardware preparation instructions state the equilibrium/known-coefficient assumptions and candidate status.

S and F were each fitted once per rig: first120 chronological calibration rows for fitting, last60 for model selection only, no refit. All12 optimizers succeeded. F was selected on path_variant, path_capacity and convection_mismatch; the other three rigs retained S. Full fitting costs: **993 residual calls / 7.238 seconds** on this host, with each optimizer bounded by max_nfev40. `nfev` excludes some numerical-Jacobian calls; actual calls are counted separately. Local Jacobian conditions and bound hits are diagnostics, not identifiability proofs.

## Results and decisions

96 episodes / 11,520 evaluation samples, plus1,080 separate commissioning samples, were produced with independent `solve_ivp` truth and RK4 model integration. No hardware or source-reference inputs were supplied to calibration/selection/control.

| New holdout metric | S | Selected model | Prespecified decision |
|---|---:|---:|---|
| Sparse-corrected hidden-source MAE °C | 1.0764 | 1.3468 | H-ENC-71 not_supported: error increases25.12%; only2/6 pair wins |
| Six-step tracking MAE °C | 1.4661 | 1.5093 | H-ENC-72 not_supported: error increases2.95% |
| Six-step sampled overtemperature s/episode | 20.00 | 20.00 | Does not establish temperature safety |
| Six-step assumed fan energy proxy Wh/episode | 0.0793 | 0.0925 | Proxy is not measured energy |
| PI tracking MAE °C | 1.4906 | 1.5699 | Same-gain model comparison only |

Per-rig sparse-corrected source MAE: contact_variant1.1205→1.1205 (S retained); path_capacity0.2711→0.2045; convection_mismatch1.8376→2.7155. Both path_capacity pairs improve; both convection_mismatch pairs worsen. F's source-capacity scale reaches the lower bound and air-capacity scale the upper bound under convection mismatch. Improved visible calibration fit therefore did not imply improved hidden-source reconstruction. F remains an exploratory candidate, not an adopted superior model.

Maximum source endpoint across all new episodes:31.6886°C. Closed-loop PWM/slew violations:0. All failures/adverse results are retained. This new study isolates structure under PI and six-step ranking; prior LQR/MPC/all-controller comparisons remain unchanged and are presented separately. No new full three-factor or arbitrary-equation-family claim is made.

## Verification actually performed

- `verify_enclosure_structure_study.py`: PASS for all96 episodes/11,520 rows, all1,080 commissioning rows, selection rules, complete Cartesian design, independently recomputed metrics, noise/time/truth continuity and independent thermal dynamics. Maximum independent state difference6.184e-08. Input-only replay passes. Timestamp, coordinated truth, fan endpoint, raw observation, metrics and selection corruption are all rejected.
- 514 historical artifact files remain byte-identical. Consumed E15 and earlier enclosure study runners were not rerun. Full unit tests use mocks for the E15 executor; their diagnostic stdout is not a new E15 execution.
- Full `.venv-mpc/bin/python -m unittest discover -s tests`: **353 tests pass /32.504s**, including9 meaningful new tests for internal energy balance, independent-capacity mapping, source-blind chronological fitting, selection/failure gates, fan solution, covariance coupling and raw-warning/cadence behavior.
- `verify_thesis_results.py`: **110 PASS /0 FAIL /0 MISSING**.
- `validate_research_openspec.py`: **PASS,14 specs /130 requirements /251 scenarios /38 active changes**.
- Native Chinese thesis/IEEE/presentation builders completed. Both experiment stages' metrics, decisions and scope appear in sources/outlines/notes and rebuilt outputs; copied outputs are byte-equal. Existing architecture figure semantics did not change because the new model remains a separate exploratory candidate.
- `verify_enclosure_structure_delivery.py`: **32 checks pass** for coupled content/copies and current hash-bound HTML/PDF observation scope.
- `git diff --check`: PASS before committing.

## Professor-facing delivery and actual visual scope

The same `docs/reports/professor_research_2026-10-12_zh.html` now contains the second-stage model selection, both earlier adverse decisions, source-checked LQR/Kalman material, updated first-person fifteen-minute talk and experimental preparation. It is self-contained for offline rendering; external sources are hyperlinks only.

An isolated headless Chrome/Playwright run (not the in-app Browser) checked1440/820/390px layouts with no body overflow, all11 anchors,38 links, keyboard details/Q/R interactions, no external runtime asset requests and no console errors. The primary agent actually inspected desktop/tablet/mobile structure screenshots, existing results and LQR screenshots, and all10 A4 print pages. The resulting PDF is a print derivative of HTML, not an Office artifact. Exact HTML/PDF and screenshot hashes are recorded in `artifacts/visual_qa_observations.json`; automatic checks alone did not author visual acceptance.

For coupled native PDFs, actual file pages90–92 of the Chinese thesis and7–8 of IEEE were inspected. This is a limited changed/adjacent-page check, not complete thesis or Office visual acceptance; thesis page92 contains an adjacent continuation line. The HTML report is the user-facing deliverable. Per the user's clarification, Office installation/mount/render is outside this HTML workstream and is not a completion gate.

Physical identification, NTC accuracy, hardware actuation, real metal/duct efficacy and complete enclosure three-factor transfer remain NOT_EVALUATED because the user confirmed no equipment/data. Actual oral presentation remains NOT_RECORDED. The authorized software/experimental-preparation/HTML stage is complete; no unobserved physical or presentation outcome is claimed.

## Reproduction without consuming new research

Run the read-only study verifier and content/QA verifier on stored data. Do not rerun the study runner: the exclusive receipt intentionally refuses another execution. Use the same native builders if reporting sources change, then perform fresh HTML/PDF QA and record new hashes. `scripts/qa_enclosure_session_html.mjs` now targets this stage's QA folder, preserving earlier frozen QA files; it requires a Playwright installation path via ENCLOSURE_QA_DEPENDENCIES and a compatible Chrome executable.

The validated implementation/report checkpoint `76d8a52` was pushed to origin/main. A fresh `git fetch origin` followed by exact local/remote SHA comparison confirmed synchronization. The post-verification receipt is stored in `artifacts/completion_receipt.json`; all applicable software/preparation/HTML tasks are checked. Hardware/three-factor/oral boundaries remain explicit.
