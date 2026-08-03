# 碩士論文完整實驗總覽

- 整理日期：2026 年 8 月 3 日
- 研究主題：以稀疏感測建構單房間空間數位孿生，學習非連網設備的環境影響
- 適用對象：教授進度報告與實驗架構確認

## 一、閱讀方式與證據分層

目前實驗不是由單一資料集完成全部驗證，而是分成四種證據層。不同層回答的問題不同，不能把結果合併成「模型已在所有環境驗證成功」。

| 證據層 | 對應實驗 | 能回答的問題 | 不能宣稱的內容 |
| --- | --- | --- | --- |
| 受控模擬 | E1–E6 | 在已知完整場真值下，模型元件、場重建、baseline、邊界敏感度與 residual 是否有效 | 任意真實房間也有相同精度 |
| 真實房間快照 | E7 | 八角落感測校正能否改善未參與校正的 pillow 參考點 | 完整三維真實場、跨房間泛化或因果控制 |
| 真實介入 | E8 | 執行建議動作後是否真的改善目標 | 目前尚無完成 trial，不能宣稱效果 |
| 公開資料相容任務 | E9 | 模型概念在 SML2010、CU-BEMS 相容時序任務中的外部比較 | 八角落三維場、完整房間幾何或真實裝置係數驗證 |

證據狀態定義：

- `REPRODUCIBLE`：已有機器可讀結果與可重跑命令。
- `DOCUMENT_ONLY`：已有設計或說明，但缺正式實驗結果。
- `NOT_EVALUATED`：尚未完成所需資料或實驗。
- `OUT_OF_DOMAIN`：結果保留，但超出目前模型應用範圍，不可支持適用性主張。

## 二、E1–E9 實驗總表

| 編號 | 實驗名稱 | 資料 | 主要比較 | 指標 | 目前狀態 | 最重要結論 |
| --- | --- | --- | --- | --- | --- | --- |
| E1 | 標準情境完整場重建 | 8 組受控模擬 | estimated field vs controlled truth | T/H/L field MAE | `REPRODUCIBLE` | Base model 平均 MAE 為 0.0474°C、0.1765%RH、2.0269 lux |
| E2 | IDW baseline | 與 E1 相同的 8 組情境與評估點 | Base model vs IDW | T/H/L field MAE | `REPRODUCIBLE` | Base model 平均優於 IDW，但個別無設備影響的變數可能由 IDW 較佳 |
| E3 | 消融與可重現性 | 8 組受控情境 | raw nominal、no reflection、no calibration、no trilinear、full base、IDW | 平均 field MAE | `REPRODUCIBLE` | 元件作用並非全部單調；no-trilinear 與 raw nominal 的部分結果優於 full base，必須保留 |
| E4 | 非連網裝置影響學習 | before/after controlled observations | sensor delta vs device spatial basis | 係數方向、sensor MAE | bounded check | 可解出冷氣負溫度／濕度方向與照明正照度方向，但不是實測因果識別 |
| E5 | 48 組窗戶矩陣與 direct input | 4 時段 × 3 天氣 × 4 季節 | 本研究模型 vs IDW；跨外部條件比較 | zone values、field MAE | `REPRODUCIBLE` | 34 組室內 target-zone 溫度在 20–30°C；14 組僅能作範圍外壓力測試 |
| E6 | Hybrid residual robustness | controlled residual samples | Base vs hybrid、Fourier vs no-Fourier、8-fold LOO | field MAE、sample count | `REPRODUCIBLE` | LOO 平均 MAE 降至 0.0017、0.0059、0.1407，但只支持標準情境 family |
| E7 | 真實臥室稀疏校正 | 7 天、28 筆快照、held-out pillow point | raw vs calibrated | pillow MAE、block bootstrap、LODO | `REPRODUCIBLE` | 三因子均改善，且 bootstrap 與逐日剔除仍為正；只限一房一點七天 |
| E8 | 推薦動作真實介入 | 規劃中的 before/after trials | top-ranked、alternative、human、no-action | actual improvement、direction accuracy、regret | `NOT_EVALUATED` | 目前 0 個完成 trial，所有因果效果指標為 null |
| E9 | 公開資料 task-aligned benchmark | SML2010、CU-BEMS | persistence、linear、project readout、transfer、RNN | MAE、RMSE、correlation | `REPRODUCIBLE` | 優勢集中在部分事件與溫度任務；照度、高慣性、次日與 RNN 有明確負向結果 |

## 三、共同實驗設定

### 受控房間與感測配置

