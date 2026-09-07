# Reproducibility

## Commands

```bash
python3 scripts/download_aau_temperature_ranges_e11f.py --check-overlaps
# Download the printed fixed ranges once with curl.
python3 scripts/download_aau_temperature_ranges_e11f.py --from-existing-curl
python3 scripts/run_aau_commissioning_confirmation.py
python3 scripts/validate_research_openspec.py
```

Reproduction runs verify the timestamp-independent canonical content of the 42 frozen `selected_models` entries. The historical full E11H result hash remains recorded, but volatile timestamps and regenerated container hashes do not block a semantic rerun.

## Frozen Outputs

The manifest records exact fragment sizes, paths, byte ranges, content ranges, and SHA-256 values. The result records the manifest, E11H, E11G, and metadata hashes plus every gate and calendar-overlap diagnostic.
