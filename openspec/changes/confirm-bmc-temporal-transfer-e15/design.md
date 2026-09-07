# Design

The downloader stores immutable per-file hashes even though the upstream raw
URLs use a mutable branch. The evaluator verifies the exact filename set,
manifest hashes, and frozen-model hash before parsing any confirmation row.

Metrics are calculated both over all rows and as equal-weighted run means.
The bootstrap resamples complete runs rather than individual timestamps to
avoid treating serially correlated samples as independent. A deterministic
seed (`20260824`) makes the interval reproducible.

The decision is conjunctive: a good average cannot override a failed data
integrity, tail-error, run-win, uncertainty, or plausibility gate.
