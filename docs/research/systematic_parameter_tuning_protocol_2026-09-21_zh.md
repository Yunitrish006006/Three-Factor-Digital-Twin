# 系統性參數調教 Protocol（2026-09-21）

**狀態：PILOT_READY；尚未產生控制結果。** 這份 protocol 回應教授要求的「參數調教要有系統性」，先固定方法，再開始任何平台比較。

## 1. 參數分層

| 層級 | 例子 | 是否可調 | 原則 |
|---|---|---:|---|
| 物理／量測常數 | 量測單位、取樣週期、感測器範圍、致動器上下限 | 否（除非校準研究） | 由平台／校準文件固定，不能為了分數改動 |
| 動態模型參數 | 增益、時間常數、延遲、熱容／散熱係數 | 是，僅在 calibration split | 先以階躍資料辨識，再鎖定至 validation |
| 控制器參數 | `Kp`、`Ki`、`Kd`、輸出限幅、anti-windup | 是 | 只用 calibration trajectory 搜尋；validation 不回饋 |
| 實驗設計參數 | step 大小、warmup、評估窗長、seed | 預先固定 | 改變即視為不同 protocol，不能事後挑選 |

## 2. 固定資料切分與尋優流程

每一個 testcase／裝置至少建立三段可重設 trace：`calibration` 60%、`validation` 20%、`stress/holdout` 20%。若資料量不足，至少使用不同日期／不同初始狀態；否則標記 `NO_INDEPENDENT_VALIDATION`。

1. **辨識**：用 calibration 的 step response 估計最低階模型；記錄初始值、上下界、搜尋方法與失敗原因。
2. **候選產生**：以對數尺度的粗網格（例如 `Kp`、`Ki` 各 5 點）建立候選，再以固定預算的 local refinement；不可無限試到滿意。
3. **評分**：主要指標為 validation-window 的 IAE／ITAE；次要指標為 overshoot、settling time、輸出飽和比例、能耗 proxy。先寫死權重與 tie-break，再跑結果。
4. **選擇**：只在 calibration score 選最佳候選；若前兩名在 validation 的差異小於預先登記的 practical margin，報告為 tie，不挑看起來較好的那個。
5. **確認**：將鎖定的參數只跑一次 validation 與一次 stress/holdout。任何重新調參都開新 run id，不覆寫原結果。

## 3. 最小可重現設定

每個 run 必須保存：`run_id`、日期、平台／testcase、版本與 commit、Python／套件版本、seed、初始狀態、step／sample time、參數 JSON、搜尋範圍、候選數、calibration/validation/holdout 邊界、原始 trace、指標 JSON、輸入與輸出 SHA-256、status。

禁止事項：把 validation 指標回饋到搜尋、混用硬體與模擬 trace、以 E15 消耗性結果重新調參、把單一 testcase 的改善外推為真實設備因果效果。

## 4. 今日 pilot 的通過門檻

- `reset → input → advance → response` 可重複至少 3 次，且欄位、單位、時間戳一致。
- 同一 seed／設定重跑的 trace hash 一致；不一致則標記 `NON_DETERMINISTIC`。
- calibration 與 validation 分界可在 artifact 中重建。
- 至少一個 baseline（固定輸出或未調參 PI）與一個調參候選完整記錄；沒有完整記錄就不報改善百分比。

## 5. 證據邊界

TCLab／BOPTEST 的成功只代表平台內 pilot 可重現；不能直接支持 3D 列印線材、桌機機箱、半導體或真實濕度介入。E15 仍只支持既有同伺服器 Phytium S2500 的 temporal/workload 邊界；E8 與真實 intervention 保持 `NOT_EVALUATED`。

