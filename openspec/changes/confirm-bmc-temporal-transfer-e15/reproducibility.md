# Reproducibility

## Acquire data

```bash
python3 scripts/download_bmc_confirmation_e15.py
```

This creates `outputs/data/enclosure/bmc_confirmation_e15_manifest.json` and
stores raw files under `outputs/data/enclosure/bmc_confirmation_e15/raw/`.

## Execute once

```bash
python3 scripts/run_bmc_confirmation_e15.py
```

The result is `outputs/data/enclosure/bmc_confirmation_e15_result.json`.
The runner refuses to overwrite an existing result. Record SHA-256 hashes for
the manifest, frozen model, and result in post-run evidence.

## Validation

```bash
python3 scripts/validate_research_openspec.py
python3 -m unittest tests.test_bmc_confirmation_e15
```
