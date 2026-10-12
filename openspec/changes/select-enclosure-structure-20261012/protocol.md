# E-ENC-71 preregistered exploratory protocol

Register before implementation and opening new evaluation seeds. No E15 or frozen enclosure study rerun. The prior negative findings motivate this design but are already-opened exploratory evidence.

## Thermal models, calibration and selection

Reuse three-temperature/fan balance and add source-air heat exchange G_ha(T_h-T_a), subtracted from source and added to air. Model S has G_ha=0 and four fitted parameters [contact, plate_fan, common capacity multiplier, fan_tau], same bounds/start as E-ENC-51. Model F has seven fitted parameters [contact, plate_fan, source capacity multiplier, plate multiplier, air multiplier, fan_tau, G_ha]. Start [.7,.8,1,1,1,15,.05]; bounds [.25,.3,.6,.6,.6,5,0] to [1.5,2,1.6,1.6,1.6,40,.3]. Nominal capacities[20,80,30]; plate_base .15, air_base1, air_fan1.5, bypass.05 remain assumed/known. Fit with least_squares, single start, max_nfev40, count actual residual calls including numerical Jacobian. Same algorithm/budget on every rig.

Commissioning: 180x5s samples, seed612700, inlet22C, initial temperatures22C/fan.4; power .8/2.8W alternating every20, PWM .25/.75 every15; SD[.1,.1,.005] for plate/air/fan. Train on first120 only (600s). Score on last60 only (300s), weighted mean squared open-loop plate/air/fan error scaled [.1,.1,.005]; propagate from the declared initial state using measured commands, no posterior sensor assimilation. F replaces S only if its finite selection score <=.95*S and its optimizer succeeded; otherwise choose S. If S fit fails use nominal parameters and report fallback; F failure cannot be selected. Do not refit on all180 after selection. Every model sees identical visible inputs; hidden-source truth is absent. Two fitting trials total per rig; report full costs, selection scores, selected model, saturation and local condition (not global identifiability).

## Fresh plants and evaluation

Validation: proportional(contact.65,gain1.05,capacities[22,88,33],tau20,G_ha0); independent_caps(contact.85,gain1.0,capacities[29,60,40],tau25,G_ha0); path_variant(contact1.05,gain1.3,capacities[18,104,25],tau11,G_ha.14).
Holdout: contact_variant(contact.48,gain.95,capacities[28,90,35],tau32,G_ha0); path_capacity(contact.95,gain1.25,capacities[19,108,23],tau13,G_ha.18); convection_mismatch(contact.9,gain1.1,capacities[25,72,38],tau18,G_ha.08,air_fan1.9). Last coefficient is absent from fit. All coefficients are assumptions, not measured devices. Known plant variants do not establish arbitrary-family or real cross-device transfer.
Validation seeds[612711,612712]; holdout[612721,612722]. Each120x5s episode: six random .8-3.2W blocks of20, inlet22+.3sin(2pi*k/120+phase), SD[.1,.1,.005], initial inlet+[1.5,.5,.2]/fan.4. Extra unseen heat.15W in evaluation only. Generate identical exogenous schedules/noise per rig/seed, independent solve_ivp truth rtol1e-8/atol1e-10; model RK4. No future power/inlet oracle, no exclusions.

## Comparators and observer/control

Open-loop PWM.4/.8 every25: S-physics, S-corrected, selected-physics, selected-corrected (48 episodes). Closed-loop: S-PI, selected-PI, S-H6, selected-H6 (48). Total96 episodes/11520 steps. Same sparse observer initialization Pdiag[4,1,1], measurement Rdiag[.01,.01], Qdiag[.02,.01,.01], Joseph update; local thermal Jacobian includes G_ha. Observed fan is supplied each step. Changing model structure is isolated from controller gains/horizon/cost, which remain E-ENC-51 values.
PI kp.12/ki.002, feedforward.6/backcalc.2. H6 nine constant request levels .2-1, feasible slew ramp, stage costs source-target square +.15u^2+.5du^2+100 positive(source-30)^2, average six steps; apply first and re-estimate. Target28, warning29.5, reported limit30; raw plate/air or estimated source warning, duty[.2,1], slew.1. No hardware actuation or safety guarantee. LQR/linear MPC introduction and prior comparison remain available; this new study isolates thermal estimation and PI/H6, not a new all-controller ranking.

## Evidence

Freeze protocol/research/code/config/calibration/source snapshots before evaluation. Preserve old evidence bytes. Per episode metrics: source/prediction MAE/RMSE, tracking MAE, max source, sampled overtemperature s, out-of-domain steps, command variation, assumed 2*f^3 energy proxy Wh, command violations, warnings, compute mean/p95/max ms. Macro equal episode weighting with per-rig results. Independently recompute metrics, complete design, selection rule, time/noise/truth continuity and plant dynamics; reject metric/timestamp/truth/selection corruption. H-ENC-71/72 criteria above; retain unsupported/negative outcomes. No opened test-driven adjustment or confirmatory population claim.
