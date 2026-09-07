# 碩士論文兩週研究進度報告（教授版）

- 報告期間：2026 年 8 月 4 日至 8 月 17 日
- 研究主題：以稀疏感測建構單房間空間數位孿生，學習非連網設備的環境影響

## 一、兩週工作摘要

本次將兩週工作集中在「比較公平性、研究適用邊界與可展示成果」三個面向。除完成 SML2010 時序 RNN 比較外，另補做教授要求的 pure RNN 完整 3-D 場 baseline，使 IDW、base model、pure RNN 與 LOO hybrid 真正使用相同八情境任務比較；第二週也把 Kalman Filter 從文獻參考推進為固定 protocol 的受控同資料實驗，最後整理成可離線開啟的成果頁與可操作的 Live Web demo。

主要結論如下：

1. Pure RNN 3-D 場比較完成 8/8 LOO folds、24 個 fold×因子比較，最低 MAE 為 0/24；SML2010 時序 RNN 也為 0/12，兩種任務都未顯示 recurrent complexity 自動轉化為優勢。
2. Kalman 受控去噪的 12 個案例中，Linear Kalman 與因果三點移動平均各取得 6/12 最低 MAE；Kalman 並非普遍最佳。
3. 人體舒適保留為具有容許範圍的 decision support，不再由低 MAE 直接推論需要極窄控制。
4. 目前室內溫度適用範圍固定為 20–30°C；動態封閉植物生長環境仍只是候選情境。
5. 新增的教授展示頁直接讀取實驗 JSON，並搭配既有 Live Web demo 展示房間三因子場、點位查詢與推薦排序。

## 二、先前表現與改進後對比

### 2.1 受控八情境的模型逐步改善

下表比較傳統 IDW、設備感知 base model、不使用 physics estimate 的 pure Elman RNN，以及 leave-one-scenario-out hybrid residual。四者使用相同八組受控情境、稀疏觀測、held-out query grid 與 dense synthetic truth；兩個 learned models 共用相同七情境訓練 folds 與每情境 96 個固定訓練點。數值為平均 field MAE，越低越好。

| 環境因子 | 傳統 IDW | Base model | Pure RNN | LOO hybrid | Hybrid 相對 base 降幅 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 溫度 | 0.1723 °C | 0.0474 °C | 0.2091 °C | **0.0017 °C** | 96.41% |
| 相對濕度 | 0.4633 %RH | 0.1765 %RH | 0.2241 %RH | **0.0059 %RH** | 96.66% |
| 照度 | 54.9052 lux | 2.0269 lux | 48.1422 lux | **0.1407 lux** | 93.06% |

Pure RNN 相對 IDW 改善濕度 51.62% 與照度 12.32%，但溫度 MAE 增加 21.36%；相對 base 與 LOO hybrid 的三項平均 MAE 都較差，24 個 fold×因子也沒有一次取得最低 MAE。此負向結果不再調參覆蓋。整個對比只代表具有完整場真值的 controlled simulation，不能當作任意真實房間的 dense 3-D 精度。

### 2.2 相同 SML2010 資料的時序模型比較（包含 RNN）

本節是另一個 SML2010 時間序列預測任務，和第 2.1 節新增的 pure RNN 3-D 場 baseline 不同。以下另列相同 history、相同 chronological 70/30 split、相同 targets 與相同 test rows 的公平比較；12/12 案例皆通過資料一致性檢查，MAE 越低越好。

