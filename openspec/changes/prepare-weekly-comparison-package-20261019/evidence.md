# Observed reporting evidence — 2026-10-19

## WPK-901: complete frozen-result audit — PASS

Executed `.venv-mpc/bin/python scripts/audit_weekly_comparison_20261019.py` before writing and after final artifact generation. The verifier reads stored CSVs and recomputes their original metrics; no controller, identification or simulation executor was run.

- First study: 88 episodes, 10,560 rows, 1,496 metric cells and all declared aggregates agree.
- Second study: 96 episodes, 11,520 rows, 1,632 metric cells and all declared aggregates agree.
- Total: 184 episodes, 22,080 rows, 3,128 original metric cells.
- All 852 baseline files retain their original SHA-256: 844 historical study artifacts plus eight selected coupled manuscript/native files.
- H-ENC-51, H-ENC-52, H-ENC-71 and H-ENC-72 remain `not_supported`. Neither original decisions nor result files were overwritten.

Receipts: `artifacts/metric_audit.json`, `artifacts/historical_hashes.json`. This is an arithmetic/source-integrity check, not new experimental replication or causal evidence.

## WPK-902: complete review manuscript — PASS within declared scope

Delivered `docs/papers/conference_review_2026-10-19/manuscript_zh.md`, HTML and PDF, plus readiness and source provenance. Six tables are generated directly from the frozen result files. The text distinguishes implementation facts, descriptive results, compatible explanations and unexecuted causal tests. It retains adverse results, independent evaluation units and synthetic/physical boundaries.

Built with the installed bundled Python/ReportLab/pypdf runtime and `scripts/build_weekly_package_20261019.py`. No Office artifacts were created or rebuilt. This is a neutral derivative of existing evidence, not an alteration of the adopted thesis method/conclusion. The original thesis and IEEE artifacts remain unchanged.

The final PDF has five A4 pages and 337,499 bytes; all five page dimensions were checked. It uses 3 cm vertical/2 cm horizontal body margins, two columns, installed BiauKai and Times New Roman, 14/11/10/12 pt title/heading/body/author sizing, synthetic bold for title/headings, four keywords and no page numbers. All pages were rendered with `pdftoppm -scale-to 1600 -png` and directly viewed. Corrections included missing Latin accents, author affiliation superscripts, right-aligned equation numbers and headings separated from tables. Final SHA-256: `e748fe17aa6fc77732ca05b27965838096ed44208d4b83909f8531b034862a09`.

The pre-existing Kalman original PDF is linked from the report; its actual page count is 18. Formulas in the new manuscript are modern method notation, not alleged verbatim equations from Kalman.

## WPK-903: weekly briefing and current venue preparation — PASS

Delivered `docs/reports/professor_weekly_2026-10-19_zh.html` and the matching first-person ten-minute script. The briefing includes the professor request/action mapping, method and platform comparisons, explanation boundaries, manuscript and original-paper links. It distinguishes the 10/12 evidence date from the 10/19 reporting/audit date; oral delivery has not been inferred.

Official CSME and ICCE-TW submission pages were checked on 10/19, and the actual CSME Chinese full-paper PDF template was downloaded, extracted and visually inspected. The saved original template and its hash are under the review directory. CSME shows 10/25/2026 and its complete-paper template says 4–6 pages; ICCE-TW shows 01/29/2027 and two English pages. These are candidate routes only. The user explicitly confirmed no selected conference and no submission; author ordering/corresponding author consent remain pending. No email, system submission or payment occurred.

Executed `scripts/qa_weekly_package_20261019.mjs` with installed Playwright in isolated Chrome, offline file URLs and no user profile. Both HTML files passed 1440/820/390 px checks; local files and fragments exist, no document overflow or raw TeX, all three MathML equations have visible geometry, phone tables respond to keyboard scrolling, and no console/page errors occurred. Both print media layouts passed the width check. Representative desktop/tablet/mobile, formula, table and print-style screenshots were directly viewed. This does not assert browser print pagination; the separate typeset PDF was inspected page by page.

Fresh observations and screenshots are SHA-bound in `artifacts/visual_observation.json`; automated results are in `artifacts/html_qa/receipt.json`. Final HTML hashes match these receipts after the final PDF-only builder adjustment.

## Validation and delivery boundary

`python3 scripts/validate_research_openspec.py` passed: 14 spec files, 130 requirements, 251 scenarios, 40 active changes. Physical experiments, new causal ablations, venue choice and formal submission remain outside the completion claim. No old test-suite result is presented as newly executed.

Package commit `8e8fad747248079caa73e85b8dbe1d0bdee83b36` was pushed to `origin/main`. An independent `git ls-remote origin refs/heads/main` returned the identical SHA on 2026-10-19. The subsequent completion-record commit changes only this evidence and the task checklist; report and manuscript bytes remain those observed above. Both unstaged and staged `git diff --check` passed before the package commit.
