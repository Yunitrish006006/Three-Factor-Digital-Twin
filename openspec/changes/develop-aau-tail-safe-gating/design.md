# Design

## Architecture

The method wraps two deterministic spatial predictors with a low-cost decision layer. It requires no neural-network training and preserves a direct fallback to local IDW, matching sparse IoT compute constraints.

## Tail-Risk Control

Clipping limits the maximum role-based correction. Fallback rejects role corrections when expert disagreement is large. Per-sensor selection acknowledges that enclosure transfer quality is spatially heterogeneous.

## Leakage Control

Hyperparameters and sensor acceptance are recomputed within each training fold. Held-out-day labels are used only after the fold choice is frozen. The deployment map is fit only after out-of-fold evaluation and is not evaluated on E11E as if independent.

