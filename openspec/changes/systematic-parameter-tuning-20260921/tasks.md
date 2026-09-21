# Tasks

- [x] 登記候選 API 類型、介面與證據邊界。
- [x] 固定參數分層、資料切分、搜尋預算、評分與停止規則。
- [x] 稽核既有 BOPTEST development artifacts 與新 protocol 的符合程度。
- [x] 建立 TCLab 最小 reset/input/advance/response smoke test；結果限於 simulation pilot。
- [x] 建立 BOPTEST testcase 欄位、單位與步長清單。
- [x] 用 deterministic toy API 驗證 calibration/validation/holdout pipeline 與 gate；明確標為非研究證據。
- [x] 產生第一個含獨立 holdout 的 calibration/validation/holdout pilot artifact；限制為單一官方 FMU、兩個新日期。
- [x] 記錄一次 holdout 執行阻擋與可重試條件；維持 `PILOT_BLOCKED`，不填入假數值。
- [x] 由獨立 holdout 結果做 gate decision：目前不進入真實裝置介入，先維持 E8 `NOT_EVALUATED`，補多 testcase／seed 後再審查。
