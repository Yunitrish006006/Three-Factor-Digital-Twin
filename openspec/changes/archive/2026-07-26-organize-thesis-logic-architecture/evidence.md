# Evidence

## Build Outputs

- `python3 scripts/build_architecture_diagrams.py`
  - Passed.
  - Rendered 11 SVG files, including Chinese and English research-logic overviews.
- `python3 scripts/build_thesis_docx.py`
  - Passed.
  - Rebuilt the Chinese thesis Markdown and DOCX.
- `python3 scripts/build_thesis_pdf.py`
  - Passed.
  - Rebuilt the 75-page Chinese thesis PDF.
  - The build emitted existing platform-font reproducibility and ToUnicode warnings but no build error.
- `python3 scripts/build_thesis_pptx.py`
  - Passed.
  - Rebuilt the 42-slide standard deck and 54-slide 30-minute deck, both outlines, and speaker notes.
- `tectonic --keep-logs --keep-intermediates paper.tex`
  - Passed from `docs/papers/ieee`.
  - Rebuilt a 7-page IEEE A4 PDF with the English companion overview.
  - Tectonic emitted underfull-box and repeated-rerun warnings but produced the final PDF without an error.

## Visual and Layout QA

- Inspected the Chinese and English 1600 x 900 overview figures at original resolution.
- Rendered the final DOCX to 60 page images and inspected the new Chapter 3 placement.
- Rendered the Chinese thesis PDF and inspected page 17 at full size.
- Rendered every slide from both decks and inspected all slides in grouped contact sheets.
- Inspected the overview slide at full size in both decks.
- Corrected a pre-existing clipped note card on the 30-minute deck's quantitative-results slide.
- Ran `slides_test.py` on both final decks; both reported `Test passed. No overflow detected.`
- Rendered the final IEEE PDF and inspected page 2 at full size; the overview is readable and the paper is A4.

## Verification

- `python3 -m unittest discover -s tests`
  - Passed: 108 tests.
- `python3 scripts/verify_thesis_results.py`
  - Passed: 31 checks, 0 failures, 0 missing.
- `python3 scripts/validate_research_openspec.py`
  - Passed before archive: 10 spec files, 62 requirements, 126 scenarios, 1 active change.
  - Passed after synchronization and archive: 10 spec files, 63 requirements, 128 scenarios, 0 active changes.
- Stale-title search
  - No remaining source occurrences of the former Figure 3-1 title, asset reference, slide title, or old-only overview wording.

## Claim Review

- The overview introduces no new method, metric, experiment, or causal claim.
- RQ1--RQ3 remain the main research line.
- RQ4 remains a secondary service/interface line.
- E8 remains a future intervention-validation protocol.
- Controlled full-field, real sparse snapshot, public task-aligned, and future intervention evidence remain explicitly non-interchangeable.
