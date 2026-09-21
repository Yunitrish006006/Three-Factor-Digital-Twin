# Evidence

本輪沒有重跑 E15，也沒有重新消耗 BOPTEST。`artifacts/protocol_audit.json` 只稽核既有 `pilot-boptest-rapid-pi` 產物，將其對照 2026-09-21 新 protocol。

## 已符合

- 既有 `result.json` 固定了 PI grid、baseline、6 小時 development trace、指標與每條 trace 的 SHA-256。
- `result_v2.json` 保存 2 小時 calibration、選出的 `Kp/Ti`、辨識退化原因與 day 3／day 180 的完整 metrics。
- 既有 `verification.json` 記錄 229 個 repository tests、CSV audit 與未採納主論文的 exploratory scope。

## 既有 artifact 的限制

- day 3／day 180 是 development evaluation dates，不是獨立 sealed holdout；新的 day 240／day 270 Linux run 是後續 locked evaluation。
- 本地官方 FMU runner 不等同公開 BOPTEST REST/KPI 服務。
- 因此既有 artifact 仍是 `PARTIAL_PROTOCOL_CONFORMANCE`；新 run 也不能改寫成已完成泛化或真實介入。
- 可執行 gate `scripts/validate_parameter_tuning_artifact.mjs --report-only` 已重現同一結論：`PILOT_INCOMPLETE`，原因只有「independent sealed holdout is missing」。

## 下一步（真實研究仍需）

增加第二個 testcase／多個 seed，並規劃真實裝置介入；目前不把單一 FMU 的兩個日期外推成通用控制或因果主張。

## 2026-09-21 執行嘗試

這次先恢復了 pinned FMU（SHA-256 與既有 artifact 一致）與隔離 FMPy 0.3.22，但在 macOS ARM 實際執行 day 270 時發現 FMU 只有 `binaries/linux64/wrapped.so`，沒有 macOS library；FMPy 在第一個 transition 前即因缺少 `darwin64/wrapped.dylib` 失敗。已保存 [`holdout_attempt_20260921.json`](artifacts/holdout_attempt_20260921.json)；沒有產生數值，也沒有把既有 development evaluation 改標成 holdout。

另外執行了 [`contract_test_run.json`](artifacts/contract_test_run.json)：它用 deterministic toy dynamic API 完整跑過 calibration／validation／holdout，trace hash 與 gate 均為 `PASS`。這只驗證 pipeline contract，不是 BOPTEST、TCLab 或真實介入證據，故 artifact 狀態明確為 `PASS_CONTRACT_TEST_NOT_RESEARCH_EVIDENCE`。

## TCLab simulation smoke test

已在隔離 `.venv` 安裝 `tclab==1.0.0`，以 `TCLabModel(synced=False)` 建立 `reset → input(Q1/Q2) → advance(update(t)) → response(T1/T2)` 循環。固定 seed 17 下，calibration／validation／holdout 三段 trace hash 彼此不同，holdout 重跑 hash 一致，且 `validate_parameter_tuning_artifact.mjs` 回報 `PASS`。artifact 狀態是 `PASS_TCLAB_SIMULATION_PILOT_NOT_HARDWARE_EVIDENCE`；它只能支持 TCLab 模擬介面與 protocol 可重現，不能支持 TCLab 硬體、BOPTEST、室內／機箱或因果介入。

## BOPTEST Linux locked holdout

GitHub Actions run [35566560483](https://github.com/Yunitrish006006/Three-Factor-Digital-Twin/actions/runs/35566560483) 在 Ubuntu x86-64 恢復固定 FMU runtime，執行預先鎖定的 `Kp=3.227185031291436`、`Ti=250.5407617068066`；沒有重新搜尋參數。day 240 作 validation、day 270 作 holdout，兩者都同時跑 fixed PI baseline，gate 與 trace hash 均通過。

| 日期 | locked PI MAE | fixed PI MAE | locked PI IAE (C·h) | fixed PI IAE (C·h) | 判讀 |
|---|---:|---:|---:|---:|---|
| 240 validation | 0.2996°C | 0.4150°C | 7.1909 | 9.9596 | 在這個新日期較低，但仍是單一 FMU |
| 270 holdout | 0.3820°C | 0.5366°C | 9.1678 | 12.8795 | holdout 仍較低；不能外推成普遍優勢 |

locked 的 saturation 比例較高，且能源分項仍需分開解讀；因此我只報 tracking metrics，不宣稱節能或因果改善。完整 JSON 與四條 CSV trace 位於 [`boptest_linux_holdout.json`](artifacts/boptest_linux_holdout.json) 與 `artifacts/traces/`。這仍是官方 FMU 的自訂 FMPy runner，不是官方 REST/KPI 等價性或真實介入證據。

## Gate decision

兩個新日期的 locked-vs-fixed 結果足以支持「在同一 FMU 上繼續做多 testcase／多 seed」的研究假說，但不足以支持真實裝置介入。因此本輪決策是 **不進入 E8 intervention**；E8 仍為 `NOT_EVALUATED`，下一個 gate 是跨 testcase／seed 的獨立確認，而不是直接部署控制器。
