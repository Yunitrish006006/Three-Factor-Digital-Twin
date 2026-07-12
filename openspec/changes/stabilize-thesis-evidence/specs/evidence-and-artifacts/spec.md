## MODIFIED Requirements

### Requirement: Temporal data uses leakage-resistant splits

具有時間相依性的真實資料、residual dataset 與公開資料 SHALL 在任何 normalization、training 或 model selection 之前完成 leakage-resistant split，並記錄 train、validation 與 test 範圍。

#### Scenario: 評估連續多日資料

- **GIVEN** 一段具有時間順序的感測器資料
- **WHEN** 建立訓練與測試集
- **THEN** 系統使用 blocked split、leave-one-day-out 或 event-separated split
- **AND** 輸出記錄每個 split 的日期、索引與 held-out sensor roles
- **AND** validation/test rows 不參與 normalization statistics

#### Scenario: 建立 residual dataset

- **GIVEN** estimator outputs 與對應 observations
- **WHEN** 系統建立 residual training rows
- **THEN** scenario/day/sensor holdout 已經決定
- **AND** held-out observations 不出現在 residual training labels 或 features 中

### Requirement: Metrics are reproducible

每個論文或簡報中的核心數值 SHALL 可由命名腳本、明確輸入 split、method configuration 與版本化輸出重新產生。

#### Scenario: 引用 target-point error

- **GIVEN** 論文或簡報引用 pillow、desk、center 或 near-furniture 的 MAE/RMSE/MaxErr
- **WHEN** 研究者追查該數值
- **THEN** 可找到產生它的 script、raw/normalized input、sensor split、method config 與 output JSON
- **AND** output 記錄 validation sensor 未參與 fitting

### Requirement: Claim-to-evidence traceability

每個核心研究問題 SHALL 對應至少一個實驗、至少一個 baseline、至少一個指標、一個結果 artifact，以及明確的 supported/unsupported claim boundary。

#### Scenario: 準備論文口試報告

- **GIVEN** 一個研究問題或 contribution
- **WHEN** 建立口試投影片
- **THEN** claim-to-evidence matrix 提供 dataset/split、comparison、metric、figure/table 與 method status
- **AND** 投影片 speaker notes 說明該證據不能支持的延伸主張

## ADDED Requirements

### Requirement: Real target-point validation uses held-out measurements

真實目標點準確度 SHALL 只以未參與 calibration、training 與 model selection 的 measurement 計算。

#### Scenario: 驗證 pillow target

- **GIVEN** pillow sensor 被指定為 `S_validation`
- **WHEN** 系統使用其他 `S_input` 預測 pillow position
- **THEN** evaluator 比較 prediction 與 pillow measurement
- **AND** 報告將結果標示為 real target-point evidence

#### Scenario: 只有單一真實 target

- **GIVEN** 目前只有 pillow location 具有完整 holdout measurement
- **WHEN** 撰寫結果與結論
- **THEN** 主張限制在 pillow target 或相同 validation setup
- **AND** 不推論所有未量測位置都具有相同準確度

### Requirement: Experiment summaries include runtime and worst cases

每個主要 estimator comparison SHALL 同時輸出 aggregate metrics、runtime 與代表性 worst cases。

#### Scenario: 建立 comparison summary

- **GIVEN** 一批 method-by-target predictions
- **WHEN** 系統產生 comparison JSON/CSV
- **THEN** 每個 method 包含 MAE、RMSE、MaxErr、bias 與 runtime
- **AND** 摘要列出至少一個 worst-case timestamp/target/scenario
- **AND** 文件分析可能的遮蔽、外氣、裝置狀態、資料品質或模型原因

### Requirement: Evidence artifacts identify provenance

每個估計與圖表 SHALL 能區分 measured、synthetic truth、nominal estimate、corrected estimate 與 pseudo support value。

#### Scenario: 匯出 target comparison figure

- **GIVEN** 圖中同時包含 measured 與 model-predicted series
- **WHEN** 產生圖表
- **THEN** legend 與 metadata 清楚標示各 series provenance
- **AND** pseudo values 不使用 ground truth 標籤

### Requirement: Thesis synchronization is checked before merge

影響研究主張、方法完成狀態或核心結果的變更 SHALL 在合併前執行跨產物同步檢查。

#### Scenario: 更新 estimator 結果

- **GIVEN** 新 comparison 改變最佳方法、核心數值或 method status
- **WHEN** 變更準備合併
- **THEN** 中文論文、英文/IEEE 稿、presentation source、speaker notes、figures 與 summary JSON 已更新
- **AND** 同一 metric 在各產物中的數值與 evidence label 一致

### Requirement: Intervention evidence is separate from action ranking

真實 before/after intervention SHALL 被視為獨立證據層，未完成時不得以 counterfactual ranking 代替。

#### Scenario: 尚未執行介入實驗

- **GIVEN** 系統只有模型預測的 action ranking
- **WHEN** 撰寫控制相關 contribution
- **THEN** 文件標示為 counterfactual recommendation
- **AND** causal effectiveness 被列為 evidence missing 或 future work