| 目標 | Horizon | Persistence | Sequence LR | Physics readout | Vanilla RNN | 最低 MAE 方法 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 餐區溫度 | 15 分鐘 | 0.118154 | **0.016487** | 0.069204 | 0.259807 | Sequence LR |
| 房間溫度 | 15 分鐘 | 0.115218 | **0.018776** | 0.067937 | 0.316127 | Sequence LR |
| 餐區濕度 | 15 分鐘 | 0.198397 | **0.189546** | 0.778755 | 0.484262 | Sequence LR |
| 房間濕度 | 15 分鐘 | 0.155824 | **0.128892** | 0.727862 | 0.633350 | Sequence LR |
| 餐區溫度 | 60 分鐘 | 0.469600 | **0.067138** | 0.093449 | 0.435441 | Sequence LR |
| 房間溫度 | 60 分鐘 | 0.457705 | **0.084668** | 0.101314 | 0.429146 | Sequence LR |
| 餐區濕度 | 60 分鐘 | **0.566856** | 0.584455 | 0.895847 | 1.209041 | Persistence |
| 房間濕度 | 60 分鐘 | 0.482232 | **0.370518** | 0.715989 | 1.113235 | Sequence LR |
| 餐區溫度 | 1,440 分鐘 | **1.521370** | 1.779259 | 1.762011 | 1.817166 | Persistence |
| 房間溫度 | 1,440 分鐘 | **1.503931** | 1.791041 | 1.785077 | 1.840638 | Persistence |
| 餐區濕度 | 1,440 分鐘 | **2.784009** | 3.294880 | 3.234758 | 3.966149 | Persistence |
| 房間濕度 | 1,440 分鐘 | **3.520060** | 4.129813 | 4.279578 | 4.322953 | Persistence |

彙總最低 MAE 案例數為 Sequence LR 7/12、Persistence 5/12、Physics readout 0/12、Vanilla RNN 0/12。這是有保留價值的負向結果：目前固定的小型 RNN 並未比簡單基準更好。

### 2.3 真實臥室保留點的校正前後

真實臥室資料包含 7 天、28 筆 snapshots，以未參與校正的 pillow 位置作為保留點。

| 環境因子 | 校正前 MAE | 校正後 MAE | 相對下降 |
| --- | ---: | ---: | ---: |
| 溫度 | 0.8967 °C | 0.1676 °C | 81.31% |
| 相對濕度 | 4.1286 %RH | 0.3939 %RH | 90.46% |
| 照度 | 309.0142 lux | 16.6450 lux | 94.61% |

這項結果支持目前房間、日期與 pillow 保留點上的稀疏校正改善；不能外推為其他房間或完整空間的普遍真值。

### 2.4 比較完整度的兩週推進

| 面向 | 先前狀態 | 兩週完成後 |
| --- | --- | --- |
| 3-D 場模型 | IDW、base、LOO hybrid | 新增同八情境 pure RNN；8/8 folds parity 通過、lowest MAE 0/24 |
| 時序模型 | persistence、linear regression、physics-structured readout | 加入相同資料的 vanilla RNN |
| 時序 RNN 結果 | 未評估 | 12/12 完成；最低 MAE 0/12 |
| Kalman | 文獻參考、`NOT_EVALUATED` | 完成 12 個受控 injected-noise filtering 案例 |
| 資料公平性 | 同公開資料與 chronological split | RNN 固定相同 history/test rows；Kalman 三方法固定相同 corrupted observations/test rows |
| 應用理由 | 人體舒適作為高精度控制主要動機 | 人體舒適改用 tolerance；另找需要動態環境配方的場景 |
| 溫度邊界 | 容易在應用討論中被忽略 | 明確限制室內受控／估測狀態為 20–30°C |
| 成果展示 | 研究數字與通用 Web demo 分開 | 新增教授離線成果頁與 8–10 分鐘 Live demo 順序 |

## 三、第一週：兩種 RNN 比較與應用範圍

### 3.1 Pure RNN 完整 3-D 場比較

Pure RNN 將同一張 snapshot 的八顆角落感測器依固定順序視為八個 sensor tokens；每個 token 包含感測器座標與三因子觀測，並重複附上查詢點座標與當下 room／environment／device context。模型直接預測查詢點的 temperature、humidity、illuminance 絕對值，不使用 base physics estimate、IDW prediction、residual target 或 held-out truth。

