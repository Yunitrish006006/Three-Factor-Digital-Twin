# Reproducibility Manifest

## Current Change

This change contains no new empirical run. Reproducibility means that every synchronized artifact carries the same four future directions, roles, boundaries, and `NOT_EVALUATED` status.

## Validation

```bash
python3 scripts/validate_research_openspec.py
python3 scripts/verify_thesis_results.py
python3 -m unittest discover -s tests
python3 scripts/build_thesis_docx.py
python3 scripts/build_thesis_pdf.py
python3 scripts/build_thesis_pptx.py
cd docs/papers/ieee && tectonic --keep-logs --keep-intermediates paper.tex
```

## Future Experiment Requirements

- Record dataset/testbed version, configuration hash, seeds, hardware/runtime, split or episode IDs, and exact comparator parity.
- Preserve null, failed, adverse, and out-of-domain results.
- Do not create the reserved future evidence files until real runs occur.
