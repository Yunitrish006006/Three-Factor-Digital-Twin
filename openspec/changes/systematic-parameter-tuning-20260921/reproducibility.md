# Reproducibility

先執行 API smoke test，再依 protocol 產生 run artifact。每一份 artifact 必須含 run id、平台與 testcase、commit、依賴版本、seed、參數 JSON、split 邊界、原始 trace、metrics JSON、輸入／輸出 SHA-256 與 status。依賴下載、硬體不可用或 API 不穩定時只記錄 `PILOT_BLOCKED`，不可以手動結果替代。
