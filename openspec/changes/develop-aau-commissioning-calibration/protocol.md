# Protocol

## New Data Split

- Dataset: AAU Server Room v4, DOI `10.5281/zenodo.19398358`.
- Eleven fixed 4 MiB ranges begin at bytes `7976889, 71792002, 135607115, 199422228, 263237341, 327052454, 390867567, 454682680, 518497793, 582312906, 646128019`.
- The phase is one eighth of each 63,815,113-byte segment.
- Before any request, the downloader must reject overlap with every existing enclosure manifest and all reserved E11F ranges.
- First and last partial records in every fragment are discarded.

## Chronological Partition

- Sort complete calendar-day blocks.
- Calibration: earliest two days.
- Selection: third day.
- Frozen test: every remaining day.
- Fewer than five complete days is a hard stop.

The target sensor is visible only during calibration and selection. Test predictions for a target use all other sensors but never that target's test value.

## Fixed Predictors

- Baseline: local IDW with `k=3`, power `p=2`.
- Secondary base: the frozen E11G sensor map, applied without E11H fitting.
- Median-offset calibration: residual median from the two calibration days, shrunk by `{0.50, 0.75, 1.00}`.
- Huber-affine calibration: 20 deterministic IRLS iterations, Huber constant 1.345, and slope clamped to `[0.5, 1.5]`.
- Total candidates per sensor: eight.

## Selection Rule

Fit candidate parameters on the two calibration days. A candidate is eligible only when its selection-day MAE, RMSE, and P95 each improve over local IDW by at least 0.02 degrees Celsius. Select lowest P95, then MAE, RMSE, and model ID. If none qualify, freeze local IDW.

## Advancement Gate

On frozen test days, every condition must pass:

- Strictly lower global MAE, RMSE, and P95 than local IDW.
- Strictly lower per-sensor MAE for at least 26 of 42 sensors.
- Day-block bootstrap 95% lower bound for baseline-minus-model MAE above zero.
- Absolute MAE at most 1.25 degrees Celsius, RMSE at most 1.90, and P95 at most 4.00.

Bootstrap settings are 20,000 replicates and seed `20260823`. Any failure yields `no_candidate_forwarded` and prohibits E11F access.

