# Reproducibility

## Environment

- Python 3.9+
- NumPy 1.26-compatible API
- No PyTorch, TensorFlow, JAX, GPU, or downloaded model weights

## Commands

```bash
python3 scripts/validate_research_openspec.py
python3 -m unittest tests.test_gru_lstm_public_comparison
python3 scripts/run_gru_lstm_public_comparison.py
```

## Evidence order

1. Validate this preregistration.
2. Run focused synthetic implementation tests.
3. Execute the full SML2010 comparison once.
4. Hash the result and populate `evidence.md` from actual output.
5. Update canonical capabilities and every synchronized artifact.

The existing normalized input hashes and the new result hash must be retained.
