## MODIFIED Requirements

### Requirement: Furniture-aware sensor placement

系統 SHALL 排除位於家具佔據區內的基礎感測器點，並將補償感測器、目標點與驗證感測器以不同角色輸出。

#### Scenario: 角落被家具佔據

- **GIVEN** 一個基礎角落感測器位於 `Ω_occ` 內
- **WHEN** 系統建立 adaptive sensor layout
- **THEN** 該角落感測器不出現在有效 `S_input` 中
- **AND** 系統嘗試在 `Ω_free` 內產生不重複的補償 input sensors
- **AND** 每個補償點記錄來源角落與產生原因

#### Scenario: 加入研究目標點

- **GIVEN** 使用者提供 pillow、desk、room center 或 near-furniture target
- **WHEN** 系統建立研究配置
- **THEN** 目標位置被記錄為 `V_target`
- **AND** 只有明確指定為量測輸入的 target sensor 才可進入 `S_input`
- **AND** 指定為 ground truth 的 target sensor 只進入 `S_validation`

### Requirement: Baseline and corrected outputs remain separable

系統 SHALL 能在相同 `S_input`、`S_validation`、target points、資料 split 與指標下比較未校正主模型、IDW、trilinear-corrected model、free-space estimators 與 residual-corrected variants。

#### Scenario: 比較估計方法

- **GIVEN** 一個具有 synthetic truth 或 holdout measurement 的評估情境
- **WHEN** 執行 estimator comparison
- **THEN** 每個方法使用相同 input observations 與 validation targets
- **AND** 每個結果記錄 method、configuration、support nodes、runtime 與 provenance
- **AND** validation observations 不得參與任何方法的 fitting

## ADDED Requirements

### Requirement: Sensor roles prevent evaluation leakage

系統 SHALL 在資料結構與 evaluator 層強制區分 `S_input` 與 `S_validation`。

#### Scenario: 擬合 power calibration

- **GIVEN** 情境同時包含 input 與 validation observations
- **WHEN** 系統擬合 active-device power scale
- **THEN** 只有 `S_input` observations 會被讀取
- **AND** validation values 不影響係數、normalization 或 model selection

#### Scenario: 評估 holdout target

- **GIVEN** 一個 validation sensor 具有真實三因子觀測
- **WHEN** 系統完成該位置的 prediction
- **THEN** evaluator 才讀取 validation observation 計算 error
- **AND** prediction artifact 記錄該點在 fitting 階段被排除

### Requirement: Fan state is an experimental condition

電風扇 SHALL 被視為獨立 experimental condition，因為它會改變局部氣流、溫度梯度、濕度混合與感測器附近對流，而不是單純背景噪音。

#### Scenario: Fan-on data enters validation

- **GIVEN** real-room validation data is collected while the fan is on
- **WHEN** results are summarized
- **THEN** the report includes `fan_on`, `fan_speed`, `fan_direction`, and `fan_oscillation` if available
- **AND** metrics are grouped separately from fan-off periods
- **AND** the claim boundary states that fan-on airflow was part of the boundary condition

#### Scenario: Fan state cannot be recovered

- **GIVEN** a time window has unknown fan state
- **WHEN** building the primary validation split
- **THEN** that window is marked `unknown_fan_state`
- **AND** it is excluded from primary validation unless explicitly analyzed as uncertain data

### Requirement: Fan-aware nodes cover airflow path and dead zone

家具房間中的實體 node deployment SHALL 包含電風扇氣流路徑與風扇難以到達的相對靜止區。

#### Scenario: Fan is present in bedroom_01

- **GIVEN** a fan has a known approximate location and facing direction
- **WHEN** the node deployment map is created
- **THEN** at least one input node is placed in the primary fan airflow path
- **AND** at least one input or validation node is placed in a fan-shadow/dead-zone region
- **AND** node metadata records distance to fan, relative angle, and whether it is in the main airflow path

### Requirement: Free-space domain is explicit

系統 SHALL 將可估計空氣空間定義為 `Ω_free = Ω_room \ Ω_occ`，並拒絕將家具佔據點當作一般空氣查詢點。

#### Scenario: 查詢點位於家具內部

- **GIVEN** 一個 query point 位於 furniture occupied volume
- **WHEN** estimator 接收該 query
- **THEN** 系統回傳 invalid/occupied status 或明確低可信度結果
- **AND** 不將該值納入自由空間 error summary

### Requirement: Estimators use a common contract

所有可比較 estimators SHALL 透過共同介面接收相同 context 並回傳帶有 provenance 的 `Estimate`。

#### Scenario: 執行相同 query

- **GIVEN** BasePhysics、IDW 與一個 free-space estimator 已註冊
- **WHEN** evaluator 對相同 target 與 metric 呼叫各 estimator
- **THEN** 每個 estimator 回傳 value、method、support nodes、confidence 與 provenance
- **AND** evaluator 不需要依方法改變 ground-truth lookup 邏輯

### Requirement: Two-dimensional triangulation is height-specific

`Triangulation2DEstimator` SHALL 只在明確指定的高度平面建立有效 triangles 並使用 barycentric interpolation。

#### Scenario: Pillow-height target lies inside a valid triangle

- **GIVEN** 三個同平面自由空間支撐點形成非退化 triangle
- **AND** pillow target 位於 triangle 內
- **WHEN** estimator 預測 target value
- **THEN** 使用非負且總和為一的 barycentric weights
- **AND** output 記錄 triangle vertices

#### Scenario: Target has no valid containing triangle

- **GIVEN** target 不在任何有效 triangle 內或 triangle 穿越不允許的 occupied region
- **WHEN** estimator 嘗試預測
- **THEN** 回傳 unavailable/fallback 狀態
- **AND** 不以任意三點外插冒充局部 triangle interpolation

### Requirement: Three-dimensional interpolation uses valid tetrahedra

`Tetrahedral3DEstimator` SHALL 只使用非退化、符合自由空間限制且包含 query point 的 tetrahedron。

#### Scenario: Four points are coplanar

- **GIVEN** 四個候選支撐點無法形成有效體積
- **WHEN** 建立 tetrahedron candidates
- **THEN** 該 cell 被拒絕並記錄 degenerate reason

### Requirement: Cell-IDW fuses valid local estimates

`Cell-IDWFusionEstimator` SHALL 先過濾有效 local cells，再以正規化 centroid-distance weights 融合 local estimates。

#### Scenario: Multiple valid cells support one target

- **GIVEN** target 具有多個有效 triangle 或 tetrahedron local estimates
- **WHEN** Cell-IDW 執行融合
- **THEN** 權重與總和正規化為一
- **AND** 輸出記錄 distance exponent、top-k、valid cell count 與 rejected reasons

### Requirement: Occlusion policy depends on metric

系統 SHALL 允許 temperature/humidity 使用 soft obstruction penalty，並要求 illuminance direct-support 使用 visibility constraint。

#### Scenario: Furniture blocks a light-support path

- **GIVEN** 光源或 illuminance support cell 到 target 的路徑被家具完全遮擋
- **WHEN** illuminance estimator 建立有效支撐
- **THEN** 該 direct support 被拒絕或權重設為零
- **AND** 不以純歐氏距離跨越遮蔽物
