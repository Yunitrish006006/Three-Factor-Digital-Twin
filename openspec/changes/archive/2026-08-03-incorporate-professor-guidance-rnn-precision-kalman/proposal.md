# Change Proposal: incorporate-professor-guidance-rnn-precision-kalman

## Summary

依本週教授建議，將研究方向補強為三條可稽核工作線：

1. 在相同資料、相同可用歷史、相同 target、相同 chronological split 與相同 test rows 下，加入 vanilla RNN 比較。
2. 弱化「一般人體舒適需要極高精度控制」的應用動機，改為篩選真正需要動態精準溫濕度與照度變化的候選場景；任何候選場景都必須保留目前模型只涵蓋 `20–30 °C` 的硬性範圍。
3. 完成 Kalman filter 文獻判讀與後續同資料基線協定，作為未來狀態估測、感測融合或線上參數更新的研究參考，不先宣稱已有數值優勢。

## Why

目前 E9 已比較 persistence、linear regression 與本研究 mapped readout，但尚未包含教授指定的 RNN。既有論述也多以人體舒適作為 decision target；然而一般人體舒適通常使用容許範圍而非極窄單點，不能只因模型 MAE 很低就推論需要同等精度的實體控制。另一方面，生長室、植物工廠或其他封閉培養環境可能具有日夜或生長階段的動態環境配方，但本研究溫度範圍只有 `20–30 °C`，且目前沒有 PPFD、CO2、基質水分或生物反應量測，因此只能作為候選轉向，不能直接宣稱可部署。

## Change Map

### RNN comparator

- **From:** E9 public-task comparison includes persistence, linear regression, project structured readout, and focused published-method transfers.
- **To:** Add a deterministic vanilla Elman RNN baseline on SML2010 S2 temperature/humidity tasks.
- **Fairness:** Every ranked method uses the same normalized records, four-step origin-history window, eligible endpoints, chronological `70/30` split, test rows, targets, and metrics. The primary parity comparison disables any learned synthetic residual checkpoint.
- **Impact:** Method-expanding and claim-neutral until actual results exist.

### Application positioning and temperature boundary

- **From:** Human comfort is the default target motivating precise three-factor estimates.
- **To:** Human comfort remains a demonstration target with tolerances, while dynamic controlled-environment cultivation within `20–30 °C` becomes a candidate high-precision application for further validation.
- **Impact:** Claim-weakening for human-comfort precision need; scope-strengthening through an explicit operational range; no current cultivation efficacy claim.

### Kalman filter reference route

- **From:** Sparse correction is spatial and residual learning is the main learned correction path.
- **To:** Register a future same-data Kalman-family baseline for temporal state estimation, sensor fusion, and online parameter adaptation.
- **Impact:** Research-planning only in this change; evidence status remains `NOT_EVALUATED` until a registered experiment is run.

## Scope

### In scope

- SML2010 S2, targets `dining_temperature`, `room_temperature`, `dining_humidity`, `room_humidity`.
- Horizons `15`, `60`, and `1440` minutes.
- Fixed vanilla RNN architecture and exact comparator data-parity audit.
- Literature-grounded application-fit matrix with a hard `20–30 °C` domain filter.
- Kalman filter literature note and future executable protocol.
- Tests, evidence JSON, result verification, thesis/IEEE/presentation/weekly-report synchronization, and rebuilds.

### Out of scope

- Claiming the RNN will outperform before execution.
- Giving any comparator additional training rows, later timestamps, target-time observations, or a different test set.
- Claiming general applicability outside `20–30 °C`.
- Claiming the present lux-based model already satisfies plant PPFD, CO2, substrate moisture, disease, yield, or biological-response requirements.
- Implementing or claiming a successful Kalman filter result without a separate registered execution.
- Claiming that smaller numerical error automatically yields perceptible human-comfort improvement.

## Research and Claim Impact

| ID | Type | Intended effect | Evidence |
| --- | --- | --- | --- |
| `RQ-RNN-01` | exploratory comparison | add professor-requested RNN baseline | same-row SML2010 JSON |
| `EQ-APP-01` | exploratory positioning | identify a dynamic precision application compatible with `20–30 °C` | primary-literature matrix |
| `EQ-KF-01` | exploratory method review | define Kalman-family future baseline | literature and protocol note |
| `CLM-RNN-01` | bounded descriptive claim | report RNN wins and losses without superiority presumption | `rnn_sml2010_comparison.json` |
| `CLM-APP-01` | bounded direction claim | controlled plant growth is a candidate, not a validated deployment | scope audit |
| `CLM-KF-01` | future-work claim | Kalman filtering is methodologically relevant but not evaluated here | `NOT_EVALUATED` status |

## Affected Capabilities and Artifacts

- Specs: `research-governance`, `spatial-field-estimation`, `evaluation-and-evidence`, `hybrid-residual-learning`, `action-recommendation`, `reproducibility-and-data`.
- Code/tests: new RNN evaluator and runner, public-comparison tests, result verifier, experiment orchestrator where applicable.
- Research notes: application-scope and Kalman-filter direction documents.
- Synchronized artifacts: Chinese thesis/build source/output, IEEE source/output, presentation sources/outlines/notes/outputs, professor weekly report.
- References: add only primary literature actually cited in synchronized text.

## Risks and Rollback

- Vanilla RNN may underperform persistence or linear regression; losses SHALL remain visible.
- One public dataset does not establish cross-domain performance.
- Fixed `20–30 °C` coverage may exclude otherwise attractive biological or laboratory processes.
- Plant-growth positioning introduces missing constructs such as PPFD, CO2, substrate moisture, and biological endpoints.
- Kalman performance depends on state/process model quality and noise assumptions; literature includes adverse filtering results.
- If exact data parity cannot be proven, RNN ranking SHALL remain `NOT_EVALUATED` rather than combining mismatched metrics.

## Completion Criteria

- [x] RNN protocol is registered before the first result run.
- [x] Every ranked comparator uses identical eligible rows, history availability, split, targets, and metrics.
- [x] `20–30 °C` is explicit in specs and all application claims.
- [x] Application and Kalman notes preserve missing variables and adverse literature.
- [x] Actual RNN results and claim decisions are recorded without post-outcome threshold changes.
- [x] Applicable thesis, IEEE, presentation, weekly-report, and generated outputs are synchronized and verified.
