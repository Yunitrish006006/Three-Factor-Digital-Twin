# Reproduction

First run focused unit tests on non-evaluation fixtures, validate OpenSpec, and commit the protocol/runner. Execute `.venv-mpc/bin/python scripts/run_enclosure_lqr_diagnostic.py` ONCE. Thereafter use `.venv-mpc/bin/python scripts/verify_enclosure_lqr_diagnostic.py` for stored-data audit only. A new independent study needs a new protocol, directory and seeds, not removal of the attempt receipt. Dependencies are the existing numpy/scipy environment; freeze records versions/hashes. Report rebuild/QA commands will be recorded after actual execution.

## Executed reporting commands

- `.venv-mpc/bin/python scripts/build_lqr_diagnostic_figures.py` reads the frozen result/CSV files only.
- `python3 scripts/enclosure_lqr_diagnostic_summary.py` synchronizes the IEEE paragraph and presentation outlines.
- Bundled Python at `/Users/yunitrish/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python` ran `scripts/build_weekly_package_20261019.py`, `scripts/build_thesis_docx.py`, and `scripts/build_thesis_pdf.py`.
- `tectonic --keep-logs --keep-intermediates paper.tex` ran in `docs/papers/ieee/`.
- `ENCLOSURE_QA_DEPENDENCIES=/Users/yunitrish/.cache/codex-runtimes/codex-primary-runtime/dependencies/node node scripts/qa_weekly_package_20261019.mjs` uses isolated local Chrome and blocked network access. It writes only this study's reporting receipts.
- `pdftoppm -scale-to 1500 -png` renders the final review PDF; native thesis / IEEE changed pages are rendered selectively.
- The documents skill's `render_docx.py` renders the synchronized DOCX into a temporary directory. Its first bundled-font preview lacked CJK glyphs and is not accepted QA. A task-local `FONTCONFIG_FILE` supplies `/System/Library/Fonts`, the system preinstalled font-assets tree and `/Library/Fonts`, with cache under `/private/tmp`; no document content or system font installation is changed.

Historical PPTX outputs are preserved under the explicit HTML preference in AGENTS.md; see evidence.md for the reporting-scope clarification. Rebuilds are not new evaluations. Do not remove attempt.json or rerun the study to regenerate charts.
