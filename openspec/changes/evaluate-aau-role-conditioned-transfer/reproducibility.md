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

For byte-for-byte reruns, volatile generation/retrieval timestamps are excluded from content identities. E11C uses stable hash `3c6ca841e100358669be193390947d94bce7096ca83da71a2e6b8b90736cd643`; the E11D manifest uses `c72925e6c15afa594a48b8dfef506eb3017bbd5c99259799b1975930fce75064`. Historical full-file hashes remain recorded separately.

## Determinism

The prediction rules contain no fitted parameters. Bootstrap resampling uses 20,000 replicates and seed `20260823`. The manifest records HTTP headers, fragment hashes, byte counts, timestamps, and boundary policy.