- 單一矩形房間，標準房間尺寸為 6.0 m × 4.0 m × 3.0 m。
- 使用地面四角與天花板四角共 8 顆感測器。
- 主要輸出為 temperature、humidity、illuminance 三個連續場。
- 標準網格為 16 × 12 × 6。
- 標準設備為冷氣、窗戶與照明，可組合成 8 組 canonical scenarios。

### 比較與解讀原則

1. 場重建比較必須使用相同評估點。
2. 公開資料模型必須使用相同 target、horizon、chronological split 與 test rows。
3. Controlled truth、真實快照、公開資料與真實介入不得互相替代。
4. 現階段室內受控、估測與目標狀態的適用範圍為 20–30°C；外部天氣可超出，但不擴張室內主張。
5. 人體舒適採目標帶與容許範圍，不由低 MAE 直接推論必須進行極窄控制。

## 四、各實驗完整整理

### E1：標準情境完整場重建

**目的**：檢查 reduced-order physics、設備影響場、反射近似與稀疏校正後，能否在 8 組受控情境中重建完整三因子場。

**情境**：idle、ac_only、window_only、light_only、ac_window、window_light、ac_light、all_active。

| 指標 | 8 情境平均 MAE | 最大 MAE |
| --- | ---: | ---: |
| Temperature | 0.0474°C | 0.0481°C |
| Humidity | 0.1765%RH | 0.1770%RH |
| Illuminance | 2.0269 lux | 2.2990 lux |

**判讀**：受控條件下，各標準情境的 base field MAE 量級穩定；但 truth 與 estimator 共享部分結構，不能外推為任意真實房間的實際精度。

**證據**：`outputs/data/validation_summary.json`  
**重跑**：`python3 scripts/run_demo.py`

### E2：IDW baseline 比較

**目的**：比較只依距離插值八角落觀測的 IDW，與具有設備位置、方向、外部邊界與變數專屬物理結構的 base model。

| 指標 | IDW 平均 MAE | Base model 平均 MAE | Base 相對 IDW 降幅 |
| --- | ---: | ---: | ---: |
| Temperature | 0.1723°C | 0.0474°C | 72.47% |
| Humidity | 0.4633%RH | 0.1765%RH | 61.90% |
| Illuminance | 54.9052 lux | 2.0269 lux | 96.31% |

**負向結果**：在 `idle` 與 `ac_only` 的 illuminance 中，沒有實際照明或窗戶變化，IDW 的 1.3210 lux 低於 base model 的 1.7625 lux。這表示設備結構並非每個變數、每個情境都必然優於簡單插值。

**證據**：`outputs/data/validation_summary.json`  
**重跑**：`python3 scripts/run_demo.py`

### E3：消融與可重現性

**目的**：檢查反射、active-device power calibration、trilinear correction 與完整 base estimator 的個別作用，並保留不支持預期的結果。

| Variant | Temperature MAE | Humidity MAE | Illuminance MAE |
| --- | ---: | ---: | ---: |
| IDW | 0.1723 | 0.4633 | 54.9052 |
| Raw nominal | 0.1312 | 0.0842 | 3.5183 |
| No reflection | 0.0472 | 0.1762 | 2.4296 |
| No calibration | 0.0493 | 0.1772 | 3.3631 |
| No trilinear | 0.0446 | 0.0274 | 0.9849 |
| Full base | 0.0474 | 0.1765 | 2.0269 |

**判讀**：

- 移除 reflection 後照度 MAE 由 2.0269 上升至 2.4296，支持反射近似的照度作用。
- 移除 calibration 後三項 MAE 均上升，支持 power calibration 的作用。
- `no trilinear` 在三項平均值均低於 full base，`raw nominal` 的 humidity 也較低；這些是必須保留的 adverse ablation，表示目前合成真值與擾動設計不能證明每個校正元件在所有條件下單調改善。
- 固定 seed 與 index-based perturbation 使實驗可重現，但不等於獨立真實量測。

**證據**：`outputs/data/submission_readiness_summary.json`  
**重跑**：`python3 scripts/run_submission_readiness_experiments.py`

### E4：非連網裝置影響學習

**目的**：由同一批感測器的 before/after delta 與裝置 spatial basis，以 least squares 學習沒有 API 回報裝置的環境影響方向與相對強度。

| Controlled scenario | Device | Temperature coefficient | Humidity coefficient | Illuminance coefficient |
| --- | --- | ---: | ---: | ---: |
| ac_only | ac_main | -36.8076 | -16.9792 | 0.0000 |
| light_only | light_main | 2.7633 | 0.0000 | 321.7206 |

