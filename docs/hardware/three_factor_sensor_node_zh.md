# 三因子感測節點設計

## 1. 設計定位

本節點用於本研究的單房間三因子空間數位孿生。它不是高精度實驗室儀器，而是低成本、可大量部署、具有固定座標與資料角色的稀疏感測節點。

本研究將 sensing nodes 分成兩個等級：

| 等級 | 主要用途 | 建議溫濕度感測器 |
|---|---|---|
| input-grade | 作為 `S_input`，支援模型校正、裝置影響學習與 residual fitting | DHT11 或 SHT31/SHT40 |
| validation-grade | 作為 `S_validation`，支援 target-point holdout evaluation | SHT31 / SHT35 / SHT40 / SHT45 或同等級 |

核心原則：

- `S_input` 可以使用較低成本 sensing node。
- `S_validation` 建議使用較高精度溫濕度感測器。
- DHT11 不應被描述為高精度 ground truth。
- 當 MAE 小於 sensor nominal accuracy 時，結果應解釋為校正量測系統下的相對誤差，而不是超越感測器能力的絕對物理準確度。

## 2. V1 硬體組成

| 模組 | input-grade 建議 | validation-grade 建議 | 用途 | 備註 |
|---|---|---|---|---|
| MCU | ESP32-C3 Dev Board | ESP32-C3 Dev Board | Wi-Fi、資料上傳、時間同步 | 同一批型號可降低 pinout 差異 |
| 溫濕度 | DHT11 / SHT31 / SHT40 | SHT31 / SHT35 / SHT40 / SHT45 | temperature / humidity | validation nodes 優先升級 |
| 照度 | BH1750 | BH1750 | illuminance_lux | I2C digital lux sensor，優先於 LDR |
| 電源 | USB 5V | USB 5V | 固定長時間供電 | 第一版不建議電池 |
| 外殼 / 基座 | 開放式固定基座 | 開放式固定基座 | 通風、固定方向 | 避免密閉自熱 |
| 線材 | 杜邦線或洞洞板 | 洞洞板或固定焊接 | 連接模組 | validation-grade 建議固定焊接 |

若因成本使用 LDR：只能先記錄 `relative_light` 或 raw ADC，經校正後才可輸出 `illuminance_lux`。

## 3. 推薦接線

### ESP32-C3 + DHT11

| DHT11 | ESP32-C3 |
|---|---|
| VCC | 3V3 |
| DATA | GPIO3 |
| GND | GND |

DATA 建議加 4.7kΩ 或 10kΩ pull-up 到 3V3。

### ESP32-C3 + SHT3x / SHT4x

SHT31、SHT35、SHT40 與 SHT45 模組通常使用 I2C。實際腳位以模組標示為準。

| SHT 模組 | ESP32-C3 |
|---|---|
| VCC / VIN | 3V3 |
| GND | GND |
| SDA | GPIO4 |
| SCL | GPIO5 |

### ESP32-C3 + BH1750

| BH1750 | ESP32-C3 |
|---|---|
| VCC / VIN | 3V3 |
| GND | GND |
| SDA | GPIO4 |
| SCL | GPIO5 |
| ADDR | GND 或不接 |

BH1750 與 SHT3x/SHT4x 可共用 I2C bus，但需確認 I2C address 不衝突。

## 4. 外殼與感測位置

外殼或固定基座設計原則：

- 溫濕度 sensor 放在側邊通風位置。
- 溫濕度 sensor 與 ESP32-C3 主晶片至少間隔 2–3 cm，validation-grade 建議 5 cm 以上。
- BH1750 需要固定感測方向，例如 upward 或 target-facing。
- 外殼不得密封；若使用開放式基座，仍須固定模組與 USB 線。
- USB 供電線與充電頭不要貼近溫濕度 sensor。
- 節點不要緊貼牆面，除非該節點本來就是 wall-near observation。

建議配置：

```text
┌──────────────────────────┐
│  BH1750 透光孔 / 朝上      │
│                          │
│  SHT / DHT 通風側          │
│                          │
│  ESP32-C3 主板             │
│                          │
│  USB 供電固定點            │
└──────────────────────────┘
```

## 5. 資料格式

每筆資料應可直接映射到論文中的 sensor role、sensor grade 與座標系統。

```json
{
  "schema": "three_factor_node_v1",
  "room_id": "bedroom_01",
  "node_id": "validation_pillow",
  "role": "validation",
  "sensor_grade": "validation_grade",
  "timestamp": "2026-07-12T18:30:00+08:00",
  "position_m": {
    "x": 3.20,
    "y": 4.10,
    "z": 0.80
  },
  "sensors": {
    "temperature_c": 27.03,
    "humidity_rh": 61.24,
    "illuminance_lux": 128.4
  },
  "raw": {
    "temp_humidity_sensor_model": "SHT40",
    "temperature_c": 27.03,
    "humidity_rh": 61.24,
    "bh1750_lux": 128.4
  },
  "context": {
    "fan_state": "off",
    "fan_speed": "unknown",
    "fan_oscillation": "unknown",
    "fan_direction": "unknown",
    "occupancy_state": "unknown"
  },
  "quality": {
    "temp_humidity_ok": true,
    "light_ok": true,
    "wifi_rssi_dbm": -58,
    "uptime_s": 3842
  },
  "firmware": "three-factor-node-v1.0.0"
}
```

