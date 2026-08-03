# Pre-Registered Protocol

## Protocol Identity

- Change: `incorporate-professor-guidance-rnn-precision-kalman`
- Protocol version: `1.0`
- Registration date: `2026-08-03`
- Related IDs: `RQ-RNN-01`, `EQ-APP-01`, `EQ-KF-01`, `CLM-RNN-01`, `CLM-APP-01`, `CLM-KF-01`, `EVD-015`
- Status: `COMPLETED`

## RNN Experimental Design

- Study type: deterministic public-task comparator study.
- Dataset/task: normalized SML2010, task `S2`.
- Targets: `dining_temperature`, `room_temperature`, `dining_humidity`, `room_humidity`.
- Horizons: `15`, `60`, `1440` minutes.
- Sampling cadence: 15 minutes.
- History: four consecutive origin records ending at the prediction origin.
- Split: earliest 70% train, latest 30% test, no shuffle.
- Eligible endpoint: exact target timestamp exists, four finite origin-history records exist, and every required target/feature is finite.
- Primary comparison set: persistence, sequence ridge linear regression, physics-structured readout, vanilla RNN.
- Learned synthetic hybrid checkpoint: disabled for the primary parity ranking.

## Exact Data-Parity Contract

1. Build one ordered eligible-endpoint index per horizon before fitting any model.
2. Apply the same index and chronological split to every comparator.
3. Give sequence linear regression and RNN the same four raw SML2010 feature records.
4. Generate physics-structured features only from those same four origin records; no later observation or target-time measured boundary may enter.
5. Evaluate persistence and every fitted model on the exact same test endpoint IDs.
6. Record endpoint hashes, train/test counts, first/last timestamps, feature contracts, and any exclusions.
7. If endpoint hashes or counts differ, the comparison status is `NOT_EVALUATED` and no ranking is reported.

## Fixed Vanilla RNN Configuration

| Parameter | Registered value |
| --- | ---: |
| architecture | one-layer Elman tanh RNN, sequence-to-one multi-output |
| sequence length | 4 |
| hidden units | 6 |
| outputs | 4 standardized S2 targets |
| optimizer | Adam |
| epochs | 30 |
| batch size | 32 |
| learning rate | 0.01 |
| gradient clipping | elementwise 1.0 |
| seed | 42 |
| target loss | mean squared error |

No architecture, feature, epoch, learning-rate, seed, target, horizon, or endpoint change is allowed after the first result run without a protocol version increment.

## Baselines

| ID | Comparator | Input/data contract | Purpose |
| --- | --- | --- | --- |
| `B-RNN-01` | persistence | current origin target value at every shared endpoint | strong inertia baseline |
| `B-RNN-02` | sequence ridge regression | flattened same four raw feature records | tests whether history alone explains RNN performance |
| `B-RNN-03` | physics-structured readout | four physics-derived feature records from the same origins; readout fitted only on shared train rows | project primary-method comparator without extra learned dataset |
| `B-RNN-04` | vanilla RNN | same four raw feature records as `B-RNN-02` | professor-requested recurrent comparator |

## Metrics and Interpretation

- Per target and horizon: MAE, RMSE, Pearson correlation.
- Summary: lowest-MAE counts and pairwise MAE differences.
- No directional success threshold is registered.
- `CLM-RNN-01` is supported only if all 12 target-horizon cases are present, data-parity checks pass, and all comparator losses remain visible.
- Any overall mean is secondary; case-level metrics remain primary because temperature and humidity have different scales.

## Application-Fit Review Protocol

- Include primary studies that program temperature/humidity/light conditions in a closed growth environment or plant factory.
- Record whether each profile is static, day/night, sinusoidal, event-based, or growth-stage dependent.
- Record minimum and maximum indoor operating/target temperature; reject direct project alignment if any such value is outside `20–30 °C`. Outdoor boundary input does not expand the indoor range.
- Record missing constructs: PPFD/PAR, spectrum, CO2, substrate/root-zone variables, airflow, biological endpoint, disease/yield response.
- Decision output is a candidate matrix with `candidate`, `needs_extension`, or `out_of_domain`; it is not efficacy evidence.

## Kalman Reference Protocol

- Current change output: literature note plus future executable design; status `NOT_EVALUATED`.
- First future baseline: linear per-metric state-space Kalman filter on the same chronological rows as unfiltered physics and moving-average baselines.
- Extension gate: use EKF only after nonlinear state transition and observation equations are explicitly defined.
- Required future parity: identical observed rows, split, initialization interval, metrics, and reference targets.
- Required future diagnostics: process/measurement covariance provenance, innovation residuals, missing-observation handling, and adverse results.

## Execution and Evidence Contract

| Step | Command or artifact | Expected output |
| --- | --- | --- |
| 1 | `python3 scripts/run_rnn_public_comparison.py` | `outputs/data/public_benchmarks/rnn_sml2010_comparison.json` |
| 2 | application-fit review | `docs/research/professor_guidance_application_scope_zh.md` |
| 3 | Kalman review | `docs/models/kalman_filter_research_direction_zh.md` |
| 4 | `python3 scripts/verify_thesis_results.py` | verified RNN counts/parity/results |

## Deviations and Failure Reporting

- All deviations SHALL be recorded in `evidence.md`.
- Failed training, non-finite predictions, mismatched rows, and RNN losses SHALL remain visible.
- No application outside `20–30 °C` may be relabeled in-domain by truncating its reported setpoints.
- Kalman literature with negative results SHALL not be omitted.
