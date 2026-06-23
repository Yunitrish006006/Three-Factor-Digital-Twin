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
