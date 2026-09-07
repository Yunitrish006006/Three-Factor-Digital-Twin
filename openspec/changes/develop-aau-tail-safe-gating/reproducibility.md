# Reproducibility

## Inputs

- `outputs/data/enclosure/aau_temperature_ranges_e11e_manifest.json`
- `/tmp/aau_server_room_temperature_ranges_e11e/*.csv.part`
- Frozen E11C sensor metadata referenced by the E11E runner

## Commands

```bash
python3 scripts/run_aau_tail_safe_development.py
python3 scripts/verify_e11g_results.py
python3 -m unittest tests.test_aau_tail_safe
python3 scripts/validate_research_openspec.py
```

## Determinism

Candidate order, metric tie breaking, day folds, and bootstrap seed are fixed. The output records the input hashes, selected model counts, per-sensor deployment map, all gates, and E11F access state.

