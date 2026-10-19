# 電風扇對三因子空間估計的處理設計

## 1. 為什麼電風扇必須納入設計

房間中的電風扇不是冷氣，也不直接提供顯著冷卻能力；但它會改變：

- 空氣混合速度
- 局部溫度梯度
- 濕度擴散與蒸發速率
- 人體附近的對流效果
- 感測器讀值的局部代表性

因此，電風扇不能只當成隨機噪音。若 fan-on 與 fan-off 資料混在一起驗證，模型誤差會被高估或解釋錯誤。

## 2. 論文定位

本研究將電風扇定義為：

```text
dynamic airflow redistribution source
```

它和其他室內作用源的差異如下：

| 來源 | 主要影響 | 是否直接改變熱濕量 |
|---|---|---|
| 冷氣 | 冷卻、除濕、氣流 | 是 |
| 窗戶 | 外氣交換、日照、濕度交換 | 是 |
| 燈光 | 照度、少量熱源 | 是，主要照度 |
| 人體 | 顯熱、潛熱、遮蔽 | 是 |
| 電風扇 | 氣流混合、對流、局部梯度改變 | 通常不作主要熱濕源 |
| 家具 | 固定遮蔽與阻隔 | 否 |

因此，電風扇在模型中應作為 airflow boundary condition 或 airflow mixing modifier，而不是等同 AC 的 cooling device。

## 3. 最小資料標記

正式收集資料時，每筆資料或每個時間段應盡量包含：

```json
{
  "fan": {
    "state": "off | on | unknown",
    "speed": "low | medium | high | unknown",
    "oscillation": "off | on | unknown",
    "direction": "toward_bed | toward_desk | toward_center | unknown",
    "source": "manual_log | smart_plug | current_sensor | inferred"
  }
}
```

如果沒有自動偵測，至少使用 manual log：

```json
{
  "start": "2026-07-12T21:00:00+08:00",
  "end": "2026-07-13T01:30:00+08:00",
  "fan_state": "on",
  "fan_speed": "medium",
  "fan_oscillation": "on",
  "fan_direction": "toward_bed"
}
```

## 4. 分析分組

正式結果應至少分成：

| Segment | 用途 |
|---|---|
| `fan_off` | 主模型背景狀態 |
| `fan_on_fixed_direction` | 固定風向造成局部擾動 |
| `fan_on_oscillating` | 擺頭造成週期性混合 |
| `fan_unknown` | 不作主要 validation，除非明確標記限制 |

主要 validation 不應將 fan-on 與 fan-off 混在一起算同一個 MAE。

## 5. 對 sensor node 部署的影響

因為房間有家具且有電風扇，建議在 10 顆 node 方案中保留：

```text
input_fan_path
input_fan_shadow_zone
```

### 建議部署

| Node | Role | 目的 |
|---|---|---|
| `input_fan_path` | input | 量測主風路徑中的混合與對流影響 |
| `input_fan_shadow_zone` | input | 量測家具或床櫃後方風難以到達區 |
| `validation_pillow` | validation | 睡眠區目標點，需標記 fan 是否吹向床 |
| `validation_desk` | validation | 工作區目標點，需標記 fan 是否吹向書桌 |

若只有 6 顆 minimum deployment，至少要在 `input_center` 或 `input_ac_path` 中選一顆放在風扇主要路徑上，並在 metadata 中標記。

## 6. 對模型的影響

第一版不必建立完整 CFD。可先採用三層處理：

### Level 1：狀態分組

將 fan-on 與 fan-off 分開統計，不混算。

### Level 2：風路 metadata

每顆 node 記錄：

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

### Level 3：簡化 fan mixing modifier

後續可加入：

```text
mixing_strength(q,t) = fan_activation(t) × speed_scale × direction_gain(q) × obstruction_penalty(q)
```

用來調整溫度與濕度的空間梯度，使 fan-on 狀態下的場分布更接近混合後狀態。

## 7. 對論文主張的影響

建議論文中這樣寫：

> 電風扇在本研究中被視為動態氣流混合來源。由於其主要作用為改變空氣混合與局部對流，而非像冷氣一樣主動移除熱量或水氣，本研究第一版不將電風扇建模為冷卻設備，而是將 fan state 作為實驗條件與模型 metadata。所有真實房間驗證結果會依 fan-on、fan-off 或 unknown state 分組，避免將不同氣流條件下的誤差混合解釋。

避免寫法：

- 「電風扇會讓房間溫度降低，所以等同冷氣。」
- 「fan-on 和 fan-off 可以直接混在一起比較。」
- 「不知道風扇狀態也不影響驗證。」
- 「風扇只是一點小噪音，可以忽略。」

## 8. 建議硬體偵測方式

第一版可先用 manual log。若要自動化，優先順序：

| 方法 | 優點 | 注意事項 |
|---|---|---|
| Manual log | 最快、零成本 | 需要紀律，適合初版 |
| Smart plug | 可記錄 on/off 與用電 | 不一定知道風速與擺頭 |
| Current sensor | 可偵測運轉狀態 | 不建議初版直接處理 AC mains 安全問題 |
| Vibration sensor | 可知道風扇是否在震動 | 可能誤判環境震動 |
| IR remote log | 可記錄控制命令 | 不一定等於實際運轉狀態 |

安全原則：不要在初版自行處理市電裸線偵測；若需要自動化，優先使用合格 smart plug 或只做低壓側、非侵入式紀錄。
