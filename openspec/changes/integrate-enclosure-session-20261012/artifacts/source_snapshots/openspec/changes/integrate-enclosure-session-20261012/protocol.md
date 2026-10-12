# E-ENC-51 preregistered exploratory protocol

Register before implementation/evaluation. All units as in E-ENC-31: C, W, J/K, W/K, s and normalized fan duty. Reuse the documented three-temperature plus fan network, sparse observer and corrected raw-sensor warning contract. No changes to frozen earlier studies.

## Session and calibration

Inputs: time_s, plate_C, air_C, fan_fraction, inlet_C, power_W. Source reference is optional scoring data, never a session input. Require finite values, fan in [0,1], power >=0 and exactly 5-second increasing samples (tolerance 1e-6). No silent sensor imputation. Invalid input returns no command by raising an error; this software does not actuate hardware or guarantee fail-safe hardware behavior. Commands have duty [.2,1], slew .1/sample; common warning uses estimated source or either raw temperature >=29.5C. Target 28C, reported limit 30C.

Each rig uses the same 180 samples (900s) of open-loop calibration at inlet22C, initial temperatures22C and fan.4; power .8/2.8W alternates every20 samples, PWM .25/.75 every15; noise SD [.10,.10,.005], seed612100. Fit [contact, plate_fan, common capacity scale, fan_tau] from observed plate/air/fan only; nominal [.7,.8,1,15], bounds [.25,.3,.6,5] to [1.5,2,1.6,40], least_squares max_nfev40. Thermal residuals divided by .1, fan residual by .005. Record nfev AND actual residual calls, numerical-Jacobian condition and elapsed cost. On failed fit use nominal and retain failure. Other coefficients and capacity ratios are assumed, not identified.

## Plants and splits

Validation rigs: capacity_variant(contact.6, fan_gain1.0, capacities[23,92,34.5], tau22); duct_variant(contact1.2, fan_gain1.4, capacities[17,68,25.5], tau9).
Holdout rigs: contact_capacity(contact.5, fan_gain.9, capacities[27,88,36], tau30); extra_path(contact1.0, fan_gain1.2, capacities[18,100,24], tau12, direct source-air conductance.12W/K). Extra path absent from fitted model. Calibration may observe each rig through the identical protocol; neither rig-specific controller gains nor manual tuning allowed. This is commissioning-assisted synthetic transfer, not zero-shot.
Validation seeds[612111,612112], holdout[612121,612122]. Each episode120x5s, six independent .8-3.2W load blocks of20 samples, inlet22+.3sin(2pi*k/120+phase), observed noise as above. Initial hidden source/plate/air = inlet+[1.5,.5,.2], fan.4; observer all temperatures=inlet. Extra unseen heat.15W only during evaluation. Per rig/seed, all methods receive the same exogenous schedule and noise draws; their closed-loop state trajectories legitimately differ. Plant evolved with independent solve_ivp rtol1e-8/atol1e-10, not estimator RK4.

## Comparators and optimization

Open-loop fixed PWM.4/.8 every25: nominal physics, calibrated physics, sparse corrected (24 episodes). Closed-loop: fixed, PI, PID, LQR, linear MPC, rank_h1, rank_h6, rank_h6_no_correction (64 episodes). Total88 episodes/10560 samples. PI/PID and ranking weights match E-ENC-31, no gain search.
LQR: reachable/clamped equilibrium at current inlet/power, linearize 4-state discrete RK4 at equilibrium, solve DARE Qdiag[1,.25,.1,.02], R[.15], state feedback around equilibrium. Recompute from current declared load, no future oracle; failures fall back to six-step ranking and are counted. Limiting the command removes unconstrained optimality claims.
Linear MPC: six-step affine discrete linearization at current estimated state and previous PWM; present inlet/power held constant. Source-target square + .15u^2 + .5du^2 +100 positive(source-30)^2, average over six steps; hard duty/slew inequalities, SLSQP ftol1e-7/maxiter40, analytic gradient, initial constant previous command. Check solver success/finiteness and all sequence constraints (tol1e-7); on failure use rank_h6, count fallback. Linearized constrained optimization is distinguished from full nonlinear MPC. All methods use the same warning override and actual command constraints.

## Evidence and decisions

No exclusions; no outcome-driven reruns. Freeze implementation, protocol/config/calibration and source snapshots before evaluation. Preserve all episodes, failure counts, command violations, timing and out-of-domain counts. Report source/prediction MAE/RMSE, tracking MAE, max source, sampled overtemperature seconds, command variation, fan proxy 2*f^3Wh, warnings, solver fallbacks and mean/p95/max computation time. Macro weight episodes equally; per-rig results accompany aggregate. Criteria H-ENC-51/52 above, no significance or physical safety claim. Independent verifier recomputes every metric, checks complete splits, raw warnings, dynamics/time/noise provenance and rejects mutated timestamps/truth/metrics. All historical evidence and original sources remain byte-identical. Hardware and oral report status remain NOT_EVALUATED unless actual evidence arrives.
