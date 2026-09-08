# SPB-001 actual evidence
Status: completed unadopted extension, not a main-thesis update.

## Frozen evaluation
20 development episodes (day8,3h each) followed by selection.json creation before any confirmation. Five known devices, existing2h identification, q=.5. Twelve unique confirmation episodes (days35/70,24h each): four hydronic baseline/candidate runs and eight other-device baselines, with explicit purePI references for their selected policies. Total32 episodes,348 scoredh+768 warmuph=1116 aggregate simulatedh. Aggregate per-episode wall time1082.136s (overlapping parallel execution, not elapsed task time). Each device requires12 extra trialh on top of existing2h identification; no total adaptation-cost superiority established.

## Results and limits
Only hydronic forwarded and passed all frozen criteria on both confirmation dates. Early MAE day35:0.962308→0.766161°C (20.383% reduction); day70:0.976246→0.775047°C (20.609%). Late MAE day35:0.273778→0.228944°C (16.376%); day70:2.120964→2.099043°C (1.034%). Acquisition onset635→619min and554→548min. Day70 candidate late peak5.609105°C: relative improvement does not establish adequate precision control or sustained all-day target maintenance.

Hydronic development all three bands had exactly identical u and next_T trajectories and exited at60min. Selected±0.2°C is only the frozen tie-break; no optimum error boundary identified. Heat_pump/apartment/commercial also have identical trajectories across their three development bands.

Air development±0.2°C improved early MAE0.127460→0.117439°C (~7.862%), but acquisition onset16→19min violates baseline+1min; all air candidates rejected. Heat_pump early improvement~0.03%, commercial~0.77% fall below1% minimum; apartment early unchanged. All four select purePI; reference reuse confirms preservation only, never counts as improvement or independent replication. Apartment actual development initialT23.688961°C is above the22°C target; other devices start near21°C.

## Verification
verify_boptest_startup.py PASS: source and selection hashes, all unique trace SHA256, every command and diagnostic replay, source-to-next-state continuity, output/correction limits, handover mismatch<1e-10, correction/active zero from minute60 onward, all windows and gates, exact baseline reference reuse. Full Python suite266 tests PASS in418.003s; seven new tests cover PI identity, dwell/crossing/deadline exit, transfer algebra, one-way exit, bounds, censored acquisition and adverse-tail rejection. See artifacts/verification.json.

## Interpretation and further hypothesis
The limited-duration helper has conditional evidence on hydronic. A shared error-only exit threshold has not been identified by this design. Temperature trend and accumulated integral state may help decide earlier exit, but this is an untested future hypothesis, not a retroactive change to these frozen results. All devices were already development devices. Official BOPTESTv0.9.0 FMUs via customFMPy runner; no REST/KPI equivalence, hardware, RH, NN or EUV claims.

Offline report: docs/reports/boptest_startup_2026-09-08_zh.html. ResearchWorkspace derives phase-specific early/late comparison pointers and explicit reuse nodes from canonical artifacts; graph synchronization recorded separately in artifacts/graph-sync-verification.json.
