# Reproducibility Manifest

## Environment

- OS: macOS or Linux with repository-supported Python tools.
- Python: 3.9+.
- Dependencies: repository package plus document-builder dependencies when rebuilding artifacts.
- Hardware assumptions: no physical node is required for controlled simulation; real validation requires role-labelled nodes.
- Timezone and locale: record actual run timezone; professor-facing documents use Traditional Chinese.

## Inputs and Provenance

| Input | Source / license | Version / checksum | Committed? |
| --- | --- | --- | --- |
| canonical validation scenarios | repository code | Git commit | yes |
| room and sensor roles | repository scenario/layout | Git commit | yes |
| real bedroom measurements | user-collected | record file hash when available | local/controlled |
| public datasets | disclosed original provider | dataset archive/hash | no, local-only |

## Determinism

- Random seeds: controlled runner uses deterministic inputs/noise behavior; any future stochastic estimator records its seed.
- Data split: explicit input/validation roles and chronological dates.
- Ordering: scenario and target identifiers are retained in output.
- Known nondeterminism: document rendering fonts and hardware sensor noise; neither changes the evidence class.

## Clean-Room Execution Order

```bash
python3 scripts/run_target_holdout_validation.py
python3 -m unittest discover -s tests
python3 scripts/verify_thesis_results.py
python3 scripts/validate_research_openspec.py
```

Rebuild synchronized artifacts only after the active change actually modifies a thesis claim or registered result.

## Expected Outputs

| Output | Producer | Required keys / invariants |
| --- | --- | --- |
| `outputs/data/target_holdout_validation_summary.json` | `run_target_holdout_validation.py` | `evidence_scope`, scenarios, leakage result |
| `outputs/data/thesis_result_verification_report.json` | `verify_thesis_results.py` | PASS/FAIL/MISSING records |

## Verification

```bash
python3 -m unittest discover -s tests
python3 scripts/verify_thesis_results.py
python3 scripts/validate_research_openspec.py
```

## Provenance Record

Future `evidence.md` SHALL record commit hash, dirty status, timestamp/timezone, exact commands, input hashes, output paths, warnings, deviations, failures and claim decisions. It SHALL not be created from this planning manifest alone.
