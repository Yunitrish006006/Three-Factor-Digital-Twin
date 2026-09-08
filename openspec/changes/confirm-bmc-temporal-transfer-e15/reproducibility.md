# Reproducibility

## Acquire data

```bash
python3 scripts/download_bmc_confirmation_e15.py
```

This creates `outputs/data/enclosure/bmc_confirmation_e15_manifest.json` and
stores raw files under `outputs/data/enclosure/bmc_confirmation_e15/raw/`.

## Execute once

```bash
python3 scripts/execute_bmc_confirmation_e15.py
```

The result is `outputs/data/enclosure/bmc_confirmation_e15_result.json`.
The runner refuses to overwrite an existing result. Record SHA-256 hashes for
the manifest, canonical `frozen_models` content, full model container, and result in post-run evidence.
The wrapper also refuses a second attempt after failure or interruption and
preserves `bmc_confirmation_e15_attempt.json` and `bmc_confirmation_e15_execution.log`.

## Validation

```bash
python3 scripts/validate_research_openspec.py
python3 -m unittest tests.test_bmc_confirmation_e15
```
