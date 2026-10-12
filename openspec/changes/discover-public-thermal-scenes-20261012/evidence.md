# Actual public-scene discovery and LQR preparation

Preregistered and pushed as `0f537ae` before external execution checks. This stage answers availability/preparation questions, not controller efficacy, model generality or hardware performance. Prior research outcomes remain unchanged.

## RQ-ENC-SIM-01: source-backed candidate findings

- **SimScale Electronics Box:** official CHT tutorial read2026-10-12. It includes component power, material/contact resistance and a fan curve. The tutorial is steady-state: its solver iterations are not physical time. Official pricing currently documents a free Community plan with limited quantitative simulations; actual account entitlement/quota and specific tutorial execution are not verified. Web reader could not open the linked import/finished project. No login, account creation, upload, payment or cloud solver run was performed. Result: **documented cloud-scene candidate, not executed**.
- **UVA HotSpot:** official source `f18831e48cef5d62580585cca0d7fab6c71bc3cc`, reviewed Makefile/LICENSE/example1 source. `make hotspot` produced a working executable with Apple clang21.0.0 ARM64, default no acceleration. One unchanged-input official example1 block-model command returned exit0; stored thermal trace has100 finite rows/30 columns. Fixed r_convec, detailed package model disabled; no fan control adapter, controller comparison, complete enclosure CFD or project-model transfer. Ambient318.15K/45°C exceeds the project's existing20–30°C validation domain. The one-second trace does not prove adequate warmup. Result: **bundled local model ready within narrow scope**.
- **TCLab:** official source `a975c36d68ccbc3c0f6dade4ae99c0abc3271f81`, version0.4.10dev. pyserial3.5 installed only in temporary dependencies. Official `TCLabModel(synced=False)` produced11 finite readouts for one fixed Q1=40%/Q2=20% sequence, seed612810; both temperature readouts responded. No hardware connection, controller tuning/ranking or project-estimator test. Inputs are heaters, not fans. Result: **offline dynamic interface ready within narrow scope**. Historical2026-09-21 pilot was not rerun.
- **BOPTEST:** official documentation still describes public REST service. GET `https://api.boptest.net/testcases` with valid TLS and20s timeout failed with curl exit6 `Could not resolve host`; same approved-network retry also failed. No instance was created or simulation advanced. This is this environment's DNS outcome, not evidence of permanent global outage. Result: **documented public API, not connected here**.

Machine-readable records: artifacts/readiness.json, hotspot_readiness.json, tclab_readiness.json, readiness_verification.json. HotSpot outputs and scoped unmodified source/license snapshots are retained; exact input hashes and pinned original sources allow reproduction. The old-fork HOWTO search was replaced by the official current wiki/README/run.sh; the official repository does not contain that HOWTO filename. Missing lookup files were not treated as simulator failures.

## RQ-ENC-LQR-01: practical guide

Delivered docs/research/lqr_practical_guide_2026-10-12_zh.md and expanded the same HTML LQR section. Topics: state/input/output/equilibrium, local linearization, continuous versus discrete Riccati/gain, Q/R scales and covariance-name confusion, stabilizability/cost-detectability versus sensor observability, estimated-state limits, saturation/slew/fan delay, disturbance/tracking, numerical residual/eigenvalue checks and fair information parity.

Modern teaching equations are explicitly not original Kalman transcription. Original paper p.104 state-known assumption and p.114 conditional stability theorem were rechecked through official parsed PDF text. Local PDF re-download timed out at25s; web screenshot cache failed, so no fresh visual acceptance of original pages was claimed. Historical10/6 source-checked notes are linked, with their original reading scope retained. Primary MIT, SciPy and python-control documentation supports the teaching material. No new gain/effectiveness results were produced; H-ENC-51/52/71/72 and E15 remain unchanged.

## Claim and scope review

C-ENC-SIM-01: **partially supported for documented public candidates and two local readiness checks**; actual cloud import/run and live BOPTEST operation are not evaluated/successful. No hypothesis of controller improvement is tested. The readiness row counts are output integrity, not new academic performance results. Native Chinese thesis/IEEE/PPTX artifacts are unchanged because the new content is candidate/teaching preparation, with no adopted method or altered scientific result. The user-facing presentation remains HTML; no Office operation occurred.

668 historical artifact files are byte-identical, including previous QA, result files and scientific source snapshots. A consumed study runner/E15 was not executed; full unit-suite E15 stdout is from mocked executor tests, not research execution.

## Actual verification and delivery

- `readiness_verification.json`: PASS for stored finite HotSpot trace shape, TCLab input/readout and no-hardware contract, visible BOPTEST error, SimScale not-run status and all668 historical hashes.
- Full unit suite: **353 tests passed /31.901s**.
- `verify_thesis_results.py`: **110 PASS /0 FAIL /0 MISSING**.
- Research OpenSpec validator: **14 specs /130 requirements /251 scenarios /39 active changes** pass.
- Current delivery verifier: **35 checks pass**, preserving both earlier stages' content/copies while reading current QA and checking new preparation files.
- Headless local Chrome/Playwright fallback:1440/820/390px, no body overflow, all12 anchors/50 links, details/Q/R keyboard interactions, scene-table keyboard horizontal scroll, no runtime external requests or console errors. Initial cramped mobile table was changed to a labeled, keyboard-focusable horizontal-scroll region; final left/right screenshots were actually inspected.
- Primary agent actually inspected final desktop/tablet/mobile public-scene and LQR screenshots and all12 A4 print pages. Current HTML and print PDF observations are exact-hash-bound. Unchanged native-PDF observations were reused only after checking identical artifact/evidence bytes, with their original timestamps/scope preserved.
- Whitespace checks cover authored sources/docs/records; unmodified upstream source snapshots and raw HotSpot tab-separated output retain source bytes rather than being reformatted.

Artifacts are docs/reports/professor_research_2026-10-12_zh.html, its print PDF and updated first-person talk; detailed scene and LQR Markdown notes are linked from the same HTML. No replacement report, deployment, physical actuation or oral-presentation completion is claimed.

Push and fresh remote-SHA verification are recorded after the actual validated checkpoint is synchronized.
