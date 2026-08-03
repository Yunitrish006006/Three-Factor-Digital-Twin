# Pre-Registered Protocol

## Protocol Identity

- Change: `improve-next-day-temperature-forecast`
- Protocol version: `2.0`
- Registration date: `2026-07-26`
- Related IDs: `RQ-ND-01`, `EQ-ND-01`, `H-ND-01`, `H-ND-ROB-01`, `CLM-ND-01`, `EVD-013`
- Status: `EXECUTED`

## Experimental Design

- Study type: deterministic chronological next-day forecasting comparison
- Dataset/task: normalized SML2010 `S2`
- Targets: `dining_temperature`, `room_temperature`
- Horizon: exactly `1440` minutes
- Unit of analysis: one origin/target timestamp pair
- Ordering: no shuffle
- Development/test split: earliest 70% development, latest 30% final test
- Selection split within all samples: earliest 60% train, next 10% validation, latest 30% final test
- Refit: after validation selection, refit the selected candidate on the earliest 70% only

## Leakage Contract

Allowed inputs are known at forecast origin:

- current dining/room temperature and humidity;
- current outdoor temperature/humidity, sunlight, rain, wind;
- origin-time `forecast_temperature_c`;
- current enthalpic motor states;
- timestamp-derived hour/day-of-week cycles;
- measured indoor temperatures at `t-24h` and `t-7d`;
- project physics prediction computed only from origin-time state.

Target-time measurements, target-time actual weather, target-time sunlight,
target-time device state, and any rows in the latest 30% test are prohibited
for feature or hyperparameter selection.

To preserve the same origin/target rows as the preceding 1440-minute
comparison, an unavailable historical lag is replaced by the nearest allowed
origin/history value and accompanied by an explicit availability flag. This
rule applies identically to development and test rows and never uses a
target-time value.

Protocol amendment `1.1` was registered after the first command stopped before
candidate fitting or metric production: the SML2010 file boundary leaves some
valid origin/target rows without an exact `t-7d` timestamp. The amendment
changes only missing-history handling; candidates, grids, split, metrics,
hypotheses, and thresholds are unchanged.

## Registered Candidates

| ID | Candidate | Definition / selection |
| --- | --- | --- |
| `B-ND-01` | seasonal persistence | `y_hat(t+24h)=y(t)` |
| `C-ND-01` | bias-corrected persistence | add mean training delta |
| `C-ND-02` | damped daily trend | `y(t)+alpha[y(t)-y(t-24h)]`; `alpha` in `0, .25, .5, .75, 1` |
| `C-ND-03` | persistence--physics blend | `(1-lambda)y(t)+lambda y_physics(t+24h)`; `lambda` in `0, .25, .5, .75, 1` |
| `C-ND-04` | seasonal residual ridge | predict `y(t+24h)-y(t)` from registered origin-known features; ridge in `1e-4, 1e-3, 1e-2, .1, 1, 10, 100` |

Candidate and hyperparameter selection is performed independently per target by
lowest validation MAE. Ties within `1e-12` are resolved by the listed candidate
order and then lower numeric hyperparameter.

## Metrics and Decision Criteria

| Hypothesis / claim | Metric | Support rule |
| --- | --- | --- |
| `H-ND-01` | final-test MAE | selected model beats persistence for both targets and mean relative reduction is at least 5% |
| `H-ND-ROB-01` | paired daily-block bootstrap MAE reduction | 95% interval lower bound is positive for both targets |
| `CLM-ND-01` | parity/leakage audit | all candidates use identical final-test rows and no prohibited feature |

Secondary descriptive metrics are RMSE, Pearson correlation, R2, CVRMSE, and
comparisons with raw physics, project readout, and the prior Oh2024-inspired
transfer on the same rows.

## Bootstrap

- Resampling unit: calendar date in the final test period
- Pairing: actual, persistence, and selected prediction move together
- Replicates: 10,000
- Seed: `20260726`
- Endpoint: paired mean absolute-error reduction
- Interval: 2.5th and 97.5th percentiles

## Execution Contract

| Step | Command | Output |
| --- | --- | --- |
| 1 | `python3 scripts/run_next_day_temperature_comparison.py` | `outputs/data/public_benchmarks/next_day_temperature_improvement.json` |
| 2 | `python3 scripts/verify_thesis_results.py` | verification JSON/Markdown |

## Deviations

All failed attempts, implementation corrections, and departures from this
protocol SHALL be recorded in `evidence.md`. Candidate features, grids, targets,
split, hypothesis threshold, and bootstrap settings SHALL NOT be changed after
the first candidate result is observed without a new protocol version.

## Protocol 2.0: Post-Primary Exploratory Adaptive Follow-up

The primary version 1.1 result is frozen and remains the basis for
`H-ND-01`, `H-ND-ROB-01`, and `CLM-ND-01`. After those decisions were observed,
version 2.0 adds a separately labeled exploratory online analysis; it does not
change or replace the primary result.

At each origin `t`, the adaptive correction may use only completed same-slot
daily deltas ending at or before `t`:

`delta(s) = y(s) - y(s-24h), s <= t`.

Registered adaptive candidates:

- rolling mean with the most recent `3`, `7`, or `14` available same-slot daily deltas;
- rolling median with the most recent `3`, `7`, or `14` available same-slot daily deltas;
- EWMA over at most 14 same-slot daily deltas with newest-value weight
  `0.25`, `0.50`, or `0.75`;
- uncorrected seasonal persistence.

Candidate selection uses only the same 10% validation interval. The selected
rule is then applied sequentially to the final 30%; origin observations that
arrive during the test period may update later forecasts, matching online
deployment. Target-time or later values remain prohibited.

Exploratory signal rule: selected adaptive MAE is lower than persistence for
both targets and mean relative MAE reduction is at least 2%. Because primary
test outcomes were already known when version 2.0 was designed, this rule is
descriptive and SHALL NOT support `CLM-ND-01`.
