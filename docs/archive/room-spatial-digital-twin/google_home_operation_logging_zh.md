# Google Home 操作紀錄作為研究資料的使用邊界

## 1. 結論

Google Home 可以作為冷氣、電風扇與電燈的 **operation event log**。若研究者是透過 Google Home UI 操作，且可確認每次操作都成功，則可將事件標記為較高可信度的 **operator-verified operation event**。

但它仍不應取代環境感測器或 validation sensor。Google Home UI 確認的是「設備操作狀態」，不是房間該位置的溫度、濕度或照度真值。

本研究將 Google Home 相關資料定位為：

```text
operation context / operator-verified command evidence
```

而不是：

```text
measured environmental truth
validation target measurement
```

## 2. 可以記錄什麼

Google Home UI 或相關控制流程可用來記錄：

| 欄位 | 用途 |
|---|---|
| command_time | 操作發生時間 |
| device_id | 被控制設備，例如 AC、fan、light |
| requested_state | 要求狀態，例如 on/off、mode、setpoint |
| command_source | google_home_ui、voice、app、automation、schedule、manual import |
| actor_type | user、automation、unknown |
| command_result | success、failed、unknown |
| state_confidence | command_sent、ui_operator_verified、reported_state、verified_state |
| verification_method | ui_observed_success、physical_observed_success、environmental_response、device_reported_state |

## 3. 可信度分級

| `state_confidence` | 意義 | 可用性 |
|---|---|---|
| `command_sent` | 只知道指令送出 | 可作低可信度 context |
| `ui_operator_verified` | 使用者透過 Google Home UI 操作，且確認 UI 顯示成功或設備已反應 | 可作主要 operation event |
| `reported_state` | 設備或平台回報狀態 | 可作主要 operation event，但需保留來源 |
| `verified_state` | 另有 smart plug、設備回報、物理觀察或其他紀錄驗證 | 最高可信度 operation event |

若你的實驗流程規定「所有冷氣、風扇、電燈操作都只透過 Google Home UI 執行，且操作者確認每次成功」，建議使用：

```text
source = google_home
source_detail = google_home_ui
state_confidence = ui_operator_verified
verification_method = ui_observed_success
```

若同時有看到設備真的開啟、燈亮、風扇轉動或冷氣出風，可標記：

```text
verification_method = physical_observed_success
```

## 4. 不可直接假設的事

### Google Home UI 成功不等於環境真值

即使 Google Home UI 操作都成功，它仍只代表設備進入某個操作狀態，不代表：

- pillow node 的真實溫度。
- desk node 的真實照度。
- 房間每個空間點的真實三因子值。
- 冷氣或風扇已經對環境產生穩定效果。

因此，Google Home UI 紀錄可作為 device context，但不能取代 `S_validation`。

### IR 冷氣或紅外線電風扇

若冷氣或電風扇是透過 IR blaster 控制，但操作者透過 Google Home UI 與現場反應確認成功，則可由 `command_sent` 提升為 `ui_operator_verified` 或 `physical_observed_success`。

若沒有確認成功，仍應標記為：

```text
state_confidence = command_sent
```

### 雲端或第三方整合設備

若設備透過雲端整合回報狀態，仍需記錄其來源：

```text
provenance = google_home | device_cloud | matter | smart_plug | manual_log
```

### 燈光

若是智慧燈泡或智慧開關，狀態通常比 IR 冷氣可靠，但仍應保留 provenance，而不是直接省略來源。

## 5. 建議資料格式

```json
{
  "schema": "operation_event_v1",
  "room_id": "bedroom_01",
  "event_id": "evt_20260712_213001_fan_on",
  "timestamp": "2026-07-12T21:30:01+08:00",
  "source": "google_home",
  "source_detail": "google_home_ui",
  "device_id": "fan_main",
  "device_type": "fan",
  "requested_state": {
    "power": "on",
    "speed": "medium",
    "oscillation": "on",
    "direction": "toward_bed"
  },
  "reported_state": {
    "power": "on"
  },
  "state_confidence": "ui_operator_verified",
  "verification_method": "ui_observed_success",
  "privacy": {
    "voice_transcript_stored": false,
    "account_identifier_stored": false
  }
}
```

