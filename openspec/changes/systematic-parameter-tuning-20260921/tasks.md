# Tasks

- [x] 登記候選 API 類型、介面與證據邊界。
- [x] 固定參數分層、資料切分、搜尋預算、評分與停止規則。
- [x] 稽核既有 BOPTEST development artifacts 與新 protocol 的符合程度。
- [ ] 建立 TCLab 最小 reset/input/advance/response smoke test。
- [ ] 建立 BOPTEST testcase 欄位、單位與步長清單。
- [x] 用 deterministic toy API 驗證 calibration/validation/holdout pipeline 與 gate；明確標為非研究證據。
- [ ] 產生第一個含獨立 holdout 的 calibration/validation/holdout pilot artifact。
- [x] 記錄一次 holdout 執行阻擋與可重試條件；維持 `PILOT_BLOCKED`，不填入假數值。
- [ ] 由獨立 holdout 結果決定是否進入真實裝置研究；在此之前維持 NOT_EVALUATED。
