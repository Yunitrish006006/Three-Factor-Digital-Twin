# Reproducibility

## Commands

```bash
python3 scripts/download_aau_temperature_ranges_e11h.py --check-overlaps
# Download the printed fixed ranges with curl into the declared /tmp directory.
python3 scripts/download_aau_temperature_ranges_e11h.py --from-existing-curl
python3 scripts/run_aau_commissioning_development.py
python3 -m unittest tests.test_aau_commissioning
python3 scripts/validate_research_openspec.py
```

## Frozen Inputs

- All prior enclosure manifests for overlap detection.
- E11C sensor metadata hash `0b667ca8bb959e332aeff0155b9dceb1318dca3f91a26c1aa5552fb6bfef7055`.
- The rerun-stable content identity of E11H's 42 selected models is `dd7947f8cdac872a6447282c232a1b8d7a827d38752c23a18f7c38f9bd7bc2af`; full-file hashes remain historical run identifiers because the JSON includes timestamps and regenerated input-container hashes.
- E11G result hash `aef099fea6b37036fd32644f4897e2aea5e47922d525f072b7b01592928466ed`.

## Determinism

Range starts, chronological partition, candidate grid, Huber iterations, tie breaking, metric thresholds, and bootstrap seed are fixed before download.