若實驗者同時現場確認風扇轉動，則可寫成：

```json
{
  "state_confidence": "verified_state",
  "verification_method": "physical_observed_success"
}
```

## 6. 對冷氣、風扇與電燈的建議

### 冷氣

優先記錄：

- power on/off
- mode：cool / dry / fan / heat
- setpoint
- fan speed
- swing / vane direction
- command source
- verification method

注意：冷氣即使成功開啟，也需要 3–15 分鐘以上才可能在遠端感測點形成可觀察環境反應。

### 電風扇

優先記錄：

- power on/off
- speed
- oscillation
- direction
- 是否吹向 bed / desk / center
- verification method

電風扇在本研究中屬於 airflow redistribution source，因此 fan-on 與 fan-off 不可混算。

### 電燈

優先記錄：

- power on/off
- brightness
- color temperature，如有
- controlled light zone
- verification method

若燈具可回報狀態，可視為比 IR 設備更可靠的 `reported_state`。

## 7. 與感測器資料的關係

Google Home event log 是模型輸入 context，不是 `S_validation`。

```text
Google Home UI operation log
  → device context / operation feature

ESP32-C3 sensing node
  → temperature / humidity / illuminance measurement

S_validation sensor
  → final target-point validation truth
```

## 8. 時間同步與延遲

所有 operation events 必須使用 ISO-8601 timestamp 並保留 timezone。

資料處理時應考慮：

- Google Home UI 操作時間。
- 裝置真正動作可能有延遲。
- 操作者確認成功的時間可能晚於按下 UI 的時間。
- 冷氣、風扇與燈光對環境感測器的反應時間不同。

建議在分析中設定 settling window，例如：

| 設備 | 建議觀察延遲 |
|---|---:|
| 電燈 | 0–10 秒 |
| 電風扇 | 10–60 秒 |
| 冷氣 | 3–15 分鐘 |
| 開窗 | 1–10 分鐘 |

## 9. 隱私邊界

研究資料只保留設備操作事件，不保留：

- 語音原始音檔
- 語音逐字稿
- Google account email
- 家庭成員身份
- 與研究無關的家庭活動
- Google Home app 原始完整 activity history

若需要人工匯出 Google Home activity，應先轉換成最小化格式，只保留 device operation fields。

## 10. 建議採集層級

### Level 1：Google Home UI 操作 + 操作者確認

適合正式初版。

做法：

- 實驗期間所有冷氣、風扇與電燈操作統一由 Google Home UI 執行。
- 操作者確認 UI 顯示成功或設備實際反應。
- 整理成 `operation_event_v1`。
- 記錄 `state_confidence = ui_operator_verified`。

### Level 2：Google Home UI + 簡表人工 log

適合較嚴格的正式資料。

做法：

- Google Home UI 作為操作入口。
- 另外用簡單表格記錄操作時間、設備、狀態與是否成功。
- Google Home activity 只作為交叉檢查。

### Level 3：自動化 operation logger

適合後續擴充。

做法：

- 使用 Home Assistant、Node-RED、smart plug、Matter device 或 Home APIs 建立操作事件紀錄。
- Google Home 仍可作為控制入口。
- Logger 以獨立資料庫或 CSV/JSON 輸出，不依賴手動截圖。

## 11. 論文用語

建議寫法：

> 本研究將 Google Home UI 控制紀錄作為裝置操作事件來源，用於標記冷氣、電風扇與照明的狀態變化。實驗期間所有相關家電操作皆由 Google Home UI 執行，並由操作者確認操作成功，因此此類紀錄被標記為 operator-verified operation events。然而，該紀錄僅代表設備操作條件，不直接作為環境三因子或目標點驗證真值。所有環境驗證仍以保留感測器之溫度、濕度與照度量測為準。

避免寫法：

- 「Google Home UI 紀錄就是環境真值。」
- 「冷氣開啟紀錄可以取代溫度感測器。」
- 「電燈開啟紀錄可以取代照度感測器。」
- 「Google Home 資料可以取代 validation sensor。」
- 「不需要保存資料來源與信心等級。」
