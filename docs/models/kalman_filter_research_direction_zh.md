# Kalman Filter 受控基線與後續研究方向

## 研究定位

教授建議將 Kalman filter 納入後續研究參考。它在本研究中較適合被定位為「隨時間更新隱藏環境狀態、融合稀疏量測，或線上調整 reduced-order model 參數」的方法，而不是直接取代目前的三維空間場模型。Kalman family 的效果取決於狀態轉移、觀測模型、process noise 與 measurement noise 是否合理。本輪已完成第一個固定 protocol 的 `CONTROLLED_INJECTED_NOISE` current-time filtering 基線，但實體 sensing-node、線上參數調整與 spatial estimator 整合仍未評估。

## 可能放置的位置

| 位置 | 狀態向量範例 | 觀測 | 可能用途 | 主要風險 |
| --- | --- | --- | --- | --- |
| 感測去噪 | 角落感測器的真實溫濕度狀態 | 8 點量測 | 平滑雜訊與短暫缺值 | 過度平滑真實突變 |
| 動態狀態估測 | room bulk state、zone deviation、device response state | 稀疏角落與 probe | 在設定值或設備狀態改變後追蹤暫態 | 轉移模型錯誤會造成系統性偏差 |
| 感測融合 | 角落、移動探針、室外邊界的共同狀態 | 不同頻率與不確定度的量測 | 統一更新多來源資料 | 時間對齊與 covariance 設定困難 |
| 線上參數調整 | 熱交換、除濕或裝置強度參數 | prediction residual | 適應季節、設備老化或場域變化 | 參數與狀態不可辨識 |

## 文獻判讀

1. Kalman（1960）提出線性狀態空間遞迴估測架構，要求明確的狀態轉移、觀測模型與雜訊假設。DOI：`10.1115/1.3662552`。
2. Speetjens、Stigter 與 van Straten（2009）將 extended Kalman filter 用於溫室模型的線上參數調整，結果支持 Kalman family 可作為 time-varying greenhouse model 的 adaptive estimation 途徑。DOI：`10.1016/j.compag.2009.01.012`。
3. van Mourik、van Beveren、López-Cruz 與 van Henten（2019）比較 moving average、EKF 與 UKF 在溫室 climate monitoring 的效果，沒有發現 filtering 普遍改善監測結果，並指出基礎模型準確性是關鍵。DOI：`10.1016/j.biosystemseng.2019.03.001`。

正面與負面結果必須同時保留。前者說明 EKF 可協助線上適應，後者則提醒：若 reduced-order transition model 本身錯誤，filter 可能只是用更平滑的方式保留錯誤，不能預設一定優於未濾波模型。

## 已執行的同資料受控比較

### 比較方法

- `raw_noisy`：目前受控 corrupted observation，不使用濾波。
- `causal_moving_average_3`：使用目前與前兩筆相同 corrupted observations。
- `linear_kalman_random_walk`：scalar random-walk model，`F=1`、`H=1`。
- EKF/UKF：本輪未執行；只有在非線性 state/observation equation 已明確定義後才納入。

### 公平性要求

1. 所有方法使用完全相同的 fixed-seed corrupted observations、chronological 70/30 split、target timestamps 與評估列。
2. Measurement covariance `R` 固定為登記的 injected-noise variance；process covariance `Q` 由 training reference 相鄰差分變異決定，不能看 test 結果後回頭修改。
3. 同時報告 MAE、RMSE、correlation、innovation、Kalman gain 與 cadence-gap reset。
4. 每個 case 保存 timestamp、corrupted observation 與 task-reference hashes。
5. 原始 SML2010 record 只是 task reference，並非 latent physical ground truth。

### 執行結果

- 12/12 target/profile 案例完成且 parity 全部通過。
- `raw_noisy` 最低 MAE：0/12。
- `causal_moving_average_3` 最低 MAE：6/12，全部為溫度案例。
- `linear_kalman_random_walk` 最低 MAE：6/12，全部為濕度案例。
- Linear Kalman 在 12/12 都優於 raw，但只在 6/12 優於 MA(3)。

結果支持「filtering 成效依變數動態與 noise/state model 而異」，不支持「Kalman 普遍優於簡單平滑」。機器可讀證據位於 `outputs/data/public_benchmarks/kalman_sml2010_filtering_comparison.json`。

## 與 20–30 °C 應用方向的關係

未來若選擇小型封閉植物生長室，Kalman filter 可以用來追蹤日夜環境配方切換後的隱藏 bulk state、估計裝置響應參數，或融合角落感測器與移動探針。但第一個 project-aligned scenario 的全部設定值與實際操作溫度仍必須在 20–30 °C 內；Kalman filter 不會擴張模型的溫度適用範圍，受控 injected-noise 結果也不構成植物環境驗證。

## 目前結論

Kalman filter 已完成第一個本專案的固定協定受控比較：在 SML2010 fixed-seed injected-noise current-time filtering 中，Kalman 與 MA(3) 各取得 6/12 最低 MAE。這不等於真實 sensing node、forecast、spatial field 或 control 效果。下一步應以獨立 validation reference 收集實體感測器 noise、missingness 與 covariance drift，再評估 real-node filtering；只有在 nonlinear state/observation equations 明確後才擴展 EKF/UKF 或 online parameter adaptation。
