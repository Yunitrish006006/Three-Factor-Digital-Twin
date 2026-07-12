# 三因子感測節點 BOM 與部署估價

> 本估價是研究規劃用的 planning estimate，非即時報價。實際採購前需依購買當日供應商、運費、套件規格與備品數量重新確認。

## 1. 單顆 v1 node BOM

| 項目 | 建議規格 | 低估 | 中估 | 高估 | 備註 |
|---|---|---:|---:|---:|---|
| ESP32-C3 Dev Board | USB-C 優先 | NT$80 | NT$120 | NT$180 | 不建議買無 USB 燒錄座版本 |
| DHT11 module | 已含 pull-up 模組較方便 | NT$20 | NT$30 | NT$45 | 低成本，需同位置校正 |
| BH1750 module | I2C digital lux sensor | NT$25 | NT$40 | NT$70 | 優先於 LDR |
| 外殼 / 開放式基座 | 打孔塑膠盒、壓克力板或 3D 列印 | NT$25 | NT$50 | NT$90 | 需通風、固定方向與 USB 線 |
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
| Defensible-B | 10 | 建議基準，可覆蓋家具邊界、風扇路徑與多目標點 | NT$2,480 | NT$4,140 | NT$6,960 |
| Dense | 12 | 支援 free-space estimator comparison 與 fan-on/fan-off 分組 | NT$2,976 | NT$4,968 | NT$8,352 |
| Dense+ | 14 | 家具遮蔽多、要做更多 holdout folds | NT$3,472 | NT$5,796 | NT$9,744 |

## 4. 依你房間家具與電風扇狀況的建議

因房間有床、書桌、櫃子、牆邊遮蔽與電風扇，節點不應只放 8 個角落。建議採用 **10 顆 node** 作為第一個可防守版本：

| 類型 | 數量 | Role | 目的 |
|---|---:|---|---|
| 房間中央／自由空間 | 1 | input | 空間基準 |
| 窗邊 | 1 | input | 外氣與日照影響 |
| 冷氣氣流路徑 | 1 | input | AC impact learning |
| 電風扇主風路徑 | 1 | input | fan-on airflow mixing |
| 電風扇陰影／死角區 | 1 | input | 風較難到達處與家具遮蔽比較 |
| 家具邊界左側 | 1 | input | 遮蔽前後差異 |
| 家具邊界右側 | 1 | input | 遮蔽前後差異 |
| 書桌工作面 | 1 | validation | 工作區目標點 |
| 枕頭區 | 1 | validation | 睡眠區目標點 |
| 備用／輪替點 | 1 | input 或 validation | 用於 near-window、near-cabinet、near-door 或 fan fold |

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
input_ac_path_or_fan_path
input_door_side
validation_pillow
validation_desk
```

可支持：

- pillow / desk 兩點 holdout validation
- 初步 AC / window / fan 事件時序

不能支持：

- 家具邊界兩側比較
- fan path 與 fan shadow zone 同時比較
- 多 fold spatial holdout
- 較完整 free-space estimator comparison

### 8 顆：Defensible-A

```text
input_center
input_window_side
input_ac_path
input_fan_path
input_near_furniture_left
input_near_furniture_right
validation_pillow
validation_desk
```

可支持：

- 最小家具邊界觀測
- 最小 fan-on/fan-off 分組
- 至少兩個真實 validation targets
- 較清楚的 input/validation separation

### 10 顆：Defensible-B，建議優先目標

```text
input_center
input_window_side
input_ac_path
input_fan_path
input_fan_shadow_zone
input_near_furniture_left
input_near_furniture_right
input_bed_side_or_room_corner_free
validation_pillow
validation_desk
```

可支持：

- 家具感知自由空間估計
- pillow / desk holdout
- AC / window / lighting / fan 分組誤差
- fan path 與 fan dead zone 比較
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
- fan-on/fan-off 對房間中心區域的影響比較

### 14 顆：Dense+

在 12 顆基礎上增加：

```text
validation_near_furniture_boundary
input_ac_return_or_airflow_dead_zone
```

可支持：

- 家具邊界 validation
- 氣流死角或回風側比較
- 更完整的 blocked cross-validation

## 6. 電風扇狀態紀錄成本

第一版可以使用 manual log，不增加硬體成本。若要自動化，可視預算追加：

| 方法 | 低估 | 中估 | 高估 | 備註 |
|---|---:|---:|---:|---|
| Manual log | NT$0 | NT$0 | NT$0 | 需人工紀錄 fan-on/off、風速、擺頭與方向 |
| 合格 smart plug | NT$250 | NT$450 | NT$800 | 可記錄 on/off 與用電；不一定知道風速與擺頭 |
| 震動感測模組 | NT$20 | NT$40 | NT$80 | 可能誤判環境震動，只適合輔助 |
| 非侵入式電流偵測 | NT$150 | NT$300 | NT$600 | 涉及電氣安全與安裝品質，不建議第一版自行處理市電裸線 |

安全原則：不要為了偵測風扇狀態直接改動市電線路。第一版優先使用 manual log 或合格 smart plug。

## 7. 採購批次建議

### 第一批：先買 6 顆 node 材料

目的：

- 驗證 ESP32-C3 + DHT11 + BH1750 韌體。
- 測試 MQTT / HTTP 上傳。
- 做同位置校正。
- 找出外殼 / 基座自熱問題。
- 測試 fan-on/fan-off manual log 格式。

### 第二批：補到 10 顆

目的：

- 建立可防守的家具感知與電風扇氣流實驗。
- 至少保留 pillow / desk validation。
- 補家具邊界、冷氣氣流路徑、風扇主風路徑與風扇死角。

### 第三批：補到 12–14 顆

目的：

- 支援 free-space estimator comparison。
- 增加 holdout folds。
- 支援 fan-on/fan-off、occupancy-aware 與 thesis failure-case analysis。

## 8. 成本控制建議

| 項目 | 建議 |
|---|---|
| ESP32-C3 | 同一批買同型號，減少 firmware pinout 差異 |
| DHT11 | 可先用，但 validation nodes 若預算允許可升級 DHT22/SHT31 |
| 光照 | 優先 BH1750，不建議 LDR 當正式 lux |
| 外殼 / 基座 | 可採開放式固定基座，避免密閉外殼造成溫濕度滯後 |
| 供電 | 先 USB 固定供電，不做電池版 |
| 風扇狀態 | 第一版 manual log；若要自動化，優先 smart plug |
| 備品 | 至少多買 10–20% DHT11 / BH1750 / 線材 |

## 9. 論文中的成本寫法

建議寫法：

> 本研究節點採低成本 ESP32-C3、DHT11 與 BH1750 組成，單顆材料成本依供應商與外殼形式約落在 NT$215–605，含備品耗損估算後約 NT$248–696。若採 10 顆節點作為家具與風扇氣流感知的防守部署，總材料成本約 NT$2,480–6,960，不含運費、組裝時間、高精度 reference sensor 與風扇狀態自動偵測裝置。

避免寫法：

- 「成本固定為某單一價格。」
- 「DHT11 可作為高精度 ground truth。」
- 「6 顆節點足以完整驗證家具遮蔽與風扇氣流下所有空間點。」