**判讀**：冷氣係數方向符合降溫與除濕，照明係數方向符合增亮與少量發熱。係數受到 envelope 尺度、設備狀態與情境設定影響，不可跨設備直接比較，也不能當作真實因果效果。

**證據**：`outputs/data/validation_summary.json` 的 `learned_device_impacts`  
**重跑**：`python3 scripts/run_demo.py`

### E5：窗戶矩陣與 direct-input sensitivity

**目的**：檢查外部溫度、外部濕度、日照、時段、季節與天氣改變時，非連網窗戶對室內 zone 的影響。

**規模**：4 季節 × 3 天氣 × 4 時段，共 48 組。

**20–30°C 室內範圍稽核**：

| 分類 | 案例數 | 可否支持目前適用性主張 |
| --- | ---: | --- |
| Target-zone temperature 在 20–30°C | 34 | 可作目前範圍內的受控敏感度證據 |
| 低於 20°C 或高於 30°C | 14 | 僅保留為 `OUT_OF_DOMAIN` 壓力測試 |

| 代表情境 | 外部 T/H/光 | Window-zone T/H/L | 範圍判定 |
| --- | --- | --- | --- |
| spring cloudy morning | 21.5°C / 70% / 5005 lux | 23.3906°C / 64.3478% / 96.7992 lux | in-domain |
| summer sunny noon | 37°C / 71% / 36000 lux | 30.1992°C / 70.5823% / 247.3004 lux | `OUT_OF_DOMAIN` |
| winter rainy night | 11°C / 78% / 15.2 lux | 17.4398°C / 61.0178% / 73.0820 lux | `OUT_OF_DOMAIN` |

**判讀**：矩陣可以說明模型對外部條件的敏感度，但 14 組範圍外室內輸出不能用來主張目前模型適用於低溫或高溫環境。Direct input 只是使用同一模型接受連續外部條件，不代表自動擴張溫度範圍。

**證據**：`outputs/data/window_matrix_summary.json`  
**重跑**：`python3 scripts/run_window_matrix.py`

### E6：Hybrid residual robustness

**目的**：在保留 reduced-order physics 主模型的前提下，用小型 residual neural network 修正剩餘結構誤差，並檢查單一 split、Fourier 去噪與 scenario generalization。

| 設定 | Train/Test | Base T/H/L MAE | Hybrid T/H/L MAE | 降幅 |
| --- | --- | --- | --- | --- |
| Default 6/2 held-out | 576 / 192 | 0.0474 / 0.1765 / 2.1757 | 0.0020 / 0.0051 / 0.1370 | 95.78% / 97.11% / 93.70% |
| No-Fourier held-out | 576 / 192 | 同上 | 0.0021 / 0.0057 / 0.1370 | 95.57% / 96.77% / 93.70% |
| 8-fold leave-one-scenario-out | 每 fold 672 / 96 | 0.0474 / 0.1765 / 2.0269 | 0.0017 / 0.0059 / 0.1407 | 96.41% / 96.66% / 93.06% |

**負向／限制**：

- Fourier 對 temperature 幾乎沒有差異，只對 humidity 有小幅改善；照度不使用低通。
- `light_only` target-zone temperature 的 baseline 已接近零，hybrid 反而由 0.0013 增至 0.0027，不能宣稱每個 zone、每個 metric 都改善。
- LOO folds 仍來自同一標準情境 family，不代表跨房間或跨幾何泛化。

**證據**：`outputs/data/hybrid_residual_summary.json`、`outputs/data/submission_readiness_summary.json`  
**重跑**：`python3 scripts/run_hybrid_residual_experiment.py`、`python3 scripts/run_submission_readiness_experiments.py`

### E7：真實臥室快照稀疏校正

**目的**：檢查 8 顆角落真實觀測能否改善未參與校正的 pillow reference point。

**資料**：2026-04-14 至 2026-04-20，共 7 天；每日 morning、afternoon、night、sleep 四個時段，共 28 筆快照。

| 指標 | Raw pillow MAE | Calibrated pillow MAE | 相對降幅 |
| --- | ---: | ---: | ---: |
| Temperature | 0.8967°C | 0.1676°C | 81.31% |
| Humidity | 4.1286%RH | 0.3939%RH | 90.46% |
| Illuminance | 309.0142 lux | 16.6450 lux | 94.61% |

**日期 block bootstrap**：固定 seed 20260726，執行 20,000 次 paired resampling。

