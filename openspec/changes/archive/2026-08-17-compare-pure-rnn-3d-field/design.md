# Design

## Data Flow

`canonical scenario -> synthetic dense truth -> same eight sparse observations -> IDW / base / pure RNN / LOO hybrid -> same held-out grid MAE -> JSON -> figures and synchronized artifacts`

## Pure RNN Flow

For one query point, eight sensor tokens are ordered by the scenario's canonical input-sensor list. Each token combines its sensor coordinates and three observed metrics with repeated query/scenario context. A vanilla Elman hidden state consumes all eight tokens and a linear head predicts the three current field values directly. Training targets are dense truth, not residuals.

## Leakage Prevention

1. Build the eight scenario folds before fitting.
2. Fit preprocessing and RNN parameters using only seven training scenarios.
3. Never pass physics estimates, residuals, IDW predictions, or held-out truth into the pure RNN input.
4. Hash the held-out sparse observation payload and query grid once per fold.
5. Evaluate all methods against the same immutable truth field and metric function.

## Compatibility

The pure RNN lives under `digital_twin/evaluation/` and is not added to the production estimator toggle. Existing service behavior remains base/hybrid. The new runner writes separate evidence and may be included in the canonical experiment orchestrator after validation.

## Requirement Mapping

| Requirement | Design response |
| --- | --- |
| `EVD-018` | eight LOO folds, same sparse inputs/grid/truth, four-method metrics and hashes |
| `HRL-011` | pure RNN stays a baseline and receives no physics/residual inputs |
| `SYN-010` | report, demo, thesis, IEEE paper, slides, and field-comparison figure use the same JSON |
