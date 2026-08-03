# Research Framing

## Problem and Gap

Oh et al. (2024) report that simulated return-air temperature and operational measurements can be combined through a learned correction to improve next-day prediction, including months outside the training temperature distribution. The paper's building data are confidential, and its CNN--LSTM implementation is not available in this project. The open question is therefore not whether the original numerical results can be reproduced, but whether the additive simulation-plus-residual principle can serve as a fair, executable baseline under this project's public task alignment.

## Research Questions

| ID | Question | Type | Linked capability |
| --- | --- | --- | --- |
| `RQ-PHB-01` | 在相同公開資料、target、horizon 與 chronological split 下，Oh et al. 啟發的 additive residual readout 是否改善未修正 physics prior？ | confirmatory | `evaluation-and-evidence` |
| `EQ-PHB-01` | 該 transfer baseline 相對 persistence、直接線性回歸與本研究 mapped readout 的優劣分布為何？ | exploratory | `evaluation-and-evidence` |

## Hypotheses

| ID | Hypothesis | Falsifier | Required evidence |
| --- | --- | --- | --- |
| `H-PHB-01` | Additive residual readout 在 6 個 SML2010 temperature target--horizon cases 中，至少 4 個具有低於 raw physics prior 的 test MAE。 | 改善少於 4 個，或任何 comparator 未使用相同 test rows。 | `oh2024_inspired_sml2010_comparison.json` |

## Construct Operationalization

| Construct | Operational definition | Unit / scale | Source |
| --- | --- | --- | --- |
| physics prior | `MappedHybridPublicPredictor` 產生、未加 learned public residual 的 S2 target-time temperature estimate | °C | project model |
| additive residual transfer | `y_hat = y_hat_phys + r_hat`, where `r_hat` is ridge-linear prediction of `y-y_hat_phys` | °C | new evaluator |
| test improvement | `MAE_phys - MAE_transfer` on identical chronological test rows | °C | output JSON |
| published-method fidelity | conceptual transfer using simulated baseline, previous measurements, operating/boundary features, and learned discrepancy; not architectural reproduction | categorical | paper audit |

## Intended Claims

| ID | Exact bounded claim | Evidence class | Forbidden overclaim |
| --- | --- | --- | --- |
| `CLM-PHB-01` | On SML2010 two-point temperature response tasks, an Oh et al. (2024)-inspired linear additive-residual baseline was evaluated on the same chronological split as the project comparators; its wins and losses are reported as a method-transfer study. | public task | reproduced the published CNN--LSTM; direct superiority over the published model; full 3-D validation |

## Grounding

- Related thesis sections: related work, hybrid residual method, public task-aligned benchmarking
- Related implementation: `digital_twin/core/public_dataset_model_comparison.py`
- Existing evidence: SML2010 15/60-minute E9 comparison
- Literature or dataset source: Oh et al. (2024), Energy and Buildings 324, 114898; SML2010 normalized public data

## Competing Explanations and Validity Threats

- Internal validity: a linear residual head and existing physics mapping differ from the original CNN--LSTM and TRNSYS/RC setup.
- Construct validity: SML2010 two-point room temperatures are not return-air temperature for a multi-zone commercial AHU.
- External validity: results cannot be generalized to the paper's Seoul office, arbitrary buildings, or dense 3-D fields.
- Statistical conclusion validity: six target--horizon cases are descriptive; no independent-building inferential claim is planned.

## Ethics, Privacy, Safety, and Licensing

- Human or occupancy data: no personally identifying occupancy records are introduced.
- Privacy handling: only normalized public SML2010 data are used.
- Intervention safety: not applicable.
- Dataset and asset licenses: preserve existing SML2010 provenance; do not redistribute or infer the paper's confidential BEMS data.
