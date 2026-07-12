## MODIFIED Requirements

### Requirement: Single-room three-factor scope

本研究 SHALL 以單一房間自由空間中的溫度、相對濕度與照度目標點估計為核心範圍，並以真實保留感測器或受控 synthetic truth 限定可驗證主張。

#### Scenario: 建立研究情境

- **GIVEN** 一個包含房間幾何、家具佔據區、外部環境與裝置狀態的情境
- **WHEN** 系統執行環境估計
- **THEN** 系統對 `Ω_free` 中的 temperature、humidity 與 illuminance 查詢點輸出估計
- **AND** 不將家具內部、完全遮蔽區域或未量測的整個真實 3-D 場宣稱為已驗證 ground truth

#### Scenario: 說明核心論文主張

- **GIVEN** 論文摘要、研究問題或口試投影片描述本研究能力
- **WHEN** 說明稀疏感測器能支持的範圍
- **THEN** 主張聚焦於可解釋、可校正且可由 holdout target sensors 評估的目標點估計
- **AND** 8-corner/trilinear pipeline 被定位為基線或低階 correction，而不是任意真實場重建定理

### Requirement: Method maturity is explicit

每個論文方法與實驗 SHALL 標示為 implemented、validated、proposed extension 或 future work 其中之一，且狀態必須由可追溯 artifact 支持。

#### Scenario: 新增方法到論文或簡報

- **GIVEN** 一個新 estimator、校正方法或驗證流程
- **WHEN** 它出現在論文、README 或簡報
- **THEN** 內容明確標示其完成狀態
- **AND** 只有存在可重現實驗輸出、資料 split 與評估指標時才能標示為 validated

#### Scenario: 方法只有設計文件

- **GIVEN** 方法已有公式、design 或程式介面規劃，但尚無完整實驗結果
- **WHEN** 該方法出現在研究產物
- **THEN** 它被標記為 proposed extension
- **AND** 不與已驗證 BasePhysics 或 IDW 結果混合呈現

## ADDED Requirements

### Requirement: Research questions map to evidence

每個核心研究問題 SHALL 對應明確的資料來源、方法比較、指標、結果 artifact 與不能支持的延伸主張。

#### Scenario: 審查研究問題

- **GIVEN** 一個列於論文中的 RQ
- **WHEN** 研究者查閱 claim-to-evidence matrix
- **THEN** 可找到該 RQ 的 experiment、baseline、metric 與 result artifact
- **AND** 若證據缺少，matrix 明確標記 evidence missing 而不是以預期結果代替
