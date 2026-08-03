# Research Framing

## Problem and Gap

E7 的 date-block bootstrap 保留了同日四個時段的相依性，但不能直接列出哪一天對平均改善影響最大。逐日剔除可提供一個容易解釋的 influence diagnostic：若移除任一日期後改善仍為正，則現有結果不依賴保留某一個特定日期。

## Research Questions

| ID | Question | Type | Capability |
| --- | --- | --- | --- |
| `RQ-E7-LODO-01` | 移除 7 個觀察日期中的任一天後，三因子 pillow-point MAE reduction 是否仍為正？ | confirmatory diagnostic | `evaluation-and-evidence` |

## Hypotheses

| ID | Directional hypothesis | Primary metric | Decision rule |
| --- | --- | --- | --- |
| `H-E7-LODO-01` | 所有 date-deletion folds 中，calibration 均降低三因子 MAE | minimum fold-level raw MAE minus calibrated MAE | temperature、humidity、illuminance 的 minimum reduction 全部 > 0 |

## Construct Operationalization

| Construct | Definition | Unit | Source |
| --- | --- | --- | --- |
| date-deletion fold | 移除一個日期的全部四筆 snapshots，保留其餘日期 | calendar date | E7 snapshot rows |
| fold-level MAE reduction | 剩餘 snapshots 的 raw MAE 減 calibrated MAE | °C, %RH, lux | paired errors |
| minimum reduction | 7 個 folds 中最小的 fold-level reduction | metric unit | deterministic summary |

## Intended Claims

| ID | Exact bounded claim | Evidence class | Forbidden overclaim |
| --- | --- | --- | --- |
| `CLM-E7-LODO-01` | 在 bedroom_01 的既有七日資料中，移除任一日期後，三因子 pillow-point calibration MAE reduction 仍保持正值。 | real-bedroom snapshot sensitivity | 不宣稱跨房間、長期母體、dense field 或因果控制效果 |

## Competing Explanations and Validity Threats

- 改善可能來自固定 pillow 幾何或固定感測器拓樸，而非一般空間轉移能力。
- 七天涵蓋的天氣、設備與行為範圍有限。
- Leave-one-date-out folds 高度重疊，不是七個獨立重複實驗。
- 正的 minimum reduction 只能排除單一日期完全主導平均改善，不能排除多日共同偏差。

## Ethics, Privacy, Safety, and Licensing

- 只分析既有去識別房間量測，不新增人員或占用資料。
- 不執行實體控制或介入。
