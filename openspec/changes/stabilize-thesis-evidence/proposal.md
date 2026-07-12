## Why

目前專案已完成可解釋三因子主模型、家具感知的 adaptive sensor layout、三線性校正、hybrid residual、公開資料 benchmark 與論文輸出，但仍有三個會直接影響口試可信度的問題：

1. 目標點感測器目前可被加入一般 sensor layout，尚未形成嚴格的 `S_input` / `S_validation` 分離，可能造成 target-point evaluation leakage。
2. 8-corner/trilinear pipeline、家具補償點與未來的 2-D/3-D free-space estimators 尚未以同一模組介面和相同資料切分比較。
3. 論文中的 synthetic full-field、real target-point、public benchmark 與 action ranking 需要更明確的 claim boundary、失敗案例與可重現輸出。

本 change 的單一目標是：**把現有研究原型整理成可防守的論文證據管線，使每個主張都有正確的感測器角色、對照方法、資料切分與輸出產物。**

## What Changes

- 將感測器與節點角色分成：
  - `S_input`：模型校正與推論可使用的真實觀測
  - `S_validation`：模型不得使用、只供最後評估的真實觀測
  - `V_target`：需要估計的研究目標位置
  - `V_pseudo`：由模型產生、不得視為 ground truth 的支撐值
- 將家具感知空間明確定義為 `Ω_free = Ω_room \ Ω_occ`，並記錄每個估計值的 provenance。
- 建立統一 estimator comparison contract，至少涵蓋：
  - BasePhysics + trilinear correction
  - sensor-level IDW baseline
  - 2-D triangulation estimator
  - 3-D tetrahedral estimator
  - Cell-IDW fusion estimator
  - optional residual corrector
- 加入 target-point holdout evaluation 與 blocked/leave-one-day-out 時序驗證。
- 在相同 split 下輸出 MAE、RMSE、MaxErr、失敗案例與運算時間。
- 建立 claim-to-evidence matrix，並同步中文論文、IEEE 稿、簡報與圖表。
- 保留 control recommendation 為 counterfactual ranking；真實 before/after intervention 另列為後續驗證里程碑。

## Capabilities

### New Capabilities

- `holdout-target-validation`: 將真實目標點從模型輸入排除，再以實測值驗證估計誤差。
- `free-space-estimator-comparison`: 在家具遮蔽後的自由空間中，以統一介面比較基線與模組化估計器。
- `claim-evidence-traceability`: 將研究問題、資料、方法、指標、圖表與可主張範圍建立可追溯關係。

### Modified Capabilities

- `research-contract`: 將主要主張由「8 點完整真實場重建」收斂為「家具感知自由空間中的可驗證目標點估計」。
- `spatial-estimation`: 將 adaptive sensor layout 與 estimator role 分離，避免 validation target 被用於 calibration。
- `evidence-and-artifacts`: 增加 leakage-resistant splits、failure cases、runtime 與跨產物同步驗證。

## Impact

- `digital_twin/core/entities.py`：新增 sensor/node role 或等價資料結構。
- `digital_twin/core/scenarios.py`：建立 input/validation/target split，不再把所有 target sensors 當作 calibration input。
- `digital_twin/physics/`：加入 estimator interface、free-space geometry utilities 與 modular estimators。
- `digital_twin/neural/`：讓 residual corrector 接受統一 estimator output，並避免 split leakage。
- `scripts/`：新增 holdout、blocked CV、estimator comparison、failure-case 與 runtime reporting scripts。
- `tests/`：新增 sensor-role separation、occlusion filtering、estimator consistency 與 leakage tests。
- `outputs/data/`、`outputs/figures/`：新增可追溯比較與 target-point evidence artifacts。
- `docs/thesis/`、`docs/papers/`、presentation sources：同步研究定位、方法完成狀態與結果。
