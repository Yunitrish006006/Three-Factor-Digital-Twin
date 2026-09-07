# Reproducibility

## Inputs

- Public AAU v4 URL and DOI recorded in the manifest.
- Frozen offsets and byte length recorded in `protocol.md` and downloader source.
- Frozen E11C role-metadata artifact identified by SHA-256.

## Commands

```bash
python3 scripts/download_aau_temperature_ranges_e11d.py
python3 scripts/run_aau_role_confirmation.py
python3 scripts/verify_e11d_results.py
```

## Determinism

The prediction rules contain no fitted parameters. Bootstrap resampling uses 20,000 replicates and seed `20260823`. The manifest records HTTP headers, fragment hashes, byte counts, timestamps, and boundary policy.

