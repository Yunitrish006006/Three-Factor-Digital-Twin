# Reproducibility Manifest

## Environment

- OS: macOS-compatible Python environment
- Python: 3.9+
- Dependencies: Python standard library plus current repository modules
- Hardware assumptions: CPU only
- Timezone and locale: output timestamp in UTC; ordering from parsed dataset timestamps

## Inputs and Provenance

| Input | Source / license | Version / checksum | Committed? |
| --- | --- | --- | --- |
| `outputs/data/normalized_public/sml2010/*.csv` | SML2010, existing repository provenance | record hash in evidence | yes |
| `outputs/data/hybrid_residual_checkpoint.json` | project experiment output | record hash in evidence | yes |
| Oh et al. (2024) PDF | local literature copy; copyrighted article | DOI `10.1016/j.enbuild.2024.114898` | no |

## Determinism

- Random seeds: none; deterministic ridge solution
- Data split: chronological `70/30`
- Ordering: timestamp ascending
- Known nondeterminism: output creation timestamp only

## Clean-Room Execution Order

```bash
# Run from repository root.
python3 scripts/run_oh2024_inspired_comparison.py
python3 scripts/verify_thesis_results.py
python3 scripts/validate_research_openspec.py
python3 -m unittest discover -s tests
```

## Expected Outputs

| Output | Producer | Required keys / invariants |
| --- | --- | --- |
| `outputs/data/public_benchmarks/oh2024_inspired_sml2010_comparison.json` | `scripts/run_oh2024_inspired_comparison.py` | method fidelity, horizons 15/60/1440, two targets, five comparators, common split, decisions |

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
