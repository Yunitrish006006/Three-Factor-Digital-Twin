# Evidence

## Reconciliation Result

- `CLM-INV-01`: supported. The professor-facing overview now covers E1–E9, keeps E9 subexperiments distinct, and points to current evidence files and producer commands.
- `EQ-E5-RANGE-01`: decided from `outputs/data/window_matrix_summary.json`. Of 48 target-zone indoor temperature results, 34 are within the inclusive `20–30 °C` domain and 14 are retained only as out-of-domain stress cases.
- No experiment was rerun to improve an observed result. Existing canonical JSON was treated as authoritative for reconciliation.
- Adverse outcomes remain visible: no-trilinear and raw-nominal ablation advantages, a target-zone hybrid regression, next-day failure, CU-BEMS persistence dominance, and RNN lowest-MAE count `0/12`.
- E8 remains `NOT_EVALUATED` with zero completed trials and null causal-effect metrics. Kalman filtering remains future work.

## Produced and Synchronized Artifacts

- `docs/reports/professor_complete_experiment_overview_2026-08-03_zh.md`
- `docs/reports/professor_weekly_report_2026-07-28_2026-08-03_zh.md`
- Chinese thesis source, build source, DOCX, TeX, and PDF copies
- IEEE source and seven-page PDF
- Short and 30-minute presentations, outlines, and long-form speaker notes
- Experiment result notes and the thesis result verifier

## Verification Results

- `python3 -m unittest discover -s tests`: 151 tests passed.
- `python3 scripts/verify_thesis_results.py`: 71 PASS, 0 FAIL, 0 MISSING.
- `python3 scripts/validate_research_openspec.py`: passed before main-spec synchronization.
- Stale-number search found no remaining occurrences of the superseded E4/E5 examples or former temperature-reduction rounding.
- DOCX archive integrity passed and the synchronized DOCX/PDF copies are byte-identical.
- Both PPTX files contain the `34`, `14`, and `20–30` range markers, with zero out-of-bounds shapes and zero empty placeholders.
- The thesis PDF was rendered to 82 page images and inspected; the initially clipped glossary table was converted to a repeated-header multi-page `longtable` and rechecked on pages 81–82.
- All seven IEEE PDF pages were rendered and visually inspected; no clipping or overlap was observed.

## Rendering Deviations

- The packaged DOCX and PPTX render helpers could not run because their active Python environment lacks `pdf2image`; LibreOffice is not installed.
- DOCX visual rendering therefore used the repository's synchronized thesis PDF as the visual source plus DOCX ZIP integrity and content checks. PPTX verification used macOS Quick Look HTML previews plus structural bounds and placeholder audits.
- Tectonic reported existing underfull-box/font portability warnings and one 1.5117 pt IEEE overfull box; the rendered pages remained readable and inside page boundaries.

## SHA-256

| Artifact | SHA-256 |
| --- | --- |
| Complete experiment overview | `76319fa1c0c5fa650fb81211de5e04e70231088a8e2baee4514775e5d8f694bc` |
| Professor weekly report | `b526e58adc97ed48a5b74701ff63314512d46156f0342a0f988477c5cbd69111` |
| E5 window evidence | `2486e186af292be1f6564c63c5df017c06218dfb801b08c494eb1a3c602ca911` |
| Verification JSON | `b99ac02f7dd18f58f48507be968bd2a46e5f91cb8984c588024ad0a35ff60fe3` |
| Chinese thesis DOCX | `d74b7388e289310672044e184c83d0d5e060cf3709be4d88dcebba9ea42e56bb` |
| Chinese thesis PDF | `793b625867d2ce80b42973be7b9f63b12cab4e61d526ec7e95377b014f9f7cd8` |
| Short PPTX | `7f12f939b12be4e66739249cd15fe2c7555dc7f97f9dba77b22ba42c4a33566e` |
| 30-minute PPTX | `e84c2f45dedf2cf81cec5b4180eb9f21c7dd6534976d965c583870ff5344ea83` |
| IEEE PDF | `491d919e74be9e6d3cf3720c06106816515676108c650c864d2cc7e7c06862b4` |
