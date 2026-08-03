# Research Framing

## Problem and Gap

現有內容具備完整方法圖與實驗圖，但缺少論文層級的 argument map。讀者可看見「系統怎麼運作」，卻不一定立即看見「每個研究問題由哪個方法回答、由哪一層證據支持、最後允許下什麼結論」。

## Research Questions

| ID | Question | Type | Linked capability |
| --- | --- | --- | --- |
| `RQ1` | 八角點感測能否支援三因子空間估計？ | confirmatory | spatial-field-estimation |
| `RQ2` | 能否從環境觀測學習非連網裝置影響？ | confirmatory | appliance-impact-learning |
| `RQ3` | 學習後模型能否支援可解釋候選動作排序？ | confirmatory + future causal validation | action-recommendation |
| `RQ4` | 能否以標準化本地工具介面暴露同一模型？ | secondary systems question | service-interfaces |

## Hypotheses

| ID | Hypothesis | Falsifier | Required evidence |
| --- | --- | --- | --- |
| `H1` | 受控情境下主模型優於 IDW | E1/E2 指標不支持 | validation summary |
| `H2` | 稀疏校正改善臥室未參與校正點 | E7 未改善 | bedroom summary |
| `H3` | Hybrid residual 在受控 scenario family 改善殘差 | held-out/LOO 未改善 | E6 summary |
| `H4` | structured prior 對事件或邊界變化任務較有幫助 | E9 任務拆解不支持 | public comparison |
| `H5` | 排名第一動作具有實際改善效果 | 尚未執行 E8 | future intervention |

## Construct Operationalization

| Construct | Operational definition | Unit / scale | Source |
| --- | --- | --- | --- |
| 研究問題對應 | RQ 至方法、證據與 claim boundary 的有向連結 | mapping edge | thesis/OpenSpec |
| 證據層級 | controlled、real snapshot、public aligned、future intervention | category | E1--E9 registry |
| 可讀性 | 論文寬度與投影片尺寸下標籤不重疊、不裁切 | visual pass/fail | rendered outputs |

## Intended Claims

| ID | Exact bounded claim | Evidence class | Forbidden overclaim |
| --- | --- | --- | --- |
| `CLM-ARCH-01` | 圖表忠實呈現目前論文的問題、方法、證據與限制關係 | artifact consistency | 圖本身不構成新的實驗證據 |

## Grounding

- Related thesis sections: 1.3、1.5、3.1、5.1--5.9、6.1--6.3
- Related implementation: architecture diagram builder、thesis/PPT builders
- Existing evidence: `outputs/data/thesis_result_verification_report.json`
- Literature or dataset source: 不新增外部資料

## Competing Explanations and Validity Threats

- Internal validity: 圖可能因過度簡化而隱藏方法分支。
- Construct validity: 「整體邏輯」若只畫系統模組，仍不能代表論證鏈。
- External validity: 圖只描述本論文，不推廣為一般 digital twin 方法論。
- Statistical conclusion validity: 本變更不新增統計推論。

## Ethics, Privacy, Safety, and Licensing

- Human or occupancy data: 不新增。
- Privacy handling: 不顯示個人或原始感測紀錄。
- Intervention safety: E8 維持 future protocol。
- Dataset and asset licenses: 使用 repository 內自製圖形與既有文字。
