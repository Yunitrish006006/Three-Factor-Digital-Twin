# 三因子低成本感測節點設計

## 1. 設計定位

本節點用於本研究的單房間三因子空間數位孿生。它不是高精度實驗室儀器，而是低成本、可大量部署、具有固定座標與資料角色的稀疏感測節點。

核心用途：

- 作為 `S_input`：供模型校正、裝置影響學習與 residual fitting 使用。
- 作為 `S_validation`：保留不給模型使用，只在最後評估 target-point error。
- 建立真實房間的多點時序資料，支援 pillow、desk、room center 與 near-furniture validation。
- 支援電風扇、冷氣、窗戶與照明等動態條件的分組分析。

## 2. V1 硬體組成

| 模組 | 建議元件 | 用途 | 備註 |
|---|---|---|---|
| MCU | ESP32-C3 Dev Board | Wi-Fi、資料上傳、時間同步 | 2.4GHz Wi-Fi，適合固定房間節點 |
| 溫濕度 | DHT11 | temperature / humidity | 低成本，需校正，不作高精度 reference |
| 照度 | BH1750 | illuminance_lux | I2C digital lux sensor，優先於 LDR |
| 電源 | USB 5V | 固定長時間供電 | 第一版不建議電池 |
| 外殼 / 基座 | 打孔盒或開放式固定基座 | 通風、固定方向 | DHT11 需遠離 ESP32-C3 自熱 |
| 線材 | 杜邦線或小洞洞板 | 連接模組 | 正式部署建議焊接或固定 |

若因成本使用 LDR：只能先記錄 `relative_light` 或 raw ADC，經校正後才可輸出 `illuminance_lux`。

## 3. 推薦接線

### ESP32-C3 + DHT11

| DHT11 | ESP32-C3 |
|---|---|
| VCC | 3V3 |
| DATA | GPIO3 |
| GND | GND |

DATA 建議加 4.7kΩ 或 10kΩ pull-up 到 3V3。

### ESP32-C3 + BH1750

| BH1750 | ESP32-C3 |
|---|---|
| VCC / VIN | 3V3 |
| GND | GND |
| SDA | GPIO4 |
| SCL | GPIO5 |
| ADDR | GND 或不接 |

## 4. 外殼與感測位置

外殼或固定基座設計原則：

- DHT11 放在側邊通風位置。
- DHT11 與 ESP32-C3 主晶片至少間隔 2–3 cm。
- BH1750 需要固定感測方向，例如 upward 或 target-facing。
- 外殼不得密封；若使用開放式基座，仍須固定模組與 USB 線。
- USB 供電線與充電頭不要貼近 DHT11。
- 節點不要緊貼牆面，除非該節點本來就是 wall-near observation。

建議配置：

```text
┌────────────────────┐
│  BH1750 透光孔/朝上 │
│                    │
│  DHT11 通風側       │
│                    │
│  ESP32-C3 主板      │
│                    │
│  USB 供電固定點     │
└────────────────────┘
```

## 5. 資料格式

每筆資料應可直接映射到論文中的 sensor role 與座標系統。

```json
{
  "schema": "three_factor_node_v1",
  "room_id": "bedroom_01",
  "node_id": "node_pillow_01",
  "role": "validation",
  "timestamp": "2026-07-12T18:30:00+08:00",
  "position_m": {
    "x": 3.20,
    "y": 4.10,
    "z": 0.80
  },
  "sensors": {
    "temperature_c": 27.0,
    "humidity_rh": 61.0,
    "illuminance_lux": 128.4
  },
  "raw": {
    "dht11_temperature_c": 27,
    "dht11_humidity_rh": 61,
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
    "dht11_ok": true,
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

上傳或保留 node 座標、role、高度、光照方向、附近家具關係與 fan-relative metadata。

## 7. 取樣頻率

| 模式 | 建議週期 |
|---|---:|
| 初始測試 | 5 秒 |
| 冷氣／開窗／風扇短事件 | 10 秒 |
| 正式長期收集 | 30 秒 |
| 低頻背景紀錄 | 60 秒 |

DHT11 反應較慢，正式論文資料不應把 1 秒高頻資料解釋成高時間解析度環境反應。

## 8. 校正流程

### Step 1：同位置校正

所有節點放在同一位置，連續記錄 12–24 小時。

計算：

```text
temp_offset_i = reference_temp - node_temp_i
rh_offset_i = reference_rh - node_rh_i
lux_scale_i = reference_lux / node_lux_i
```

若沒有高精度 reference，可先使用多節點 median 作為低成本相對校正基準，但論文需標明不是實驗室 reference。

### Step 2：方向校正

BH1750 的方向需固定並記錄：

- `upward`：量測環境光。
- `workplane_upward`：桌面／床面高度向上照度。
- `target_facing`：朝向窗戶或燈具，需明確標示。

### Step 3：部署後 sanity check

正式收集前先跑 24 小時，檢查：

- 是否掉線。
- Wi-Fi RSSI 是否穩定。
- 某顆 node 是否長期偏高或偏低。
- 光照方向是否造成不可比較讀值。
- USB 電源是否造成 DHT11 自熱偏差。
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

## 10. 論文用語

建議寫法：

> 本研究設計低成本三因子感測節點，以 ESP32-C3 作為無線通訊與資料上傳核心，搭配 DHT11 量測溫濕度，並以 BH1750 量測照度。每個節點具有固定空間座標與資料角色，可作為模型輸入感測器或保留驗證感測器。若實驗期間使用電風扇，資料會額外標記 fan state，並將 fan-on 與 fan-off 時段分開分析。

避免寫法：

- 「DHT11 提供高精度 ground truth。」
- 「LDR 原始 ADC 即為 lux。」
- 「所有未量測點都由這些 node 直接驗證。」
- 「validation node 同時用於模型校正與驗證。」
- 「fan-on 與 fan-off 可以直接混在一起作為同一種環境條件。」
