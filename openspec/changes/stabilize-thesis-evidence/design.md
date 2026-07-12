## Context

現有專案已具備：

- 變數專屬 nominal models
- 冷氣、窗戶、照明影響函數
- active-device power calibration
- 八參數 trilinear residual correction
- furniture-aware adaptive sensor placement
- hybrid residual neural network
- synthetic validation suite、window matrix、CU-BEMS/SML2010 task-aligned benchmark
- 中文論文、IEEE 稿、PPT 產生器與 MCP/Web demo

目前主要風險不是缺少模型，而是**研究證據與方法角色尚未完全對齊**。尤其 target point 被加入一般 sensor list 時，若同時參與 power calibration 或 residual fitting，就不能再當成獨立 ground truth。另一個風險是家具補償點、三線性校正與未來 simplex estimators 的功能界線不清楚，容易在論文中被寫成已經完成且已驗證的同一套方法。

## Goals / Non-Goals

### Goals

- 建立不洩漏 target measurement 的 holdout validation pipeline。
- 將房間空間、家具佔據空間與自由空間明確分離。
- 將現有主模型、baseline 與 proposed estimators 放入同一比較介面。
- 讓每個結果都包含資料 split、method config、metric、failure case 與 provenance。
- 讓論文、IEEE 稿與簡報以同一份 claim-to-evidence matrix 為依據。

### Non-Goals

- 不在本 change 中宣稱重建真實房間完整 3-D dense field。
- 不將 pseudo nodes 當成新的真實觀測。
- 不保證 2-D triangulation、3-D tetrahedral 或 Cell-IDW 一定優於 base physics。
- 不在本 change 中完成自動閉環控制。
- 不把 MCP protocol 或 agent integration 當成新研究方法。

## Decision 1: Separate geometry, observation, and evaluation roles

### Model

```text
Ω_room                 房間幾何體積
Ω_occ                  家具佔據體積聯集
Ω_free = Ω_room-Ω_occ  可估計空氣空間

V_geom                  幾何與邊界節點
V_target                枕頭、書桌、房間中央等研究目標
V_pseudo                模型產生的支撐值，不是量測

S_input                 校正與推論可使用的真實感測器
S_validation            只在評估階段讀取的真實感測器
S_all = S_input ∪ S_validation
S_input ∩ S_validation = ∅
```

### Rationale

目前 `create_adaptive_sensor_layout()` 可以加入 target sensors，但沒有角色欄位。將 sensor role 變成一級概念，可以從資料結構層阻止 evaluation leakage，而不是靠呼叫端自律。

### Consequence

- calibration、impact learning 與 residual fitting 只能接收 `S_input`。
- evaluation 可以同時讀取預測值與 `S_validation` 真值。
- `V_target` 可存在但沒有感測器；有真實感測器時才同時屬於 validation location。

## Decision 2: Preserve BasePhysicsEstimator as the primary baseline

### Rationale

現有 nominal + calibration + trilinear pipeline 已經是專案最成熟、可解釋且有結果的核心。新方法應該在它上面比較或後處理，而不是先刪除它。

### Interface

```python
class Estimator(Protocol):
    name: str

    def fit(self, context: EstimationContext) -> None: ...
    def predict(self, query: QueryPoint, metric: str) -> Estimate: ...
```

`Estimate` 至少包含：

```text
value
method
metric
query_position
support_nodes
is_measured
confidence
provenance
```

### Estimators

- `BasePhysicsEstimator`
- `SensorIDWEstimator`
- `Triangulation2DEstimator`
- `Tetrahedral3DEstimator`
- `CellIDWFusionEstimator`
- `ResidualCorrector(base_estimator)`

## Decision 3: Use variable-aware geometry constraints

### Temperature / Humidity

- cell 或 support path 穿過家具時，使用 hard rejection 或 soft obstruction penalty。
- 允許非視線傳播，但要降低跨家具支撐的可信度。

### Illuminance

- direct-light 相關 estimator 必須使用 visibility constraint。
- 被完全遮蔽的 support cell 不得以純距離權重跨越障礙物。

### Rationale

三種環境量可以共用 estimator interface，但不能假設同樣的傳播規則。

