# sensing-node Specification

## Purpose

定義本研究使用的低成本三因子感測節點，使硬體部署、成本估算、節點數量、資料格式與論文中的 `input` / `validation` sensor roles 保持一致。

## Requirements

### Requirement: Node measures three environmental factors

每個正式研究節點 SHALL 至少量測溫度、相對濕度與照度三項資料。

#### Scenario: 節點上傳 state payload

- **GIVEN** 一個已部署於房間內的感測節點
- **WHEN** 節點完成一次取樣
- **THEN** payload 包含 `temperature_c`、`humidity_rh` 與 `illuminance_lux`
- **AND** payload 包含 `node_id`、`room_id`、`role`、`timestamp` 與 `position_m`

### Requirement: V1 hardware uses ESP32-C3, DHT11, and digital light sensor

V1 節點 SHALL 以 ESP32-C3 作為無線 MCU，DHT11 作為低成本溫濕度感測器，並優先使用 BH1750 或等價 I2C digital lux sensor 作為照度感測器。

#### Scenario: 建立 v1 node BOM

- **GIVEN** 研究者準備採購 v1 感測節點材料
- **WHEN** 產生 BOM
- **THEN** 每個 node 至少包含 ESP32-C3 dev board、DHT11、BH1750 或等價 digital lux sensor、外殼、線材與 USB 供電材料
- **AND** 若以 LDR 取代 BH1750，該 node 必須標記為 `relative_light_only`，不能直接輸出未校正的 `illuminance_lux`

### Requirement: Node roles are deployment roles

每個實體 node SHALL 在部署表中標記為 `input` 或 `validation`；只有模型產生或非量測位置才使用 `target` 或 `pseudo`。

#### Scenario: 部署枕頭驗證節點

- **GIVEN** 一顆 node 被放在 pillow target 並用於驗證
- **WHEN** 建立 node config
- **THEN** 該 node 的 role 是 `validation`
- **AND** 該 node 的 measurements 不得進入 calibration、trilinear fitting 或 residual training

### Requirement: Furniture-aware room needs more than corner nodes

房間存在家具遮蔽時，node deployment SHALL 包含自由空間、家具邊界與使用者目標位置，而不是只部署原始 8-corner nodes。

#### Scenario: 房間有床、書桌與櫃子

- **GIVEN** 家具佔據造成部分角落或視線路徑不可用
- **WHEN** 規劃節點部署
- **THEN** deployment 至少包含 room center、window side、AC airflow path、desk、pillow 與 near-furniture boundary 類型
- **AND** 每個 node 記錄座標、高度、光照方向與附近家具關係

### Requirement: Deployment levels define expected node count

研究部署 SHALL 以 minimum、defensible、dense 三種等級描述節點數量，避免把單一節點數視為固定設計。

#### Scenario: 口試前可防守部署

- **GIVEN** 研究者需要口試前可防守的真實目標點驗證
- **WHEN** 選擇 deployment level
- **THEN** 建議使用 `defensible` level：8–10 顆 node，其中至少 2 顆為 validation nodes
- **AND** 若只完成 4–6 顆 node，報告必須標記為 minimum deployment 並限制主張範圍

### Requirement: Calibration precedes formal collection

正式資料收集前，所有實體 nodes SHALL 先完成同位置校正與部署後 sanity check。

#### Scenario: 多顆 DHT11 節點準備進入正式實驗

- **GIVEN** 多顆 node 已組裝完成
- **WHEN** 開始正式實驗前
- **THEN** 所有 nodes 需在同一位置同步記錄至少 12 小時
- **AND** 產生 temperature offset、humidity offset 與 light scale 或 light offset
- **AND** 校正參數需寫入 node metadata 或資料前處理設定

### Requirement: Cost estimate is a planning artifact

BOM cost estimate SHALL 被標記為採購規劃用途，並保留單顆、minimum、defensible 與 dense deployment 的預估成本。

#### Scenario: 更新採購數量

- **GIVEN** node 單價區間或節點數量改變
- **WHEN** 更新 BOM 文件
- **THEN** 同步更新 per-node、6-node、8-node、10-node、12-node 與 14-node 成本估算
- **AND** 文件明確提醒最終價格以購買當日供應商報價為準

### Requirement: Node payload supports provenance and quality flags

節點資料 SHALL 保留 raw readings、calibrated readings、quality flags 與 firmware metadata。

#### Scenario: 節點讀值異常

- **GIVEN** DHT11 回傳錯誤或光照讀值超出有效範圍
- **WHEN** node 上傳資料
- **THEN** payload 的 quality flags 標示對應 sensor 狀態
- **AND** 後端不得把錯誤讀值直接納入正式 validation metric
