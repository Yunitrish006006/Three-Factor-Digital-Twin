# BOPTEST rapid PI pilot evidence — 2026-09-08

Status: COMPLETED DEVELOPMENT PILOT; independent confirmation and thesis adoption NOT_EVALUATED.

## Actual execution and deviations

Official bestest_air FMU v0.9.0 was executed locally through FMPy, using the pinned commit/FMU hashes in result.json. Public service probes failed (HTTPS SSL error; HTTP 404). Full official service/KPI equivalence was not established. No humidity or semiconductor plant was simulated.

Attempt 01 failed before simulation due to missing libgfortran.so.4. The official Ubuntu compatibility package was extracted locally (runtime_provenance.json). Attempt 02 completed the calibration trace but failed serializing an infinite matrix condition number from zero nighttime solar excitation. The diagnostic-only correction stores null, rank and solar_identifiable; coefficients and protocol were unchanged. Both attempts remain in artifacts; attempt02_identification.csv remains in outputs. Final calibration matches its retained predecessor.

The final v1 run contains 1 identification episode, 9 grid search episodes and 14 evaluation episodes. V2 adds 2 evaluation episodes. Every episode uses a fresh FMU and 24 h common embedded warmup. Warmup is excluded from MAE and from active identification exposure, explicitly reported. V1 evaluation uses day 3 and 180. V2 reuses these dates after v1 inspection and is adaptive development, not independent testing.

## Results

| Method | Active calibration/trial h | Day 3 MAE C | Day 180 MAE C |
|---|---:|---:|---:|
| fixed_pi | 0 | 0.299946 | 0.164638 |
| grid_pi | 54 | 0.025244 | 0.033827 |
| auto_2h | 2 | 0.130993 | 0.088296 |
| auto_2h_ff | 2 | 0.129124 | 0.191049 |
| auto_6h | 6 | 0.147812 | 0.096489 |
| auto_6h_ff | 6 | 0.110313 | 0.166064 |
| auto_2h_v2 | 2 | 0.039226 | 0.041212 |
| embedded | 0 | 0.058706 | 0.898779 |

Grid selected Kp=6, Ti=300 s by calibration score. V2 uses the 2 h fitted tau=250.5408 s and lambda=max(3*60,tau/2)=180 s, giving Kp=3.227185 and Ti=250.5408 s. No additional identification data, no old spatial-network weights, and no neural model were used.

V2 is within +/-0.5 C for 99.2361% / 100% of winter/summer evaluation minutes; maximum error 1.4962 / 0.4359 C. Initial transient is included. Thus this does not meet a presumed industrial precision tolerance; no such tolerance was supplied or validated.

V1 plain auto PI passes its exploratory gate against fixed PI on both dates; both static environmental-feedforward variants fail the two-date gate. V2 passes the newly declared practical margin against grid (+0.05 C MAE, +0.5 C max error) on both dates. That margin was declared after inspecting v1 and is NOT a pre-registered thesis success threshold.

## Boundaries, nulls and cost accounting

- RQ-BPI-01: supported as local simulated feasibility for a newly fitted dynamical model; not validation of the original h=0 estimator as a controller.
- RQ-BPI-02: partially supported. Short identification beats the fixed preset but the grid is still better in MAE. More calibration data did not monotonically improve control.
- RQ-BPI-03: supported within reused development cases only. The response-time adjustment improves v1; independent generalization remains unknown.
- C-BPI-01: only feasibility is supported. Lower human tuning time, novelty, strong conventional auto-tuning comparisons, physical hardware, humidity, EUV and product quality remain NOT_EVALUATED.
- Nighttime solar was identically zero; design rank=3 of 4. Outdoor temperature during first 2 h spans only -7.173 to -4.4 C. Static feedforward learned there worsens summer outcomes. Full-rank data alone would still not guarantee transfer outside calibration conditions.
- 2 h budget means the first 120 transitions of a collected 360-transition calibration trace. It does not mean the entire research effort lasted 2 h. Grid active exposure is 9*6=54 h. All initialization, simulation evaluation, failed attempts and developer iteration are extra costs. No human labor was timed.
- Calibration next-temperature excursions outside 20–30 C: 40/120 for the 2 h prefix, 159/360 for full 6 h. All retained (calibration_domain_audit.json). V2 evaluation has 0/1440 excursions on each date. This does not expand the earlier spatial model operating domain; commissioning disturbance needs a future safe constrained protocol.
- Per-case energy channels remain separately labelled. Fixed fan makes external-controller comparisons comparable but not the embedded variable-fan reference. Cooling saturation in summer can limit further improvement.

## Validation and artifacts

`python3 scripts/verify_boptest_rapid_pi.py` passed: 26 CSV traces / 16 evaluation episodes, every recorded metric recalculated, hash checks, chronology, bounded commands, equal warmup temperature and fixed fan parity. `python3 -m unittest discover -s tests`: 229 tests passed in 253.813 s; subsequent targeted five BOPTEST tests passed after the diagnostic fix. Original suite logs include fixture-generated failure records; the suite itself passed. OpenSpec validator passed.

Report source: scripts/build_boptest_briefing.py. Offline HTML: docs/reports/boptest_rapid_pi_2026-09-08_zh.html. Standalone scientific plot: docs/reports/boptest_rapid_pi_2026-09-08.png. Report manifest contains result/HTML/plot hashes. Static link checks performed; plotted figure visually inspected; browser viewport rendering was not exercised.

## Claim and synchronization decision

This is a separate exploratory extension, not adopted thesis evidence. Main Chinese/English manuscripts, prior E15 evidence and original estimator remain at their prior accepted state. The new professor report clearly records the pilot status. No new PPTX was generated. If this becomes a thesis method or result, the project-wide manuscript/source/document synchronization and independent confirmation must occur under a subsequent research change. This change remains unarchived.
