# E12 Reproducibility

## Required Artifacts

- Downloader with the frozen 31-file split.
- Manifest containing source URL, split, bytes, and SHA-256 for each complete file.
- Standard-library parser, candidate-selection code, frozen model record, and deterministic evaluator.
- Machine-readable result JSON containing all candidates, gates, null results, and limitations.
- A development data-quality failure SHALL still write structured result JSON, record `final_test_opened: false`, and exit nonzero.
- Unit tests for Influx metadata parsing, split disjointness, ridge fitting, and frozen test evaluation.

## Environment

The implementation SHALL use Python standard-library modules only. All random resampling SHALL use seed `20260824`. Raw source files SHALL not be silently repaired or imputed.

## Source Limitation

The upstream branch URL is mutable. Reproducibility therefore depends on the frozen per-file SHA-256 manifest; a later byte mismatch SHALL fail closed rather than replace the expected digest.

To reconstruct the registered manifest byte-for-byte, use the original retrieval date:

```bash
python3 scripts/download_bmc_cross_run_e12.py --retrieval-date 2026-08-24
```
