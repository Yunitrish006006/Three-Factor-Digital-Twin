# E13 Reproducibility

- Python standard library only.
- Exact E12 manifest hash required.
- Minimum valid rows fixed at 10.
- Bootstrap seed fixed at `20260824` with 10,000 samples.
- Frozen-model JSON SHALL exist and be hashed before test-file parsing.
- A data-availability failure SHALL produce structured JSON rather than only a traceback.
