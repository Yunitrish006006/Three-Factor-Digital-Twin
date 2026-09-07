# 教授版兩週研究 Demo 操作指南

## 展示入口

1. 離線成果頁：`outputs/demos/professor_two_week_demo_2026-08-04_2026-08-17_zh.html`
2. Live Web demo：

```bash
python3 scripts/run_web_demo.py
```

瀏覽器開啟 `http://127.0.0.1:8765`。

## 建議展示順序（約 8–10 分鐘）

### 1. 兩週研究摘要（1 分鐘）

- 第一週：Pure RNN 在相同八情境 3-D 場的 8/8 LOO folds 完成比較，最低 MAE 為 0/24；SML2010 時序 RNN 另為 0/12。
- 第二週：線性 Kalman 與未濾波、因果 MA(3) 使用相同受控雜訊序列；Kalman 與 MA(3) 各取得 6/12 最低 MAE。
- 強調研究沒有因模型較複雜就假設一定較好。

### 2. 前後表現對比（2 分鐘）

- 先看八情境受控模擬中的 IDW、base model、pure RNN 與 LOO hybrid；說明 pure RNN 不使用 physics estimate。
- Pure RNN 平均 MAE 為 0.2091°C、0.2241%RH、48.1422 lux，沒有勝過 base 或 hybrid；負向結果保留。
- 再看真實臥室 pillow 保留點的校正前後 MAE。
- 清楚區分 controlled full-field 與 one-room held-out point evidence。

### 3. Kalman Filter 實際結果（2 分鐘）

- 顯示 12 個 target/profile 的 raw、MA(3)、Kalman MAE。
- 濕度 6 案例由 Kalman 勝出；溫度 6 案例由 MA(3) 勝出。
- 說明這是 fixed-seed controlled injected-noise current-time filtering，不是真實感測器驗證。

### 4. Live 房間 Demo（3–5 分鐘）

1. 勾選冷氣、窗戶與照明，切換溫度／濕度／照度並旋轉 3-D 場。
2. 調整時間軸，觀察設備啟動後至準穩態的場變化。
3. 切換 base 與 hybrid estimator，說明 learned residual 是修正層。
4. 在 point sample 查詢指定座標的三因子估計。
5. 輸入完整三因子目標並展示 recommendation ranking。
6. 說明推薦仍是 model-based counterfactual ranking；E8 真實介入仍為 `NOT_EVALUATED`。

## 不應在 Demo 中宣稱的內容

- 不把 Web UI 操作視為新的量化實驗。
- 不把受控 Kalman 結果稱為 DHT11 或其他實體感測器驗證。
- 不把 SML2010 比較稱為完整 3-D 場驗證。
- 不把 pure RNN 的 controlled synthetic 3-D 結果稱為真實房間 dense-field 驗證，也不宣稱所有 recurrent architecture 都不適用。
- 不把低 MAE 直接等同於人體舒適需要極窄控制。
- 不把候選植物生長環境描述為已驗證應用；目前溫度範圍仍限 20–30°C。

## 重建離線成果頁

```bash
python3 scripts/run_rnn_3d_field_comparison.py
python3 scripts/run_kalman_filter_comparison.py
python3 scripts/build_professor_demo.py
```

離線頁的數值由現有 machine-readable JSON 產生，不手動複製研究結果。
