# Change Proposal: compare-oh2024-inspired-hybrid-baseline

## Summary

將 Oh、Sfarra 與 Kim（2024）提出的 simulation-informed hybrid 概念轉寫為可在本專案公開資料流程執行的加法 residual baseline，並在相同 target、horizon、sample 與 chronological split 下，與 persistence、直接線性回歸、未修正 physics prior 及本研究 mapped readout 比較。此變更只主張「方法概念移植」，不主張重現原論文的 CNN--LSTM、TRNSYS/RC 模型或機密 BEMS 資料。

## Why

目前專案已引用該文並說明 `t+h`，但尚未回答該文方法能否成為本研究的可執行比較基線。原文資料明示為 confidential，且未提供可直接重跑的模型程式，因此直接搬用原文 CVRMSE 與本研究 MAE 做排名會造成資料、任務與指標不對等。需要一個有清楚方法忠實度標籤、同資料同切分的 transfer comparison。

## Change Map

### Published-method transfer benchmark

- **From:** 文獻只作為 hybrid residual 邏輯與時間符號的依據。
- **To:** 新增 `Oh2024-inspired additive residual readout`，用本研究 physics prediction 作 baseline，再由固定 ridge linear head 學習 target residual。
- **Reason:** 在不偽稱原文重現的前提下，實際檢查 simulation-plus-residual 概念於本研究公開任務的表現。
- **Impact:** 非破壞性；新增 E9 補充比較輸出、測試與同步論文敘述，不改寫既有 24/12 task headline。

### Claim boundary

- **From:** 原文數字與本研究數字只能在敘述上分開呈現。
- **To:** 原文 published results 只列為 literature context；本專案 transfer results 使用 SML2010、同 split 與同 metric 重新計算。
- **Reason:** 避免把不同建築、不同 horizon、不同 metric 的數字當作 head-to-head。
- **Impact:** 強化方法透明度；禁止 `reproduced Oh et al.` 或 `outperformed the published model` 等字樣。

## Scope

### In scope

- SML2010 `S2` temperature response 任務。
- Forecast horizons `15`, `60`, `1440` minutes。
- Chronological `70/30` split。
- Temperature targets `dining_temperature` 與 `room_temperature`。
- MAE、RMSE、Pearson correlation、R2、CVRMSE。
- Machine-readable JSON、tests、result verification、thesis/IEEE/presentation synchronization。

### Out of scope

- 重建原文 TRNSYS Type 56 或 RC building model。
- 重建原文 CNN--LSTM 與 GA hyperparameter search。
- 使用或推定原文機密 BEMS raw data。
- 將 SML2010 two-point task 稱為完整 3-D field validation。
- 把原文 published CVRMSE 與本研究重新計算 metric 合併排名。

## Research and Claim Impact

| ID | Current status | Intended effect | Evidence needed |
| --- | --- | --- | --- |
| `RQ-PHB-01` | new | determine transfer feasibility | focused SML2010 JSON |
| `H-PHB-01` | planned | test benefit over raw physics prior | 6 target-horizon MAE comparisons |
| `EQ-PHB-01` | new | compare against persistence, direct linear, and current readout | same-split metrics |
| `CLM-PHB-01` | not evaluated | permit bounded method-transfer statement | script output plus verifier |

## Affected Capabilities and Artifacts

- Current specs: `evaluation-and-evidence`
- Code and tests: new evaluation module/runner/tests; result verifier and all-experiment entrypoint
- Data and evidence: `outputs/data/public_benchmarks/oh2024_inspired_sml2010_comparison.json`
- Chinese thesis: method comparison, E9 result boundary, reference interpretation
- English IEEE paper: concise transfer result and limitation
- Presentation: method comparison slide/content, outlines, notes
- Figures and generated outputs: no new architecture figure planned; rebuild all synchronized paper and deck outputs

## Risks and Rollback

- Risks: linear residual head may underfit the original deep architecture; 1440-minute task may expose boundary/control forecast limitations; current physics prior is a pseudo-room mapping rather than TRNSYS/RC.
- Stop or rollback condition: if target/sample alignment or leakage cannot be demonstrated, retain the protocol and report `NOT_EVALUATED` without publishing comparison numbers.

## Completion Criteria

- [x] Future-state delta specs are accepted.
- [x] Protocol and reproducibility plan are accepted.
- [x] Evidence and claim decisions are recorded.
- [x] Applicable synchronized artifacts are rebuilt and verified.
