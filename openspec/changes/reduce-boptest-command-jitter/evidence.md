# Jitter and delay improvement evidence — 2026-09-08

Status: COMPLETED exploratory round. Main thesis adoption remains NOT_ADOPTED.

## Actual run and selection

All16 development episodes and18 frozen-transfer episodes completed without execution failures. Development compared unchanged v4, actual-applied-action feedback alone, and feedback with smoothing alpha0.6/0.35 on previously used days95/245, each with noise0.05C and delay0/1. Selected smooth035 under the predeclared tracking-plus-command-variation gate, before transfer. Source/protocol/prior/FMUs and development hashes were frozen; transfer matched them. No parameter changes occurred after unseen dates opened.

Transfer used new days65/155/275, each clean/no-delay and noisy/60s-delay. Comparators are v4, smooth035, and prior grid PI with handover. The grid has no matching smoothing, so the primary improvement claim is against v4, not superiority to all PID designs. Noise sequences were seeded52000+day and common within each comparison. A fixed FIFO transport delay is simulated, not physical continuous actuator dynamics. Scoring uses true temperature while controllers see noisy measurements.

## Full transfer table

|Day|Noise SD C|Delay steps|Controller|MAE C|Max error C|Requested TV C|Applied TV C|
|---:|---:|---:|---|---:|---:|---:|---:|
|65|0|0|v4|0.002899|0.158210|31.964|31.964|
|65|0|0|smooth035|0.007402|0.239479|31.586|31.586|
|65|0|0|grid|0.018179|0.169826|32.150|32.150|
|65|0.05|1|v4|0.040564|0.269904|503.715|503.428|
|65|0.05|1|smooth035|0.027440|0.361408|151.172|151.096|
|65|0.05|1|grid|0.048376|0.296385|669.129|668.786|
|155|0|0|v4|0.002247|0.166552|16.850|16.850|
|155|0|0|smooth035|0.005099|0.253918|17.189|17.189|
|155|0|0|grid|0.009743|0.163250|16.851|16.851|
|155|0.05|1|v4|0.037536|0.250840|486.151|485.646|
|155|0.05|1|smooth035|0.027297|0.339774|145.043|144.788|
|155|0.05|1|grid|0.042912|0.263036|648.921|648.347|
|275|0|0|v4|0.215134|1.385006|26.014|26.014|
|275|0|0|smooth035|0.219519|1.386495|26.073|26.073|
|275|0|0|grid|0.228530|1.390099|26.051|26.051|
|275|0.05|1|v4|0.243729|1.386004|390.783|390.369|
|275|0.05|1|smooth035|0.235080|1.387616|115.864|115.666|
|275|0.05|1|grid|0.251492|1.391126|512.768|512.511|

## Findings and claim decisions

RQ-BPJ-01 partially supported as an engineering tradeoff: noisy/delayed macro requested TV drops460.2162 to137.3595 C (70.1533% reduction). Macro MAE drops0.1072762 to0.0966059 C. All three noisy/delayed dates improve MAE. However all three clean dates have higher MAE: macro0.0734267 to0.0773398 C, per-date increase0.002852–0.004503 C. Maximum error increases in all six cases, by up to0.091504 C. The predeclared +0.02 C MAE/+0.2 C max-error tolerance and >=20% TV-reduction gate passes, but this is not Pareto dominance or statistical equivalence.

RQ-BPJ-02 supported only in the tested development cases: using actual prior applied supply reduces delayed-case MAE (day95 0.038155 to0.032799 C; day245 0.260724 to0.256947 C). Feedback correction alone does not remove command jitter; development macroTV rises454.496 to456.867 C. Smoothing is responsible for most of the TV reduction. No claim of unknown-delay robustness is supported.

Selected alpha0.35 reuses2h identified gain and adds no new identification excitation. Alpha was nevertheless chosen on development simulations, so the whole algorithm is not tuning-free. Back-calculation gain0.1 is a fixed design choice. No new neural model or neural effectiveness was tested.

The high-load day275 remains difficult: all methods have a substantial midday temperature rise. It is retained in clean/noisy averages, plots and per-case evidence. Requested saturation and separate applied saturation (applied_saturation_diagnostic.json) are distinct. The presence of saturation is consistent with capacity constraints; smoothing does not expand available cooling. Total variation measures action activity, not energy, wear or lifetime.

## Audit and costs

python3 -m unittest discover -s tests:239 tests passed in218.642s. Added tests cover smoothing bounds, first action, observer applied-action semantics, identity smoothing and filtered-command interpolation. python3 scripts/verify_boptest_jitter.py verified34 trace hashes, source freeze, exact FIFO transport sequence, prior-action readback, true-temperature metric recomputation, common deterministic noise, timing, actuator bounds, warmup state parity and selection. OpenSpec validation passed.

Each episode has24h warmup+24h scoring, for1632 aggregate reset-episode simulated hours this round. This is not human time. Prior2h budget means a prefix of a collected6h trajectory; nine-grid historical trial exposure54h is not the general cost of auto-tuning. Offline candidate selection, all current runs and ongoing observer computation are extra costs. No human commissioning-time reduction was measured.

## Report and remaining limits

Offline report: docs/reports/boptest_jitter_2026-09-08_zh.html. Source: scripts/build_boptest_jitter_report.py. Both requested and applied command variation are shown. Full source/evidence/plot/HTML hashes retained. Scientific plot visually inspected; HTML static links/assets checked; browser viewport rendering not exercised. Older studies and E15 evidence remain untouched.

New dates are still the same official bestest_air FMU/weather year. Only one noise seed per date and one fixed-delay size are used. Clean versus noisy/delayed transfer cases vary two factors together; do not attribute the combined difference to noise alone. Future work: multiple seeds, variable/longer delay, filter-matched strong PI, a second plant and constrained calibration. Neither real hardware nor humidity, semiconductor precision, product yield, human time or novelty is validated.

This is a separate exploratory extension, not an adopted change to Chinese/English main manuscripts or primary estimator claims. New professor report is HTML. Full thesis/source/generated-output synchronization is still required upon adoption. Keep unarchived.
