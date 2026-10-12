# 機箱溫度量測與介入實驗準備

2026-10-12 使用者確認尚無設備或資料。本文件完成操作與資料準備，不代表已製作或量測。軟體目前只離線產生 PWM 提案，沒有硬體驅動。真實介入前需另固定設備特有額定條件與停止規則，不能把合成原型的 28／30°C 門檻直接套到 CPU。

## 裝置與量測配置

候選為可控熱源、固定接觸方式的金屬片／散熱片、可讀 RPM 與控制 PWM 的風扇、可拆裝導流罩。先記錄設備料號、尺寸、金屬材料、熱源功率範圍、風扇額定條件、入口與出口位置、表面探頭接觸方法，才決定實測模型係數。導流罩改變入口／對流，金屬接觸改變固體熱導；兩項分開施作及比較。

輸入探頭：金屬片表面、局部空氣、入口空氣；另保存功率、PWM 與 RPM。驗證探頭：熱源上獨立校正的參考溫度，不送入辨識、觀測器或控制器。每點的座標／接觸／安裝照片和共同時鐘需留存。低成本 NTC 精度程序沿用 [既有硬體可行性筆記](ntc_temperature_hardware_feasibility_zh.md)，需先取得實際料號與共址參考，不能把型錄精度當作本研究結果。

## 資料契約與初始條件

每 5 秒一筆，同一單調時鐘，以秒、°C、W 與無因次風扇比例為單位。`fan_fraction=RPM/已量測的該平台滿速RPM`，不是將 PWM 當 RPM；保存原始 RPM、ADC 和換算係數另檔。功率需對應本模型熱輸入，不能未經量測就當整機耗電等於熱源功率。

- [觀測 CSV 空白模板](../templates/enclosure_observations.csv)：`time_s,plate_C,air_C,fan_fraction,inlet_C,power_W`。
- [校正 CSV 空白模板](../templates/enclosure_commissioning.csv)：上述欄位再加當下施作的 `pwm`。
- [參考溫度空白模板](../templates/enclosure_reference.csv)：`time_s,source_reference_C`，單獨保存，僅供獨立評分。

目前四參數辨識假設啟動時三個溫度節點等於入口，風扇比例為 .4；真實平台必須先確認這個條件或另登錄新的初始條件程序，不能直接用未平衡的資料。已知容量比例、環境熱導和旁路係數仍需獨立取得或在新 protocol 中增加辨識。

## 執行順序

1. 先做感測共址校正，再留不同溫度點或日期作確認；記錄 MAE、RMSE、偏差、漂移及反應時間。
2. 固定一個可反覆重設的平台狀態，量測功率、入口、RPM 尺度及接觸條件。登錄 heater／fan 實際可操作範圍。
3. 採共同、有限預算的激發程序辨識參數；本次合成程序為 900 秒、四參數單一起點。真實時間和幅度經平台可行性確認後另行預註冊，不在看過 validation／holdout 後改動。
4. 凍結模型、共同控制參數和來源雜湊。新資料按完整回合／工作負載切成 calibration、validation、holdout；避免相鄰列隨機切分造成洩漏。
5. 先離線跑通，檢查丟樣、重複時間、缺感測、參數落界、估測與參考不一致；輸入錯誤時軟體不產生提案，但這不等於實機失效保護。
6. 硬體介面完成並驗證後，對相同負載、初始條件和裝置配置比較固定、PI／PID、LQR、線性 MPC 和排序。獨立實體保護與停止事件要保存，失敗回合不得刪除。
7. 報告追蹤與估測誤差、最高溫、取樣超溫、實測能耗、命令變化、計算時間和試驗成本。固定接觸／導流改動的前後對照，不能由控制器比較推導材料導熱效益。

## 離線軟體操作

從 school 根目錄執行；輸出路徑必須不存在：

```sh
.venv-mpc/bin/python scripts/run_enclosure_session.py --input observations.csv --calibration-csv commissioning.csv --method rank_h6 --output proposals.json
.venv-mpc/bin/python scripts/score_enclosure_reference.py --proposals proposals.json --reference reference.csv --output reference_scores.json
```

第一個命令只有輸入感測；第二個命令才載入參考溫度。實驗程式不得把參考檔合入控制輸入。示範檔與本次所有數字屬合成資料；沒有收到實測資料就維持 `NOT_EVALUATED`。

## 第二階段探索候選與校正切分

另備妥 S／F 有限模型選擇的離線介面：

```sh
.venv-mpc/bin/python scripts/run_calibrated_enclosure.py --input observations.csv --commissioning commissioning.csv --method pi --output structure_proposals.json
.venv-mpc/bin/python scripts/score_enclosure_reference.py --proposals structure_proposals.json --reference reference.csv --output structure_scores.json
```

此版本要求恰好 180 筆、間隔 5 秒的校正記錄；前 120 筆辨識、後 60 筆選擇，沒有選擇後重新擬合。S 辨識共同容量，F 分別辨識三個容量與源—氣熱導；初始平衡、固定其餘係數等假設仍須成立。每個模型單一起點、max_nfev=40，成本包含數值 Jacobian 的殘差呼叫。

第二階段的可見擬合較好，但新合成 holdout 隱藏熱源誤差反而增加；此介面是探索候選，不表示已驗證較佳，不直接取代既有流程。尚無實測平台，禁止以合成係數推定真實容量、熱導或對流。實機若不能滿足此初始條件或取樣程序，需先登錄新的量測／模型規則。
