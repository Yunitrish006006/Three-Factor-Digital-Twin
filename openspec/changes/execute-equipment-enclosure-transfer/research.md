# Research Framing

## Problem and Gap

現有研究能估測單一房間的環境場，但機箱具有更小尺度、集中熱源、強迫對流及快速負載變化。房間模型與證據不能直接證明機箱適用性。第一階段先縮小為公開 BMC air-state 時序任務，檢查可解釋 thermal terms 是否提供比簡單 baseline 更穩定的預測價值。

## Research Questions

| ID | Question | Type | Linked capability |
| --- | --- | --- | --- |
| `RQ-ENC-01` | 在相同 BMC trace 與 chronological split 下，thermal-balance readout 是否比 persistence 降低下一時間點 outlet-temperature MAE？ | confirmatory | `ENC-002` |
| `RQ-ENC-02` | 改善或失敗是否與 fan mode、工作負載、功率變化或 cadence 有關？ | exploratory | `ENC-003` |
| `RQ-ENC-03` | 公開資料提供哪些 3-D 幾何與 airflow 欄位，可支援後續 enclosure spatial transfer？ | exploratory | `ENC-004` |

## Hypotheses

| ID | Hypothesis | Falsifier | Required evidence |
| --- | --- | --- | --- |
| `H-ENC-01` | thermal-balance readout 在至少 3 個合格 trace 中，多數 trace 的 test MAE 低於 persistence。 | 合格 trace 少於 3，或改善 trace 不超過半數。 | `enclosure_bmc_baseline.json` case-level test metrics |

## Construct Operationalization

| Construct | Operational definition | Unit / scale | Source |
| --- | --- | --- | --- |
| air-state prediction error | predicted 與下一有效時間點 `Outlet_Temp` 的 MAE/RMSE | °C | BMC CSV |
| thermal driving force | current `Inlet_Temp - Outlet_Temp` | °C | BMC CSV |
| heat input | `PSU1_Total_Power + PSU2_Total_Power` | W | BMC CSV |
| forced convection proxy | available fan-speed fields 的平均值 | RPM | BMC CSV |
| operating-domain eligibility | current/next inlet/outlet 均在 20–30 °C | Boolean | protocol filter |

## Intended Claims

| ID | Exact bounded claim | Evidence class | Forbidden overclaim |
| --- | --- | --- | --- |
| `CLM-ENC-01` | 在所執行的公開 BMC traces 與 20–30 °C air-state 子集合中，thermal-balance readout 相對 persistence 的 case-level 結果。 | public task-aligned | 3-D 機箱驗證、真實部署、CPU hotspot、普遍控制優勢 |

## Grounding

- Related thesis sections: future-work enclosure paragraph only；結果尚未同步。
- Related implementation: room reduced-order physics and public-dataset chronological comparisons。
- Existing evidence: none for enclosure applicability。
- Primary literature: Wang et al., *Energy and Buildings* 258 (2022), DOI `10.1016/j.enbuild.2021.111790`; Tong et al., *Applied Thermal Engineering* 230 (2023), DOI `10.1016/j.applthermaleng.2023.120737`。
- Primary datasets: arealuser/bmcdata (MIT); AAU server-room dataset v4, DOI `10.5281/zenodo.19398358`; HazardNet dataset, DOI `10.5281/zenodo.10050368`。

## Competing Explanations and Validity Threats

- Internal validity: fan controller and workload can change together; adjacent rows may have irregular cadence。
- Construct validity: BMC fan RPM is a proxy, not measured volumetric airflow；outlet air is not component temperature。
- External validity: one server platform or server room does not establish arbitrary enclosure transfer。
- Statistical conclusion validity: trace-level counts are descriptive and traces may not be independent。

## Ethics, Privacy, Safety, and Licensing

- Human or occupancy data: none required。
- Privacy handling: preserve only machine telemetry and dataset provenance；do not infer users or workloads beyond published labels。
- Intervention safety: no physical fan or thermal control is executed in `E11A`。
- Dataset and asset licenses: record repository/dataset license and checksum before execution；do not redistribute source files unless permitted。
