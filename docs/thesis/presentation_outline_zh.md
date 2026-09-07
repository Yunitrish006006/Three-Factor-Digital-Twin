# 論文報告投影片大綱

## Slide 1: 封面
- 題目、姓名、雙指導教授、研究定位

## Slide 2: 研究問題與動機
- 非連網裝置無法直接回報狀態
- 有限感測器下仍需估計全室環境
- 早期純插值與 local-only 模型都不合理

## Slide 3: 論文整體邏輯：問題、方法、證據與結論邊界
- RQ1--RQ3 為主要研究線，RQ4 為次要服務線
- 每個研究問題對應方法、E1--E9 證據層與可支持／不可過度宣稱的結論

## Slide 4: 房間拓樸、感測器與目標區域
- 8 顆角落感測器
- 三個主要區域與三個核心裝置

## Slide 5: 數學模型
- 變數專屬 nominal model
- trilinear correction
- 裝置與家具模組化
- 溫度、濕度、照度分別使用不同公式

## Slide 6: 模型學習、推論與推薦資料流
- 學習端：raw records → 對齊 → scenario state → labels → coefficients/checkpoint
- 推論端：runtime input → nominal field → correction / hybrid → point or zone prediction
- 推薦端：sample / cluster + T/H/L 目標 → 反事實重跑 → penalty reduction 排序

## Slide 7: 系統實作與介面
- MCP 是工具化介面，不是預測模型本身
- initialize：設定 scenario、室內 baseline、外部邊界、設備/家具、預設時間與 estimator
- AC state：模式、目標溫度、風量、水平/垂直角度與固定/擺動
- sample point：查指定座標在特定時間或穩定態的溫濕照度
- learn impacts：start/finish before-after record
- window direct / rank actions：輸入外部窗戶資料；rank actions 需指定 sample 與 T/H/L 目標
- Gemma bridge 與 Web demo 分別負責 AI tool calling 與人機展示

## Slide 8: learn_impacts：動作如何成為資料記錄
- start：device_name + device_state 記錄實際操作狀態
- record：儲存 learning_record_id、baseline、外部邊界、家具、elapsed time 與 before observations
- finish：用同一批感測器 after observations 計算 after-before delta
- least squares：由 influence envelope 與 delta 求 learned_device_impacts

## Slide 9: 驗證流程與比較原則
- E1-E3：synthetic full-field、IDW baseline、ablation
- E4：非連網裝置影響學習與推薦排序
- E5：48 組窗戶矩陣（34 範圍內／14 範圍外壓力測試）與 direct input
- E6：hybrid residual no-Fourier 與 LOO cross-validation
- E7：bedroom_01 7 天真實快照與 pillow hold-out
- E8 execution kit：schema / template / analyzer；0 trials、NOT_EVALUATED
- E9 public benchmark；E10 controlled filtering；E11A BMC temporal transfer；demo 不是量化實驗

## Slide 10: 主要結果
- 平均 field MAE
- IDW / Base / Pure RNN / LOO Hybrid 同八情境比較
- Pure RNN lowest MAE 0/24
- 真實臥室 pillow MAE 比較
- 推薦排序目前為 counterfactual simulation
- 3D 視覺化案例

## Slide 11: Pure RNN 與 Hybrid Residual 結果
- Pure RNN 直接預測完整場、不使用 physics estimate，lowest MAE 0/24
- default held-out、no-Fourier、LOO hybrid MAE
- train/test sample count
- LOO 結果限標準情境 family
- E7 date-block bootstrap 的三因子改善區間下界均大於 0
- E7 逐日剔除的最小 MAE 降幅仍為 T 0.6123、H 3.5551、L 290.5716

## Slide 12: 公開資料任務拆解
- SML2010：S1 純照度劣勢、S2 長視窗溫度部分優勢、S3 事件 delta 主要優勢
- Oh2024-inspired transfer：15min 兩點溫度最佳、60min 本研究 readout 最佳、24h persistence 最佳
- 次日 primary 與 post-primary adaptive 均未建立優勢；未選中 bias correction 僅約 1% 改善
- RNN 與其他模型共用四筆 history、split、targets、test rows；12/12 parity 通過，RNN lowest MAE 0/12
- Kalman controlled filtering 12/12 parity；MA(3) 與 Linear Kalman 各 lowest MAE 6/12
- CU-BEMS：C1/C3 勝 linear regression 但不勝 persistence，C2 照度劣勢
- 明確說明 public benchmark 不是 full 3D 場驗證

## Slide 13: 研究貢獻與資料策略
- 三因子、有限感測器、非連網裝置、服務化
- canonical synthetic benchmark + real-bedroom snapshots + task-aligned public datasets
- 室內應用溫度限 20–30 °C；人體舒適採目標帶與 tolerance
- 明確列出每種資料支援的驗證範圍

## Slide 14: E11B：AAU 伺服器機房空間轉移
- 42 個高信心 PT100、1,641 個一分鐘快照；六個不明通道預先排除
- MAE：全域平均 2.293 °C、最近鄰 1.175 °C、3D IDW 1.687 °C
- 感測器勝出：最近鄰 30/42、IDW 6/42，未達預註冊 60% 門檻
- H-ENC-02 不支持；不事後調參，可能原因須另行驗證

