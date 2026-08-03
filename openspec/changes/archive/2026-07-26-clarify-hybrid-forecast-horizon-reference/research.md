# Research Framing

## Problem and Gap

本變更處理的是文獻與符號可解釋性缺口，而非新增方法。引用研究以物理模擬的 forecast-day output 作為基線，再學習 historical simulation--measurement discrepancy；本專案則主要在指定 elapsed time 對當前 scenario state 做空間場估測。若不區分 forecast target 與 information availability，公式可能被誤讀為使用未來真值。

## Research Questions

| ID | Question | Type | Linked capability |
| --- | --- | --- | --- |
| `RQ-HRL-TIME-01` | Additive hybrid forecast 中，physics 與 residual 項應如何保持 target-time 對齊並避免 leakage？ | confirmatory notation audit | `hybrid-residual-learning` |

## Hypotheses

本變更不執行新實驗，因此不建立新的效能假設。

## Construct Operationalization

| Construct | Operational definition | Unit / scale | Source |
| --- | --- | --- | --- |
| forecast horizon | 從 forecast origin `t` 到 target time `t+h` 的 lead | hours or model time unit | method notation |
| information set | forecast origin `t` 時合法可得的 state、boundary/control forecast 與歷史資料 | set membership | method/protocol |
| target-time alignment | additive terms 均估計同一空間點、變數與 `t+h` | Boolean audit | synchronized prose/formula |

## Intended Claims

| ID | Exact bounded claim | Evidence class | Forbidden overclaim |
| --- | --- | --- | --- |
| `CLM-HRL-TIME-01` | 在 `h`-step additive hybrid forecast 中，physics baseline 與 residual forecast 必須對齊同一 target time `t+h`; `h` 是 lead time，非額外物理參數。 | literature-grounded notation | 不表示本研究已完成 next-day forecasting experiment |

## Grounding

- Related thesis sections: 2.7、3.8。
- Related implementation: `digital_twin/neural/hybrid_residual.py`。
- Existing evidence: current-state controlled scenarios and LOO residual learning.
- Literature source: Ju-Hong Oh, Stefano Sfarra, and Eui-Jong Kim, Energy and Buildings 324 (2024) 114898, DOI `10.1016/j.enbuild.2024.114898`.

## Competing Explanations and Validity Threats

- Internal validity: 符號正確不代表 forecasting implementation 已通過 leakage audit。
- Construct validity: `t` 在本專案亦可表示 elapsed scenario time；必須避免和 forecast origin 混用。
- External validity: 引用論文處理 next-day indoor temperature，不直接驗證本研究三因子 3-D spatial field。
- Statistical conclusion validity: 無新增統計結論。

## Ethics, Privacy, Safety, and Licensing

- Human or occupancy data: 不新增。
- Privacy handling: 不新增個資。
- Intervention safety: 不新增介入。
- Dataset and asset licenses: 僅新增書目與短篇方法摘要，不複製論文全文或圖表。
