# Change Proposal: add-e7-leave-one-date-out-sensitivity

## Summary

為 E7 真實臥室 7 天、28 筆 pillow hold-out 快照加入 leave-one-date-out 敏感度分析，逐一移除每個日期後重算 raw 與 calibrated MAE，檢查既有改善是否由單一日期主導。

## Why

現有 paired day-block bootstrap 顯示三因子 MAE reduction 的 95% interval 下界均大於 0，但論文也使用「並非由單一日期驅動」的解讀。逐日剔除分析能直接檢查移除任一日期後改善是否仍為正，讓此穩健性敘述有可稽核的診斷結果。

## Change Map

- **From:** E7 具有整體 MAE 與 date-block bootstrap interval。
- **To:** 額外提供 7 個 leave-one-date-out folds、各 fold 三因子 MAE reduction，以及跨 folds 的最小與最大 reduction。
- **Impact:** 小幅強化 E7 內部敏感度證據；不增加樣本、不改變外部效度，也不涉及 E8 因果介入。
- **Claim effect:** claim-strengthening within the existing one-room, one-point, seven-date boundary.

## Scope

### In scope

- 擴充 weekly bedroom producer、machine-readable JSON、tests 與 result verifier。
- 同步中文論文、IEEE 稿、兩版簡報來源與教授版週報。
- 重建並驗證所有受影響產物。

### Out of scope

- 不新增或修改原始量測資料。
- 不把 leave-one-date-out 稱為外部驗證、cross-room generalization 或因果證據。
- 不執行 E8 真實介入。

## Research and Claim Impact

| ID | Status | Intended effect | Evidence |
| --- | --- | --- | --- |
| `RQ-E7-LODO-01` | new confirmatory diagnostic | 檢查 E7 改善是否依賴單一日期 | 7-fold deletion analysis |
| `H-E7-LODO-01` | pre-registered | 三因子在每個 date-deletion fold 的 MAE reduction 均大於 0 | weekly summary JSON |
| `CLM-E7-LODO-01` | proposed | 移除任一觀察日期後，三因子校正改善仍為正 | bounded real-bedroom evidence |
| `EVD-014` | proposed | leave-one-date-out evidence contract | accepted delta spec |

## Risks and Rollback

- 只有 7 個日期，分析僅能檢查單日影響，不能證明長期或跨場域泛化。
- 每個 fold 仍使用相同房間與 pillow point，結果彼此不是獨立實驗。
- 若任一 metric 的最小 reduction 小於或等於 0，假設判定為不支持並保留該 adverse fold。

## Completion Criteria

- [x] JSON 保存 7 個 folds 與三因子 min/max reduction。
- [x] tests 與 verifier 可重現並核對結果。
- [x] 中文論文、IEEE 稿、簡報與教授週報同步相同結果與限制。
- [x] 所有適用輸出重建，tests、result verifier 與 OpenSpec validator 通過。
