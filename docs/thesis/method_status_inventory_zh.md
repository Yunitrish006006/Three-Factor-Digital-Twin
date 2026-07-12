# 論文方法完成狀態盤點

本文件用來避免把「已有設計」誤寫成「已有實驗證據」。狀態定義如下：

- **implemented**：已有可執行程式或明確資料流程。
- **validated**：除實作外，已有可重現的實驗輸出與指標。
- **proposed extension**：已有設計、公式或 OpenSpec，但尚未完成充分實驗。
- **future work**：目前尚未實作或不列入口試前必要範圍。

## 目前狀態

| 方法／功能 | 狀態 | 現有依據 | 尚缺證據 |
|---|---|---|---|
| 三因子 variable-specific nominal models | implemented | `digital_twin/physics/model.py` | 真實多點 holdout comparison |
| 冷氣、窗戶、照明局部影響函數 | implemented | 主模型與 scenario tests | 更完整真實裝置事件資料 |
| 家具遮蔽對氣流與照度的近似 | implemented | furniture-aware influence functions、unit tests | 遮蔽 on/off 實驗矩陣 |
| Adaptive corner sensor layout | implemented | `create_adaptive_sensor_layout()` | 真實房間配置圖與 sensor deployment evidence |
| Sensor roles：input / validation / target / pseudo | implemented | `digital_twin/core/entities.py` | 更多既有 pipeline 的全面整合 |
| Synthetic target-point holdout pipeline | implemented | `digital_twin/core/validation.py`、runner、tests | 執行後的版本化 output JSON |
| Active-device power calibration | implemented | `DigitalTwinModel.calibrate_active_device_powers()` | validation sensors 完全排除的 end-to-end regression report |
| Trilinear residual correction | implemented | `TrilinearCorrection` 與 fitting flow | 在 holdout targets 的系統比較 |
| IDW baseline | implemented | `digital_twin/physics/baselines.py` | 與所有 proposed estimators 使用同一 split 的報告 |
| Hybrid residual neural network | validated（synthetic scenario split） | hybrid residual experiment outputs | real target-point blocked temporal validation |
| CU-BEMS / SML2010 task-aligned benchmark | validated（task-aligned） | public benchmark scripts and outputs | 不可延伸為 3-D field evidence |
| 2-D triangulation estimator | proposed extension | OpenSpec design | 程式、unit tests、holdout results |
| 3-D tetrahedral estimator | proposed extension | OpenSpec design | 非共面支撐點、程式與真實驗證 |
| Cell-IDW fusion | proposed extension | OpenSpec design | 程式、參數敏感度、ablation |
| Estimator-independent residual corrector | proposed extension | OpenSpec design | 統一 estimator interface 與比較 |
| Claim-to-evidence matrix 自動產生 | proposed extension | OpenSpec tasks | generator 與同步檢查 |
| 真實 pillow target validation | implemented / preliminary | bedroom weekly data 與 pillow reference | 嚴格 `S_input`/`S_validation` 重跑與多目標點 |
| Desk / room center / near-furniture real validation | future work | 目標位置規劃 | 感測器部署與多日資料 |
| Counterfactual action ranking | implemented | recommendation module | 真實 before/after intervention |
| 自動閉環控制有效性 | future work | 尚無 causal evidence | intervention protocol 與實驗 |
| MCP / Web / agent tools | implemented | service and interface modules | 只屬應用層，不作為估計方法證據 |

## 報告用語規則

### 可以使用

- 「本研究已實作……」
- 「在 synthetic scenario split 中得到……」
- 「在 pillow reference point 的初步資料中……」
- 「本研究提出 2-D／3-D／Cell-IDW 作為後續 modular estimators……」
- 「目前控制輸出為模型式反事實排序……」

### 不可直接使用

- 「本研究已證明 8 顆感測器可準確重建真實完整 3-D 場。」
- 「所有 target points 都已完成真實驗證。」
- 「Cell-IDW 一定優於 2-D triangulation。」
- 「公開資料集證明本方法具有真實 3-D 空間準確度。」
- 「推薦第一名的動作已證明能造成真實因果改善。」

## 下一個狀態更新條件

一個方法從 `implemented` 升為 `validated`，至少需要：

1. 明確的 dataset 與 split。
2. 至少一個相容 baseline。
3. MAE、RMSE、Max Error 或對應任務指標。
4. 命名 script 與版本化 output file。
5. 至少一個 failure case 或限制分析。
6. 論文、IEEE 稿與簡報使用一致數值及證據標籤。
