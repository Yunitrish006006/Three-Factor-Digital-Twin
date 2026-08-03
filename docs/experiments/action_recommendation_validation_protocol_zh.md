# 推薦動作實際介入驗證方法

本文件定義本專案用來驗證「推薦動作是否真的有效」的實驗流程。此流程用於補強目前已完成的真實臥室快照驗證：快照資料已驗證 sparse-sensor calibration 能改善非感測點估計，但尚不能單獨證明推薦動作具有實際因果改善效果。

## 1. 驗證目標

推薦動作驗證要回答的問題是：

- 系統推薦的動作是否讓目標位置或目標區域更接近 comfort target？
- 系統預測的改善方向是否和實測改善方向一致？
- 排名第一的動作是否比不動作、人工基準動作或其他候選動作更有效？

## 2. 實驗流程

每一次介入實驗至少包含下列步驟：

1. 記錄介入前狀態：量測 8 顆角落感測器與目標參考點，例如 `pillow_position`。
2. 使用目前量測值校正數位孿生模型。
3. 讓系統輸出候選動作排序，例如開冷氣、開窗、開燈或冷氣加照明。
4. 記錄系統預測的各候選動作 comfort penalty 與 predicted improvement。
5. 實際執行排名第一的推薦動作。
6. 等待固定 settling interval，建議先採 18 到 30 分鐘，後續可依設備反應時間調整。
7. 再次量測 8 顆角落感測器與目標參考點。
8. 計算實際 comfort penalty 是否下降。

若時間允許，應在相近外部條件下加入對照組，例如 `no_action`、人工選擇動作、或排名第二的候選動作。

### 2.1 可執行資料套件

為避免收集資料後才改變欄位或指標定義，本專案已加入下列預註冊工具：

- `docs/requirements/e8_intervention_trial_schema.json`：固定 study、trial、target、before/after observation、predicted ranking、executed action、settling interval、control condition 與 protocol deviation 欄位。
- `docs/templates/e8_intervention_trials_template.json`：以 `bedroom_01` 與 `pillow_position` 為目標的空白收集範本。
- `scripts/analyze_e8_intervention_trials.py`：重新計算 penalty、actual improvement、prediction error、direction accuracy，以及設計允許時的 top-1 regret 與 Spearman rank correlation。

目前範本仍為零筆 trial。執行：

```bash
python3 scripts/analyze_e8_intervention_trials.py
```

會產生 `outputs/data/e8_intervention_summary.json` 與 Markdown 摘要；目前狀態必須是 `NOT_EVALUATED`，所有效益估計維持 `null`。這代表資料與分析流程已可執行，不代表推薦效果已驗證。

## 3. 主要指標

推薦動作的預測改善量定義為：

```text
predicted_improvement(action) =
    penalty_before - predicted_penalty_after(action)
```

實際改善量定義為：

```text
actual_improvement(action) =
    penalty_before - measured_penalty_after(action)
```

建議報告下列指標：

- success rate：`actual_improvement > 0` 的比例。
- mean actual improvement：實測 comfort penalty 平均下降量。
- prediction error：`abs(predicted_improvement - actual_improvement)`。
- direction accuracy：溫度、濕度、照度改善方向是否與預測一致。
- top-1 regret：排名第一動作與實測最佳動作之間的 improvement 差距。
- rank correlation：若同一狀態可測多個候選動作，計算預測排名與實測排名的 Spearman correlation。

分析器不直接相信人工填入的 penalty，而是依三因子 target、tolerance 與 weight 重新計算。`top-1 regret` 與 `rank correlation` 只有在同一 `block_id` 具有可比較的多個實測 action arm 時才輸出，否則維持 `null`。單一 top-ranked trial 不足以推論排名優於其他候選動作。

## 4. 論文表述原則

在尚未完成實際介入資料前，論文應採用下列表述：

```text
The current real-room bedroom snapshots validate sparse-sensor calibration and point-level estimation at an unseen pillow location. The action recommendation module is therefore evaluated as a model-based counterfactual ranking. Causal validation of recommendation efficacy requires a before/after intervention protocol in which the top-ranked action is executed in the room and the measured comfort-penalty reduction is compared against the predicted improvement.
```

中文論文可寫為：

```text
目前真實臥室快照資料已驗證稀疏感測校正對非感測點估計的改善效果；推薦動作則定位為基於校正模型的反事實模擬排序。若要驗證推薦動作本身具有實際因果改善效果，需進一步執行介入式 before/after 實驗：先量測介入前狀態並輸出推薦排序，再實際執行排名第一的動作，於固定等待時間後再次量測，最後比較實測 comfort penalty 是否下降，以及預測改善量與實測改善量是否一致。
```

截至目前，E8 已具備 versioned schema、空白 trial template 與 deterministic analyzer，但完成真實介入試驗數仍為 0，因此證據狀態為 `NOT_EVALUATED`，不得報告 success rate 或其他實測效益數字。