## Slide 15: E11C：局部鄰域獨立確認
- 11 個 E11B-disjoint ranges、42 點、1,505 快照、11 個 day blocks
- MAE：最近鄰 1.301 °C、local IDW 1.223 °C、global IDW 1.844 °C
- paired improvement 0.0783 °C；bootstrap 95% CI [0.0546, 0.1063]
- local 與 nearest 各勝出 21/42；未達 26/42，H-ENC-03 不支持

## Slide 16: 結論與未來工作
- 長期真實資料、dense real-room ground truth、更多因子、multi-zone 與推薦動作介入驗證
- GRU/LSTM 簡易同資料比較完成：lowest MAE 皆 0/12，GRU 2/12、LSTM 0/12 勝 vanilla；PID 尚未評估
- E11C aggregate 改善但 sensor coverage 不足；後續 sensor-role/topology model 須新資料與預註冊
- 候選動態植物生長情境需補 PPFD/CO2/基質/生物 endpoint
- Kalman 受控比較為混合結果；下一步以獨立 reference 驗證實體 sensor filtering

## Slide 17: 公式說明 1：三因子場與查詢點
- 場的定義
- 適用範圍

## Slide 18: 公式說明 2：總估計式
- 主公式
- 為什麼這樣拆

## Slide 19: 公式說明 3：Indoor baseline
- baseline 定義
- 跟 baseline 比較法的差別

## Slide 20: 公式說明 4：baseline 的取得方式
- 有啟動前觀測時
- 沒有啟動前觀測時

## Slide 21: 公式說明 5：高度正規化
- 垂直座標
- 為什麼需要

## Slide 22: 公式說明 6：設備 activation
- 時間響應
- 使用原因

## Slide 23: 公式說明 7：influence envelope
- 空間作用範圍
- 距離衰減

## Slide 24: 公式說明 8：溫度場主式
- 溫度 nominal model
- 使用原因

## Slide 25: 公式說明 9：溫度的全室與局部項
- 分解式
- 三類來源

## Slide 26: 公式說明 10：冷氣溫度項
- 冷氣全室項
- 冷氣局部項

## Slide 27: 公式說明 11：窗戶與燈具溫度項
- 窗戶熱交換
- 燈具熱源

## Slide 28: 公式說明 12：濕度場主式
- 濕度 nominal model
- 使用原因

## Slide 29: 公式說明 13：濕度來源項
- 全室濕度項
- 局部濕度項

## Slide 30: 公式說明 14：照度場主式
- 照度 nominal model
- 為什麼不同於溫濕度

## Slide 31: 公式說明 15：直射光與環境光
- 窗戶直射光
- 燈具與環境光

## Slide 32: 公式說明 16：一次漫反射
- 反射公式
- 模型限制

## Slide 33: 公式說明 17：8 參數校正多項式
- 三線性形式
- 為什麼剛好 8 點

## Slide 34: 公式說明 18：角點 residual
- residual 定義
- 直覺意義

## Slide 35: 公式說明 19：三線性校正式
- 校正公式
- 重要性質

## Slide 36: 公式說明 20：校正後估計值
- 回到主公式
- 適用範圍

## Slide 37: 公式說明 21：可完全表示的 residual 空間
- 函數空間
- 適用範圍

## Slide 38: 公式說明 22：平滑 residual 的誤差界
- 這個上界在衡量什麼
- 為什麼會這樣

## Slide 39: 公式說明 23：非連網裝置影響學習
- before/after delta
- least-squares 估計

## Slide 40: 公式說明 24：Hybrid residual
- 第二層修正
- 定位

## Slide 41: 公式說明 25：Hybrid 訓練目標
- residual label
- 損失函數

## Slide 42: 公式說明 26：MAE、RMSE 與 Correlation
- 誤差指標
- 使用原因

## Slide 43: 公式說明 27：IDW baseline
- IDW 插值
- 比較基準理由

## Slide 44: 公式說明 28：推薦排序與驗證
- 推薦分數
- 驗證限制


## 補充結果：E11D 角色條件式確認

- H-ENC-04：supported；1,505 分鐘快照。
- 全域平均 MAE/RMSE：2.3972/2.9748 C；角色條件模型：1.6517/2.3648 C。
- 角色模型勝出 30/42；配對改善 0.7455 C，95% CI [0.6867, 0.8124] C。
- 僅為預測性角色資訊，不宣稱氣流因果。

## E11E 開發結果

- 最佳 role_local_k5_p2：MAE 1.0187 C，但 P95 3.7699 C 高於 baseline 3.4900 C。
- 只贏 25/42，決策為 no_candidate_forwarded；E11F 未下載。


## E11G tail-safe 自適應開發

- 12 日 leave-one-day-out、42 感測器、30 個裁切與回退候選。
- MAE 1.1168→0.8945°C；RMSE 1.7250→1.5415°C；P95 3.4900→3.1013°C。
- bootstrap 95% CI：[0.1847, 0.2620]°C。
- 嚴格勝率僅 21/42，低於 26/42；`no_candidate_forwarded`，E11F 未存取。


## E11H commissioning 與 E11F confirmation

- E11H：2 日校正、1 日選模、9 日凍結測試；MAE 0.4039°C，P95 1.2900°C，39/42。
- E11F：不 refit；MAE 0.3966°C、RMSE 0.6723°C、P95 1.2756°C，39/42。
- H-ENC-05 僅於同 campaign 未見 bytes 獲支持；日期重疊，非跨機箱或 NTC 硬體驗證。
- 決策：`h_enc_05_supported_within_campaign`。
