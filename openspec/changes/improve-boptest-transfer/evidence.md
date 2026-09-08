# BOPTEST continued improvement evidence

Status: COMPLETED exploratory round, 2026-09-08. No thesis adoption.

## Actual runs and frozen selection

8 development episodes compared old v2, v3 heat-equivalent handover, v4 handover plus causal disturbance observer, and grid PI with the same handover. v4 was selected only on days3/180 and the selection/source hashes were saved before transfer. Source verification passed before and after transfer. 18 transfer episodes cover four new dates and two same-date noisy repetitions. Noise SD=0.05 C with one deterministic common seed per date. All episodes completed; no simulation failures. No transfer-driven parameter changes occurred.

The FMI adapter initializes a valid supply setpoint before actuator activation. Reproduced v2 metrics on both development dates exactly equal prior result_v2.json, so the lifecycle adjustment did not alter legacy scored behavior. True room temperature is scored; only controller measurement gets noise. Fresh FMU and common24h warmup are preserved.

Protocol clarification: observer starts integral at zero and explicitly outputs the heat-equivalent command at k=0, rather than algebraically matching the subsequent bias for nonzero initial error. This was recorded in design.md before transfer. The retained runner is authoritative for reproduction; no hidden tuning of that initial condition occurred.

## Complete transfer results

|Day|Noise SD C|Controller|MAE C|Max error C|Command total variation C|
|---:|---:|---|---:|---:|---:|
|35|0|v2|0.018539|1.262891|20.644|
|35|0|v4_observer|0.002396|0.154337|11.375|
|35|0|grid_handover|0.006532|0.152630|11.352|
|95|0|v2|0.024646|0.270722|27.454|
|95|0|v4_observer|0.002581|0.164238|25.779|
|95|0|grid_handover|0.014803|0.168479|25.849|
|245|0|v2|0.255715|1.379972|23.678|
|245|0|v4_observer|0.234867|1.372965|23.098|
|245|0|grid_handover|0.246721|1.377259|22.297|
|305|0|v2|0.029174|0.721657|32.491|
|305|0|v4_observer|0.002756|0.158776|27.421|
|305|0|grid_handover|0.015801|0.179847|27.434|
|95|0.05|v2|0.031208|0.299090|369.483|
|95|0.05|v4_observer|0.027984|0.166952|601.850|
|95|0.05|grid_handover|0.032052|0.183777|788.003|
|245|0.05|v2|0.262379|1.380888|255.310|
|245|0.05|v4_observer|0.252739|1.374200|415.011|
|245|0.05|grid_handover|0.259669|1.378567|544.213|

## Decisions and adverse findings

- RQ-BPT-01 supported in bounded development: winter maximum error drops from1.4962 C to0.2354 C with handover alone. This generic improvement also benefits the grid baseline.
- RQ-BPT-02 supported for temperature tracking within these simulations: v4 development MAE0.003238/0.024173 C, compared with v3 0.029375/0.040357 C. No additional excitation data were used; the observer uses past live transitions, not new gain identification or future values.
- RQ-BPT-03 supported only for the frozen same-FMU transfer protocol: all6 cases improve MAE against v2 and against the handover-enabled grid. Protocol improvement/nonregression gate passes. Mean paired MAE gain versus v2 is0.0163896 C. Four clean-date macro MAE v2=0.0820184, v4=0.0606500, grid=0.0709643 C. Two noisy-date macro MAE v2=0.1467937, v4=0.1403617, grid=0.1458603 C. No IID-minute confidence intervals; the six cases are not six independent buildings.
- Day245 remains a difficult retained case: selected clean MAE0.2348667 C / max1.3729648 C. All293 minutes above22.5 C coincide with minimum supply12 C. This is consistent with the fixed-fan/supply-bound capacity bottleneck; not proof that a hardware replacement is required. All measured-limit overlaps are in saturation_diagnostic.json.
- Measurement noise increases action variation. Noisy macro command total variation: v2=312.3965 C, v4=508.4302 C, grid=666.1081 C. New controller is about62.8% more active than old v2, though less than grid. Tracking improvement is therefore not a universal control-cost win. Action variation is not energy or measured wear.
- Remaining failures of scope: no actuator delay, sensor bias/drift, noisy repeats across multiple seeds, new building, cross-region weather model, real hardware, humidity, semiconductor tolerance, product yield, or measured human tuning time. No neural-network efficacy or novelty claim. Prior calibration excursions outside20–30 C remain disclosed; no primary spatial-estimator domain expansion.

## Cost and validation

All automatic methods reuse the first2h of a6h calibration trajectory. Grid previously used9x6h active trials. This round adds26 episodes, each24h warmup+24h scored simulation; these1248 aggregate reset-episode simulation hours are not elapsed human time. The observer also has ongoing per-step computation. Do not describe a2h prefix as the entire research effort.

`python3 -m unittest discover -s tests`:234 tests passed in254.927s. `python3 scripts/verify_boptest_transfer.py`:26 trace hashes, source freeze, prior-v2 equality, ground-truth metrics, timing, warmup parity, actuator limits, deterministic noise parity and selection checks passed. OpenSpec validation passed. Full suite output includes intentional fixture-generated failure records; overall suite is OK.

Offline HTML: docs/reports/boptest_transfer_2026-09-08_zh.html; builder scripts/build_boptest_transfer_report.py. All26 cases and the hot-day outlier remain visible. Plot visually inspected; static links and offline assets audited. Browser viewport rendering not exercised. Source/JSON/report hashes retained. Original pilot files and E15 evidence unchanged.

## Next development target and synchronization boundary

Prioritize noise-aware disturbance estimation / command smoothing with explicit tracking-versus-actuation tradeoff, then test actuator lag and a second plant. New tuning must use development data and a new frozen evaluation contract; these opened dates cannot be relabelled unseen confirmation. Full manuscript/source/generated-document adoption remains outside this exploratory round, so no thesis main claims or main presentation were revised. New professor briefing is HTML, not PPTX. Keep this change unarchived until any subsequent adoption and independent scope expansion are handled.
