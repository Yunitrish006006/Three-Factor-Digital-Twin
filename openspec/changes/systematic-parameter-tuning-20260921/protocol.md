# Protocol

完整 protocol 見 [`docs/research/systematic_parameter_tuning_protocol_2026-09-21_zh.md`](../../docs/research/systematic_parameter_tuning_protocol_2026-09-21_zh.md)。本 change 的最小執行循環為：

1. 固定平台、版本、seed、sample time、初始狀態與輸入範圍。
2. 以 calibration trace 做動態辨識與候選參數搜尋。
3. 鎖定參數後，僅一次讀取 validation 與 holdout。
4. 保存 trace／metrics／hash／status；若 reset、欄位或分界不可重建，標記 `PILOT_BLOCKED`。
