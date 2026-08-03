# Research Record

## Research Question

### RQ-ND-01

在 SML2010 S2 的兩點溫度次日預測中，以 seasonal persistence 為基準並學習
跨日 delta，能否比既有 persistence、raw physics、project readout 與
Oh2024-inspired transfer 取得更低的固定測試集 MAE？

### EQ-ND-01

偏差校正、damped daily trend、persistence--physics blend 與
origin-known seasonal residual ridge 中，哪一種會在 validation-only
selection 下被選為各 target 的次日模型？

## Hypotheses

### H-ND-01

對 dining 與 room 兩個 target，validation-selected next-day model 在固定
末段 30% test 的 MAE 都低於 seasonal persistence，且兩點平均相對 MAE
改善至少 5%。

### H-ND-ROB-01

以 test date 為 block 的 paired bootstrap 中，兩個 target 的
`persistence MAE - selected model MAE` 95% percentile interval 下界都大於
0。

## Claim

### CLM-ND-01

只有在 `H-ND-01` 支持且 selection/leakage audit 完整時，才可主張
「在此 SML2010 fixed split 上，seasonal-delta formulation 增加次日預測
優勢」。若 `H-ND-ROB-01` 不支持，必須補充改善對日期區塊不具穩健性。
所有結論都只限此 two-point public task，不外推至原論文商辦資料或本研究
完整 3-D room field。

## Post-Primary Exploratory Question

### EQ-ND-ADAPT-01

`H-ND-01` 的 primary 執行完成後，validation-selected fixed model 在 test
退化。為診斷部署上是否能吸收季節漂移，另行註冊一個探索性 online
follow-up：在每個 forecast origin，只使用當下及過去相同時刻已完成的
daily deltas，計算 rolling mean、median 或 EWMA correction。

此分析是在 primary test 結果已知後提出，不能升格為新的 confirmatory
hypothesis。若兩點都勝過 persistence 且平均相對改善至少 2%，只記為
`exploratory_signal`；否則記為 `not_supported`。
