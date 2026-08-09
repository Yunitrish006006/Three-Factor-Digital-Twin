# Research Framing

## Problem and Gap

目前模型可使用多個感測點校正，但若目標點量測同時進入 fitting，target-point 誤差就不是獨立驗證。本變更先把感測器角色、自由空間、比較介面與證據產物分開，再逐步完成真實多日驗證。

## Research Questions

| ID | Question | Type | Linked capability |
| --- | --- | --- | --- |
| `RQ-STAB-01` | 明確分離 input 與 validation observation，能否建立無 target leakage 的估測流程？ | confirmatory | `spatial-estimation` |
| `RQ-STAB-02` | BasePhysics、IDW 與 free-space estimators 在相同 holdout split 下的誤差與失敗模式為何？ | exploratory | `spatial-estimation` |
| `RQ-STAB-03` | 哪些實體節點與資料紀錄足以支援可防守的真實 target-point validation？ | exploratory | `sensing-node` |

## Hypotheses

| ID | Hypothesis | Falsifier | Required evidence |
| --- | --- | --- | --- |
| `H-STAB-01` | role-aware pipeline 在 fitting 階段完全不讀取 validation truth。 | 任一 calibration、impact learning、normalization 或 model selection 路徑讀取 validation observation。 | unit tests、holdout summary、data-flow audit |
| `H-STAB-02` | 所有 comparator 可在相同 input/validation split 與 metric contract 下輸出可追溯結果。 | comparator 使用不同 target、split 或 truth lookup。 | comparison JSON 與 parity audit |

## Construct Operationalization

| Construct | Operational definition | Unit / scale | Source |
| --- | --- | --- | --- |
| leakage absence | fitting inputs 與 validation names/value 的交集為空 | boolean + audited names | holdout result JSON |
| target error | prediction 與 synthetic 或 measured holdout truth 的差 | MAE、RMSE、MaxErr、bias | evaluator output |
| method maturity | implemented / validated / proposed / future | categorical | method-status inventory |
| provenance | method、support nodes、roles、split、data class | structured metadata | result JSON |

## Intended Claims

| ID | Exact bounded claim | Evidence class | Forbidden overclaim |
| --- | --- | --- | --- |
| `CLM-STAB-01` | controlled scenarios 中的 target truth 未參與 calibration，且流程可輸出 holdout error。 | controlled simulation | 不稱為真實房間 dense-field validation |
| `CLM-STAB-02` | 真實 target-point 結果只能在 validation-grade measurement 實際收集後成立。 | real holdout, pending | 不以 DHT11 或 pseudo value 宣稱高精度 ground truth |
| `CLM-STAB-03` | action ranking 在 E8 前仍是 model-based counterfactual decision support。 | model output | 不宣稱真實因果控制效益 |

## Grounding

- Related thesis sections: problem statement、method status、target-point validation、limitations.
- Related implementation: `digital_twin/core/entities.py`、`digital_twin/core/validation.py`、`digital_twin/physics/learning.py`.
- Existing evidence: controlled simulation, E7 real-bedroom snapshots, public task-aligned benchmarks.
- Hardware planning: `docs/hardware/`；價格與型號為部署規劃，不是效能證據。

## Competing Explanations and Validity Threats

- Internal validity: validation value 可能透過 normalization、device calibration 或人工設定間接洩漏。
- Construct validity: synthetic truth 與真實 sensor measurement 的不確定度不同。
- External validity: 單房間與 20–30 °C 範圍不能外推到其他空間或極端環境。
- Statistical conclusion validity: repeated timestamps 與同日樣本不獨立，需 blocked/leave-one-day-out 分析。

## Ethics, Privacy, Safety, and Licensing

- Human or occupancy data: 不收集人臉、語音或不必要的個人活動內容。
- Privacy handling: Google Home 紀錄只保留研究所需裝置、動作與時間欄位。
- Intervention safety: E8 不繞過設備安全限制，異常時停止。
- Dataset and asset licenses: 公開資料 provenance 與 license 分開記錄；外部論文不是本研究 evidence。
