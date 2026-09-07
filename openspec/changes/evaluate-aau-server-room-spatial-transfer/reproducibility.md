# Reproducibility

## Fixed Inputs

- Zenodo record: `19398358`, version v4.
- File size: 706,160,545 bytes.
- File checksum: MD5 `fdb84fef0733db5a0a9564e028725494`.
- Range count: 12.
- Range size: 4,194,304 bytes.
- Aggregation: one-minute median.
- Included sensors: 42; excluded cooling sensors: 6.
- IDW power: 2; epsilon: `1e-12`.

## Planned Commands

```bash
python3 scripts/download_aau_temperature_ranges.py
python3 scripts/run_aau_spatial_baseline.py
python3 scripts/validate_room_design.py docs/templates/room_design_aau_server_room.json
```

## Planned Outputs

- `outputs/data/enclosure/aau_temperature_ranges_manifest.json`
- `outputs/data/enclosure/aau_spatial_baseline.json`

## Provenance Requirements

The result SHALL record the retrieval URL, source DOI, source size/checksum, byte offsets, local fragment checksums, project revision when available, runtime parameters, timestamp range, and all exclusions.
