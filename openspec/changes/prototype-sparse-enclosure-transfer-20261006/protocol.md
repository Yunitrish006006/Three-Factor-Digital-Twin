# E-ENC-31 preregistered exploratory protocol

Registered before implementation and result generation; checkpoint commit records this order.

## Model and observations

Units: temperatures °C, conductances W/K, capacities J/K, power W, time s, duty dimensionless. State: source, plate, air, normalized fan. Source validation temperature is never an input. Observed plate/air noise SD=0.10°C; fan SD=0.005 duty. Inlet and declared power observed exactly. Unmodeled extra heat=0.15 W in validation/holdout, zero in calibration. No future load oracle.

Capacities [20,80,30], contact G=0.7, plate-air G=0.15+0.8*f, air-inlet G=1+1.5*f, source-inlet bypass G=0.05, fan tau=15. All assumptions, not hardware measurements. Rigs: contact-poor (G=0.45, fan gain=0.8), metal-path (G=1.1, gain=0.8), duct-assumption (G=1.1, gain=1.3). The last label assigns an assumed convection change; it does not encode measured NA-FD1 response. No room coordinates/dense field generated.

## Calibration and splits

Each rig gets the same 120×5s open-loop excitation record, seed 610600, alternating heater powers 0.8/2.8 W every 20 steps and PWM 0.25/0.75 every 15 steps; inlet=22°C, initial temperatures=inlet, fan=.4. Fit only contact G and plate-air fan gain using plate/air data: least_squares, single start [.7,.8], bounds [.25,.3] to [1.5,2], max_nfev=30. Known capacities and other coefficients remain fixed; report nfev, cost and Jacobian singular-value condition. If fit fails keep nominal parameters and mark fallback, retaining all cases.

No controller tuning: fixed PWM=.6; PI/PID kp=.12, ki=.002, PID kd=.05 with derivative low-pass .25, anti-windup backcalc=.2. Observer Qdiag=[.02,.01,.01], Rdiag=[.01,.01], initial Pdiag=[4,1,1]; innovations use measured plate/air only. Frozen settings identical across rigs. Kalman prediction uses local fixed-fan thermal Jacobian RK4 transition; covariance update Joseph form.

Validation seeds [610611,610612], holdout [610621,610622]. Each episode 180×5s. Piecewise powers independently sampled 0.8–3.2 W every 30 steps, inlet=22+0.3*sin(2*pi*k/180+seed phase). Initial source/plate/air at inlet+[1.5,.5,.2], while observer initializes all at inlet; fan .4. Open-loop PWM=.4/.8 every 25 steps. Common open-loop forecast comparison: nominal physics, calibrated physics, calibrated sparse correction. Three rigs × two seeds × two splits=12 episodes, evaluated on identical commands.

Closed-loop methods fixed, PI, PID, rank_h1, rank_h6, rank_h6_no_correction; 72 episodes. All source-blind. The last is calibrated physics-only; the other methods share the corrected observer. Target=28°C, warning=29.5°C, limit=30°C; PWM .2–1, slew .1/step. Ranking evaluates 9 evenly spaced request levels with a feasible slew ramp, assuming present power/inlet constant; mean stage cost=(Tsource-target)^2+0.15*u^2+0.5*du^2+100*max(Tsource-limit,0)^2. Receding horizon H=1 or6, apply first action. Warning override uses estimated source or observed plate/air, never truth; it is not a safety guarantee.

## Evidence and metrics

No exclusions. Report per episode source estimation MAE/RMSE, one-step source prediction MAE, tracking MAE, max source temperature, sampled overtemperature seconds, 20–30°C out-of-domain steps, sum |du|, fan energy proxy 2*f^3 W (not whole-system power), observer calibration failures and command violations, wall time. Macro equal episode weighting. H-ENC-31/32 evaluated on specified holdout; validation also reported and cannot tune. No significance/real-device population claim from six synthetic pairs. Truth timestamps at current state for estimate, next state for forecast and tracking.

Output: artifacts/config.json, calibration.json, freeze.json (source hashes before evaluation), traces/*.csv, result.json, verification.json. Existing consumed studies untouched. Frozen-source edits after evaluation require a declared deviation/new study, not hidden reruns. Result verifier checks CSV metrics, splits, sample count, bounds, information flow, freeze hashes and decision rules. A fixed-command observable/source-truth invariance test checks no truth input.
