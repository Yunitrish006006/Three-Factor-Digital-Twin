# spatial-estimation Specification

## Purpose

定義目前三因子空間估計管線、家具感知感測器配置、校正流程與可替換估計方法的行為契約。

## Requirements

### Requirement: SPE-001 Variable-specific nominal models

系統 SHALL 對溫度、濕度與照度使用各自的 nominal model，而不是以同一個通用公式描述三種物理量。

#### Scenario: 計算三因子 nominal prediction

- **GIVEN** 相同房間、裝置、家具、外部條件與時間
- **WHEN** 系統計算三因子 nominal prediction
- **THEN** 溫度路徑包含熱交換與熱源近似
- **AND** 濕度路徑包含水氣交換與除濕近似
- **AND** 照度路徑包含光源方向、距離、遮蔽與反射近似

### Requirement: SPE-002 Fan is modeled as airflow redistribution, not a primary cooling source

電風扇 SHALL 被建模為動態氣流混合與局部對流增強來源，而不是等同冷氣的主動降溫設備。

#### Scenario: Fan is on during validation

- **GIVEN** electric fan state is `on` with known or logged speed, direction, and oscillation state
- **WHEN** the model estimates target-point temperature and humidity
- **THEN** fan effect is recorded as airflow redistribution or mixing strength
- **AND** reported results are grouped or filtered by fan state
- **AND** fan-on data is not mixed with fan-off data as if they were the same boundary condition

#### Scenario: Fan state is unknown

- **GIVEN** real-room data includes a period where fan state is unknown
- **WHEN** the period is considered for primary validation
- **THEN** the evidence label is downgraded to `unknown_fan_state`
- **AND** the period is not used as primary validation evidence unless the limitation is explicitly stated

### Requirement: SPE-003 Furniture-aware sensor placement

系統 SHALL 排除位於家具佔據區內的基礎感測器點，並可在自由空間加入補償感測器與指定目標點。

#### Scenario: 角落被家具佔據

- **GIVEN** 一個基礎角落感測器位於家具 bounding box 內
- **WHEN** 系統建立 adaptive sensor layout
- **THEN** 該角落感測器不出現在有效配置中
- **AND** 系統嘗試在房間範圍內產生不重複且未被家具佔據的補償點

#### Scenario: 加入指定目標點

- **GIVEN** 使用者提供書桌、枕頭或房間中央等目標點
- **WHEN** 系統建立 adaptive sensor layout
- **THEN** 有效且不重複的目標點會出現在輸出配置中
- **AND** 超出房間邊界的座標會被限制在房間範圍內

### Requirement: SPE-004 Device power calibration precedes spatial correction

當存在有效感測觀測時，系統 SHALL 先校準啟用裝置的影響強度，再估計空間 residual correction。

#### Scenario: 執行感測器校正

- **GIVEN** 一組 active devices、感測器位置與三因子觀測
- **WHEN** 系統執行 calibrated simulation
- **THEN** 系統先估計 active device power scale
- **AND** 再使用校準後模型與觀測差建立 residual correction

### Requirement: SPE-005 Trilinear correction is a low-order correction

系統 SHALL 將 trilinear correction 定位為低階空間殘差近似，而不是任意真實場的唯一重建。

#### Scenario: 使用多個觀測點擬合 correction

- **GIVEN** 一組觀測點與 nominal residual
- **WHEN** 系統擬合八參數 trilinear correction
- **THEN** correction 可表示常數、一階與交互項造成的平滑空間偏差
- **AND** 文件不得宣稱它能重建未觀測的高頻局部變化

### Requirement: SPE-006 Baseline and corrected outputs remain separable

系統 SHALL 能在相同情境與資料切分下比較未校正主模型、IDW baseline、校正模型與 residual-corrected model。

#### Scenario: 比較估計方法

- **GIVEN** 一個具有 truth 或 holdout measurement 的評估情境
- **WHEN** 執行方法比較
- **THEN** 每個方法使用相同輸入點、目標點與評估指標
- **AND** 結果可追溯到方法名稱與設定

### Requirement: SPE-007 Dense grid values are estimates unless simulation truth is declared

非直接量測網格點 SHALL 被標記為 model estimate；只有受控模擬產生的 reference field 才能被標記為 synthetic truth。

#### Scenario: 匯出 3-D grid

- **GIVEN** 系統輸出 16 × 12 × 6 或其他解析度的場域網格
- **WHEN** 該網格不是由真實密集感測取得
- **THEN** 輸出與文件將其標記為 estimated field
- **AND** 不使用 real ground truth 描述該網格
