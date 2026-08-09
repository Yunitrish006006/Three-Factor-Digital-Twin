# 研究問題定義

## 核心問題

本研究要解決的核心問題是：

**在具有家具遮蔽、稀疏感測與非連網裝置的單房間中，如何建立一個可解釋、可校正且可驗證的三因子空間數位孿生，使系統能估計未直接量測目標點的溫度、濕度與照度，並從環境變化中學習冷氣、窗戶與照明等裝置的影響。**

這個問題不再以「少量感測器精確重建整個真實房間的完整 3-D 連續場」作為主要主張，而是聚焦於：

- 家具遮蔽後仍有物理意義的自由空間。
- 未直接量測目標點的估計。
- input sensors 與 validation sensors 的嚴格分離。
- 可量化、可追溯的目標點誤差。

## 問題背景

智慧建築或智慧家庭系統通常假設設備可以被連線、讀取或控制，例如透過 Wi-Fi、Bluetooth、Matter、BACnet、Modbus 或廠商 API 取得設備狀態。然而在真實場域中，許多裝置並不具備這些能力。

例如：

- 傳統冷氣可能無法回報目前實際出風量或冷卻效果。
- 手動窗戶無法回報開啟程度。
- 一般燈具可能只能被牆壁開關控制，無法提供亮度回饋。
- 新增家具、遮光物或熱源也可能改變空間環境，但不會主動提供資料。

這些裝置雖然不連網，卻會持續影響空間中的溫度、濕度與照度。如果系統只依賴裝置 API，就無法建立完整的環境理解。

## 研究缺口

現有方法常見兩種假設：

1. 假設裝置是智慧裝置，可直接取得狀態或控制參數。
2. 假設有大量感測器或高精度模擬工具，可完整觀測空間狀態。

本研究關注的是更受限但更接近一般場域的情況：

- 裝置本身可能沒有連網能力。
- 感測器數量有限。
- 房間內有家具與遮蔽物，並非空長方體。
- 不使用高成本 CFD 或完整 BIM/BMS 系統。
- 仍希望能估計使用者真正關心的位置，例如枕頭、書桌或房間中央。
- 估計結果必須透過保留感測器驗證，而不是把模型補值當成 ground truth。

## 研究目標

本研究目標分為五層：

1. **空間與感測層**：建立家具感知的 adaptive sensor layout，將被家具佔據的感測點排除，並區分 input、validation、target 與 pseudo roles。
2. **物理估計層**：分別建立溫度、濕度與照度的 nominal models，描述裝置、外部環境與家具遮蔽的主要影響。
3. **校正與學習層**：先校準裝置影響強度，再使用低階空間 residual correction 或 hybrid residual model 修正剩餘誤差。
4. **驗證層**：模型只使用 `S_input`；`S_validation` 的實測值在預測完成後才用來計算 MAE、RMSE、Max Error 與 bias。
5. **應用層**：根據模型預測對候選動作排序；在完成真實介入實驗前，該結果只稱為 counterfactual action ranking。

## 感測器與節點角色

```text
S_input
  模型校正、裝置影響學習與 residual fitting 可使用的真實感測器。

S_validation
  模型估計時禁止使用，只在最後評估階段讀取的真實感測器。

V_target
  枕頭、書桌、房間中央或家具邊界等研究目標位置；不一定有感測器。

V_pseudo
  由模型產生的支撐值，不是直接量測，也不能稱為 ground truth。
```

集合關係：

```text
S_all = S_input ∪ S_validation
S_input ∩ S_validation = ∅
```

## 可形成的研究問題

### RQ1：物理先驗與空間估計

在相同感測器輸入與目標點條件下，加入變數專屬物理先驗的估計方法，是否比純距離插值更能降低三因子誤差？

對應比較：

- BasePhysicsEstimator
- IDW baseline
- BasePhysics + trilinear correction

### RQ2：家具與自由空間

家具感知的 adaptive sensor layout 與 free-space estimators，是否能比原始固定 8-corner 假設更合理地估計家具遮蔽後的目標位置？

對應比較：

- Original corner-based baseline
- Furniture-aware compensation sensors
- 2-D triangulation
- 3-D tetrahedral interpolation
- Cell-IDW fusion

其中 2-D、3-D 與 Cell-IDW 必須依實作與實驗進度標記為 implemented、validated 或 proposed extension。

### RQ3：資料校正與 residual learning

在不使用 validation observations 的條件下，power calibration、trilinear correction 或 hybrid residual learning 是否能降低保留目標點與未見情境的誤差？

對應驗證：

- sensor holdout
- blocked temporal split
- leave-one-day-out
- leave-one-scenario-out

### 應用層問題

以下功能保留為系統應用，不一定作為主要 RQ：

- 非連網裝置影響學習。
- 候選控制動作排序。
- MCP、Web 與 agent tools。

## 系統輸入與輸出

### 輸入

- 房間尺寸、家具佔據區與自由空間。
- `S_input` 的溫度、濕度與照度資料。
- 裝置可能位置、類型與可用設定，例如冷氣、窗戶、照明。
- 外部環境條件，例如室外溫度、濕度與日照。
- `V_target` 位置與候選控制動作。

### 驗證時額外輸入

- `S_validation` 的真實量測值。
- 這些數值只能在預測完成後供 evaluator 使用。

### 輸出

- 自由空間目標座標的溫度、濕度與照度估計值。
- 各區域的三因子平均值。
- 裝置影響係數與校正資訊。
- 目標點 MAE、RMSE、Max Error 與 bias。
- 每個估計值的 method、support nodes、confidence 與 provenance。
- 候選動作的模型式反事實排序。
- MCP／Web／CLI 回應，供外部 client 使用。

## 證據邊界

| 證據層級 | 可以支持 | 不能支持 |
|---|---|---|
| Synthetic full-field | 受控模擬真值下的方法比較 | 真實房間所有未量測點的準確度 |
| Synthetic target holdout | 不使用 holdout target 的受控目標點驗證 | 真實感測器部署效果 |
| Real target-point | 有實測感測器位置的目標點誤差 | 完整真實 3-D dense field |
| Public task-aligned benchmark | 相容時序任務的泛化比較 | 家具感知 3-D 空間估計 |
| Intervention validation | 真實動作前後效果 | 未執行前不能由 action ranking 代替 |

## 與一般智慧家庭系統的差異

一般智慧家庭系統偏向「控制已知裝置」：

```text
Device API → device state → control command
```

本研究偏向「從環境反推裝置影響，並以保留感測器驗證目標點估計」：

```text
S_input observations
→ physical estimation and calibration
→ target-point prediction
→ compare with S_validation
→ appliance impact learning
→ counterfactual action ranking
```

因此，即使裝置不是智慧裝置，只要它對環境造成可觀測變化，模型仍可逐步估計其影響；但所有準確度主張都必須限定在具有正確證據的資料層級。

## 一句話版本

本研究建立一個家具感知、稀疏感測且可透過 holdout target sensors 驗證的單房間三因子空間數位孿生，利用可解釋物理模型與 residual correction 估計未量測目標點，並學習非連網裝置影響以支援模型式控制候選排序。
