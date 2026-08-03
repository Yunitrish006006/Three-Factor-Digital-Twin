# Change Proposal: clarify-hybrid-forecast-horizon-reference

## Summary

將 Oh、Sfarra 與 Kim（2024）的 simulation--operational-data hybrid indoor-temperature study 納入論文參考，並統一說明 additive hybrid 公式中的 forecast horizon `h`、target time `t+h` 與 forecast-origin information set `I_t`。

## Why

目前專案已使用「主模型 + learned residual」架構，但文獻表未包含這篇直接以物理模擬結果與營運量測差異進行 next-day indoor-temperature prediction 的研究。另因簡寫公式 `ŷ_hybrid(t+h)=ŷ_phys(t+h)+ê(t+h)` 未顯式標出資訊集合，容易被誤解為物理項使用了未來量測，或把 `h` 看成物理模型額外參數。

## Change Map

### 文獻定位

- **From:** 專案未引用 Oh、Sfarra 與 Kim（2024）。
- **To:** 中英文論文加入完整書目，並在 hybrid related work 中說明其使用 forecast-day physical simulation 與 learned simulation--measurement gap。
- **Reason:** 補足與本研究 additive residual 架構直接相關的先行研究。
- **Impact:** Claim-neutral；增加來源依據，不改變現有實驗數字。

### 預測時間符號

- **From:** 專案主要使用 `F(p,t)+R(p,t)`，未集中說明若推廣為 `h`-step forecast 時，為何 physics term 也標為 `t+h`。
- **To:** 定義 `h` 為 forecast lead，`I_t` 為預測起點可得資訊，兩個加總項均對齊同一 target time `t+h`；明定 `I_t` 不得含未來觀測。
- **Reason:** 回應公式質疑並防止 target leakage。
- **Impact:** 非破壞性符號釐清；目前空間估測仍使用 `t`，可視為 `h=0`。

## Scope

### In scope

- 新增中英文書目與 related-work 定位。
- 更新 hybrid residual 模型說明與公式時間語意。
- 更新兩版簡報的 hybrid formula walkthrough。
- 重建並驗證 DOCX、PDF、PPTX 與 IEEE PDF。

### Out of scope

- 不新增 forecasting code、資料切分或預測實驗。
- 不宣稱引用論文的公式逐字等同於本研究公式。
- 不將 next-day forecasting evidence 當成本研究現有 current-state spatial reconstruction 證據。

## Research and Claim Impact

| ID | Current status | Intended effect | Evidence needed |
| --- | --- | --- | --- |
| `CLM-HRL-TIME-01` | 新增符號契約 | 中立；消除時間語意歧義 | PDF 內容核對、同步來源與輸出 |
| `HRL-007` | 新增規格 | 防止未來資料洩漏 | 文字搜尋與建置驗證 |

## Affected Capabilities and Artifacts

- Current spec: `hybrid-residual-learning`
- Chinese thesis: `scripts/build_thesis_docx.py`、Markdown、DOCX/PDF outputs
- English IEEE paper: `paper.tex`、`references.bib`、`paper.pdf`
- Model note: `docs/models/hybrid_residual_model_zh.md`
- Presentation: `scripts/build_thesis_pptx.py`、兩版 outline、speaker notes、PPTX outputs
- Figures: 無

## Risks and Rollback

- Risk: 將 `h` 誤解為物理參數，或誤寫成使用未來 observation。
- Risk: 新增文字使 IEEE 稿超過 7 頁或簡報文字溢出。
- Stop condition: IEEE 超過目標頁數，或 DOCX/PPTX 出現無法修復的版面問題。
- Rollback: 保留書目，將長公式說明移至註解或附錄，但不得刪除 leakage boundary。

## Completion Criteria

- [x] 專案能搜尋到 DOI `10.1016/j.enbuild.2024.114898`。
- [x] 中英文方法均說明 `h`、`t+h`、`I_t` 與 `h=0` 的關係。
- [x] 未來觀測不得進入 `I_t` 的限制明確可見。
- [x] 所有同步輸出重建並完成視覺 QA。
