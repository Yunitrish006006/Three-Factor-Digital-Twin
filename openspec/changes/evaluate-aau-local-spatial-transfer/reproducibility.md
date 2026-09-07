# Reproducibility

## Fixed Inputs

- Room design: `docs/templates/room_design_aau_server_room.json`.
- Discovery manifest retained for overlap checks: `outputs/data/enclosure/aau_temperature_ranges_manifest.json`.
- Confirmation manifest: `outputs/data/enclosure/aau_temperature_ranges_e11c_manifest.json`.
- Raw confirmation directory: `/tmp/aau_server_room_temperature_ranges_e11c`.
- Seed: `20260823`; bootstrap replicates: `20000`.

## Commands

```bash
python3 scripts/download_aau_temperature_ranges_e11c.py
python3 scripts/run_aau_local_idw_confirmation.py
python3 -m unittest tests.test_aau_local
python3 scripts/validate_research_openspec.py
```

## Expected Machine-Readable Output

- `outputs/data/enclosure/aau_local_idw_confirmation.json`.
- Expected fields describe schema and provenance only; no expected metric or decision is preregistered as evidence.

## Clean-Room Order

1. Validate OpenSpec and room design.
2. Confirm the committed offsets and E11B non-overlap assertion.
3. Retrieve all confirmation fragments.
4. Execute one fixed evaluation and preserve its output even if adverse.
5. Populate `evidence.md` only from the actual output.
