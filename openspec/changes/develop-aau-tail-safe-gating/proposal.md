# Proposal: Develop AAU Tail-Safe Gating

## Why

E11E reduced mean error but worsened P95 error and improved only 25 of 42 sensors. The next development step must target this tail-risk failure without relaxing the advancement gate or accessing E11F.

## What Changes

- Reuse E11E strictly as adaptive development data.
- Compare clipped corrections and high-disagreement fallback rules around the local-IDW safety baseline.
- Select rules per sensor inside leave-one-day-out folds only.
- Advance nothing unless out-of-fold aggregate, tail, coverage, and bootstrap gates all pass.

## Scope

This is a predictive development study, not enclosure deployment, airflow causality, or external confirmation.

