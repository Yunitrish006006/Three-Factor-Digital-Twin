# Change Proposal: improve-next-day-temperature-forecast

## Summary

建立一個專門針對 `h=1440 min` 的 SML2010 次日溫度預測器。模型不再只以
當下狀態直接回歸明日溫度，而是以「今天同時刻溫度」作季節性基準，學習
明日相對今日同時刻的變化量，並比較偏差校正、日趨勢、physics blend 與
origin-known ridge residual。候選模型只用開發集選擇，最後在固定且與前次
比較相同的末段 30% 測試資料上評估。

## Why

前一輪 `Oh2024-inspired` transfer 顯示，24 小時 horizon 的兩個溫度點皆由
persistence 取得最低 MAE；這是因為 `y(t)` 對 `y(t+24h)` 本身就是「昨天
同時刻」的強季節性基準。現有直接回歸與 physics residual 沒有顯式利用
日變化趨勢、週期特徵或 validation-only model selection，因此容易在跨日
季節漂移時退化。

## Change Map

### Next-day target formulation

- **From:** 直接預測 `y(t+24h)`，或修正 pseudo-room physics prediction。
- **To:** 以 `y(t)` 為次日同時刻基準，預測 delta `y(t+24h)-y(t)`。
- **Reason:** 把 persistence 已掌握的日週期保留下來，只學跨日變化。
- **Impact:** 新增獨立 E9 follow-up JSON，不覆寫既有公開資料 headline。

### Model selection

- **From:** 固定 ridge 或在單一 `70/30` split 上直接報告。
- **To:** 固定 `60/10/30` chronological train/validation/test，候選與超參數只由 validation MAE 決定；選定後以最前 70% refit，再評估末段 30%。
- **Reason:** 避免為了改善已知測試結果而直接調整測試集。
- **Impact:** 增加可重現的 selection trace、leakage audit 與不確定性估計。

## Scope

### In scope

- SML2010 `S2` dining/room temperature。
- Forecast horizon `1440 min`。
- Seasonal persistence、bias-corrected persistence、damped daily trend、
  persistence--physics blend、origin-known seasonal residual ridge。
- MAE、RMSE、Pearson correlation、R2、CVRMSE。
- Paired daily-block bootstrap MAE-reduction interval。
- Machine-readable JSON、tests、verifier 與論文/IEEE/簡報同步。

### Out of scope

- 使用 target-time 實測室外溫度、日照或裝置狀態作輸入。
- 在 final 30% test 上選 feature、ridge 或 candidate。
- 宣稱跨建築泛化、因果控制效果或重現 Oh et al. 的 CNN--LSTM。
- 為了得到正結果而刪除任一 target 或改變 1440 分鐘 horizon。

## Research and Claim Impact

| ID | Current status | Intended effect | Evidence needed |
| --- | --- | --- | --- |
| `RQ-ND-01` | new | determine whether seasonal-delta formulation improves next-day prediction | fixed-split comparison JSON |
| `EQ-ND-01` | new | identify which registered candidate is selected for each target | validation selection trace |
| `H-ND-01` | planned | test improvement over seasonal persistence | final-test MAE for both targets |
| `H-ND-ROB-01` | planned | test robustness under daily-block resampling | paired bootstrap intervals |
| `CLM-ND-01` | not evaluated | permit a bounded next-day-improvement statement | complete leakage audit and metrics |

## Risks and Rollback

- Candidate models may still lose to persistence because the public dataset is short and strongly autocorrelated.
- `forecast_temperature_c` may be noisy; it remains an origin-time forecast feature, not target-time truth.
- If the registered hypothesis fails, the negative result remains visible and the thesis states that no next-day advantage was established.

## Completion Criteria

- [x] Protocol is registered before candidate execution.
- [x] Final test remains excluded from model selection.
- [x] Machine-readable output contains every registered candidate and target.
- [x] Negative and uncertainty results are preserved.
- [x] Synchronized artifacts are rebuilt and verified.
