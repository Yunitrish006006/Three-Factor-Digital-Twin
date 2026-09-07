# Evidence

## Run Identity

- First full experiment run: `2026-08-17T08:25:33.996156+00:00`
- Command: `python3 scripts/run_kalman_filter_comparison.py`
- Protocol version: `1.0`
- Output: `outputs/data/public_benchmarks/kalman_sml2010_filtering_comparison.json`
- Output SHA-256 after first run: `b215666a122f3874ee00a986e3369c83dab3dd7b91bf88bcaac467ad3c5aa44b`
- Deviations from registered seed, profiles, split, methods, covariance, and decision rules: none.

## Input Provenance

| File | SHA-256 | Bytes |
| --- | --- | ---: |
| `corner_sensor_timeseries.csv` | `7be1dcde9ffaa42a327b7f21a24da28e995ac39dc6f2ee2bf13ad91e91d882c8` | 530,746 |
| `outdoor_environment.csv` | `09c4eb14a63fa69992d6cda2b1f502937b09937d0b4b0c08db5c2d2816f751c9` | 278,439 |
| `auxiliary_features.csv` | `c625fd0fd7d8c56b0b6832e1e4d68de3875696d6ace33d32f0772d72d5e41e5d` | 654,379 |

## Completion and Parity

- Study status: `COMPLETE`.
- Evaluated cases: 12/12.
- All-case data parity: passed.
- Each method contract records identical test timestamp, corrupted-observation, reference-target hashes, and test counts within its case.
- Unit tests for scalar update, deterministic injection, parity, gap reset, adverse-winner retention, and protocol-window rejection: 5 passed.

## Results

| Target | Profile | Raw MAE | MA(3) MAE | Kalman MAE | Lowest |
| --- | --- | ---: | ---: | ---: | --- |
| dining temperature | low | 0.396702 | 0.258668 | 0.379129 | MA(3) |
| dining temperature | nominal | 0.785927 | 0.453059 | 0.723036 | MA(3) |
| dining temperature | high | 1.577985 | 0.927776 | 1.235473 | MA(3) |
| room temperature | low | 0.405814 | 0.252429 | 0.340791 | MA(3) |
| room temperature | nominal | 0.816080 | 0.492713 | 0.666853 | MA(3) |
| room temperature | high | 1.624714 | 0.934859 | 1.148491 | MA(3) |
| dining humidity | low | 1.178247 | 0.728383 | 0.622890 | Kalman |
| dining humidity | nominal | 2.331636 | 1.353087 | 0.921164 | Kalman |
| dining humidity | high | 3.861846 | 2.259842 | 1.217964 | Kalman |
| room humidity | low | 1.145203 | 0.678723 | 0.574575 | Kalman |
| room humidity | nominal | 2.338500 | 1.367243 | 0.915512 | Kalman |
| room humidity | high | 3.846942 | 2.244045 | 1.190780 | Kalman |

Lowest-MAE counts:

- `raw_noisy`: 0/12.
- `causal_moving_average_3`: 6/12.
- `linear_kalman_random_walk`: 6/12.
- Kalman beat raw in 12/12 and beat MA(3) in 6/12.
- All six non-Kalman winners remain listed as adverse cases in the JSON.

## Interpretation

The fixed scalar Kalman filter is useful under the registered humidity corruption cases but is not universally best: the simpler causal MA(3) wins all registered temperature cases. This supports a variable- and model-dependent filtering conclusion, not a Kalman superiority claim.

The evidence class is `CONTROLLED_INJECTED_NOISE`. The original SML2010 record is a task reference, not latent physical ground truth, and the injected standard deviations do not characterize a deployed physical sensor.

## Claim Decisions

| ID | Decision | Evidence |
| --- | --- | --- |
| `RQ-KF-01` | evaluated | 12 complete cases and parity audit |
| `CLM-KF-02` | supported | executable same-data comparison completed; superiority not required |
| real-sensor denoising claim | not evaluated | no independent physical reference sensor |
| forecast/spatial/control claim | not supported by this experiment | current-time scalar filtering only |

## Professor Demo Evidence

- Builder: `python3 scripts/build_professor_demo.py`.
- Output: `outputs/demos/professor_two_week_demo_2026-08-04_2026-08-17_zh.html`.
- Initial output SHA-256: `06447eb0cf835addc581cf754754df581c41237c316c0304347d7d3c1ceb7b82`.
- Final output SHA-256 after adding both the same-data temporal RNN comparison and the same-task pure RNN 3-D field comparison to the main progress section: `5c4351b75509cc407c3d22663cfcaf16c1b172681f42a222e91685c6cf50ae2e`.
- Static HTTP retrieval found the expected title, Kalman section, navigation and copy functions.
- Live Web demo started on `127.0.0.1:8765`; its landing page and `/api/public_benchmarks` returned valid content.
- Visual browser screenshot QA was not available because the configured browser runtime reported no available browser instances. This is a presentation-QA limitation, not missing experiment evidence; the change remains active until the applicable final review is completed.

## Artifact and Validation QA

- Rebuilt the Chinese thesis DOCX/PDF, both PPTX variants, and the IEEE PDF from their canonical sources.
- Visually inspected all 83 Chinese thesis PDF pages and all 7 IEEE PDF pages after Poppler rendering; no clipping, overlap, missing page, or broken-table defect was observed.
- Rendered and visually inspected all 42 standard-deck slides and all 54 extended-deck slides through the artifact-tool renderer. The canonical overflow checker passed both decks with no overflow detected.
- The DOCX ZIP package passed structural integrity checks and contains the Kalman, `12/12`, and `20–30` content. DOCX-specific LibreOffice rendering was unavailable because LibreOffice is not installed; the synchronized PDF source was still fully rendered and inspected.
- Full unit-test suite: 166 passed.
- Thesis result verifier: 78 PASS, 0 FAIL, 0 MISSING.
- Research OpenSpec validator: 14 spec files, 111 requirements, 213 scenarios, 2 active changes.
