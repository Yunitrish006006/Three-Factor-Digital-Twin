# Google Home 操作紀錄作為研究資料的使用邊界

## 1. 結論

Google Home 可以作為冷氣、電風扇與電燈的 **operation event log**，但不應直接視為設備真實狀態的 ground truth。

本研究將 Google Home 相關資料定位為：

```text
operation context / command evidence
```

而不是：

```text
measured environmental truth
actual device-state ground truth
validation target measurement
```

## 2. 可以記錄什麼

Google Home 或相關控制流程可用來記錄：

| 欄位 | 用途 |
|---|---|
| command_time | 操作發生時間 |
| device_id | 被控制設備，例如 AC、fan、light |
| requested_state | 要求狀態，例如 on/off、mode、setpoint |
| command_source | voice、app、automation、schedule、manual import |
| actor_type | user、automation、unknown |
| command_result | success、failed、unknown |
| state_confidence | command_sent、reported_state、verified_state |

## 3. 不可直接假設的事

### IR 冷氣或紅外線電風扇

若冷氣或電風扇是透過 IR blaster 控制，Google Home 可能只知道「指令已送出」，不一定知道設備是否真的成功執行。

因此應標記：

```text
state_confidence = command_sent
```

而不是：

```text
state_confidence = verified_state
```

### 雲端或第三方整合設備

若設備透過雲端整合回報狀態，仍需記錄其來源：

```text
provenance = google_home | device_cloud | matter | smart_plug | manual_log
```

### 燈光

若是智慧燈泡或智慧開關，狀態通常比 IR 冷氣可靠，但仍應保留 provenance，而不是直接省略來源。

## 4. 建議資料格式

```json
{
  "schema": "operation_event_v1",
  "room_id": "bedroom_01",
  "event_id": "evt_20260712_213001_fan_on",
  "timestamp": "2026-07-12T21:30:01+08:00",
  "source": "google_home",
  "source_detail": "voice | app | automation | script | manual_export",
  "device_id": "fan_main",
  "device_type": "fan",
  "requested_state": {
    "power": "on",
    "speed": "medium",
    "oscillation": "on",
    "direction": "toward_bed"
  },
  "reported_state": null,
  "state_confidence": "command_sent",
  "privacy": {
    "voice_transcript_stored": false,
    "account_identifier_stored": false
  }
}
```

## 5. 對冷氣、風扇與電燈的建議

### 冷氣

優先記錄：

- power on/off
- mode：cool / dry / fan / heat
- setpoint
- fan speed
- swing / vane direction
- command source

注意：若是紅外線冷氣，沒有回報機制時只能視為 command log。

### 電風扇

優先記錄：

- power on/off
- speed
- oscillation
- direction
- 是否吹向 bed / desk / center

電風扇在本研究中屬於 airflow redistribution source，因此 fan-on 與 fan-off 不可混算。

### 電燈

優先記錄：

- power on/off
- brightness
- color temperature，如有
- controlled light zone

若燈具可回報狀態，可視為比 IR 設備更可靠的 `reported_state`。

## 6. 與感測器資料的關係

Google Home event log 是模型輸入 context，不是 `S_validation`。

```text
Google Home operation log
  → device context / operation feature

ESP32-C3 sensing node
  → temperature / humidity / illuminance measurement

S_validation sensor
  → final target-point validation truth
```

## 7. 時間同步與延遲

所有 operation events 必須使用 ISO-8601 timestamp 並保留 timezone。

資料處理時應考慮：

- Google Home 指令發出時間。
- 裝置真正動作可能有延遲。
- IR 指令可能失敗。
- 冷氣、風扇與燈光對環境感測器的反應時間不同。

建議在分析中設定 settling window，例如：

| 設備 | 建議觀察延遲 |
|---|---:|
| 電燈 | 0–10 秒 |
| 電風扇 | 10–60 秒 |
| 冷氣 | 3–15 分鐘 |
| 開窗 | 1–10 分鐘 |

## 8. 隱私邊界

研究資料只保留設備操作事件，不保留：

- 語音原始音檔
- 語音逐字稿
- Google account email
- 家庭成員身份
- 與研究無關的家庭活動
- Google Home app 原始完整 activity history

若需要人工匯出 Google Home activity，應先轉換成最小化格式，只保留 device operation fields。

## 9. 建議採集層級

### Level 1：手動對照 Google Home activity

適合初期。

做法：

- 每天或每次實驗後檢查操作記錄。
- 手動整理成 `operation_event_v1`。
- 不保存語音或帳號資訊。

### Level 2：手動 log + Google Home 對照

適合正式初版。

做法：

- 實驗時用簡單表格記錄冷氣、風扇、燈光狀態。
- Google Home activity 只作為交叉檢查。

### Level 3：自動化 operation logger

適合後續擴充。

做法：

- 使用 Home Assistant、Node-RED、smart plug、Matter device 或 Home APIs 建立操作事件紀錄。
- Google Home 仍可作為控制入口。
- Logger 以獨立資料庫或 CSV/JSON 輸出，不依賴手動截圖。

## 10. 論文用語

建議寫法：

> 本研究將 Google Home 控制紀錄作為裝置操作事件來源，用於標記冷氣、電風扇與照明的狀態變化。由於部分設備可能透過紅外線或第三方雲端控制，Google Home 紀錄僅代表操作指令或回報狀態，不直接作為設備實際狀態的 ground truth。所有環境驗證仍以保留感測器之溫度、濕度與照度量測為準。

避免寫法：

- 「Google Home 紀錄就是設備真實狀態。」
- 「IR 指令送出就代表冷氣一定開啟。」
- 「Google Home 資料可以取代 validation sensor。」
- 「不需要保存資料來源與信心等級。」