八個 LOO folds 都以七個情境、每情境 96 個固定點訓練 Pure RNN 與 hybrid，再於 held-out 情境完整 1,152 點評估；8/8 parity 通過。結果如第 2.1 節：Pure RNN 平均 field MAE 為 0.2091°C、0.2241%RH、48.1422 lux，最低 MAE 0/24。這表示目前八情境與固定小型 Elman architecture 下，pure recurrent baseline 無法取代設備感知結構與 hybrid residual；但只支持這個受控設定，不能推論所有 RNN／LSTM／GRU 都不適合空間重建。

### 3.2 SML2010 時序 RNN 同資料比較

比較使用 SML2010 S2 的 dining/room 溫度與濕度，horizon 為 15、60 與 1,440 分鐘。逐案例 MAE 與最低方法已移到第 2.2 節的主對比區，避免教授只看到 3-D 場重建表而漏掉 RNN。四種方法共用相同四筆 origin history、chronological 70/30 split、targets 與 test rows；12/12 案例通過資料一致性檢查。

結果表示，目前固定小型 RNN 沒有建立整體優勢；若要測試不同 history length、LSTM 或 GRU，應另行定義 protocol，且其他模型仍需取得相同資料。

### 3.3 高精度應用與 20–30°C 邊界

一般人體舒適通常使用目標帶與容許範圍，因此低估測 MAE 不代表實際空調必須進行同等精度的致動。現階段較合理的候選，是具有日夜或生長階段環境配方的小型封閉植物生長室；但目前系統只有 lux，缺少 PPFD/PAR、CO₂、基質水分、氣流與生物 endpoint，因此不能宣稱植物培養效益或部署準備度。

任何候選室內情境都必須維持在目前研究的 20–30°C 範圍；外部天氣輸入超出此區間，不會擴張室內適用性主張。

## 四、第二週：Kalman Filter 實際比較

### 4.1 實驗目的與公平性

直接拿同一筆量測同時作為 filtering input 與 ground truth，會讓未濾波方法得到零誤差。因此本次保留原始 normalized SML2010 溫濕度序列作為 task reference，再用固定 seed 加入三種已登記的 Gaussian measurement-noise stress profile。所有方法都取得完全相同的 corrupted observations、chronological 70/30 split、current-time targets、test timestamps 與 metrics。

比較方法為：

- 未濾波 raw noisy observation；
- causal moving average，固定使用目前與前兩筆資料；
- scalar linear Kalman random-walk model，`F=1`、`H=1`，`R` 取登記的 injected-noise variance，`Q` 由 training reference 的相鄰差分變異估計。

Noise profile 為溫度 0.5／1.0／2.0°C，以及濕度 1.5／3.0／5.0 %RH。這些是 controlled stress levels，不代表特定 DHT11、DHT22 或 SHT31 的實測雜訊。

### 4.2 實驗結果

12/12 案例完成且資料 parity 全部通過。最低 MAE 分布如下：

| 方法 | 最低 MAE 案例數 |
| --- | ---: |
| 未濾波 | 0/12 |
| Causal MA(3) | 6/12 |
| Linear Kalman | 6/12 |

逐案例 MAE：

| 目標 | 雜訊 | 未濾波 | MA(3) | Kalman | 最低方法 |
| --- | --- | ---: | ---: | ---: | --- |
| 餐區溫度 | low | 0.3967 | 0.2587 | 0.3791 | MA(3) |
| 餐區溫度 | nominal | 0.7859 | 0.4531 | 0.7230 | MA(3) |
| 餐區溫度 | high | 1.5780 | 0.9278 | 1.2355 | MA(3) |
| 房間溫度 | low | 0.4058 | 0.2524 | 0.3408 | MA(3) |
| 房間溫度 | nominal | 0.8161 | 0.4927 | 0.6669 | MA(3) |
| 房間溫度 | high | 1.6247 | 0.9349 | 1.1485 | MA(3) |
| 餐區濕度 | low | 1.1782 | 0.7284 | 0.6229 | Kalman |
| 餐區濕度 | nominal | 2.3316 | 1.3531 | 0.9212 | Kalman |
| 餐區濕度 | high | 3.8618 | 2.2598 | 1.2180 | Kalman |
| 房間濕度 | low | 1.1452 | 0.6787 | 0.5746 | Kalman |
| 房間濕度 | nominal | 2.3385 | 1.3672 | 0.9155 | Kalman |
| 房間濕度 | high | 3.8469 | 2.2440 | 1.1908 | Kalman |

