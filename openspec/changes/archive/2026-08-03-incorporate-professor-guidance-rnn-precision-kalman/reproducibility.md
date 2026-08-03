# Reproducibility Manifest

## Environment

- Python 3.9+.
- Standard library and current repository modules only; no NumPy, PyTorch, or TensorFlow requirement.
- CPU execution.
- Fixed RNN seed `42`.

## Inputs and Provenance

| Input | Source | Use |
| --- | --- | --- |
| `outputs/data/normalized_public/sml2010/*.csv` | existing SML2010 normalization/provenance | all RNN comparators |
| `outputs/data/hybrid_residual_checkpoint.json` | project synthetic output | explicitly not loaded for primary parity ranking |
| primary literature DOIs in `research.md` | publisher/repository pages | application and Kalman direction only |

## Determinism

- Chronological ordering; no shuffling.
- Fixed architecture, seed, optimizer, epochs, batch size, and learning rate.
- Train-only feature and target standardization.
- Same endpoint index and split for every comparator.
- Known nondeterminism is limited to output creation timestamps.

## Clean-Room Execution Order

```bash
python3 scripts/run_rnn_public_comparison.py
python3 scripts/verify_thesis_results.py
python3 -m unittest discover -s tests
python3 scripts/validate_research_openspec.py
python3 scripts/build_architecture_diagrams.py
python3 scripts/build_thesis_docx.py
python3 scripts/build_thesis_pdf.py
python3 scripts/build_thesis_pptx.py
cd docs/papers/ieee && tectonic --keep-logs --keep-intermediates paper.tex
```

## Expected Outputs

| Output | Required invariants |
| --- | --- |
| `outputs/data/public_benchmarks/rnn_sml2010_comparison.json` | 3 horizons, 4 targets, 4 comparators, endpoint-parity audit, fixed RNN config |
| `docs/research/professor_guidance_application_scope_zh.md` | `20–30 °C` boundary and missing-variable matrix |
| `docs/models/kalman_filter_research_direction_zh.md` | positive and adverse literature plus future same-data protocol |

## Evidence Record

Record commands, input/output checksums, endpoint hashes/counts, RNN configuration, every case metric, all losses, literature decisions, range exclusions, tests, builds, visual QA, and claim decisions in `evidence.md`.
