# Reproducibility

## Environment
- Python >= 3.9
- no new third-party dependency

## Clean-room Rerun
```bash
python3 -m unittest tests/test_research_orchestration.py -v
python3 scripts/research_orchestration.py example-task
python3 scripts/validate_research_openspec.py
python3 -m unittest discover -s tests
```

## Determinism
- no random seeds required;
- scoring weights/thresholds are committed in code;
- regression fixtures use fixed structured inputs;
- paper dedup uses normalized DOI first, title/year fallback.

## Provenance to Record
- branch and commit SHA;
- Python version;
- commands, stdout/stderr, exit codes;
- deviations from registered thresholds or fixtures.
