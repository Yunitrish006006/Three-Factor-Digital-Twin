# Executed evidence and delivery status

## Frozen research result

45 calibration + 60 formal episodes / 12,600 rows completed. Five methods share each split/seed's exogenous inputs, initial conditions, state visibility and actuator constraints. `artifacts/result.json` SHA-256 is `e9953311d4528786b17b558cca6757db9dd1f1194a3f96c3c52748d689cb7552`.

Stored-data verifier PASS: 1,995 metric checks, max independent scalar dynamics difference 0, 371 historical files unchanged, 15 paired schedule groups, and both corruption fixtures rejected. It does not independently re-optimize LQR/MPC. Focused five tests and full suite (363 tests / 38.938s) were recorded before report completion. No calibration/evaluation rerun occurred in this continuation.

Holdout MAE fixed/PI/PID/LQR/MPC=2.3462/2.2964/2.2879/1.4104/1.4428 C; energy proxy=.7200/.9550/.9538/1.1048/1.1064 Wh. Lowest MAE in validation/holdout/mismatch/overload=LQR/LQR/MPC/MPC. All methods overheat in overload. One MPC residual-gate rejection/fallback is preserved. No universal winner or hardware claim.

## Professor report and package

The complete offline HTML, explicitly labelled Markdown executive summary, 7-page PDF, figures, 105-run CSV, professor message draft, complete protocol/config/freeze/verification, 105 trace CSVs, source snapshots and hashes are staged in the separate delivery and ZIP. `artifacts/reporting/professor_qa.md` records actual QA scope and limitations. PDF pages and all report figures were visually inspected; HTML was structurally checked but not browser-rendered because the local-file browser URL was rejected by policy.

Chinese thesis DOCX/PDF copies match their `outputs/papers/` copies by SHA-256. Thesis, IEEE and Chinese review manuscript received synchronized research supplements and were rebuilt earlier; their entire documents were not visually inspected. DOCX has a 74-page render only. Existing presentation outlines/build source were synchronized; historical PPTX was preserved under the repository's offline-HTML preference.

## Limitations / state

This is full-state assumed-model simulation only. Actual PC enclosure performance, sparse-sensing efficacy, measured fan/system power and hardware safety remain NOT_EVALUATED. Cause statements are explanations to test, not isolated causal findings. The OpenSpec change remains active because broad manuscript visual QA and hardware validation are incomplete; no commit/push, email, submission or publication was performed.
