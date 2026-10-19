# 專案資料來源與使用摘要

## 1. 主要資料類別

### 自製 synthetic benchmark
- 儲存在 `outputs/data/`
- 包含完整 3D 場重建輸出檔，例如 `ac_light_field.csv`、`window_only_field.csv`、`all_active_field.csv` 等
- 主要用於 thesis 中的 8 組標準情境、48 組窗戶矩陣與 full-field reconstruction

### 真實房間 sparse calibration
- 來源於 `bedroom_01`
- 相關輸出存放於 `outputs/data/bedroom_01_weekly/`
- 重要內容：7 天、28 筆快照、8 顆角落感測器觀測、裝置狀態、外部邊界條件與 pillow 位置參考值
- 相關房間設計與資料描述：
  - `docs/templates/room_design_bedroom_01.json`
  - `docs/requirements/bedroom_01_combined_room_and_weekly_simulation.json`

### 公開資料集 task-aligned benchmark
- 主要使用資料集：SML2010、CU-BEMS
- raw 資料存放於：`outputs/data/raw_public/`
- 正規化中介格式存放於：`outputs/data/normalized_public/`
- 最終 benchmark summary 存放於：`outputs/data/public_benchmarks/`
  - `sml2010_hybrid_twin_comparison.json`
  - `cu_bems_hybrid_twin_comparison.json`

## 2. 相關腳本與流程

### `scripts/prepare_experiment_data.py`
- 下載與檢查 raw public dataset
- 管理 `outputs/data/raw_public/`、`outputs/data/normalized_public/`、`outputs/data/public_benchmarks/`
- 提供 `--download` 與 `--normalize` 參數

### `scripts/normalize_public_benchmark_data.py`
- 將 raw SML2010 / CU-BEMS 轉成 repo 對齊的 normalized public templates
- 輸出目錄預設為 `outputs/data/normalized_public`

### `scripts/run_public_dataset_benchmark.py`
- 對 normalized public dataset 執行 shared-task benchmark
- 產生 persistence 與 linear regression baseline 的 summary
- 輸出預設為 `outputs/data/public_benchmarks`

### `scripts/run_public_dataset_model_comparison.py`
- 將本研究 hybrid digital twin / residual model 映射到 public task
- 與 baseline 進行 head-to-head 比較
- 產生 hybrid twin comparison JSON summary

### `scripts/run_bedroom_weekly_simulation.py`
- 用於 `bedroom_01` 真實快照模擬與 sparse calibration驗證
- 讀取 `docs/templates/room_design_bedroom_01.json` 與 `docs/requirements/bedroom_01_combined_room_and_weekly_simulation.json`
- 輸出 `outputs/data/bedroom_01_weekly/`

## 3. thesis 中資料使用角色

- `synthetic benchmark`：主要 full-field 重建與模型元件驗證
- `bedroom_01`：真實 sparse 校正驗證，檢查未參與校正的 pillow 參考點是否改善
- `SML2010` / `CU-BEMS`：公開資料 task-aligned benchmark，僅做相容子任務比較，不宣稱完整 3D dense-field 驗證

## 4. 檔案定位

- `docs/templates/room_design_template.json`：房間設計格式範本
- `docs/templates/room_design_standard_room_example.json`：參考標準房間
- `docs/thesis/thesis_draft_zh.md`：中文論文主體，已有對資料屬性與使用角色的說明
- `README.md`：包含公開資料 benchmark 的執行順序

## 5. 重點提示

- 公開資料集應視為外部合理性檢查，而非完整 3D 場驗證
- `bedroom_01` 只支援 sparse calibration 檢查，不是 dense truth
- `outputs/data/` 是目前專案實際使用的結果存放位置，raw public dataset 也在這個工作資料夾下但通常不會 commit


## 2026-10-05機箱控制模擬補充

本階段不是新增實測dataset：v1三方法歷史36正式回合保留；v2每方法3候選/3seed，共36校準+48正式回合/10080步，讀取 openspec/changes/validate-enclosure-four-controllers-20261005/artifacts/result.json。假設名義參數已知，三組指定plant variants為合成壓力測試。MPC對PID＋FF/LQR的holdout改善假設不支持；來源snapshot/完整CSV/獨立核對/篡改測試保留。7步殘差拒絕回退，不是全程零回退。實體機箱、NTC、throttling、整機功耗與E8仍未評估。

## 2026-10-06 稀疏機箱候選原型

資料為三組指定熱網路參數的合成軌跡，未新增實測 dataset。共同有限辨識採金屬片／空氣／風扇觀測，每組 600 秒；熱源真值只用於評估。108 回合／19,440 步的設定、來源凍結、CSV、結果、獨立核對及輸入限定重播位於 `openspec/changes/prototype-sparse-enclosure-transfer-20261006/artifacts/`。校正估測 MAE 從 0.6580 降到 0.3352°C；六步排序較單步追蹤改善 9.03%，仍未優於 PI。容量與部分係數已知、單一方程家族、合成噪聲限制保留；未擴張原 20–30°C 室內適用域。這是獨立溫度候選流程，完整三因子與實體介入仍未評估。
