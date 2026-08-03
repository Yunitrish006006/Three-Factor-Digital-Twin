# Reproducibility Manifest

## Environment

- OS: current repository build environment.
- Python: repository-supported Python 3.9+.
- Dependencies: existing thesis, LaTeX, DOCX, PPTX, Poppler, and LibreOffice toolchain.
- Hardware assumptions: none beyond current build scripts.
- Timezone and locale: Asia/Taipei; UTF-8.

## Inputs and Provenance

| Input | Source / license | Version / checksum | Committed? |
| --- | --- | --- | --- |
| Oh, Sfarra, and Kim article PDF | user-provided scholarly article; citation-only use | Energy and Buildings 324 (2024) 114898; DOI `10.1016/j.enbuild.2024.114898` | no |
| screenshot formula | user-provided excerpt | `ŷ_hybrid(t+h)=ŷ_phys(t+h)+ê(t+h)` | no |
| thesis/IEEE/presentation sources | repository | current worktree | yes |

## Determinism

- Random seeds: unchanged; no new experiment.
- Data split: unchanged.
- Ordering: build sources first, then generated outputs, then render QA.
- Known nondeterminism: DOCX/PPTX metadata timestamps and LaTeX auxiliary files.

## Clean-Room Execution Order

```bash
# Run from repository root.
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
| `docs/papers/thesis/thesis_draft_zh.docx` | `build_thesis_docx.py` | DOI and timing explanation present |
| `docs/papers/thesis/thesis_draft_zh.pdf` | `build_thesis_pdf.py` | readable reference and formula section |
| `outputs/papers/thesis_presentation_zh*.pptx` | `build_thesis_pptx.py` | formula slide defines `h`, `I_t`, and `h=0` |
| `docs/papers/ieee/paper.pdf` | Tectonic | citation resolves and page count remains within target |

## Verification

```bash
python3 -m unittest discover -s tests
python3 scripts/verify_thesis_results.py
python3 scripts/validate_research_openspec.py
```

## Provenance Record

Record in `evidence.md`:

- dirty-worktree status and execution timestamp;
- exact build and verification commands;
- output paths and page/slide counts;
- visual-QA result and warnings;
- citation and leakage-boundary search results.
