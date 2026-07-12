## 0. 已完成基礎盤點

- [x] 0.1 建立三因子 variable-specific nominal models。
- [x] 0.2 建立 active-device power calibration 與 trilinear residual correction。
- [x] 0.3 建立 furniture-aware adaptive sensor layout，可排除被家具佔據的角落並加入補償點。
- [x] 0.4 建立 hybrid residual neural network 實驗模組。
- [x] 0.5 建立 synthetic validation suite、48 組 window matrix 與 CU-BEMS/SML2010 task-aligned benchmark。
- [x] 0.6 建立中文論文、IEEE 稿、圖表與簡報產生流程。

## 1. 研究主張與資料角色收斂

- [ ] 1.1 在共用資料結構中加入 sensor/node role：`input`、`validation`、`target`、`pseudo`。
- [ ] 1.2 保持現有 `Sensor(name, position)` 相容性，未指定 role 時預設為 `input`。
- [ ] 1.3 將 scenario builder 改為分別輸出 `input_sensors`、`validation_sensors` 與 `target_points`。
- [ ] 1.4 新增測試：validation sensor 不得出現在 power calibration、impact learning 或 trilinear fitting 的輸入。
- [ ] 1.5 新增測試：validation observation 不得進入 residual dataset、normalization statistics 或 model selection。
- [ ] 1.6 在 `docs/thesis/problem_statement_zh.md` 與主論文草稿中，將核心主張改為「家具感知自由空間中的可驗證目標點估計」。
- [ ] 1.7 建立 method-status inventory，逐項標示 implemented / validated / proposed extension / future work。

## 2. 自由空間與幾何支撐

- [ ] 2.1 新增 `Ω_room`、`Ω_occ`、`Ω_free` 的程式與文件定義。
- [ ] 2.2 新增查詢：點是否位於自由空間、線段是否穿越家具、cell 是否退化或與家具非法相交。
- [ ] 2.3 定義 `V_geom`、`V_target`、`V_pseudo` 與支撐節點 provenance。
- [ ] 2.4 將 adaptive compensation sensor 的產生原因、來源角落與 rejection reason 寫入 metadata。
- [ ] 2.5 新增測試：補償點不重複、不超出房間、不位於家具內。
- [ ] 2.6 新增測試：illuminance 的 visibility constraint 不允許直接跨越完全遮蔽家具。
- [ ] 2.7 匯出自由空間、家具佔據區、input sensors、validation sensors 與 target points 的 2-D/3-D 配置圖。

## 3. 統一 Estimator 介面與基線

- [ ] 3.1 定義 `EstimationContext`、`QueryPoint`、`Estimate` 與 `Estimator` protocol。
- [ ] 3.2 以 adapter 將現有 `DigitalTwinModel` 包裝為 `BasePhysicsEstimator`，不改變現有主模型結果。
- [ ] 3.3 將現有 IDW 包裝為 `SensorIDWEstimator`。
- [ ] 3.4 `Estimate` 輸出加入 method、metric、support nodes、confidence 與 provenance。
- [ ] 3.5 建立共用 evaluator，使所有 estimator 使用相同 input/validation split 與相同 metric calculation。
- [ ] 3.6 新增 regression test：adapter 前後 BasePhysics 數值一致。
- [ ] 3.7 新增 baseline report：BasePhysics、BasePhysics+trilinear、IDW 在相同 target points 的 MAE/RMSE/MaxErr。

## 4. Free-space modular estimators

- [ ] 4.1 實作 `Triangulation2DEstimator`，明確要求固定高度平面與 barycentric interpolation。
- [ ] 4.2 新增 2-D 測試：目標點在 triangle 內、邊界上、外部與退化 triangle。
- [ ] 4.3 實作 `Tetrahedral3DEstimator`，檢查 non-coplanar vertices 與 tetrahedron containment。
- [ ] 4.4 新增 3-D 測試：有效 tetrahedron、退化 cell、家具交疊與目標點不在 cell 內。
- [ ] 4.5 實作 `CellIDWFusionEstimator`，輸出 `p`、top-k、valid cell count 與 rejected cells。
- [ ] 4.6 加入 temperature/humidity 的 soft obstruction factor 與 illuminance 的 hard visibility constraint。
- [ ] 4.7 建立參數敏感度：`p ∈ {1,2,3}`、top-k、minimum volume/area threshold。
- [ ] 4.8 不將任何 pseudo node 標記為 measured ground truth，並新增對應測試。

## 5. Residual corrector 與資料切分

- [ ] 5.1 將 residual corrector 改為可包裝任一 estimator，而不是只耦合單一主模型輸出。
- [ ] 5.2 在建立 residual dataset 前完成 scenario/day/sensor holdout split。
- [ ] 5.3 新增 leave-one-scenario-out synthetic evaluation。
- [ ] 5.4 新增 leave-one-day-out 或 blocked split 的 real-room evaluation。
- [ ] 5.5 對每個 estimator 比較 residual off/on，輸出相同指標。
- [ ] 5.6 新增 leakage test：held-out day、scenario 或 sensor 不得進入 training rows。
- [ ] 5.7 保存 checkpoint metadata：training split、features、normalization、seed、base estimator 與 code version。

