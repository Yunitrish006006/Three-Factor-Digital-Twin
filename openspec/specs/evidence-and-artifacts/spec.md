# evidence-and-artifacts Specification

## Purpose

定義本研究的證據分層、資料切分、評估輸出與論文相關產物同步規則，使每個研究主張都有可追溯證據。

## Requirements

### Requirement: EAA-001 Evidence layers remain separate

系統與論文 SHALL 將 synthetic full-field、real target-point、public task-aligned benchmark 與 intervention validation 分開呈現。

#### Scenario: 報告 synthetic full-field result

- **GIVEN** 指標由受控模擬 reference field 計算
- **WHEN** 結果寫入論文或簡報
- **THEN** 結果標示為 synthetic full-field evidence
- **AND** 不延伸宣稱真實房間所有未量測點具有相同準確度

#### Scenario: 報告 public dataset result

- **GIVEN** 結果來自 CU-BEMS 或 SML2010 的相容時序任務
- **WHEN** 結果寫入論文或簡報
- **THEN** 結果標示為 task-aligned benchmark
- **AND** 不將其描述為單房間 3-D 空間場驗證

### Requirement: EAA-002 Temporal data uses leakage-resistant splits

具有時間相依性的真實資料與公開資料 SHALL 使用保留時間區塊的切分方式，並記錄 train、validation 與 test 範圍。

#### Scenario: 評估連續多日資料

- **GIVEN** 一段具有時間順序的感測器資料
- **WHEN** 建立訓練與測試集
- **THEN** 系統使用 blocked split、leave-one-day-out 或其他不打散相鄰時間的方式
- **AND** 輸出記錄每個 split 的日期或索引範圍

### Requirement: EAA-003 Metrics are reproducible

每個論文或簡報中的核心數值 SHALL 可由命名腳本與版本化輸出重新產生。

#### Scenario: 引用 MAE 或 RMSE

- **GIVEN** 論文、README 或簡報引用一個 MAE、RMSE、R²、correlation 或 improvement score
- **WHEN** 研究者追查該數值
- **THEN** 可找到產生它的 script、輸入資料、設定與 output file
- **AND** output file 包含方法名稱、資料 split 與產生時間或版本資訊

### Requirement: EAA-004 Strong baselines are reported honestly

研究結果 SHALL 同時呈現具代表性的 baseline，包含 persistence、linear regression、IDW 或未校正 base model 中與任務相容者。

#### Scenario: Proposed method does not beat persistence

- **GIVEN** public temporal task 中 persistence 的誤差低於 proposed method
- **WHEN** 結果寫入論文或簡報
- **THEN** 報告保留該結果
- **AND** 研究討論說明 proposed method 的不同用途與限制，而不是隱藏 baseline

### Requirement: EAA-005 Failure cases are part of the evidence package

每次主要 estimator comparison SHALL 保存至少一組誤差最高或代表性失敗案例。

#### Scenario: 產生方法比較摘要

- **GIVEN** 一批已完成的比較結果
- **WHEN** 系統產生研究摘要
- **THEN** 摘要包含平均結果與 worst-case/failure-case 索引
- **AND** 文件分析可能的資料、遮蔽、邊界條件或模型原因

### Requirement: EAA-006 Thesis-facing artifacts stay synchronized

中文論文、英文/IEEE 稿、簡報、圖表與 benchmark 敘述 SHALL 使用一致的研究問題、方法狀態與核心結果。

#### Scenario: 修改核心研究主張

- **GIVEN** research scope、method status 或核心指標發生變更
- **WHEN** 變更準備合併
- **THEN** 相關 thesis Markdown/LaTeX、paper、presentation source 與圖表說明已同步更新
- **AND** 不存在同一方法在不同產物中被描述為不同完成狀態的情形

### Requirement: EAA-007 Claim-to-evidence traceability

每個核心研究問題 SHALL 對應至少一個實驗、至少一個指標與一個明確的可支持主張範圍。

#### Scenario: 準備論文口試報告

- **GIVEN** 一個研究問題或 contribution
- **WHEN** 建立口試投影片
- **THEN** 可找到對應實驗名稱、資料來源、方法比較與結果圖表
- **AND** 同時列出該證據不能支持的主張