| 指標 | 平均絕對 MAE 降幅 | 95% interval | 改善快照 |
| --- | ---: | --- | ---: |
| Temperature | 0.7292°C | [0.4582, 1.0232] | 26 / 28 |
| Humidity | 3.7346%RH | [3.2005, 4.2524] | 28 / 28 |
| Illuminance | 292.3692 lux | [288.3083, 297.0237] | 28 / 28 |

**Leave-one-date-out**：七個 folds 的最小降幅仍為 0.6123°C、3.5551%RH、290.5716 lux。

**判讀**：目前七天、單一房間、單一 held-out pillow point 中，改善方向具有內部穩定性；這不是完整三維 real ground truth、七次獨立重複或跨房間結果。

**證據**：`outputs/data/bedroom_01_weekly/weekly_simulation_summary.json`  
**重跑**：`python3 scripts/run_bedroom_weekly_simulation.py`

### E8：推薦動作真實介入

**目的**：驗證排名第一的推薦動作實際執行後，是否造成預測方向一致的環境改善。

**設計**：top-ranked、alternative action、human baseline、no-action；記錄 before/after、settling interval、完整 target 與實際執行動作。

**目前狀態**：

- Completed trials：0。
- Evidence status：`NOT_EVALUATED`。
- Success rate、prediction error、direction accuracy、top-1 regret、rank correlation：全部為 null。
- 目前推薦只可稱為 model-based counterfactual ranking。

**證據**：`outputs/data/e8_intervention_summary.json`  
**重跑**：`python3 scripts/analyze_e8_intervention_trials.py`

### E9：公開資料 task-aligned benchmark

#### E9-A：公開資料 baseline

| Dataset | 任務 | 規模 | Baseline 結果 |
| --- | --- | --- | --- |
| SML2010 | S1 daylight、S2 thermal-humidity | 約 4,133 筆 | 短期溫度多由 linear regression 改善；照度與部分濕度由 persistence 較佳 |
| SML2010 | S3 boundary/event delta | 約 1,294 筆 | 線性模型對溫度 delta 有明顯優勢 |
| CU-BEMS | C1/C2 zone response | 約 1,145 萬筆 | persistence 全面強於 linear regression |
| CU-BEMS | C3 event delta | 約 16.8 萬筆 | linear regression correlation 提升，但 MAE 仍不勝 persistence |

#### E9-B：本研究 mapped readout 比較

| Dataset | Target-horizon cases | 最低 MAE | 勝 linear regression | 勝 persistence | 判讀 |
| --- | ---: | ---: | ---: | ---: | --- |
| SML2010 | 24 | 12 | 15 | 14 | 主要優勢在 S3 event delta 與部分 60 分鐘溫度；15 分鐘照度與濕度較弱 |
| CU-BEMS | 12 | 0 | 9 | 0 | C1/C3 可勝 linear，但 zone inertia 使 persistence 最強；C2 照度明顯較弱 |

#### E9-C：Oh et al. (2024) 啟發的 additive residual transfer

- 比較 15、60、1,440 分鐘 dining/room temperature，共 6 案例。
- Transfer 相對 raw physics 改善 4/6，因此註冊假設得到支持。
- 最低 MAE 分布：persistence 2、project readout 2、Oh-inspired transfer 2。
- 1,440 分鐘仍由 persistence 最佳，不能重現文獻中的 next-day advantage。
- 此方法是 fixed ridge-linear surrogate，不是原文 CNN–LSTM、TRNSYS/RC 或 confidential BEMS data 重現。

#### E9-D：次日溫度預測 follow-up

| 方法 | Dining MAE | Room MAE | 判讀 |
| --- | ---: | ---: | --- |
| Seasonal persistence | 1.5175 | 1.4996 | Confirmatory baseline |
| Validation-selected damped trend | 1.6289 | 1.6250 | 惡化 7.34% / 8.36% |
| Registered bias correction，未被 validation 選中 | 1.5018 | 1.4884 | 約 1% 訊號，不可事後改為主要結果 |
| Post-primary adaptive median 14d | 1.6515 | 1.6456 | 探索性分析亦惡化 |

**決策**：`H-ND-01`、robustness hypothesis 與 next-day claim 均不支持；不能宣稱次日預測優勢。

#### E9-E：Vanilla RNN 同資料公平比較

**方法**：persistence、sequence linear regression、physics-structured readout、vanilla Elman RNN。

**公平性**：所有模型共用相同 eligible endpoints、四筆 origin history、chronological 70/30 split、targets、test rows、metric functions 與 input-content audit；physics features 只能從相同 origin records 衍生，沒有載入額外 synthetic learned checkpoint。

