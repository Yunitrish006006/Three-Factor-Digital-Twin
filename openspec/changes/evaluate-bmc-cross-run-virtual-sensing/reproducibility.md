# E12 Reproducibility

## Required Artifacts

- Downloader with the frozen 31-file split.
- Manifest containing source URL, split, bytes, and SHA-256 for each complete file.
- Standard-library parser, candidate-selection code, frozen model record, and deterministic evaluator.
- Machine-readable result JSON containing all candidates, gates, null results, and limitations.
- Unit tests for Influx metadata parsing, split disjointness, ridge fitting, and frozen test evaluation.

## Environment

The implementation SHALL use Python standard-library modules only. All random resampling SHALL use seed `20260824`. Raw source files SHALL not be silently repaired or imputed.

## Source Limitation

The upstream branch URL is mutable. Reproducibility therefore depends on the frozen per-file SHA-256 manifest; a later byte mismatch SHALL fail closed rather than replace the expected digest.
