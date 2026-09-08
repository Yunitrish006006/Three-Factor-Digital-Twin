# PDM-001 Post-run evidence — 2026-09-08

## Decision
Identification recovered; control benefit is mixed. This exploratory round is complete, but cross-scenario low-cost superiority is not confirmed and thesis adoption remains deferred. Both air and hydronic are development plants after this work. Days 20/50 are new within-plant checks, not untouched-plant confirmation.

## Actual execution
Both result JSONs report COMPLETED, with no failures or skips. Reused original 6h calibration traces and their 2h prefixes; zero new calibration excitation. Each plant executed eight 2h tuning episodes and eight 24h evaluation episodes, for 32 new FMU episodes in total. Every episode had 24h warmup: aggregate 768h warmup + 32h tuning + 384h evaluation = 1184 simulated hours. Per-method active adaptation is 2h/6h identification + four tuning hours = 6h/10h. Offline fitting and episode execution durations are recorded in the result files and report manifest; these are not researcher labor measurements.

Same ten-candidate ARX bank was applied to both plants, with no pole repair or device-specific controller branch. All four banks selected admissible full-prefix refits. Air 2h selected order 1/delay 0; air 6h order 2/delay 0; hydronic 2h order 1/delay 3 minutes; hydronic 6h order 2/delay 0. These selected predictive structures are not uniquely identified physical time constants or delays. Calibration rollout scores are model-selection evidence, not independent control scores. All bounded q selections were 0.5, made before evaluation.

## Full paired MAE evidence (°C)
| Plant | ID h | Day | auto-PI | proposed |
|---|---:|---:|---:|---:|
| air | 2 | 20 | 0.02960114 | 0.00798672 |
| air | 2 | 50 | 0.04838227 | 0.02974873 |
| air | 6 | 20 | 0.02967829 | 0.00797937 |
| air | 6 | 50 | 0.04844941 | 0.02973893 |
| hydronic | 2 | 20 | 0.19819610 | 0.05459612 |
| hydronic | 2 | 50 | 0.59572354 | 0.41583243 |
| hydronic | 6 | 20 | 0.01091488 | 0.04966064 |
| hydronic | 6 | 50 | 0.32884147 | 0.34379066 |

Predeclared nonregression/mean-improvement gate passes air 2h/6h and hydronic 2h, fails hydronic 6h. Hydronic 6h proposed MAE exceeds auto-PI by 0.038746°C on day 20 and 0.014949°C on day 50. On day 20 this exceeds the +0.02°C margin. Its maximum errors are 0.102757°C and 1.521235°C versus baseline 0.048935°C and 1.533756°C. More identification data improved proposed absolute performance relative to 2h, but improved auto-PI more. Additional compensation is not consistently beneficial; no post-evaluation tuning was performed.

## Verification and reproduction
- `python3 -m unittest discover -s tests`: 250 tests passed in 282.204s. Log: `outputs/boptest_delayed_dynamics_tests.log`.
- `python3 scripts/verify_boptest_delayed_dynamics.py`: PASS; all 32 traces checked, source hashes match, candidate selection/refits and control metrics verified. See `artifacts/verification.json`.
- Frozen sources, original results/calibration hashes and FMUs: `artifacts/freeze.json`. Prior rounds remain intact.
- Report source: `scripts/build_boptest_delayed_dynamics_report.py`; generated offline HTML, PNG and SHA-256 manifest: `docs/reports/boptest_delayed_dynamics_2026-09-08_zh.*`.
- Runtime: official BOPTEST v0.9.0 FMUs, local FMPy 0.3.22 and libgfortran4, existing upstream licensing/provenance retained. Custom direct-FMU runner, not a demonstrated official REST/KPI equivalent.

## Scope and synchronization decision
Air measures zone air temperature; hydronic measures operative temperature. No pooled cross-device MAE, independent repeats, industrial/EUV/humidity validation, neural-network benefit, or real hardware results are claimed. No manual tuning labor comparison establishes total adjustment-cost savings yet. A common bounded compensation-selection rule is a possible next separately preregistered development study; an untouched plant is still required after freezing that design.

This is a separate, unadopted research extension; the adopted Chinese/English thesis and historical presentation claims remain unchanged. The professor briefing is offline HTML as explicitly requested. Thesis synchronization and generated thesis builds become required upon adoption, which has not occurred. Do not archive this change as adopted evidence.
