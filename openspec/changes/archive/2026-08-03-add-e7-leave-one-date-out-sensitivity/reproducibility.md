# Reproducibility Manifest

## Environment and Inputs

- Python 3.9+; standard library only for the new calculation.
- Input room and snapshots: existing committed bedroom_01 files covering 2026-04-14 through 2026-04-20.
- Random seed: not applicable; analysis is deterministic.

## Clean-Room Execution Order

```bash
python3 scripts/run_bedroom_weekly_simulation.py
python3 -m unittest discover -s tests
python3 scripts/verify_thesis_results.py
python3 scripts/build_architecture_diagrams.py
python3 scripts/build_thesis_docx.py
python3 scripts/build_thesis_pdf.py
python3 scripts/build_thesis_pptx.py
cd docs/papers/ieee && tectonic --keep-logs --keep-intermediates paper.tex
python3 scripts/validate_research_openspec.py
```

## Expected Outputs

| Output | Required invariant |
| --- | --- |
| `outputs/data/bedroom_01_weekly/weekly_simulation_summary.json` | 7 sorted folds and per-metric extrema |
| result verification report | all registered values PASS or explicit failure |
| synchronized research artifacts | same result, decision, and boundary |

## Evidence Record

Record exact fold results, hypothesis and claim decisions, commands, test counts, build outcomes, layout checks, warnings, and checksums in `evidence.md` after execution.
