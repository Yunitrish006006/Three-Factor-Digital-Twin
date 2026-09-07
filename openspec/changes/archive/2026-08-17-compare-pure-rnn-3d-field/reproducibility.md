# Reproducibility

## Environment

- Python 3.9+ standard library.
- No network or external ML package is required.
- Repository-generated canonical scenarios are deterministic.

## Clean-Room Run Order

```bash
python3 scripts/validate_research_openspec.py
python3 scripts/run_rnn_3d_field_comparison.py
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

- Eight canonical scenarios and eight LOO folds.
- 96 deterministic training points per training scenario; 1,152 test points per held-out field.
- Sensor sequence length 8, hidden units 8, epochs 40, batch size 32, learning rate 0.01, clip 1.0.
- Base seed 42 with fold offset 97.
- Training-only standardization with `1e-6` scale floor.

## Verification

- Every fold contains the same four methods and three finite field MAEs.
- Fold names, training scenarios, sparse-input hashes, query-grid hashes, and sample counts are complete.
- RNN inputs contain no physics estimate or truth feature.
- Professor and thesis artifacts preserve the synthetic full-field boundary and pure RNN result even when adverse.
- OpenSpec validator, result verifier, tests, stale-text searches, and `git diff --check` pass.
