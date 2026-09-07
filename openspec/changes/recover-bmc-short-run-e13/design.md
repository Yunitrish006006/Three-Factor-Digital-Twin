# E13 Design

E13 uses `select_and_refit` and `evaluate_frozen` as separate APIs. The first API has no test argument. The runner persists development decisions, baseline parameters, ridge scaling, coefficients, and final-test filenames before calling the second API.

The 10-row threshold is an availability guard, not an accuracy target. Short runs remain complete files and retain equal status in run-level wins and bootstrap resampling even when they contribute fewer rows to pooled metrics.
