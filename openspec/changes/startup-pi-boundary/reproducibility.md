# Reproduction
Use the existing outputs/boptest-venv/bin/python with LD_LIBRARY_PATH pointing to outputs/vendor/boptest-runtime/usr/lib/x86_64-linux-gnu (libgfortran4).

1. Run scripts/run_boptest_startup.py --plant NAME --phase development for air, hydronic, heat_pump, apartment, commercial. The first invocation exclusively creates freeze.json before simulation; all subsequent invocations verify every source hash. Run the first plant before parallelizing other invocations to avoid freeze creation races.
2. Run python3 scripts/select_boptest_startup.py once after all five development results complete. This freezes all development JSON hashes and automatic choices.
3. Run scripts/run_boptest_startup.py --plant NAME --phase confirmation for all five. Existing traces/results cannot be overwritten. PurePI fallback references its same-date baseline; unique episodes exclude reuse.
4. Run python3 scripts/verify_boptest_startup.py to replay every command and diagnostic, recompute both windows, check source/selection integrity and eligibility, and verify trace continuity.
5. Run python3 scripts/build_boptest_startup_report.py for the offline HTML.
6. Run python3 -m unittest discover -s tests and python3 scripts/validate_research_openspec.py.
7. In ResearchWorkspace, run validate-boptest-graph, validate-paper-graph, validate-viewer-parity, build-index and both graph renderers; copy the generated graph asset into the existing Flutter web build, then verify API/static asset paperGraph equality after reloading the idle local server.

Frozen inputs are prior2h models/calibration and official FMUs. Verification and presentation code are post-run derivations, not selection inputs. All dates/devices remain known-device pipeline evaluation; no real hardware or lower manual-tuning-cost claim. Cost separates existing calibration, new trial exposure, scored/warmup simulated time and wall time.
