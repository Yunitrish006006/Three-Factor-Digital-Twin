# Change Proposal: organize-complete-experiment-inventory

## Summary

建立一份教授可直接閱讀的完整實驗總覽，統一整理 E1–E9、E7 敏感度分析、E9 公開資料子實驗、RNN、公平資料條件、失敗結果、證據路徑與適用範圍。同時以目前機器可讀 JSON 為準，修正既有實驗文件與中文論文中的過期範例數值。

## Why

目前實驗資訊分散在多份文件與 JSON。盤點時發現部分舊範例數字已與目前 `validation_summary.json` 或 `window_matrix_summary.json` 不一致；若直接彙整，會讓教授看到互相矛盾的版本。另外，教授已把室內適用範圍限定為 `20–30 °C`，因此 E5 舊窗戶矩陣中的範圍外室內結果必須和範圍內證據分開標示。

## Scope

### In scope

- E1–E9 的目的、資料、方法、指標、結果、證據狀態、限制與重現命令。
- E9 的 public baseline、project mapped comparison、published-method transfer、next-day follow-up 與 same-data RNN 子實驗。
- E5 對目前 `20–30 °C` 室內邊界的描述性範圍稽核。
- 修正實驗文件與中文論文/build source 中過期的代表數值。
- 重建所有規定的同步輸出並驗證。

### Out of scope

- 重新訓練或調參以改變既有結果。
- 把 E8 寫成已完成，或把推薦排序寫成因果效果。
- 把 E5 範圍外案例當成目前模型適用性證據。
- 新增投稿資訊、個人開發紀錄或未有 evidence 的推測結果。

## Claim Impact

- `CLM-INV-01`: claim-neutral consolidation；所有結果維持既有強度，但來源與限制更清楚。
- E5 範圍說明屬 claim-weakening：範圍外案例只保留為壓力測試，不支援目前應用主張。
- 過期數字修正屬 evidence synchronization，不代表新模型進步。

## Completion Criteria

- [x] E1–E9 與所有已執行子實驗均出現在統一總覽。
- [x] 每項結果均有 evidence path、producer command、support level 與 claim boundary。
- [x] 舊文件與目前 JSON 的已知數字漂移已修正。
- [x] E5 範圍內與範圍外案例明確分開。
- [x] 中文論文、build source、IEEE、簡報與所有生成輸出完成同步檢查。
- [x] 測試、結果驗證、OpenSpec validator 與視覺 QA 通過。
