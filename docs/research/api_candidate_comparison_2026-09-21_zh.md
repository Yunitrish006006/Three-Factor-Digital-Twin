# 動態模擬與控制 API 候選比較（2026-09-21）

**狀態：EXPLORATORY / NOT_EVALUATED**  
本文件是研究設計與介面盤點，不是新的實驗結果。E15 為一次性既有證據，不在本輪重跑；E8 真實介入仍為 `NOT_EVALUATED`。

## 我這輪要回答的問題

我要找的不是「資料集最多」的 API，而是能否穩定重現下列閉迴路：

`reset → 讀取量測與可控輸入 → advance(step, input) → 取得新狀態 → 重複 → 匯出 trace/KPI`

只有通過這個介面門檻，平台才可進入後續的參數調教 pilot。任何模擬結果只能支持模擬平台內的比較，不能直接支持真實線材、機箱或半導體設備的因果主張。

## 候選矩陣

| 候選 | 類型 | 目前確認的介面／資料 | 可回答 | 不能回答／風險 | 本輪決策 |
|---|---|---|---|---|---|
| IBPSA BOPTEST | 互動式建築動態模擬 | 官方 REST RTE；選 testcase、initialize/warmup、讀 measurements/inputs、step/advance、results/KPI；支援控制 override | 可重設的閉迴路控制比較、跨 testcase 的策略與調教成本 | 仍是模擬；本地 FMU runner 不等同於公開 REST/KPI 服務；設備語意、量測點與時步需逐案確認 | **主平台**，先做 API smoke test，再做小型 PI pilot |
| APMonitor TCLab／TCLabModel | 小型熱動態模型／實驗平台 | 官方 Apps 提供 TCLab 控制與 simulation studio；本地 `tclab==1.0.0` 的 `TCLabModel(synced=False)` 已完成 reset/input/advance/response smoke test | 快速檢查階躍回應、低維參數辨識、簡單 baseline 調教 | 不代表 3D 空間或機箱流場；硬體與模擬模式要分開；不能把辨識資料當任意反事實 API | **第一個輕量 simulation pilot 已通過**，但仍非硬體／因果證據 |
| OpenHumidistat | 開源濕度控制硬體 | 文獻確認為可負擔、可重現的濕度控制實驗裝置；未確認標準可呼叫的雙變數 simulator API | 未來可做真實濕度介入與硬體可行性 | 目前沒有本地設備、完整 simulator、同步資料規格或校準流程 | **硬體備案**，不列入今日 API 主比較 |
| UCI SECOM | 靜態製程資料集 | 1567 筆製程紀錄與 pass/fail 標籤 | 製程分類、缺失值與資料品質研究 | 沒有 setpoint、連續致動器、時間序列控制循環或任意 action→response；不能作主要控制 API | **排除**於閉迴路控制主線 |

## 來源與本地證據

- BOPTEST 官方介紹與使用者 API：<https://ibpsa.github.io/project1-boptest/>、<https://ibpsa.github.io/project1-boptest/docs-userguide/introduction.html>、<https://ibpsa.github.io/project1-boptest/docs-userguide/api.html>。
- APMonitor Apps／TCLab：<https://apmonitor.com/apps/>；本地研究筆記：`docs/research/precision_environment_pid_data_review_2026-09-08_zh.md`。
- OpenHumidistat：<https://pmc.ncbi.nlm.nih.gov/articles/PMC9058855/>。
- 本地 API 尋找與 BOPTEST 連線失敗紀錄：`docs/reports/professor_catchup_report_2026-09-14_zh.html#journey`、`#problems`。

歷史上我對公開 `api.boptest.net` 做過 HTTPS/HTTP probe，但遇到 TLS／404；因此改用固定版本官方 FMU 加 FMPy 本地 runner。這個 workaround 只能證明本地模型可執行，不能宣稱已驗證公開 REST 服務等價性。

## 決策與停止條件

1. 先以 TCLab 建立 1 個可重設、可記錄 trace 的最小調教流程；若依賴或硬體不可用，停止於介面設計，不偽造結果。
2. 再對 BOPTEST 逐一記錄 testcase 的輸入／量測名稱、單位、步長、warmup、reset 與 KPI；缺一項就標記 `PILOT_BLOCKED`。
3. 參數調教只在 calibration split 選參數；validation split 僅在最後一次讀取。若沒有獨立 split 或可重設機制，不宣稱泛化。
4. 所有輸出都保留候選版本、設定檔、seed、環境、輸入 hash、trace hash 與 status（`PASS`、`PILOT_BLOCKED`、`NOT_EVALUATED`）。
