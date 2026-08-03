# Reproducibility Manifest

## Environment

- Python: repository-supported Python 3.9+.
- Dependencies: Python standard library for bootstrap analysis; existing DOCX/PDF/PPTX/LaTeX build toolchain.
- Timezone and locale: Asia/Taipei; UTF-8.

## Inputs and Provenance

| Input | Source / license | Version / checksum | Committed? |
| --- | --- | --- | --- |
| bedroom room design | repository user-supplied research data | current worktree | yes |
| weekly room and sensor snapshots | repository user-supplied research data | 2026-04-14 through 2026-04-20 | yes |
| thesis/IEEE/presentation sources | repository | current worktree | yes |

## Determinism

- Seed: 20260726.
- Replicates: 20,000.
- Block: `date`.
- Percentiles: 2.5 and 97.5 with deterministic linear interpolation.
- Known nondeterminism: generated document metadata timestamps only.

## Clean-Room Execution Order

```bash
python3 scripts/run_bedroom_weekly_simulation.py
python3 scripts/verify_thesis_results.py
python3 scripts/build_thesis_docx.py
python3 scripts/build_thesis_pdf.py
python3 scripts/build_thesis_pptx.py
cd docs/papers/ieee && tectonic --keep-logs --keep-intermediates paper.tex
python3 -m unittest discover -s tests
python3 scripts/verify_thesis_results.py
python3 scripts/validate_research_openspec.py
```

## Expected Outputs

| Output | Producer | Required keys / invariants |
| --- | --- | --- |
| `outputs/data/bedroom_01_weekly/weekly_simulation_summary.json` | weekly simulation | method, date block, 20,000 replicates, seed, per-metric CIs |
| `outputs/data/thesis_result_verification_report.json` | verifier | new E7 uncertainty rows PASS |
| synchronized thesis/PDF/PPTX/IEEE outputs | build scripts | identical bounded metrics and wording |

## Provenance Record

Record commands, seed, replicate count, output values, test counts, visual QA, page/slide counts, warnings, and claim decisions in `evidence.md`.
