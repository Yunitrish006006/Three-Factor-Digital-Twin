# Reproducibility Manifest

## Environment

- OS: current macOS workspace
- Python: repository-supported Python 3.9+
- Dependencies: existing thesis, presentation, SVG, Tectonic, LibreOffice and Poppler toolchain
- Hardware assumptions: none beyond current build scripts
- Timezone and locale: Asia/Taipei; UTF-8

## Inputs and Provenance

| Input | Source / license | Version / checksum | Committed? |
| --- | --- | --- | --- |
| RQ and claim registry | `openspec/specs/research-governance/spec.md` | current worktree | yes |
| E1--E9 registry | `openspec/specs/evaluation-and-evidence/spec.md` | current worktree | yes |
| thesis narrative | `docs/thesis/thesis_draft_zh.md` | current worktree | yes |
| existing diagrams | `docs/thesis/system_architecture_diagrams_zh.md` | current worktree | yes |

## Determinism

- Random seeds: not applicable
- Data split: not applicable
- Ordering: fixed problem → RQ → method → evidence → claims
- Known nondeterminism: document pagination and renderer font substitution

## Clean-Room Execution Order

```bash
python3 scripts/build_architecture_diagrams.py
python3 scripts/build_thesis_docx.py
python3 scripts/build_thesis_pdf.py
python3 scripts/build_thesis_pptx.py
cd docs/papers/ieee
tectonic --keep-logs --keep-intermediates paper.tex
```

## Expected Outputs

| Output | Producer | Required keys / invariants |
| --- | --- | --- |
| `outputs/figures/architecture/研究整體邏輯架構.svg` | architecture builder | valid 1600×900 SVG |
| thesis DOCX/PDF outputs | thesis builders | overview visible and caption adjacent |
| two PPTX outputs | presentation builder | overview readable, no overlap |
| `docs/papers/ieee/paper.pdf` | Tectonic | overview legible in column/page width |

## Verification

```bash
python3 -m unittest discover -s tests
python3 scripts/verify_thesis_results.py
python3 scripts/validate_research_openspec.py
```

## Provenance Record

Record build commands, output paths, visual QA results, deviations, and unavailable tools in `evidence.md`.
