# Target Holdout Validation

本實驗用來確認：**validation target 的真值不會參與模型校正，只在預測完成後用來計算誤差。**

## 資料角色

- `input`：可用於 power calibration、trilinear correction 與裝置影響學習。
- `validation`：只能在 evaluator 階段讀取。
- `target`：需要估計的位置，不代表已有量測。
- `pseudo`：模型產生的支撐值，不是 ground truth。

## 執行方式

```bash
python3 scripts/run_target_holdout_validation.py
```

只執行指定情境：

```bash
python3 scripts/run_target_holdout_validation.py --scenario ac_only --scenario all_active
```

輸出：

```text
outputs/data/target_holdout_validation_summary.json
```

## 目前證據範圍

目前 runner 使用 controlled simulation truth，證據標籤為：

```text
synthetic_target_point_holdout
```

它可以驗證：

- input 與 validation names 互斥。
- validation truth 未傳入 calibration。
- 每個 validation target 可計算 MAE、RMSE、Max Error 與 bias。
- adaptive sensor layout 與 holdout evaluator 的資料角色正確。

它不能驗證：

- 真實房間完整 3-D dense field 準確度。
- pillow、desk 等真實感測器的實際誤差。
- counterfactual action ranking 的真實因果效果。

## 後續替換成真實資料

真實房間版本應保留相同流程：

```text
S_input measurements
→ calibration / fitting
→ target prediction
→ read S_validation measurements
→ compute errors
```

需要額外保存：

- sensor coordinates and height
- sampling interval
- device states
- outdoor conditions
- train/validation/test date ranges
- raw measurement provenance
