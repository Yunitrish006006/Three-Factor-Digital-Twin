# Design

## Data Flow

`normalized SML2010 -> target/profile noise stream -> one shared corrupted series -> raw / causal MA(3) / scalar KF -> same test-row metrics -> JSON -> thesis/report/demo`

## Implementation Decisions

1. Keep the experiment dependency-free and separate from the primary spatial estimator.
2. Use a scalar random-walk filter per metric so state, transition, observation, `Q`, and `R` are inspectable.
3. Derive `Q` from training reference differences and fix `R` from registered injection variance.
4. Reset at time gaps so a long missing interval is not treated as one 15-minute transition.
5. Hash timestamps and corrupted values once per case; every method records the same hashes rather than constructing independent inputs.
6. Preserve per-case diagnostics and non-Kalman winners.

## Demo Design

The offline professor page has four bounded sections:

1. previous versus improved field/sparse-calibration performance;
2. RNN same-data negative result;
3. Kalman controlled filtering results and adverse cases;
4. live system demonstration instructions for 3-D field query and recommendation ranking.

The page is a presentation artifact, not a new experiment. Values are loaded at build time from canonical JSON and embedded with provenance labels.

## Compatibility

No primary estimator API changes. The Kalman module lives under `digital_twin/evaluation/`; runners remain in `scripts/`. Existing RNN, public benchmark, thesis, and Web demo behavior remain compatible.

## Requirement Mapping

| Requirement | Design response |
| --- | --- |
| `EVD-017` | shared corrupted series, hashes, split, metrics, adverse-case preservation |
| `HRL-010` | Kalman stays an evaluation comparator, not a silent primary-model replacement |
| `SYN-009` | offline evidence demo plus live service guide, both labeled by evidence status |