| Horizon | Eligible | Train | Test | Parity |
| ---: | ---: | ---: | ---: | --- |
| 15 min | 4,121 | 2,884 | 1,237 | passed |
| 60 min | 4,110 | 2,877 | 1,233 | passed |
| 1,440 min | 3,933 | 2,753 | 1,180 | passed |

| 最低 MAE 方法 | 案例數 |
| --- | ---: |
| Sequence linear regression | 7 / 12 |
| Persistence | 5 / 12 |
| Physics-structured readout | 0 / 12 |
| Vanilla RNN | 0 / 12 |

**判讀**：RNN 有 2 案例勝 persistence、2 案例勝 physics readout，但 12 案例均未勝 sequence linear regression。在目前資料、四步歷史與固定小型架構下，recurrent complexity 沒有建立優勢。

**E9 證據**：`outputs/data/public_benchmarks/`  
**詳細逐案例表**：`docs/experiments/public_dataset_model_comparison_results_zh.md`

## 五、先前模型與改進後模型對比

| 層級 | 方法 | Temperature MAE | Humidity MAE | Illuminance MAE | 證據邊界 |
| --- | --- | ---: | ---: | ---: | --- |
| 傳統 baseline | IDW | 0.1723 | 0.4633 | 54.9052 | 8 組受控情境 |
| 先前主模型 | Full base | 0.0474 | 0.1765 | 2.0269 | 8 組受控情境 |
| 改進後模型 | LOO hybrid | 0.0017 | 0.0059 | 0.1407 | 8-fold standard-scenario family |

Base model 相對 IDW 的平均降幅為 72.47%、61.90%、96.31%；LOO hybrid 再相對 base model 降低 96.41%、96.66%、93.06%。這是 controlled simulation 的方法比較，不能直接代表真實房間精度。

真實房間的可用對比應改看 E7：pillow point 由 0.8967°C、4.1286%RH、309.0142 lux 降至 0.1676°C、0.3939%RH、16.6450 lux。

## 六、可以成立、不能成立與尚待完成的結論

### 目前有證據支持

1. 在受控完整場真值下，設備感知 base model 平均優於 IDW。
2. Hybrid residual 在標準 scenario family 的 held-out 與 LOO 中可進一步降低平均場誤差。
3. 真實臥室七天資料中，稀疏校正可改善未參與校正的 pillow 參考點，且日期 block bootstrap 與逐日剔除結果保持正向。
4. 公開資料中，結構化方法的優勢集中於部分 event/boundary delta 與中期溫度任務。
5. RNN 已完成同資料公平比較，但沒有最低 MAE 案例。

### 必須保留的負向或限制

1. E3 中 no-trilinear 與 raw nominal 的部分指標優於 full base，元件效益不是全面單調。
2. E6 並非每個 target zone 指標都改善。
3. E5 有 14/48 個 target-zone 室內溫度落在 20–30°C 之外，只能視為範圍外壓力測試。
4. CU-BEMS 沒有任何任務勝過 persistence；C2 照度是明顯弱點。
5. 次日主要方法與 post-primary adaptive 方法都未建立優勢。
6. RNN 最低 MAE 為 0/12。
7. 人體舒適不等於需要極窄控制；植物應用仍缺 PPFD/PAR、CO2、基質、氣流與生物 endpoint。

### 尚未完成

1. E8 真實推薦介入與因果效果。
2. 跨房間與長期 dense real-room ground truth。
3. 全程位於 20–30°C 的動態封閉植物環境驗證。
4. 相同資料的 unfiltered、moving average、KF、EKF 比較；目前 Kalman 仍為 `NOT_EVALUATED`。

## 七、完整重現命令索引

```text
python3 scripts/run_demo.py
python3 scripts/run_window_matrix.py
python3 scripts/run_hybrid_residual_experiment.py
python3 scripts/run_submission_readiness_experiments.py
python3 scripts/run_bedroom_weekly_simulation.py
python3 scripts/analyze_e8_intervention_trials.py
python3 scripts/run_public_dataset_benchmark.py
python3 scripts/run_public_dataset_model_comparison.py
python3 scripts/run_oh2024_inspired_comparison.py
python3 scripts/run_next_day_temperature_comparison.py
python3 scripts/run_rnn_public_comparison.py
python3 scripts/verify_thesis_results.py
```

完整流程也可由 `python3 scripts/run_all_thesis_experiments.py` 統一執行；公開資料存在時才執行相應 benchmark，缺資料不得以預期結果替代。