## 6. 真實目標點驗證

- [ ] 6.1 固定並文件化至少四類 validation locations：pillow、desk、room center、near-furniture boundary。
- [ ] 6.2 記錄每個 validation sensor 的座標、高度、裝置距離、家具遮蔽關係與取樣頻率。
- [ ] 6.3 收集或整理連續多日 measured values，明確區分 raw measurement、人工整理值與 model estimate。
- [ ] 6.4 產生每個目標點的 measured-vs-predicted 時序圖。
- [ ] 6.5 產生分組誤差：day/night、AC on/off、window open/closed、light on/off。
- [ ] 6.6 產生每個 method/target/metric 的 MAE、RMSE、MaxErr 與 bias。
- [ ] 6.7 記錄 worst-case timestamps，分析外氣、裝置狀態、遮蔽與 sensor anomaly。
- [ ] 6.8 若無法同時部署四個 validation sensors，文件化輪替量測限制，不將跨時段資料當作同時空間場真值。

## 7. 實驗輸出與運算成本

- [ ] 7.1 新增統一 JSON summary schema，包含 dataset、split、method、status、metrics、runtime、worst cases、provenance。
- [ ] 7.2 新增 `scripts/run_estimator_comparison.py` 或等價入口。
- [ ] 7.3 新增 `scripts/run_target_holdout_validation.py` 或等價入口。
- [ ] 7.4 新增 `scripts/build_claim_evidence_matrix.py` 或等價入口。
- [ ] 7.5 記錄單點推論、完整網格、校正、residual inference 與整批評估時間。
- [ ] 7.6 產生 occlusion on/off、residual on/off 與 estimator family 的消融表。
- [ ] 7.7 保存代表性失敗案例與方法排名反轉案例，不只輸出平均最佳結果。
- [ ] 7.8 在 README 或 experiment docs 提供完整重現指令與預期 output paths。

## 8. Claim-to-evidence matrix 與論文同步

- [ ] 8.1 建立 claim-to-evidence matrix：RQ、claim、method status、dataset/split、baseline、metric、artifact、supported/unsupported claims。
- [ ] 8.2 更新中文論文摘要、研究問題、方法、實驗與限制，使其對應 matrix。
- [ ] 8.3 更新英文/IEEE 稿，使用相同方法名稱、完成狀態與核心數值。
- [ ] 8.4 更新簡報產生器，投影片只放圖表與論據，完整解釋放 speaker notes。
- [ ] 8.5 更新圖表標題，明確標示 synthetic、real target-point 或 public task-aligned。
- [ ] 8.6 在論文與簡報中保留 persistence 優於本模型的 CU-BEMS 結果並說明用途差異。
- [ ] 8.7 新增一頁/一節 failure cases、threats to validity 與不能主張的範圍。
- [ ] 8.8 執行 thesis sync check，確認 Markdown、LaTeX/PDF、IEEE、PPT 與 output JSON 數值一致。

## 9. 控制候選排序的證據邊界

- [ ] 9.1 在所有文件中將目前控制功能標示為 counterfactual action ranking。
- [ ] 9.2 為 action ranking 輸出 current state、candidate action、predicted delta、comfort penalty 與 uncertainty/provenance。
- [ ] 9.3 設計 before/after intervention protocol：基準期、介入期、穩定時間、外氣控制、指標與停止條件。
- [ ] 9.4 決定 intervention experiment 是否為口試前必做；若否，明確列為 future work。
- [ ] 9.5 在沒有 intervention evidence 前，不使用「已證明控制有效」或同義敘述。

## 10. 驗證與完成條件

- [ ] 10.1 `python3 -m unittest discover -s tests` 全部通過。
- [ ] 10.2 既有 demo、window matrix、hybrid residual 與 public benchmark 可正常執行。
- [ ] 10.3 target holdout 報告證明 validation observations 未參與 fitting/training。
- [ ] 10.4 estimator comparison 至少包含 BasePhysics、IDW 與一個 free-space estimator。
- [ ] 10.5 real target-point 結果至少涵蓋 pillow，並盡可能涵蓋 desk、center 與 near-furniture。
- [ ] 10.6 claim-to-evidence matrix 的每個核心 RQ 都有對應 artifact 或明確標記 evidence missing。
- [ ] 10.7 論文與簡報不再把 synthetic dense field、public dataset 或 pseudo nodes 描述成真實完整 3-D ground truth。
- [ ] 10.8 完成 OpenSpec review 後，將 delta specs merge 至 main specs 並 archive 此 change。
