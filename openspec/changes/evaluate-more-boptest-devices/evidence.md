# MDV-001 Post-run evidence — 2026-09-08

## Decision
All three additional FMUs completed the predeclared workflow. Five of six device/budget banks fit; apartment 6h rejected all ten training candidates. Zero of six registered device/budget control gates passed (five evaluated budgets plus one incomplete/rejected budget). Proposed compensation won 0/10 completed paired MAE comparisons. The frozen algorithm's cross-device control-improvement hypothesis is not supported in this round. Execution/verification success is not hypothesis success.

## Registered device coverage
- Heat-pump floor heating: bestest_hydronic_heat_pump; compressor speed; operative temperature.
- Apartment floor heating: twozone_apartment_hydronic; shared supply temperature, day valve fixed open; day-zone air target only, night loop native with declared setpoint.
- Commercial radiator: singlezone_commercial_hydronic; radiator valve, fixed pump/supply; zone air temperature; AHU remains native.

Both prior development plants (air and hydronic) retain their previous artifacts. There are now five examined FMUs, not five real devices or five independent physics families. The three new FMUs did not contribute tuning of the frozen controller; only documented native interface and installation settings were chosen from metadata before simulation. All installation overrides are declared in scripts/boptest_more_devices.json and apply during warmup as specified. They are applicability conditions, not evidence of setup-free transfer.

## Actual workload and cost
43 completed episodes: three 6h calibration episodes, twenty 2h tuning episodes, twenty 24h evaluation episodes. Eight planned apartment-6h control episodes were skipped following identification rejection. No runtime failures, no source repair, no retry or replacement. Total simulated exposure: 1032h warmup + 18h calibration + 40h tuning + 480h evaluation = 1570h. Calibration prefixes share the same six-hour trace per plant. Successful per-method active adaptation budget is 2h/6h plus four tuning hours = 6h/10h; failed identification does not incur the omitted trials. All costs are reported separately from the data label.

66 offline fits including refits, with recorded fitting wall time summed to 0.127936s. Episode execution wall times sum to 1779.602s across concurrently running plant processes; this is not total elapsed research time or human labor. No human tuning cost or time-to-equal-quality comparison is established.

## Complete paired MAE (°C)
| FMU | ID h | Day | auto-PI | proposed | Result |
|---|---:|---:|---:|---:|---|
| heat_pump | 2 | 20 | 0.03323068 | 0.05152881 | loss |
| heat_pump | 2 | 50 | 0.21117031 | 0.25779734 | loss |
| heat_pump | 6 | 20 | 0.03382159 | 0.09615869 | loss |
| heat_pump | 6 | 50 | 0.20235071 | 0.37600036 | loss |
| apartment | 2 | 20 | 1.21508798 | 1.62143751 | loss |
| apartment | 2 | 50 | 1.07355040 | 1.40949414 | loss |
| apartment | 6 | 20 | — | — | identification rejected |
| apartment | 6 | 50 | — | — | identification rejected |
| commercial | 2 | 20 | 0.00373212 | 0.00968012 | loss |
| commercial | 2 | 50 | 0.01435968 | 0.02197070 | loss |
| commercial | 6 | 20 | 0.00347032 | 0.00958836 | loss |
| commercial | 6 | 50 | 0.01405867 | 0.02174618 | loss |

## Interpretation and adverse cases
Heat-pump proposed MAE and requested command TV exceed auto-PI in all four pairs. Apartment 2h proposed loses on both dates; 6h has no admissible training candidate, so no refit or controls are fabricated. Commercial proposed loses in all four pairs despite small absolute errors. Complete RMSE, maximum errors, saturation, domain violations, energy channels, and startup/post-30-minute errors remain in the JSONs and traces.

Apartment calibration spans roughly 23.6–23.8°C; its day-valve-open installation and native supply warmup start above target. Both compared methods share the same initial conditions per date, so within-device comparison is retained. This does not isolate the contributions of installation settings, slab storage, native subordinate loops, or heating-only capacity. Selected delays/models are predictive fits, not uniquely verified physical mechanisms. Rejected banks and low closed-loop gains warrant separately preregistered development, not post-result manual exceptions. Any later controller changes based on these outcomes consume these FMUs as development evidence.

## Verification
- 253 unit tests passed in 313.723s: outputs/boptest_more_devices_tests.log.
- outputs/boptest-venv/bin/python scripts/verify_boptest_more_devices.py: PASS. 43 full traces hashed, chronological continuity and native readback mapping checked, calibration excitation reproduced, every stored control step replayed, metrics recalculated, candidate selection/refits checked, bounded q selection verified against pre-evaluation snapshots, all frozen sources match. See artifacts/verification.json.
- Three native FMU interface schemas were checked against modelDescription.xml before simulation (causality, types, units, bounds).
- Research OpenSpec validation: PASS (14 spec files, 130 requirements, 251 scenarios, 25 active changes).
- Offline report source: scripts/build_boptest_more_devices_report.py; generated HTML, PNG and SHA-256 manifest under docs/reports/boptest_more_devices_2026-09-08_zh.*.

## Provenance and scope
Official BOPTEST v0.9.0 local wrapped FMUs and documentation hashes are frozen before runs; upstream model/weather provenance and licenses are retained in the vendor tree and prior research record. FMPy 0.3.22 with local libgfortran4 uses a custom direct-FMU runner; no official REST/KPI equivalence is asserted. No external data download or real-world intervention occurred. No neural-network benefit, humidity/EUV result, material quality measurement, or industrial validation is claimed. Deterministic days 20/50 are not independent random repetitions or statistical significance evidence. Air and operative temperatures are not pooled.

## Synchronization decision
This standalone exploratory extension is not adopted into the main thesis. Chinese/English adopted thesis methods, claims and generated documents remain unchanged; professor reporting is offline HTML according to the explicit user preference. Adoption would require synchronized Chinese/English/presentation sources and applicable output builds. Do not archive as an adopted or positive confirmation result.