## Decision 4: Define simplex estimators precisely

### 2-D triangulation

- 只在明確高度平面使用，例如 pillow height、desk height、breathing height。
- 目標點必須位於有效 triangle 內，才使用 barycentric interpolation。

### 3-D tetrahedral interpolation

- 四個節點必須形成非退化 tetrahedron。
- cell 不得與 `Ω_occ` 產生不允許的交疊。
- 目標點在 tetrahedron 內時使用 barycentric weights。

### Cell-IDW fusion

對每個有效單元 `u` 先求局部估計 `F_u(q)`，再依 cell centroid 距離融合：

```text
w_u(q) = obstruction_u(q) / (||q-c_u|| + ε)^p
F(q) = Σ w_u(q)F_u(q) / Σ w_u(q)
```

必須輸出 `p`、top-k、valid cell count 與 rejection reason，方便敏感度與失敗分析。

## Decision 5: Use leakage-resistant validation

### Spatial holdout

- 每次 fold 將一組真實 sensors 指定為 `S_validation`。
- 所有 calibration、impact learning、residual training 只使用 `S_input`。
- 評估只在 `S_validation` 位置計算。

### Temporal validation

真實多日資料優先使用：

- leave-one-day-out
- blocked train/validation/test split
- event-separated before/after split

不得隨機打散相鄰時間點後聲稱 generalization。

## Decision 6: Standardize experiment outputs

每次比較輸出一個 machine-readable summary：

```json
{
  "dataset": "...",
  "split": "...",
  "method": "...",
  "method_status": "implemented|validated|proposed|future",
  "metrics": {
    "temperature": {"mae": 0, "rmse": 0, "max_error": 0},
    "humidity": {"mae": 0, "rmse": 0, "max_error": 0},
    "illuminance": {"mae": 0, "rmse": 0, "max_error": 0}
  },
  "runtime_ms": 0,
  "worst_cases": [],
  "provenance": {}
}
```

### Required comparisons

- BasePhysics without residual
- IDW
- each implemented free-space estimator
- estimator + residual corrector
- occlusion on/off ablation

## Decision 7: Claim-to-evidence matrix is the thesis source of truth

建立單一表格，欄位至少包含：

```text
research question
claim
method status
dataset/split
baseline
metric
result artifact
supported claim
unsupported extension
thesis section
presentation slide
```

中文論文、英文稿與簡報不得自行維護互相矛盾的核心數值或完成狀態。

## Risks / Trade-offs

### Risk: Scope grows too large

Mitigation：先完成 sensor role separation、holdout evaluation 與 BasePhysics/IDW 比較，再依序加入 2-D、3-D、Cell-IDW。每個 estimator 可獨立交付。

### Risk: Real sensor count is insufficient

Mitigation：先使用 pillow、desk、center、near-furniture 四類目標；若硬體不足，採輪替量測，但必須記錄時間與裝置狀態，不能把不同時段直接視為同時空間真值。

### Risk: Synthetic result dominates

Mitigation：所有 full-field 圖表都標記 synthetic；真實證據只報告 measured target points。

### Risk: Residual model learns the held-out target indirectly

Mitigation：split 在建立任何 residual dataset 之前完成；validation sensor 的 observation 不得進入 normalization statistics、power calibration、feature fitting 或 model selection。

## Migration Plan

1. 新增 sensor/node role，不改變現有 `Sensor(name, position)` 呼叫的預設行為。
2. 將現有 scenarios 明確產生 `input_sensors` 與 `validation_sensors`。
3. 以 adapter 包裝目前 `DigitalTwinModel` 為 `BasePhysicsEstimator`。
4. 建立共用 evaluation runner，先接 BasePhysics 與 IDW。
5. 依序加入 free-space estimators。
6. 重新產生研究輸出與 thesis artifacts。
7. 驗證完成後再更新 main specs 並 archive change。

## Open Questions

- 真實房間目前可同時部署多少個 validation sensors？
- 書桌、枕頭與房間中央的正式座標與高度是否已固定？
- 3-D estimator 是否有足夠不共面的實測支撐點，或應先以 2-D fixed-height evaluation 為主？
- before/after intervention 是否納入口試前必做，或列為 future work？
