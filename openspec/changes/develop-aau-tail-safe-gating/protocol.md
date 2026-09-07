# Protocol

## Data and Leakage Boundary

- Development data: the frozen E11E AAU fragments, 42 mapped sensors, and frozen E11C metadata.
- Evaluation unit: minute snapshot, grouped by calendar day.
- Cross-validation: leave one complete day out; model selection for a sensor uses every other day only.
- Reserved confirmation data: E11F byte ranges remain untouched.
- E11E has already informed this design, so all E11G findings remain adaptive development evidence.

## Fixed Baseline and Expert

- Safety baseline: unstratified local IDW, `k=3`, power `p=2`.
- Role expert: same-role local IDW, `k=5`, power `p=2`.

## Candidate Grid

Let `b` be the baseline prediction, `r` the role-expert prediction, and `d=r-b`.

- Alpha: `{0.50, 0.75, 1.00}`.
- Disagreement threshold in degrees Celsius: `{0.25, 0.50, 1.00, 1.50, 2.00}`.
- Clipped family: `b + alpha * clip(d, -threshold, threshold)`.
- Fallback family: use `b + alpha*d` only when `abs(d) <= threshold`; otherwise use `b`.
- Total fixed candidates: 30.

## Fold-Internal Sensor Selection

A candidate is eligible for one sensor only when, on training days:

- MAE improves over baseline by at least 0.02 degrees Celsius.
- RMSE improves by at least 0.02 degrees Celsius.
- P95 absolute error improves by at least 0.02 degrees Celsius.
- Daily MAE is lower on at least 60% of training days, rounded upward.

Among eligible candidates, select lowest P95, then MAE, RMSE, and model ID. If none qualify, use the baseline. Apply the frozen choice to the held-out day.

## Advancement Gate

The out-of-fold model passes only if all conditions hold:

- MAE, RMSE, and P95 are each strictly lower than baseline.
- At least 26 of 42 sensors have lower out-of-fold MAE.
- The 95% day-block bootstrap lower bound for baseline-minus-model MAE is above zero.
- Absolute MAE is at most 1.25 degrees Celsius, RMSE at most 1.90, and P95 at most 4.00.

Bootstrap settings are 20,000 replicates with seed `20260823`. A failed gate yields `no_candidate_forwarded`; E11F must not be accessed.

