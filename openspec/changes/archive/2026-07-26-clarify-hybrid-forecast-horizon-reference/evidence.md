# Evidence

## Run Metadata

- Execution time: `2026-07-26T12:09:32+0800` (Asia/Taipei).
- Base commit: `1ca4b73`.
- Worktree: dirty before this change because the synchronized research-logic OpenSpec work was already present; those changes were preserved.
- Literature input: user-provided Energy and Buildings PDF, title/author/venue/DOI verified with PDF metadata and full-text inspection.

## Literature Audit

- Repository search before editing found no match for the exact title, DOI `10.1016/j.enbuild.2024.114898`, authors, or article number.
- PDF metadata confirmed:
  - Ju-Hong Oh, Stefano Sfarra, and Eui-Jong Kim.
  - *Energy and Buildings*, vol. 324, article 114898, 2024.
  - DOI `10.1016/j.enbuild.2024.114898`.
- Full-text and page-image inspection confirmed the study uses forecast-day physical simulation output and historical simulation--measurement discrepancy in a next-day indoor-temperature hybrid predictor.
- The screenshot equation was treated as a general time-aligned residual-forecast notation, not claimed as a verbatim displayed equation from the article.

## Synchronized Source Evidence

- Chinese thesis related work includes Oh et al. as reference `[26]`.
- Chinese Section 3.8 defines current-state `F(p,t)+R(p,t)`, the `h`-step form conditioned on `I_t`, and the `h=0` implementation boundary.
- IEEE Related Work cites `oh2024hybridmodeling`; the Method section defines the same target-time and leakage semantics.
- `docs/models/hybrid_residual_model_zh.md` contains the focused explanation for why the physics term carries `t+h`.
- Formula walkthrough slide 38 in the standard deck and slide 50 in the 30-minute deck define `h`, `I_t`, target-time alignment, and the current `h=0` scope.
- Exact-source searches found the DOI, `mathcal{I}_t`, `h=0`, and future-observation exclusion in the expected sources.

## Builds

- `scripts/build_thesis_docx.py`: passed; rebuilt Markdown and DOCX.
- `scripts/build_thesis_pdf.py`: passed; rebuilt the 75-page A4 Chinese thesis PDF.
- `scripts/build_thesis_pptx.py`: passed; rebuilt 42-slide and 54-slide decks, outlines, and speaker notes.
- `tectonic --keep-logs --keep-intermediates paper.tex`: passed; rebuilt a 7-page IEEE A4 PDF with a resolved reference `[10]`.
- Generated Chinese thesis DOCX/PDF copies in `outputs/papers/` are byte-identical to the corresponding `docs/papers/thesis/` outputs.

## Visual and Layout QA

- Rendered the final DOCX to 60 page images and inspected all pages; inspected related-work page 8, method page 30, and reference page 58 at full size.
- Rendered the final Chinese PDF to 75 page images and inspected all pages; inspected PDF pages 37, 39, and 73 at full size.
- Rendered and inspected every slide in both final decks; formula slides 38 and 50 were inspected at full size.
- `slides_test.py` passed for both decks with no overflow.
- Rendered and inspected all seven IEEE pages; formula page 3 and reference page 7 were inspected at full size.
- No clipping, overlap, unresolved citation, or page-count regression was found.

## Verification

- `python3 -m unittest discover -s tests`
  - Passed: 108 tests.
- `python3 scripts/verify_thesis_results.py`
  - Passed: 31 checks, 0 failures, 0 missing.
- `python3 scripts/validate_research_openspec.py`
  - Before archive: 10 spec files, 63 requirements, 128 scenarios, 1 active change.
  - After syncing `HRL-007` and archiving: 10 spec files, 64 requirements, 131 scenarios, 0 active changes.

## Output Hashes

- Chinese DOCX: `b464f0030f62595f68772a484d9b09d961d054dfa3606f71158f09db7e7df640`.
- Chinese PDF: `0bac4d7435640ba7446c4157a851fb9bf079bdc79e9066c62a1c0a02bc6704aa`.
- Standard PPTX: `46439c0ea7f8ad94a33c5118accca21f1986ccad8b0db5a2aaa4e7df1b70756e`.
- 30-minute PPTX: `a12da451e17ae3e7de243678c9d6aaf83c2ade7f8d280e328d8116af114ff290`.
- IEEE PDF: `3e441e0a5238694a58d5347646bec99268ad32ed912d8545fdb5ab99dcaeaa6b`.

## Warnings and Deviations

- The Chinese PDF build retained existing platform-font reproducibility and ToUnicode warnings but completed successfully.
- Tectonic retained existing underfull-box warnings and one 1.51 pt overfull equation warning; full-page inspection confirmed the equation remains inside the visible two-column page area.
- No new forecasting experiment was executed; all `h>0` content is explicitly a notation generalization and leakage boundary.

## Claim Decision

- `CLM-HRL-TIME-01`: **supported as a literature-grounded notation clarification**.
  - Both additive terms target `t+h`.
  - `h` is forecast lead, not a physical coefficient.
  - `I_t` excludes target-time truth and truth residuals.
  - Current project evidence remains bounded to current-state spatial estimation (`h=0`), not next-day forecasting.
