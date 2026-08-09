# research-contract Specification

## Purpose

定義本研究目前可成立的研究範圍、研究問題、方法角色與主張邊界，避免論文、程式與簡報對研究目標產生不同解讀。

## Requirements

### Requirement: RCT-001 Single-room three-factor scope

本研究 SHALL 以單一房間中的溫度、相對濕度與照度估計為核心範圍。

#### Scenario: 建立研究情境

- **GIVEN** 一個包含房間幾何、家具、外部環境與裝置狀態的情境
- **WHEN** 系統執行環境估計
- **THEN** 系統輸出 temperature、humidity 與 illuminance 三個環境變數
- **AND** 不將多房間交換或完整 CFD 流場列為目前已驗證能力

### Requirement: RCT-002 Non-networked appliance impact learning

本研究 SHALL 將冷氣、窗戶與照明視為可能無法直接回報完整狀態的環境作用來源，並以觀測前後差異或情境參數描述其影響。

#### Scenario: 裝置缺少遙測介面

- **GIVEN** 一個無法透過 API 取得完整運轉狀態的裝置
- **WHEN** 系統取得裝置作用前後的環境觀測
- **THEN** 系統可建立或更新該裝置對三因子的影響估計
- **AND** 不將推估狀態宣稱為裝置原生遙測值

### Requirement: RCT-003 Interpretable model remains the primary estimator

本研究 SHALL 以可解釋的變數專屬 nominal model 作為主估計器，資料驅動模型只負責修正主模型剩餘誤差。

#### Scenario: 啟用 hybrid residual

- **GIVEN** 已有一組 nominal prediction 與可用的 residual model
- **WHEN** 系統啟用 hybrid residual inference
- **THEN** 最終估計為 nominal prediction 加上 residual correction
- **AND** 報告中可分別輸出 base 與 corrected 結果

### Requirement: RCT-004 Interface layers are not the core scientific contribution

MCP、Web、CLI 與 agent bridge SHALL 被定位為模型能力的服務與展示介面，而不是主要估計方法或主要學術貢獻。

#### Scenario: 口試或論文介紹系統架構

- **GIVEN** 研究報告需要介紹 MCP 或 Web demo
- **WHEN** 說明其研究角色
- **THEN** 內容先說明估計模型與驗證證據
- **AND** 將 MCP/Web 放在應用或系統整合層

### Requirement: RCT-005 Recommendation is counterfactual ranking

在完成真實介入驗證之前，控制輸出 SHALL 被描述為模型式反事實候選動作排序。

#### Scenario: 輸出候選動作

- **GIVEN** 一個有效目標點、完整三因子目標與候選裝置動作
- **WHEN** 系統計算候選動作的預測效果
- **THEN** 系統依預測 comfort penalty 改善幅度排序
- **AND** 不宣稱排序第一的動作已被證明能在真實房間造成因果改善

### Requirement: RCT-006 Method maturity is explicit

每個論文方法與實驗 SHALL 標示為 implemented、validated、proposed extension 或 future work 其中之一。

#### Scenario: 新增方法到論文或簡報

- **GIVEN** 一個新 estimator、校正方法或驗證流程
- **WHEN** 它出現在論文、README 或簡報
- **THEN** 內容明確標示其完成狀態
- **AND** 只有存在對應實驗輸出時才能標示為 validated
