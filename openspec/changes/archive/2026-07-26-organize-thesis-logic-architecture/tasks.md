# Tasks

## 1. Specification and Data Contracts

- [x] 1.1 Define the research-logic mapping without changing RQ or evidence status (`SYN-007`).
- [x] 1.2 Validate every problem, method, evidence, and claim-boundary label.

## 2. Implementation

- [x] 2.1 Add the semantic Mermaid source and deterministic SVG renderer.
- [x] 2.2 Add the overview to Chinese thesis Markdown and DOCX builder.
- [x] 2.3 Add an equivalent overview placement to the IEEE paper.
- [x] 2.4 Update short and 30-minute presentation sources, outlines, and notes.
- [x] 2.5 Add or update tests for the new diagram.

## 3. Execution and Evidence

- [x] 3.1 Rebuild architecture figures and inspect the new SVG.
- [x] 3.2 Rebuild DOCX/PDF/PPTX/IEEE outputs.
- [x] 3.3 Render and inspect affected document pages and every presentation slide.
- [x] 3.4 Populate `evidence.md` with actual build and QA results.

## 4. Claim Review

- [x] 4.1 Confirm the figure adds no new method, metric, or causal claim.
- [x] 4.2 Confirm E8 remains future intervention validation and RQ4 remains secondary.

## 5. Synchronized Research Artifacts

- [x] 5.1 Update Chinese thesis and build source.
- [x] 5.2 Update IEEE source.
- [x] 5.3 Update presentation source and both outlines.
- [x] 5.4 Rebuild affected figures, DOCX, PDF, PPTX, and IEEE PDF.
- [x] 5.5 Search for stale figure titles, captions, and old-only system-overview wording.

## 6. Final Verification

- [x] 6.1 Run `python3 -m unittest discover -s tests`.
- [x] 6.2 Run `python3 scripts/verify_thesis_results.py`.
- [x] 6.3 Run `python3 scripts/validate_research_openspec.py`.
- [x] 6.4 Sync `SYN-007` into main specs and archive the completed change.
