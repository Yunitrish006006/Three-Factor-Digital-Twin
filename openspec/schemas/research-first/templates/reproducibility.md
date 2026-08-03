# Reproducibility Manifest

## Environment

- OS:
- Python:
- Dependencies:
- Hardware assumptions:
- Timezone and locale:

## Inputs and Provenance

| Input | Source / license | Version / checksum | Committed? |
| --- | --- | --- | --- |
| <!-- --> | <!-- --> | <!-- --> | yes / no |

## Determinism

- Random seeds:
- Data split:
- Ordering:
- Known nondeterminism:

## Clean-Room Execution Order

```bash
# Run from repository root.
python3 ...
```

## Expected Outputs

| Output | Producer | Required keys / invariants |
| --- | --- | --- |
| `outputs/...` | `scripts/...` | <!-- --> |

## Verification

```bash
python3 -m unittest discover -s tests
python3 scripts/verify_thesis_results.py
python3 scripts/validate_research_openspec.py
```

## Provenance Record

Record in `evidence.md`:

- commit hash and dirty-worktree status;
- execution timestamp and timezone;
- exact commands and arguments;
- input versions or checksums;
- output paths and relevant hashes;
- deviations, warnings, and failures.
