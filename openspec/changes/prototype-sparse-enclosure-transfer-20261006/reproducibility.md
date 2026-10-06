# Reproducibility

Python 3.11, numpy 1.26.4, scipy 1.14.1 from existing `.venv-mpc`; dependencies will be snapshotted. Run from thesis root:

```sh
.venv-mpc/bin/python -m unittest tests.test_sparse_enclosure
.venv-mpc/bin/python scripts/run_sparse_enclosure.py
.venv-mpc/bin/python scripts/verify_sparse_enclosure.py
.venv/bin/python scripts/validate_research_openspec.py
.venv/bin/python scripts/build_sparse_enclosure_report.py
```

Runner refuses to overwrite existing result/freeze. Config, sparse calibration traces, source snapshots/hash manifest and all evaluation CSVs are versioned under this change; no dataset downloads or E15 execution. Checkpoint before results, freeze before evaluation. Rebuild sources/outputs using existing build_thesis_docx/pdf/pptx and tectonic per AGENTS, checking copies and scientific claims. Record exact commands, environment and failures in evidence.md after runs. Full unit discovery uses `.venv-mpc` with numpy/scipy/osqp; document missing ancillary dependencies if any.
