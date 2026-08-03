# Reproducibility Manifest

## Environment

- Python: repository-supported Python 3.9+.
- Runtime dependencies: Python standard library and repository modules only.
- Locale: UTF-8.

## Inputs

| Input | Role | Current status |
| --- | --- | --- |
| `docs/templates/e8_intervention_trials_template.json` | default E8 dataset | zero trials |
| `docs/requirements/e8_intervention_trial_schema.json` | field contract | version 1.0.0 |
| temporary synthetic unit-test fixtures | formula validation only | not evidence |

## Determinism

The analyzer contains no stochastic estimation. Records are sorted by
`trial_id`, blocks by `block_id`, and JSON keys are emitted deterministically.

## Commands

```bash
python3 scripts/analyze_e8_intervention_trials.py
python3 -m unittest tests.test_intervention_evaluation
python3 -m unittest discover -s tests
python3 scripts/verify_thesis_results.py
python3 scripts/validate_research_openspec.py
```

## Expected Current Result

- summary status: `NOT_EVALUATED`
- completed real trials: `0`
- efficacy estimates: null
- E8 manuscript claim: protocol and execution kit ready, efficacy unverified