Kalman 在 12/12 案例都優於未濾波，但只在濕度 6 案例優於 MA(3)；溫度 6 案例全部由 MA(3) 勝出。合理的研究結論是：filtering 方法是否有利與變數動態、process model 與 covariance 有關，不能宣稱 Kalman 普遍優於簡單平滑。

此實驗是 fixed-seed controlled injected-noise current-time filtering，不是實體感測器去噪、未來值預測、完整 3-D 場、跨場域或控制效益驗證。

## 五、完整實驗盤點

| 編號 | 實驗 | 目前狀態與邊界 |
| --- | --- | --- |
| E1 | 八情境完整場重建 | 已完成；IDW／base／pure RNN／LOO hybrid 同任務比較，pure RNN lowest MAE 0/24；只代表 controlled full-field truth。 |
| E2 | IDW baseline | 已完成；同八角點觀測比較，個別 idle 照度仍可由 IDW 較佳。 |
| E3 | 消融實驗 | 已完成；no-trilinear 平均表現較佳的負向結果保留。 |
| E4 | 非連網設備影響學習 | 已完成受控方向檢查；不是真實因果識別。 |
| E5 | 48 組窗戶矩陣 | 34 組室內 target-zone 溫度在 20–30°C；14 組只作範圍外壓力測試。 |
| E6 | Hybrid residual | 八折 LOO 平均降至 0.0017°C、0.0059%RH、0.1407 lux；只支持標準情境 family。 |
| E7 | 真實臥室稀疏校正 | 7 天 28 筆、held-out pillow 三因子改善；一房、一點、七日。 |
| E8 | 推薦動作真實介入 | Trial 為 0，仍是 `NOT_EVALUATED`。 |
| E9 | 公開資料 task-aligned benchmark | RNN 同資料比較已完成；公開資料不是 full 3-D 驗證。 |
| E10 | Kalman controlled filtering | 12/12 完成；Kalman 與 MA(3) 各勝 6 案例，僅支持 injected-noise current-time filtering。 |

## 六、教授可觀看的實際 Demo

### 6.1 離線兩週成果頁

入口：`outputs/demos/professor_two_week_demo_2026-08-04_2026-08-17_zh.html`

可直接雙擊開啟，內容包括：

- 兩週工作摘要；
- IDW、base、pure RNN、LOO hybrid 與真實 pillow 校正前後；
- Pure RNN 3-D 場與 SML2010 時序 RNN 的兩種同資料結果；
- 12 個 Kalman 案例、adverse cases 與代表性 trace；
- 20–30°C、植物候選情境與 E8 證據限制；
- Live Web demo 的啟動方式與講解順序。

### 6.2 Live Web demo

```bash
python3 scripts/run_web_demo.py
```

瀏覽器開啟 `http://127.0.0.1:8765`，建議依序展示：

1. 切換冷氣、窗戶與照明，旋轉 3-D 溫度／濕度／照度場。
2. 調整時間軸，觀察設備啟動至準穩態的場變化。
3. 切換 base 與 hybrid estimator，說明 learned residual 是修正層。
4. 以 point sample 查詢指定座標。
5. 輸入完整三因子目標並查看 recommendation ranking。
6. 說明推薦仍是 model-based counterfactual ranking，E8 未完成真實介入。

完整展示腳本位於 `docs/demos/professor_demo_guide_2026-08-17_zh.md`。

## 七、後續研究方向

下列項目是後續研究規劃，**目前皆為 `NOT_EVALUATED`，不是本週已完成結果**。

