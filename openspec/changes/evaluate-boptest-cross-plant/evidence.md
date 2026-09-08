# Cross-plant small-data adaptation evidence — 2026-09-08

Status: EXECUTION COMPLETED; CROSS-PLANT OBJECTIVE NOT MET. No main-thesis adoption.

## Shared method and actual execution

Source freeze covers portable_pi.py, runner, both device configurations, protocol and both official FMUs before any generalized simulation. Air began first; hydronic then ran independently while air evaluation completed. This differs only in scheduling from the listed serial reproduction order; no source or parameter-design edits intervened. Same frozen hashes verified for both. Calibration coefficients and one q parameter were adapted only by the specified same procedure.

Device-specific changes are confined to mapping/units/limits/auxiliary settings. The core has no plant-name input or branch. Auxiliary air fan0.5 / hydronic pump1 remains fixed during24h warmup and scoring, eliminating the old air-specific handover formula. This changes the prior air experimental setup, so new air scores must not be compared directly to historical v4/v5 as an algorithm-only improvement. Air target is air temperature; hydronic target is operative temperature. Their raw errors are not pooled.

Air completed17 episodes:1x6h calibration,8x2h selection trials,8x24h evaluations. Hydronic completed1x6h calibration;2h and6h prefixes both yielded rejected first-order fits, so8planned trials+8planned evaluations were skipped with explicit reasons. Total18completed episodes,16adaptive episodes NOT_EVALUATED. Execution status COMPLETED does not mean research success. No software execution failures.

## Parameter and model results

|Plant|Budget h|l|b per normalized u|Training one-step RMSE C|Status|
|---|---:|---:|---:|---:|---|
|air|2|0.21617152|2.56950523|0.006434|FITTED|
|air|6|0.21544720|2.56195487|0.012686|FITTED|
|hydronic|2|-0.03937939|0.22630949|0.025024|REJECTED_NONPHYSICAL|
|hydronic|6|-0.02495597|0.20175785|0.026322|REJECTED_NONPHYSICAL|

The same predeclared admissibility gate0<l<1,b>0 was applied. Hydronic l=-0.0393794/-0.0249560 implies scalar discrete poles1.0393794/1.0249560, rejected as a model for this stable first-order tuning formula. This is a fitted-model finding, not a claim that the real/simulated physical plant is unstable. Full matrix rank4 does not establish adequate excitation or correct model order. Plausible causes include omitted storage/delay, insufficient excitation duration and exogenous confounding; none was isolated as the sole cause. No sign-flipping, threshold relaxation, forced gains or special hydronic exception occurred.

## Air control results

|Budget h|Day|auto-PI MAE C|Proposed MAE C|
|---:|---:|---:|---:|
|2|10|0.024001|0.007254|
|2|40|0.020728|0.006747|
|6|10|0.024011|0.007247|
|6|40|0.020736|0.006739|

Both methods independently selected q=.5 for both air budgets using their two trial scores. Shared-data auto-PI and proposed control have identical identification and trial exposure. All four air paired comparisons have positive MAE gain and pass the declared error margins. Hydronic has no scored paired comparison and must not contribute zeros or a success count.

## Questions and cost accounting

RQ-BCP-01 partially supported: two different plant interfaces execute through configuration only, but the hydronic model does not pass automatic identification. RQ-BCP-02 supported only within air:2h plus4h trials achieves improvement against matched auto-PI; cross-plant claim NOT SUPPORTED by this round. RQ-BCP-03 identifies a shared-model limitation requiring future controlled investigation, not a resolved cause. Original estimator, E15 and neural weights were not changed; this is a newly parameterized dynamical controller.

Low-data budget refers to the usable2h/6h prefix of a6h collected calibration. Successful methods add2trials x2h=4h, yielding6h/10h active adaptation per method/budget. Shared calibration can be reused in the simulator comparisons; do not sum prefixes as independent experiments. All18episodes additionally consume24h common warmup each (432aggregate simulation h); scored work is12h calibration+16h trials+192h evaluation=220h, total652aggregate reset-episode h. Neither this nor solver wall clock is measured human commissioning time.

## Verification and report

python3 -m unittest discover -s tests:245 tests passed in219.763s. New tests cover normalized handover, antiwindup, known-dynamics recovery, invalid-model rejection and nonfinite commands. Cross-plant verifier recomputes18trace hashes/metrics, both fit decisions, normalization/readback, auxiliary settings, initial-state parity, trial count and order, selected trial hashes and pre-evaluation adaptation snapshot. Source freeze passes for both models. OpenSpec validation passed.

Offline report: docs/reports/boptest_cross_plant_2026-09-08_zh.html; builder scripts/build_boptest_cross_plant_report.py; plot depicts both identification trajectories. Plot visually inspected and static report links audited; browser viewport rendering not exercised. Upper/lower temperatures and out-of-domain calibration retained; the excitation recipe is not certified safe for a real precision process. Full individual energy channels stay in JSON and are not combined as a generic energy total.

## Next work and claim boundary

Do not patch a hydronic-specific model or keep adjusting until the same case passes. A future shared identification change may support multiple time constants/delay or a bounded data-sufficiency strategy, with equal budgets and predeclared candidate selection for all plants. Once hydronic calibration outcomes inform design, it is an adaptation/development plant; another untouched plant is needed to substantiate stronger generality. Air/hydronic are still HVAC, not cross-industrial proof. Winter days10/40 were specified before execution because hydronic is heating-only; no summer cooling, humidity, real hardware, EUV precision, novelty or human-time-saving claim is supported.

Main Chinese/English manuscripts and main presentation remain at the prior adopted evidence level. This exploratory negative report is separate; global thesis source/generated-output synchronization remains required upon adoption. New professor report is HTML. Keep change unarchived; the user objective of successful low-data cross-scenario adaptation is still outstanding.
