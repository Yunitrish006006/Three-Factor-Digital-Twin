# 腳本導覽

正式流程優先使用本頁列出的 canonical scripts。不要另外建立 `*_updated.py`、`*_final.py` 或特定代理版本。

## 驗證與完整執行

| 腳本 | 用途 |
| --- | --- |
| `run_all_thesis_experiments.py` | 執行目前完整研究實驗集合 |
| `verify_thesis_results.py` | 核對論文登錄結果與輸出證據 |
| `validate_research_openspec.py` | 驗證 OpenSpec 結構與規格 |
| `validate_room_design.py` | 驗證房間尺寸、點位與 bounding boxes |
| `run_submission_readiness_experiments.py` | 執行資料範圍與 readiness 稽核；不是投稿動作 |

## 論文、簡報與圖表建置

| 腳本 | 正式輸出 |
| --- | --- |
| `build_architecture_diagrams.py` | 架構 SVG 與論文圖片資產 |
| `build_thesis_docx.py` | 中文論文 DOCX |
| `build_thesis_pdf.py` | 中文論文 PDF |
| `build_thesis_pptx.py` | 短版與 30 分鐘版簡報 |
| `build_public_benchmark_figures.py` | 公開資料比較圖 |

## 研究實驗

- `run_demo.py`：標準受控模擬與輸出。
- `run_window_matrix.py`：48 組窗戶情境矩陣。
- `run_hybrid_residual_experiment.py`：hybrid residual 實驗。
- `run_bedroom_weekly_simulation.py`：真實臥室週資料分析。
- `run_public_dataset_benchmark.py`：公開資料 shared-task baseline。
- `run_public_dataset_model_comparison.py`：同資料模型比較。
- `run_oh2024_inspired_comparison.py`：文獻概念移植比較。
- `run_next_day_temperature_comparison.py`：次日溫度比較。
- `run_rnn_3d_field_comparison.py`：同八情境、同稀疏觀測的 pure RNN 完整 3-D 場 LOO baseline。
- `run_rnn_public_comparison.py`：SML2010 時序 vanilla RNN 公平比較。
- `run_kalman_filter_comparison.py`：固定 protocol 的同資料受控 Kalman filtering 比較。
- `build_professor_demo.py`：由 canonical JSON 產生教授版兩週離線成果頁。
- `run_target_holdout_validation.py`：以分離的 input／validation roles 執行受控 target-point holdout；目前證據類型是 synthetic。
- `analyze_e8_intervention_trials.py`：E8 真實介入資料分析；空白模板只能得到 `NOT_EVALUATED`。

## 資料準備

- `prepare_experiment_data.py`
- `build_training_templates.py`
- `build_public_dataset_benchmark_templates.py`
- `normalize_public_benchmark_data.py`

大型 raw/normalized public data 保存在被忽略的 `outputs/data/`，不要複製進 `docs/`。

## 服務與展示

- `run_web_demo.py`
- `run_mcp_server.py`
- `ask_gemma.py`

## 非主論文腳本

`build_lagrange_interpolation_paper_pptx.py` 只重建封存在 `docs/archive/course_reports/lagrange/` 的外部課程論文報告，不屬於目前論文主線。
