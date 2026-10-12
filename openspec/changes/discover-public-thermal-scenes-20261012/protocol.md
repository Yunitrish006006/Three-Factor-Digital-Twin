# Availability and educational preparation protocol

Candidate set: SimScale Electronics Box CHT tutorial; official UVA HotSpot; TCLab offline emulator; BOPTEST public REST service. Read primary documentation/source and record source URL, access date, version/commit/license, inputs/outputs, assumptions, accounts/dependencies and limits.

Bounded readiness checks, not algorithm experiments:
- SimScale: inspect official tutorial, public project import destination and access requirements. No account creation, private upload, paid resource or solver launch.
- BOPTEST: one GET https://api.boptest.net/testcases with valid TLS and <=20s timeout; if sandbox blocks network, retry the same request with approved network permission. Preserve HTTP/TLS failure. Do not infer permanent outage. No test instance/control experiment.
- HotSpot: read official Makefile/license/HOWTO, pin downloaded official source commit, build in temporary isolation, then execute at most one bundled unchanged block-model example. No performance/controller ranking, tuning, trace exclusion or hardware claim. Retain all command failures.
- TCLab: inspect official offline-emulator source/docs, pin version. If lightweight isolated execution is available, exercise one two-heater/read-temperature interface sequence using the official emulator only. This is a functionality check, not a new LQR or project-estimator comparison. Never access hardware.

LQR guide: separately label modern continuous/discrete teaching equations and the Kalman1960 original. Verify original page locations and use primary MIT/SciPy/control documentation for equilibrium, Q/R scaling, Riccati/eigenvalue checks, stabilizability/detectability, state estimation, saturation, disturbance/tracking and fair comparison. Numerical rank alone and solver success are not hardware safety. No new gains or efficacy outcomes are invented.

Update the same HTML/talk source without modifying prior numerical conclusions. Perform fresh1440/820/390px, anchors/keyboard/offline/console/local-link and full print observation, exact hashes. Keep prior QA bytes; new outputs under this change. Preserve failures and distinguish proposed next steps from executed tests.
