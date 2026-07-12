## ADDED Requirements

### Requirement: Physical nodes support thesis sensor roles

實體 sensing nodes SHALL 直接支援論文中的 `input` 與 `validation` roles，並將 role 寫入 node config 與上傳 payload。

#### Scenario: Input node participates in calibration

- **GIVEN** 一顆 node 被標示為 `input`
- **WHEN** 後端接收該 node 的 measurements
- **THEN** 這些 measurements 可用於 power calibration、trilinear correction 與 residual feature construction
- **AND** output provenance 記錄該 node 是 measured input

#### Scenario: Validation node is held out

- **GIVEN** 一顆 node 被標示為 `validation`
- **WHEN** 後端執行模型 fitting 或 training
- **THEN** 該 node 的 measurements 被排除
- **AND** 只有 evaluator 在 prediction 完成後可讀取該 node 作為 holdout truth

### Requirement: Furniture-aware deployment uses expanded node count

因房間內有床、書桌、櫃子與其他遮蔽物，正式部署 SHALL 不只依賴 8-corner layout，而要增加自由空間與家具邊界觀測。

#### Scenario: Defensible thesis deployment

- **GIVEN** 研究者需要支撐 pillow、desk、room center 與 near-furniture validation
- **WHEN** 規劃房間節點數量
- **THEN** 使用 8–10 顆 node 作為建議基準
- **AND** 至少 2 顆 node 作為 validation nodes
- **AND** input nodes 覆蓋 window side、AC path、room center、door side 與 furniture boundary

#### Scenario: Dense furniture-aware deployment

- **GIVEN** 家具遮蔽造成多個角落、光照路徑或氣流路徑不可觀測
- **WHEN** 需要更完整的 free-space estimator comparison
- **THEN** 可擴充到 12–14 顆 node
- **AND** 額外 nodes 優先放在家具邊界兩側、床邊、書桌工作面與窗邊高度差位置

### Requirement: Node BOM cost is tracked by deployment level

OpenSpec SHALL 記錄單顆感測節點與多節點部署的成本區間，並將價格定位為 planning estimate。

#### Scenario: Estimate 10-node deployment

- **GIVEN** v1 node 單價包含 ESP32-C3、DHT11、BH1750、外殼、線材與 USB 供電材料
- **WHEN** 估算 defensible 10-node deployment
- **THEN** 文件輸出低、中、高三種預算區間
- **AND** 成本不包含 3D 列印失敗、運費、備品耗損與替代高精度感測器升級

### Requirement: DHT11 is low-cost input, not high-precision reference

使用 DHT11 的 node SHALL 被定位為低成本稀疏感測輸入；若作為 validation node，論文 SHALL 說明其精度限制與校正流程。

#### Scenario: DHT11 validation node is used at pillow

- **GIVEN** pillow validation node 使用 DHT11
- **WHEN** 報告 real target-point error
- **THEN** 方法段落說明 DHT11 為低成本 sensor，已做同位置 offset calibration
- **AND** 不將單顆 DHT11 讀值描述為高精度實驗室 reference

### Requirement: Light sensor should produce calibrated lux

正式照度節點 SHOULD 使用 BH1750 或等價 digital lux sensor；若使用 LDR，資料 SHALL 經過校正才可進入 illuminance_lux 欄位。

#### Scenario: LDR-only node reports light

- **GIVEN** node 使用 LDR 而非 BH1750
- **WHEN** node 上傳資料
- **THEN** raw ADC value 保存於 `raw.light_adc`
- **AND** 未校正前只能標示為 `relative_light`
- **AND** 不能直接參與 lux-based validation metric
