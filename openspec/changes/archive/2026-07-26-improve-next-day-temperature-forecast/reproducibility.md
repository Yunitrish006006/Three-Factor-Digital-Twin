# Reproducibility Plan

## Environment

- Python standard library and existing repository modules only
- No network download or new dependency
- Deterministic chronological ordering
- Fixed bootstrap seed `20260726`

## Inputs

- `outputs/data/normalized_public/sml2010/corner_sensor_timeseries.csv`
- `outputs/data/normalized_public/sml2010/outdoor_environment.csv`
- `outputs/data/normalized_public/sml2010/auxiliary_features.csv`
- `outputs/data/hybrid_residual_checkpoint.json`

Every input SHA-256 SHALL be written to the result.

## Reproduction

```text
python3 scripts/run_next_day_temperature_comparison.py
python3 scripts/verify_thesis_results.py
python3 -m unittest discover -s tests
```

## Expected Boundary

The output reproduces only the repository's registered SML2010 follow-up
experiment. It does not reproduce the confidential data or deep architecture
from Oh et al. and does not establish cross-building performance.
