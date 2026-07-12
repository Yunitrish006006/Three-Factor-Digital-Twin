# 三因子感測節點 BOM 與部署估價

> 本估價是研究規劃用的 planning estimate，非即時報價。實際採購前需依購買當日供應商、運費、套件規格與備品數量重新確認。

## 1. 單顆 v1 node BOM

| 項目 | 建議規格 | 低估 | 中估 | 高估 | 備註 |
|---|---|---:|---:|---:|---|
| ESP32-C3 Dev Board | USB-C 優先 | NT$80 | NT$120 | NT$180 | 不建議買無 USB 燒錄座版本 |
| DHT11 module | 已含 pull-up 模組較方便 | NT$20 | NT$30 | NT$45 | 低成本，需同位置校正 |
| BH1750 module | I2C digital lux sensor | NT$25 | NT$40 | NT$70 | 優先於 LDR |
| 外殼 | 打孔塑膠盒或 3D 列印 | NT$25 | NT$50 | NT$90 | 需通風與透光孔 |
| 線材／洞洞板／排針 | 固定接線 | NT$15 | NT$30 | NT$60 | 正式部署建議焊接 |
| USB 線與供電 | 5V USB | NT$40 | NT$70 | NT$120 | 可視現有材料扣除 |
| 雜項備品 | 電阻、熱縮套、雙面膠 | NT$10 | NT$20 | NT$40 | 每顆平均攤提 |
| **單顆小計** |  | **NT$215** | **NT$360** | **NT$605** | 不含運費與失敗耗損 |

## 2. 建議加 15% 備品與耗損

| 單顆估價 | 加 15% 後 |
|---:|---:|
| NT$215 | NT$248 |
| NT$360 | NT$414 |
| NT$605 | NT$696 |

後續表格採用加 15% 後的估計，避免少估線材、外殼修改、焊接失敗與備品。

## 3. 部署等級與總價

| 部署等級 | 節點數 | 用途 | 低估 | 中估 | 高估 |
|---|---:|---|---:|---:|---:|
| Minimum | 6 | 初步 pillow / center / window / AC path 驗證 | NT$1,488 | NT$2,484 | NT$4,176 |
| Defensible-A | 8 | 口試前較可防守，含至少 2 validation | NT$1,984 | NT$3,312 | NT$5,568 |
| Defensible-B | 10 | 建議基準，可覆蓋家具邊界與多目標點 | NT$2,480 | NT$4,140 | NT$6,960 |
| Dense | 12 | 支援 free-space estimator comparison | NT$2,976 | NT$4,968 | NT$8,352 |
| Dense+ | 14 | 家具遮蔽多、要做更多 holdout folds | NT$3,472 | NT$5,796 | NT$9,744 |

## 4. 依你房間家具狀況的建議

因房間有床、書桌、櫃子與牆邊遮蔽，節點不應只放 8 個角落。建議採用 **10 顆 node** 作為第一個可防守版本：

| 類型 | 數量 | Role | 目的 |
|---|---:|---|---|
| 房間中央／自由空間 | 1 | input | 空間基準 |
| 窗邊 | 1 | input | 外氣與日照影響 |
| 冷氣氣流路徑 | 1 | input | AC impact learning |
| 門邊或回風側 | 1 | input | 房間交換與邊界效應 |
| 家具邊界左側 | 1 | input | 遮蔽前後差異 |
| 家具邊界右側 | 1 | input | 遮蔽前後差異 |
| 書桌工作面 | 1 | validation | 工作區目標點 |
| 枕頭區 | 1 | validation | 睡眠區目標點 |
| 床邊自由空間 | 1 | input 或 validation | 床造成的局部場差異 |
| 備用／輪替點 | 1 | input 或 validation | 用於 near-window、near-cabinet、near-door fold |

建議 role 分配：

```text
S_input: 7–8 顆
S_validation: 2–3 顆
```

## 5. 6 / 8 / 10 / 12 / 14 顆節點部署建議

### 6 顆：Minimum

```text
input_center
input_window_side
input_ac_path
input_door_side
validation_pillow
validation_desk
```

可支持：

- pillow / desk 兩點 holdout validation
- 初步 AC / window 事件時序

不能支持：

- 家具邊界兩側比較
- 多 fold spatial holdout
- 較完整 free-space estimator comparison

### 8 顆：Defensible-A

```text
input_center
input_window_side
input_ac_path
input_door_side
input_near_furniture_left
input_near_furniture_right
validation_pillow
validation_desk
```

可支持：

- 最小家具邊界觀測
- 至少兩個真實 validation targets
- 較清楚的 input/validation separation

### 10 顆：Defensible-B，建議優先目標

```text
input_center
input_window_side
input_ac_path
input_door_side
input_near_furniture_left
input_near_furniture_right
input_bed_side
input_room_corner_free
validation_pillow
validation_desk
```

可支持：

- 家具感知自由空間估計
- pillow / desk holdout
- AC / window / lighting 分組誤差
- 之後擴充 2-D triangulation 或 Cell-IDW 的基本支撐

### 12 顆：Dense

在 10 顆基礎上增加：

```text
validation_room_center
input_window_high_or_low
```

可支持：

- room center 也作為 holdout
- 窗邊高度差與日照梯度

### 14 顆：Dense+

在 12 顆基礎上增加：

```text
validation_near_furniture_boundary
input_ac_return_or_dead_zone
```

可支持：

- 家具邊界 validation
- 氣流死角或回風側比較
- 更完整的 blocked cross-validation

## 6. 採購批次建議

### 第一批：先買 6 顆 node 材料

目的：

- 驗證 ESP32-C3 + DHT11 + BH1750 韌體。
- 測試 MQTT / HTTP 上傳。
- 做同位置校正。
- 找出外殼自熱問題。

### 第二批：補到 10 顆

目的：

- 建立可防守的家具感知實驗。
- 至少保留 pillow / desk validation。
- 補家具邊界與氣流路徑。

### 第三批：補到 12–14 顆

目的：

- 支援 free-space estimator comparison。
- 增加 holdout folds。
- 支援 thesis failure-case analysis。

## 7. 成本控制建議

| 項目 | 建議 |
|---|---|
| ESP32-C3 | 同一批買同型號，減少 firmware pinout 差異 |
| DHT11 | 可先用，但 validation nodes 若預算允許可升級 DHT22/SHT31 |
| 光照 | 優先 BH1750，不建議 LDR 當正式 lux |
| 外殼 | 先用可打孔塑膠盒，確認熱偏差後再 3D 列印 |
| 供電 | 先 USB 固定供電，不做電池版 |
| 備品 | 至少多買 10–20% DHT11 / BH1750 / 線材 |

## 8. 論文中的成本寫法

建議寫法：

> 本研究節點採低成本 ESP32-C3、DHT11 與 BH1750 組成，單顆材料成本依供應商與外殼形式約落在 NT$215–605，含備品耗損估算後約 NT$248–696。若採 10 顆節點作為家具感知防守部署，總材料成本約 NT$2,480–6,960，不含運費、組裝時間與高精度 reference sensor。

避免寫法：

- 「成本固定為某單一價格。」
- 「DHT11 可作為高精度 ground truth。」
- 「6 顆節點足以完整驗證家具遮蔽下所有空間點。」
