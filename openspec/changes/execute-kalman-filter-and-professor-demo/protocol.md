# Pre-Registered Protocol

## Identity

- Change: `execute-kalman-filter-and-professor-demo`
- Protocol version: `1.0`
- Registration date: `2026-08-17`
- Status before execution: `REGISTERED_NOT_RUN`
- Related IDs: `RQ-KF-01`, `CLM-KF-02`, `CLM-DEMO-01`, `EVD-017`, `HRL-010`, `SYN-009`

## Dataset and Units

- Dataset: normalized SML2010.
- Variables: `dining_temperature`, `room_temperature`, `dining_humidity`, `room_humidity`.
- Cadence contract: 15 minutes; discontinuities reset state/history.
- Unit of analysis: one target/profile/test timestamp.
- Split: earliest 70% rows for covariance initialization context and latest 30% for reported metrics; no shuffle.

## Fixed Comparison

- Methods: `raw_noisy`, `causal_moving_average_3`, `linear_kalman_random_walk`.
- Noise profiles: low, nominal, high as registered in `research.md`.
- Seed: 42 plus a deterministic target/profile stream offset.
- Reference: original normalized SML2010 current record.
- Input: identical corrupted current records for every method.
- Metrics: MAE, RMSE, Pearson correlation on the same test timestamps.
- Summary: lowest-MAE count, wins versus raw, wins versus moving average, and adverse cases.

## Kalman Contract

- Transition: `F=1`.
- Observation: `H=1`.
- Measurement covariance: `R=sigma_injected^2` from the registered noise profile.
- Process covariance: sample variance of first differences in the clean training reference, with a floor of `1e-9`.
- Initial state: first corrupted observation in each contiguous segment.
- Initial covariance: `R`.
- Missing/non-finite row or cadence gap: reset state and moving-average history; record reset count.
- Diagnostic output: mean absolute innovation, maximum absolute innovation, mean Kalman gain, `Q`, `R`, and reset count.

## Decision Rules

- The experiment is `COMPLETE` only if all 12 target/profile cases exist, hashes/counts agree across methods, and every metric is finite.
- `CLM-KF-02` is supported by completion and parity, regardless of whether Kalman wins.
- Any method may win a case. No covariance, profile, seed, or moving-average window changes are allowed after the first full run without protocol versioning.
- The output must label the study `CONTROLLED_INJECTED_NOISE`, not real-sensor validation.

## Demo Contract

- Offline HTML reads only committed evidence JSON and contains no invented metrics.
- It must show evidence class, method status, negative results, 20–30 °C boundary, and E8 `NOT_EVALUATED` status.
- It may link to the live Web demo command, but interface operation is not quantitative evidence.

## Expected Commands and Outputs

| Command | Output |
| --- | --- |
| `python3 scripts/run_kalman_filter_comparison.py` | `outputs/data/public_benchmarks/kalman_sml2010_filtering_comparison.json` |
| `python3 scripts/build_professor_demo.py` | `outputs/demos/professor_two_week_demo_2026-08-04_2026-08-17_zh.html` |
| `python3 scripts/run_web_demo.py` | local live 3-D/query/recommendation demo |

## Failure Handling

Missing data, non-finite outputs, parity mismatch, or incomplete cases produce `NOT_EVALUATED` or `PARTIAL`. Failures and adverse winners remain visible and may not be removed by rerunning with a new unregistered seed.
