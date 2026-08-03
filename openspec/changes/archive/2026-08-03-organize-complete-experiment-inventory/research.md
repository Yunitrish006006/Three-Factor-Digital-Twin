# Research Framing

## Questions and Claims

| ID | Type | Question or claim | Decision basis |
| --- | --- | --- | --- |
| `RQ-INV-01` | audit question | E1–E9 是否都能追溯至目前機器可讀 evidence 與明確支援層級？ | inventory completeness and verifier |
| `EQ-E5-RANGE-01` | descriptive audit | E5 的 48 個案例中，多少 target-zone 室內溫度位於目前 20–30 °C 範圍？ | inclusive range check on current JSON |
| `CLM-INV-01` | bounded claim | 完整實驗總覽忠實保留成功、負向、未評估與範圍外結果。 | cross-file reconciliation |

## Evidence Classes

- Controlled simulation: E1–E6.
- Real-bedroom snapshots: E7.
- Real intervention: E8, currently no completed trials.
- Public task-aligned data: E9 and its subexperiments.
- Literature/future method direction: application-scope and Kalman notes; not counted as completed experiments.

## Competing Explanations and Threats

- Controlled truth and implemented estimator share structural assumptions, so very low synthetic MAE may overestimate generalization.
- E7 has one room, one held-out pillow point, seven dates, and overlapping sensitivity folds.
- Public datasets lack matched room geometry and eight-corner topology.
- E5 range classification is a descriptive audit of existing outputs, not a new independent experiment.
- Old prose can remain stale even when the verifier passes if that number is not registered; the inventory must therefore include explicit source reconciliation.

## Claim Boundaries

- No evidence class may be merged into a single universal performance claim.
- E8 remains `NOT_EVALUATED`.
- RNN and next-day negative results remain visible.
- E5 indoor target-zone values outside `20–30 °C` are `out_of_domain` for current applicability claims.

