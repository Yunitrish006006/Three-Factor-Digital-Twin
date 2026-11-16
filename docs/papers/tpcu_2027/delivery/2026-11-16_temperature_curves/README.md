# 五種策略 CPU／GPU 溫度曲線

2026-11-16。資料來源為論文既有雙熱源模型模擬，採用已保存的60個正式評估回合。

## 主要圖表

- [CPU／GPU溫度曲線](holdout_102621_temperature.png)：保留測試 seed 102621；上圖CPU、下圖GPU；固定PWM、PI、PID、LQR、MPC共用相同負載、入口溫度與初始條件。黑色虛線為60°C追蹤目標。
- [同回合的負載、入口溫度與PWM](holdout_102621_inputs_pwm.png)：依序呈現CPU／GPU熱功率、入口溫度及五種策略的PWM命令。

主圖依種子編號選取保留測試第一個回合，未依曲線或排名挑選。以下完整呈現其餘分組及種子：

|分組|全部三種子的CPU／GPU曲線|
|---|---|
|驗證|[檢視](validation_all_seeds.png)|
|保留測試|[檢視](holdout_all_seeds.png)|
|參數失配|[檢視](plant_holdout_all_seeds.png)|
|過載|[檢視](overload_all_seeds.png)|

每張分組圖上排為CPU、下排為GPU，各欄對應一個種子；同一張圖使用共同溫度軸範圍。過載圖另外標出CPU 80°C與GPU 85°C的評分上限。各分組的負載與參數定義沿用論文表一及第二節。

## 時間與資料對應

- 時間範圍0–1200秒，控制步長10秒，每條溫度曲線包含初始狀態及120個步末狀態，共121點。
- 原始CSV的time_s表示控制區間起點；next_cpu_C及next_gpu_C對應time_s+10秒。繪圖依此對齊，未將步末溫度放到區間起點。
- 溫度圖以直線連接原始保存點，未平滑。輸入與PWM圖使用階梯線表示各控制區間內的設定。
- PI與PID在主圖幾乎重疊，LQR與MPC也相近，使用不同線型區分。
- [曲線數據CSV](temperature_curves.csv)共7260列，包含分組、種子、策略、時間、CPU與GPU溫度。
- 同名SVG為向量圖，可供論文排版；PNG為300 dpi。

## 圖說草稿

五種風扇控制策略於保留測試回合之CPU與GPU溫度響應（seed 102621）。五種策略共用相同熱功率序列、入口溫度與初始條件；控制週期為10秒，模擬時間為1200秒。虛線為60°C追蹤目標。

## 重現與核對

於school目錄執行：`.venv-mpc/bin/python docs/papers/tpcu_2027/build_temperature_curves.py`。

已核對60份原始軌跡雜湊、同組同種子的外生輸入一致性、相鄰時步的狀態連續性，以及由繪圖資料重算的MAE與論文凍結結果一致；六張圖已目視確認。來源與版本詳見[provenance.json](provenance.json)。保留測試seed 102621的CPU／GPU主圖已以單欄版型插入論文v4第6頁圖三；其餘圖表保留為補充資料。
