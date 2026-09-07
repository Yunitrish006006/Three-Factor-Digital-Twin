# Change Proposal: execute-kalman-filter-and-professor-demo

## Summary

將教授先前指定的 Kalman filter 方向由 `NOT_EVALUATED` 推進為一個有明確資料公平性與證據邊界的受控 current-time filtering 實驗，並把既有 RNN 結果、新增 Kalman 結果、20–30 °C 應用邊界與主要系統操作整理成教授可直接觀看的兩週 demo。

## Why

RNN 已在 SML2010 S2 相同四筆歷史、split、targets 與 test rows 下完成比較，但 Kalman 目前只有文獻與未來 protocol。直接以同一筆公開量測同時當 noisy input 與 ground truth 會使未濾波方法產生零誤差，也無法回答去噪問題；本 change 因此採固定種子的受控雜訊注入，保留原始 SML2010 溫濕度序列作為 task reference，並讓所有 comparator 取得完全相同的 corrupted observations。

教授版成果也需要可直接展示，而不是只提供研究數字或開發指令。因此本 change 另外產生一個無外部依賴、可離線開啟的 evidence demo，並保留既有 live Web demo 作為實際房間查詢、3D 場與推薦流程入口。

## Scope

### In scope

- SML2010 dining/room temperature and humidity current-time filtering.
- Chronological 70/30 split and fixed-seed controlled Gaussian measurement noise.
- Three pre-registered noise profiles and identical corrupted rows for raw, causal moving average, and scalar linear Kalman filter.
- State transition, observation model, process/measurement covariance, gap reset, innovations, MAE/RMSE/correlation, and adverse cases.
- A professor-facing two-week report and offline demo built from committed evidence JSON.
- Synchronization of thesis, IEEE paper, presentation sources/outlines, and generated outputs.

### Out of scope

- Real sensor denoising validation, dense 3-D field validation, forecasting, EKF/UKF, controller efficacy, or plant-growth efficacy.
- Tuning covariance or moving-average window after observing test outcomes.
- Hiding cases where raw or moving average beats Kalman.
- Extending the indoor operating claim beyond 20–30 °C.
- Treating demo UI behavior as quantitative research evidence.

## Claim Impact

| ID | Effect | Intended bounded claim |
| --- | --- | --- |
| `RQ-KF-01` | exploratory | Under fixed controlled noise, how often does a registered scalar Kalman filter reduce current-time MAE relative to raw and causal moving average on identical SML2010 rows? |
| `CLM-KF-02` | claim-strengthening if complete | The project has executed a same-data controlled filtering benchmark; results are limited to injected-noise SML2010 current-time filtering. |
| `CLM-DEMO-01` | claim-neutral | The professor demo renders existing machine-readable evidence and live service behavior without becoming a new evidence class. |

## Affected Artifacts

- OpenSpec: evaluation/evidence, hybrid residual learning, and artifact synchronization deltas.
- Code/tests: Kalman evaluator, runner, evidence/demo builder, and unit tests.
- Evidence: `outputs/data/public_benchmarks/kalman_sml2010_filtering_comparison.json`.
- Demo: `outputs/demos/professor_two_week_demo_2026-08-04_2026-08-17_zh.html` and a professor demo guide.
- Synchronized research artifacts: Chinese thesis/build/output, IEEE paper/output, presentation builders/outlines/outputs.
- Professor report: a two-week report excluding personal-development and submission content.

## Risks

- Controlled injected noise is not proof that the same gain occurs with DHT11, DHT22, SHT31, or another physical sensor.
- The original recorded sequence is a task reference, not latent physical ground truth.
- A random-walk scalar model may lag real environmental transitions.
- Known injection variance gives the Kalman filter a model prior; conclusions must remain within this protocol.
- The offline demo can become stale if it is not rebuilt from canonical JSON.

## Completion Criteria

- [ ] Protocol and covariance rules are registered before the first full result run.
- [ ] All three methods share the same corrupted rows, split, test indices, and metrics.
- [ ] Output preserves innovations, gap resets, method losses, and non-Kalman winners.
- [ ] Professor demo is generated from evidence and visually/runtime checked.
- [ ] Professor two-week report includes previous/improved comparison and research limitations.
- [ ] Applicable synchronized sources and generated outputs are rebuilt and verified.
