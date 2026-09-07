# Reproducibility

## Environment

- Python 3.9+ standard library.
- Repository root: `/Volumes/DataExtended/school` in the current workspace; commands use repository-relative paths.
- No network download is required when normalized SML2010 inputs already exist.

## Inputs

- `outputs/data/normalized_public/sml2010/corner_sensor_timeseries.csv`
- `outputs/data/normalized_public/sml2010/outdoor_environment.csv`
- `outputs/data/normalized_public/sml2010/auxiliary_features.csv`

## Clean-Room Run Order

```bash
python3 scripts/validate_research_openspec.py
python3 scripts/run_rnn_public_comparison.py
python3 scripts/run_kalman_filter_comparison.py
python3 scripts/build_professor_demo.py
python3 scripts/verify_thesis_results.py
python3 -m unittest discover -s tests
```

After synchronized source edits:

```bash
python3 scripts/build_architecture_diagrams.py
python3 scripts/build_thesis_docx.py
python3 scripts/build_thesis_pdf.py
python3 scripts/build_thesis_pptx.py
cd docs/papers/ieee && tectonic --keep-logs --keep-intermediates paper.tex
```

## Fixed Parameters

- Seed: 42 with deterministic target/profile offsets.
- Split: chronological 70/30.
- Moving-average window: 3.
- Kalman model: scalar random walk, identity observation.
- Noise profiles: low/nominal/high values in `research.md`.

## Verification

- All expected target/profile cases are present.
- All methods share the same timestamp and corrupted-observation hashes.
- All metrics and diagnostics are finite.
- Demo contains the current evidence timestamp/status and no missing placeholder.
- OpenSpec validator, thesis result verifier, unit tests, `git diff --check`, and stale-text searches pass.
