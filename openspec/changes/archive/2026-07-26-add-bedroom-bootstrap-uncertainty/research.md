# Research Framing

## Problem and Gap

E7 目前顯示 pillow hold-out MAE 在 sparse calibration 後下降，但平均值不足以表達 7 天資料中的日間變異。每日四個時段共享天氣、房間與使用脈絡，因此分析應保留 date-level clustering。

## Research Questions

| ID | Question | Type | Linked capability |
| --- | --- | --- | --- |
| `RQ-E7-UNC-01` | 在以日期為 block 的 paired bootstrap 中，三因子 MAE reduction 是否仍保持正值？ | confirmatory | `evaluation-and-evidence` |

## Hypotheses

| ID | Directional hypothesis | Primary metric | Decision rule |
| --- | --- | --- | --- |
| `H-E7-UNC-01` | calibration 對 temperature、humidity、illuminance 的 mean absolute-error reduction 均為正 | 95% percentile interval of paired MAE reduction | 三個 interval 下界皆大於 0 |

## Construct Operationalization

| Construct | Operational definition | Unit / scale | Source |
| --- | --- | --- | --- |
| paired error reduction | 每筆快照 `raw_abs_error - calibrated_abs_error` 的平均 | °C, %RH, lux | E7 snapshot rows |
| date block | 同一日期的四個 time-segment snapshots | calendar day | snapshot `date` |
| improvement fraction | calibrated absolute error 小於 raw absolute error 的快照比例 | 0--1 | E7 snapshot rows |
| uncertainty interval | 20,000 date-block bootstrap replicates 的 2.5/97.5 percentiles | metric unit | deterministic analysis |

## Intended Claims

| ID | Exact bounded claim | Evidence class | Forbidden overclaim |
| --- | --- | --- | --- |
| `CLM-E7-UNC-01` | 在 bedroom_01 的 7 天、28 筆 pillow hold-out 快照中，三因子校正 MAE reduction 的 date-block bootstrap 95% interval 均保持正值。 | real-bedroom snapshot | 不宣稱跨房間泛化、dense 3-D truth、因果控制效益或正式母體推論 |

## Competing Explanations and Validity Threats

- Calibration may benefit from the fixed pillow geometry rather than general spatial transfer.
- Seven date blocks provide limited coverage of weather and behavior.
- Snapshot labels may contain measurement or manual-recording error.
- Bootstrap quantifies variation in the observed seven-day sampling structure; it does not create new independent data.
- Improvement fraction is descriptive and is not an intervention success rate.

## Ethics, Privacy, Safety, and Licensing

- No new participant, identity, or occupancy data are introduced.
- No physical intervention is performed.
- Existing user-supplied room data remain local to the repository.