| 方向 | 在本研究中的角色 | 執行前必須固定的公平條件或擴充 | 目前狀態 |
| --- | --- | --- | --- |
| GRU | gated recurrent estimator comparator | 與 vanilla RNN 使用相同資料、fold、input、target、test points、訓練與調參預算 | `NOT_EVALUATED` |
| LSTM | gated recurrent estimator comparator | 與 RNN／GRU 共用資料與測試點，架構和停止規則須在看 test 結果前固定 | `NOT_EVALUATED` |
| PID | 閉環控制 baseline，不是 3-D 場估測器 | 固定同一 plant、setpoint trajectory、disturbance、sampling、actuator limit 與安全 cutoff；比較 tracking MAE、settling time、overshoot、control effort | `NOT_EVALUATED` |
| 機箱／設備櫃內熱環境 | 20–30°C 內的候選轉移場景 | 需新增機箱尺度、風道／風扇、元件熱源、動態負載、sensor/reference 配置；房間結果不得直接外推 | `NOT_EVALUATED` |

GRU 與 LSTM 的目的，是檢查 gated memory 是否在相同資料條件下改善固定 Elman RNN；它們不能用來覆蓋已完成的 pure RNN 3-D `0/24` 與 SML2010 時序 RNN `0/12`。PID 則屬於推薦排序之後的控制研究，必須先完成 E8 before/after 介入與安全 plant 定義。機箱具有負載快速變化、局部熱點與強迫對流，確實比一般人體舒適更有動態精準溫控理由，但常見元件熱點可能超過 30°C，超出部分必須列為 out-of-scope；而且部分機箱不需要濕度或照度，因此不得直接沿用目前三因子貢獻。

## 八、目前研究結論

1. 目前最穩定的主線仍是「稀疏 IoT 感測、單房間空間校正、非連網設備影響建模與可解釋決策支援」。
2. 受控模擬與真實 pillow 保留點均顯示校正有價值，但證據類型不能混為完整真實 3-D 場驗證。
3. Pure RNN 在完整 3-D 場為 0/24，時序 RNN 在 SML2010 為 0/12；Kalman 只在濕度受控去噪案例勝過 MA(3)。三項結果都支持保留簡單 baseline、結構先驗與負向結果。
4. Kalman 可作為往後 sensor-state filtering 或 online estimation 的參考，但真實部署仍需獨立 reference sensor、missingness 與 covariance-drift protocol。
5. 人體舒適不應作為極窄控制需求的唯一理由；候選動態植物環境仍須遵守 20–30°C 並補足植物專屬變數。
6. Live demo 證明系統可操作與可查詢，但不能替代量化實驗或真實因果介入。

## 九、希望與教授確認的事項

1. 是否同意把 Kalman 下一階段優先放在實體 sensing-node 的 current-time state filtering，而不是直接改成主模型或預測器。
2. 真實感測器 Kalman 比較應優先使用哪一種 validation reference（例如 SHT31 或更高精度設備）。
3. 是否同意以「MA(3) 在溫度較佳、Kalman 在濕度較佳」作為方法依變數而異的負向／混合結果。
4. 候選應用是否繼續以 20–30°C 內的小型封閉植物生長環境為方向，或改找另一個具動態設定需求且能使用現有三因子量測的場景。
5. E8 真實 before/after 介入是否列為下一個必要研究工作。
6. 是否同意把 Pure RNN 0/24 保留為 standalone black-box baseline 的負向結果，而不在看到結果後改用 LSTM／GRU 覆蓋本次 protocol。
7. GRU／LSTM 是否先做完整 3-D 場同八情境比較，還是優先做 SML2010 時序任務；兩者將分開註冊，避免混用指標。
8. PID 是否以 20–30°C 動態 setpoint tracking 作為第一個閉環控制 baseline，並與相同 plant／disturbance 下的模型式控制比較。
9. 「機箱／設備櫃內熱環境」是否值得作為下一個轉移情境；若確認，需先界定風道、風扇、元件熱源及是否仍保留濕度／照度研究問題。
