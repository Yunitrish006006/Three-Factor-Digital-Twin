# Change Proposal: add-bedroom-bootstrap-uncertainty

## Summary

為 E7 真實臥室 7 天、28 筆 pillow hold-out 快照加入 paired day-block bootstrap，不只報告 raw 與 calibrated MAE，也報告校正後 MAE 降幅的 95% confidence interval 與逐快照改善比例。

## Why

目前 E7 已有 before/after MAE，但沒有不確定性區間。四個每日時段來自同一天，若直接把 28 筆快照視為完全獨立樣本，會低估日內相依性。以日期為 block 重抽樣可以保留同一天四筆快照的相關結構，提供較誠實的描述性不確定性分析。

## Change Map

### E7 uncertainty

- **From:** 僅報告 28 筆快照的 raw 與 calibrated pillow MAE。
- **To:** 以日期為 resampling block，固定 seed 執行 20,000 次 paired bootstrap，報告每個 metric 的 mean MAE reduction、95% percentile interval、relative reduction 與 improved snapshot fraction。
- **Reason:** 檢查改善是否跨日期穩定，而非由少數快照主導。
- **Impact:** 強化既有 E7 證據；不把單房間結果外推為 dense 3-D 或任意房間驗證。

## Scope

### In scope

- 擴充 `run_bedroom_weekly_simulation.py` 與 machine-readable summary。
- 新增 deterministic bootstrap tests。
- 更新 result verifier、中文論文、IEEE 稿與兩版簡報。
- 重建並驗證所有同步輸出。

### Out of scope

- 不新增量測資料或改動既有 28 筆快照。
- 不執行 E8 實體介入。
- 不宣稱 bootstrap 能消除單一房間、單一 hold-out 點或短期量測限制。

## Research and Claim Impact

| ID | Current status | Intended effect | Evidence needed |
| --- | --- | --- | --- |
| `RQ-E7-UNC-01` | 新增分析問題 | 判斷 E7 改善在日期 block resampling 下是否維持正值 | bootstrap JSON、tests、verifier |
| `H-E7-UNC-01` | pre-registered | 三因子 MAE reduction 的 95% interval 下界均大於 0 | 20,000-replicate paired day-block bootstrap |
| `CLM-E7-UNC-01` | proposed | 在此 7 天單房間資料中，三因子校正改善跨日期重抽樣仍為正 | bounded E7 evidence |
| `EVD-010` | proposed | E7 uncertainty contract | main-spec synchronization after acceptance |

## Risks and Rollback

- Risk: 只有 7 個 date blocks，confidence interval 仍屬小樣本描述。
- Risk: 將 snapshot-level improvement rate 誤讀為跨房間成功率。
- Stop condition: interval computation不具決定性、任一輸出與原始 MAE 不一致，或同步文件出現不一致。
- Rollback: 移除新增統計主張，但保留原始 E7 MAE 與限制。

## Completion Criteria

- [x] JSON 記錄 method、block、seed、replicates、interval 與 improvement fraction。
- [x] 三因子 observed reduction 與 interval 可由相同腳本重現。
- [x] verifier 核對新增數字。
- [x] 中文、IEEE、簡報與產出檔同步完成。
- [x] tests、OpenSpec validator 與視覺 QA 通過。
