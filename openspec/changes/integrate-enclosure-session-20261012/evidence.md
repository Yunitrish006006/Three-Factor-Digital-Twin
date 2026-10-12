# Executed enclosure-session integration evidence

2026-10-12. User confirmed no hardware or measured data; complete software and experimental preparation first. Preregistration checkpoint `2a12362` was pushed before implementation/evaluation. Actual software/evaluation was performed by the primary agent; no new independent agent review is claimed.

## Actual execution

- Canonical package exposes the lazy-loaded `digital_twin.enclosure.EnclosureSession`, `Observation` and `fit_observations` interfaces. Room humidity/light/spatial estimation remains a separate capability.
- `run_enclosure_session.py` reads only declared observation channels and emits offline command proposals; the separate `score_enclosure_reference.py` joins current/next reference times for scoring. Neither script sends hardware commands.
- The new study executed exactly once: **88 episodes / 10,560 evaluation samples**, plus 4x180 commissioning samples. The evaluation ran in 5.967 seconds on this host. The receipt guards one attempt; terminal outcome is `result.json`, not the receipt's initial `started` marker.
- All four bounded fits succeeded: nfev 7/9/9/13, actual residual calls 35/45/45/65, wall times 0.364/0.478/0.547/0.675 seconds. The extra-path contact estimate hits its 1.5 W/K upper bound; solver success is not physical correctness or global identifiability.
- Freeze precedes evaluation and records source/config/calibration hashes, environment and pre-evaluation source snapshots. No gain adjustment or outcome-driven evaluation rerun occurred.

## Results and decisions

Macro open-loop holdout source MAE nominal/calibrated/corrected: **1.0086 / 0.4681 / 0.3689 C**. Correction improves mean by **21.1905%**, but only **2/4** rig-seed pairs improve; H-ENC-51 is **not_supported**, failing the predeclared 3/4 coverage gate. Contact-capacity per-rig means worsen **0.2123 to 0.3326 C**; the extra-path means improve **0.7238 to 0.4051 C**.

Fixed/PI/PID/LQR/linear-MPC/H1/H6/H6-without-correction tracking MAE: **1.7310 / 1.3471 / 1.3472 / 1.4872 / 1.3695 / 1.3764 / 1.3755 / 1.3943 C**. H6 improves only **0.0686%** over H1; H-ENC-52 is **not_supported**, failing the 5% tracking gate. H6 does not outperform PI. H6 sampled overtemperature averages **3.75 seconds/episode**; all 64 closed-loop episodes have zero command violations, optimizer fallbacks total zero. Across all episodes, actual maximum source is **30.6744 C**. All adverse and out-of-domain samples remain in evidence.

Timing and proxy energy are per-method/per-run in result JSON; they are host measurements and assumed fan proxy, not embedded timing, measured electricity or hardware efficacy. LQR uses sparse estimated states and bounded commands; linear MPC is six-step affine optimization, not nonlinear MPC. Calibration-assisted transfer and one extra-path variant do not establish zero-shot or arbitrary-family generality.

## Actual verification and review

- `verify_enclosure_session_study.py`: **PASS 88 episodes / 10,560 rows**. Independently recomputes CSV metrics, macro aggregates and decisions, checks split completeness, current/next truth/time continuity, workload/noise provenance, raw warning contract and input-only session replay. Independent temperature integration with analytic fan differs at most **6.473e-8** in state values, below 1e-5 tolerance.
- Five actual opened-trace mutation probes reject timestamp shift, coordinated source-truth shift, fan endpoint replacement, raw observation corruption and wrong metrics. These are regression probes, not new research episodes.
- All **372 historical research artifact files** in the pre-evaluation manifest remain byte-identical. Original frozen v1/v2/pilot sources and evidence were not modified. E15 was not rerun. E15-looking output from the full unit suite is from existing mock guard fixtures, not real confirmation execution.
- Full `.venv-mpc/bin/python -m unittest discover -s tests`: **344 tests passed / 32.728 seconds**. New coverage includes source-reference invariance, raw warning at threshold for all methods, stale-input atomicity, bounds/slew, equilibrium/differential consistency, optimizer failure fallback and reference scorer timestamp semantics.
- Actual CLI smoke processes **120 synthetic observation samples** and separately scores **120 current / 120 next-time references** with zero missing next references. Inputs/outputs are in `artifacts/cli_smoke/`, explicitly synthetic; they are not NTC or physical evidence.
- `verify_thesis_results.py`: **110 PASS / 0 FAIL / 0 MISSING**.
- `validate_research_openspec.py`: **PASS 14 specs / 130 requirements / 251 scenarios / 36 active changes**.

Primary-agent source/claim review checked source-truth isolation, failure handling, actual computational budget, calibration-bound saturation, the failed coverage/benefit criteria and cross-artifact wording. No independent-agent acceptance is implied.

## Synchronized artifacts and observed QA

Rebuilt Chinese thesis Markdown/DOCX/PDF, IEEE source/PDF and existing presentation sources/outlines/PPTX through native builders. Presentation changes synchronize historical outputs; the new professor presentation is offline HTML as requested. The IEEE bibliography was preserved because existing source entries cover these methods. Changed PDF scopes are Chinese file pages **90-91**, IEEE file pages **7-8**; IEEE remains **8 pages**, and submission page reduction is not completed or claimed.

Professor HTML includes device paths, method flow, fresh results, negative comparisons, LQR/Kalman 1960 reading and limits, a fifteen-minute talk, hardware procedure and blank CSV templates. Actual browser checks at **1440/820/390 px** found no body overflow; all ten navigation anchors, local links, keyboard details and Q/R interaction passed; console errors and external runtime asset requests were zero. The mobile chart is locally scrollable for readable labels. The full eight-page report print PDF was rendered with all details expanded and visually inspected. Actual screenshots and browser checks are in `artifacts/qa/`; the final hash-bound observations are recorded separately.

The Browser plugin's required JavaScript execution tool was not available in this session after capability discovery. Browser QA therefore used a standalone Playwright 1.58.2 process with isolated headless local Chrome, not a claimed in-app Browser execution. A reusable script is `scripts/qa_enclosure_session_html.mjs`; supply `ENCLOSURE_QA_DEPENDENCIES` pointing to a Playwright package environment and optionally `ENCLOSURE_CHROME_PATH`. Initial npm network resolution failed in the sandbox; the approved retried download succeeded. Native document rebuilds also required approved retry after a sandbox path-filter initialization failure.

## Remaining boundaries

Software and experimental preparation are complete after final delivery checks. Physical identification/actuation, sensor precision, measured energy and material/duct efficacy remain **NOT_EVALUATED**, consistent with the user's equipment clarification. Full enclosure humidity/light/spatial transfer remains uncompleted; actual professor oral presentation is **NOT_RECORDED**.

Full DOCX/PPTX Office visual rendering remains unavailable: the prescribed document renderer failed on missing `pdf2image`, and neither a workspace dependency loader nor bundled LibreOffice is exposed. Native PDFs and structural OOXML checks do not replace Office rendering. No Office visual acceptance is claimed. The research change stays active with these deferred scopes explicit.

Final content/copy checks and exact observed artifact hashes are in `artifacts/delivery_verification.json`. A validated implementation checkpoint is committed/pushed and remotely verified after final checks; its identity is available in Git history without embedding a self-referential commit hash here.
