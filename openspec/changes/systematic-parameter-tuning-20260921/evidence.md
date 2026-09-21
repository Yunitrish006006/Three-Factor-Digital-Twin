# Evidence

本輪沒有重跑 E15，也沒有重新消耗 BOPTEST。`artifacts/protocol_audit.json` 只稽核既有 `pilot-boptest-rapid-pi` 產物，將其對照 2026-09-21 新 protocol。

## 已符合

- 既有 `result.json` 固定了 PI grid、baseline、6 小時 development trace、指標與每條 trace 的 SHA-256。
- `result_v2.json` 保存 2 小時 calibration、選出的 `Kp/Ti`、辨識退化原因與 day 3／day 180 的完整 metrics。
- 既有 `verification.json` 記錄 229 個 repository tests、CSV audit 與未採納主論文的 exploratory scope。

## 尚未符合

- day 3／day 180 是 development evaluation dates，不是獨立 sealed holdout。
- 本地官方 FMU runner 不等同公開 BOPTEST REST/KPI 服務。
- 因此本輪狀態是 `PARTIAL_PROTOCOL_CONFORMANCE`，不能改寫成已完成泛化或真實介入。
- 可執行 gate `scripts/validate_parameter_tuning_artifact.mjs --report-only` 已重現同一結論：`PILOT_INCOMPLETE`，原因只有「independent sealed holdout is missing」。

## 下一步

建立一個不同初始狀態或日期的 holdout run，沿用已鎖定參數，只讀取一次；若平台或依賴不可用，保存 `PILOT_BLOCKED` artifact，而不是手動補數字。

## 2026-09-21 執行嘗試

這次檢查發現目前 checkout 沒有 pinned FMU 或 `outputs/boptest-venv`；`.venv/bin/python` 也沒有 FMPy，系統 Python 受 macOS Xcode license prompt 阻擋。因此已保存 [`holdout_attempt_20260921.json`](artifacts/holdout_attempt_20260921.json)；沒有產生數值，也沒有把既有 development evaluation 改標成 holdout。
