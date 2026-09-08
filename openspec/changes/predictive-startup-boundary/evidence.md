# PSB-001 actual evidence
Status: completed unadopted research; H-PSB-01 not supported across both confirmation dates. No adopted thesis changes.

## Execution and costs
15 new development episodes plus12 unique confirmation episodes=27 newFMU runs,333 scoredh+648 warmuph=981 simulatedh.13 explicit reuse records:5 old development baselines+8 same-date confirmation fallback references. Aggregate episode wall time846.674s, not elapsed task time due parallel runs. New candidate trial exposure9h/device, existing baseline3h and identification2h retained; nominal cumulative adaptation14h excludes prior research search costs, which cannot be treated as zero. No cost advantage established.

## Selection and confirmation
Only hydronic selected a candidate:3min horizon, by tie-break; all three hydronic candidate physical trajectories exactly equal, all triggered55min and reachedzero56min. Thus no horizon optimum identified. Other devices choose purePI. Four exact fallback pipelines are preservation only, not independent improvement.
Hydronic day42 earlyMAE0.994999→0.830848°C (~16.50%); late1.750634→1.754072°C, within frozen retention tolerance; acquisition1306→1305min; composite gatePASS. Hydronic day77 early0.952741→0.798939°C (~16.14%); late0.261483→0.265403°C, within tolerance; acquisition576→581min, violating+1min criterion; composite gateFAIL. Zero devices demonstrate candidate superiority across both dates.
Same development-day hydronic prior helper earlyMAE0.747819 versus new0.788826°C: new worse. Its lateMAE0.701277 baseline→0.706005 candidate, within tolerance but strictly worse. Air no longer delays acquisition, but early improvement disappears. Commercial early improvement~0.084% does not meet1%; heat_pump/apartment do not establish meaningful early gains. Preserve all exact figures in source JSON.

## Post-result descriptive diagnosis
artifacts/verification.json records per-command snapshots at55/60/120min, with source CSV row references. Hydronic day77 minute60 candidateT21.238321°C versusbaseline21.121179°C, but u0.248275 versus0.262683 and integral-0.307014 versus-0.301108. At120min candidateT21.294953 versusbaseline21.310047. Day42 also shows warmer-at60/lower-command/slightly-colder-at120. Consistent with loss of progress following withdrawal, but not independent causal proof. Controller changes both predictive exit and integral handling; this study cannot isolate their contributions. A subsequent preregistered ablation should separate assistance duration from withdrawal/state handling. No post-confirmation tuning performed here.

## Verification and artifacts
verify_boptest_predictive_startup.py PASS: frozen source and selection hashes, full trace hashes, all commands/diagnostics replay, ordinaryPI core tests, trajectory continuity, rate and amplitude bounds, irreversible withdrawal, correctionzero after60min, all metric windows and gates, explicit priorbaseline reuse validation. Full Python suite270 tests PASS in332.114s;4 new meaningful controller tests. Offline report docs/reports/boptest_predictive_startup_2026-09-08_zh.html. Graph-sync checks recorded separately.

## Limits
Known-device simulation, not unknown-plant generality, real control hardware, RH/EUV/NN or REST/KPI equivalence. The prior method remains historical best on its tested dates; different confirmation dates here do not directly rank old/new policies. Absolute lateMAE~1.75°C is not precision temperature regulation. Do not adopt the new method as an improvement.