## 6. MQTT Topic 設計

```text
dt/bedroom_01/node/<node_id>/state
dt/bedroom_01/node/<node_id>/status
dt/bedroom_01/node/<node_id>/config
```

### state

上傳三因子感測資料。

### status

上傳在線狀態、IP、RSSI、韌體版本。

### config

上傳或保留 node 座標、role、sensor grade、高度、光照方向、附近家具關係與 fan-relative metadata。

## 7. 取樣頻率

| 模式 | 建議週期 |
|---|---:|
| 初始測試 | 5 秒 |
| 冷氣／開窗／風扇短事件 | 10 秒 |
| 正式長期收集 | 30 秒 |
| 低頻背景紀錄 | 60 秒 |

DHT11 反應較慢，正式論文資料不應把 1 秒高頻資料解釋成高時間解析度環境反應。SHT 系列反應與解析度較好，但正式資料仍應以穩定取樣週期與事件 settling window 為主。

## 8. 校正流程

### Step 1：同位置校正

所有節點放在同一位置，連續記錄 12–24 小時。

建議：

- `reference-grade`：SHT35 / SHT45 或較高階溫濕度計。
- `validation-grade`：SHT31 / SHT40 / SHT45。
- `input-grade`：DHT11 或其他低成本節點。

計算：

```text
temp_offset_i = reference_temp - node_temp_i
rh_offset_i = reference_rh - node_rh_i
lux_scale_i = reference_lux / node_lux_i
```

若沒有高精度 reference，可先使用多節點 median 作為低成本相對校正基準，但論文需標明不是實驗室 reference。

### Step 2：sensor-grade metadata

每顆 node 必須記錄：

```json
{
  "sensor_grade": "input_grade | validation_grade | reference_grade",
  "temp_humidity_sensor_model": "DHT11 | SHT31 | SHT35 | SHT40 | SHT45 | other",
  "calibration_source": "reference_node | median_alignment | factory_only"
}
```

### Step 3：方向校正

BH1750 的方向需固定並記錄：

- `upward`：量測環境光。
- `workplane_upward`：桌面／床面高度向上照度。
- `target_facing`：朝向窗戶或燈具，需明確標示。

### Step 4：部署後 sanity check

正式收集前先跑 24 小時，檢查：

- 是否掉線。
- Wi-Fi RSSI 是否穩定。
- 某顆 node 是否長期偏高或偏低。
- 光照方向是否造成不可比較讀值。
- USB 電源是否造成溫濕度 sensor 自熱偏差。
- fan-on 與 fan-off 的時段是否有被正確標記。

## 9. 電風扇相關部署

房間有電風扇時，10 顆 node 方案建議保留：

```text
input_fan_path
input_fan_shadow_zone
```

- `input_fan_path`：放在風扇主要氣流路徑，觀察 fan-on 時溫濕度混合變化。
- `input_fan_shadow_zone`：放在家具或床櫃後方風較難到達的位置，觀察風扇無法有效混合的區域。

每顆 node 的 config metadata 建議加入：

```json
{
  "fan_relative_position": {
    "distance_m": 1.4,
    "angle_deg": 25,
    "in_primary_airflow_path": true,
    "fan_shadow_zone": false
  }
}
```

## 10. 建議採購策略

不建議一開始把 8–10 顆全部升級。較可防守且成本可控的第一版為：

```text
validation_pillow：SHT31 / SHT40 / SHT45
validation_desk：SHT31 / SHT40 / SHT45
reference/calibration：SHT35 / SHT45 或較高階溫濕度計
其他 input nodes：DHT11 或逐步升級 SHT31/SHT40
```

## 11. 論文用語

建議寫法：

> 本研究將 sensing nodes 分為 input-grade 與 validation-grade。input-grade nodes 以低成本為主，用於空間稀疏觀測；validation-grade nodes 採較高精度溫濕度感測器，用於 target-point holdout evaluation，以避免模型誤差被低精度感測器解析度與精度限制混淆。DHT11 可作為低成本輸入節點，但不作高精度 validation truth。

避免寫法：

- 「DHT11 提供高精度 ground truth。」
- 「模型 MAE 小於 sensor accuracy 就代表絕對物理準確度。」
- 「LDR 原始 ADC 即為 lux。」
- 「所有未量測點都由這些 node 直接驗證。」
- 「validation node 同時用於模型校正與驗證。」
- 「fan-on 與 fan-off 可以直接混在一起作為同一種環境條件。」
