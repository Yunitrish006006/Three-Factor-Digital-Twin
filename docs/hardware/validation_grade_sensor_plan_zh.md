# validation-grade 溫濕度感測器升級規劃

## 1. 結論

本研究不需要一次將所有 sensing nodes 升級為高階溫濕度感測器；較合理的策略是區分：

```text
S_input：可使用 DHT11 作為 low-cost input-grade sensing
S_validation：建議使用 SHT31 / SHT35 / SHT40 / SHT45 或同等級 sensor
reference：建議使用 SHT35 / SHT45 或較高階溫濕度計
```

核心原因是：`S_validation` 會被用來計算 target-point error，因此其感測器不確定性會直接影響論文結論的可信度。

## 2. 感測器等級定義

| 等級 | 用途 | 建議元件 | 論文定位 |
|---|---|---|---|
| input-grade | 稀疏空間輸入、模型校正、裝置影響學習 | DHT11 / SHT31 / SHT40 | 低成本觀測點 |
| validation-grade | pillow、desk、room center 等 target holdout truth | SHT31 / SHT35 / SHT40 / SHT45 | target-point validation |
| reference-grade | 同位置校正基準 | SHT35 / SHT45 / 較高階溫濕度計 | calibration reference |

## 3. 建議採購優先順序

### 最低可防守版本

```text
SHT40 或 SHT31 × 2
```

用途：

- `validation_pillow`
- `validation_desk`

估計：NT$300–900。

### 較穩版本

```text
SHT40 / SHT31 × 2
SHT45 / SHT35 × 1
```

用途：

- `validation_pillow`
- `validation_desk`
- `reference_calibration`

估計：NT$900–1,800。

### 全面升級版本

```text
SHT31 / SHT40 / SHT45 × 8–10
```

用途：

- 全部 sensing nodes 同等級化。

估計：NT$1,600–6,000+，視模組來源與等級而定。

## 4. 成本估算

> 本表為 planning estimate，不是即時報價。實際價格需依採購日期、供應商、模組版本、運費與備品數量更新。

| 項目 | 單顆低估 | 單顆中估 | 單顆高估 | 備註 |
|---|---:|---:|---:|---|
| SHT31 module | NT$150 | NT$250 | NT$450 | validation-grade 入門 |
| SHT40 module | NT$120 | NT$220 | NT$400 | validation-grade 入門，常見模組價格浮動大 |
| SHT35 module | NT$250 | NT$450 | NT$800 | 可作 reference-grade |
| SHT45 module | NT$300 | NT$500 | NT$900 | 可作 reference-grade |

## 5. 對既有 node BOM 的影響

原本 input-grade v1 node 以 DHT11 估算，單顆材料成本約 NT$215–605，含 15% 備品耗損後約 NT$248–696。

若將一顆 DHT11 node 改為 SHT40 / SHT31，通常是替換溫濕度模組，不需要更換 ESP32-C3 或 BH1750。因此 upgrade cost 可用下列方式估：

```text
upgrade_delta ≈ SHT module cost - DHT11 module cost
```

粗估：

| 升級 | 每顆增加成本 |
|---|---:|
| DHT11 → SHT40 | 約 NT$80–370 |
| DHT11 → SHT31 | 約 NT$100–420 |
| DHT11 → SHT45 | 約 NT$250–850 |

## 6. 推薦實作方案

目前最建議的配置：

| Node | Role | Sensor grade | 建議溫濕度 sensor |
|---|---|---|---|
| `validation_pillow` | validation | validation-grade | SHT40 / SHT31 / SHT45 |
| `validation_desk` | validation | validation-grade | SHT40 / SHT31 / SHT45 |
| `reference_calibration` | reference | reference-grade | SHT45 / SHT35 |
| 其他 input nodes | input | input-grade | DHT11 或逐步升級 SHT31/SHT40 |

這樣成本不會爆，但可以讓 validation truth 的可信度明顯高於 DHT11-only 設計。

## 7. 論文寫法

建議寫法：

> 本研究將 sensing nodes 分為 input-grade 與 validation-grade。input-grade nodes 以低成本 DHT11 為主，用於稀疏空間觀測與模型校正；validation-grade nodes 則採用較高精度之 SHT31/SHT40/SHT45 等級感測器，用於 pillow 與 desk 等 target-point holdout evaluation。此設計避免將低成本感測器的解析度與精度限制誤解為模型估計能力。

若仍暫時使用 DHT11 作為 validation node，應寫：

> 由於 validation node 仍使用 DHT11，本階段 real target-point result 應視為 preliminary low-cost validation，不能解釋為高精度物理量測結果。

## 8. 避免寫法

- 「DHT11 validation truth 可以支撐 0.1°C 絕對精度結論。」
- 「模型誤差小於 sensor accuracy 代表模型比感測器更準。」
- 「所有 input 與 validation nodes 可不區分 sensor grade。」
- 「reference node 不需要紀錄 sensor model。」
