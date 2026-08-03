# Kalman Filter 後續研究方向

## 研究定位

教授建議將 Kalman filter 納入後續研究參考。它在本研究中較適合被定位為「隨時間更新隱藏環境狀態、融合稀疏量測，或線上調整 reduced-order model 參數」的方法，而不是直接取代目前的三維空間場模型。Kalman family 的效果取決於狀態轉移、觀測模型、process noise 與 measurement noise 是否合理，因此本輪只完成文獻判讀與未來公平比較協定，證據狀態為 `NOT_EVALUATED`。

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

## 預註冊的未來同資料比較

### 比較方法

- `unfiltered_physics`：目前 reduced-order state prediction，不使用濾波。
- `moving_average`：使用相同量測列的簡單平滑基準。
- `linear_kalman_filter`：先從每一環境因子的線性狀態空間模型開始。
- `extended_kalman_filter`：只有在非線性狀態轉移與 observation equation 已明確定義後才納入。

### 公平性要求

1. 所有方法使用完全相同的原始量測、缺值位置、時間切分、初始化區間、target timestamps 與評估列。
2. covariance、初始狀態與調參只能由 training/validation 區間決定，不能看 test 結果後回頭修改。
3. 同時報告 MAE、RMSE、innovation residual、缺值期間表現與事件後暫態誤差。
4. 對日夜或 setpoint 改變區段另報告 transition-response 誤差，避免整體平均被穩態資料支配。
5. 若任何方法使用額外外部資料，必須另列為不同實驗，不能與同資料主比較混排。

## 與 20–30 °C 應用方向的關係

未來若選擇小型封閉植物生長室，Kalman filter 可以用來追蹤日夜環境配方切換後的隱藏 bulk state、估計裝置響應參數，或融合角落感測器與移動探針。但第一個 project-aligned scenario 的全部設定值與實際操作溫度仍必須在 20–30 °C 內；Kalman filter 不會擴張模型的溫度適用範圍。

## 目前結論

Kalman filter 已被列為後續研究方法參考，但尚未在本專案資料上執行，因此不能宣稱已改善去噪、狀態估測、場重建或控制效果。下一步必須先定義 state/observation equations 與 covariance 來源，再用同資料協定進行實驗。
