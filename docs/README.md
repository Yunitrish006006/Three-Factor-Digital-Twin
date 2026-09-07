# 文件導覽

這裡只按「使用目的」導覽，不再逐檔重複列出整個 repository。

## 教授報告

- [`reports/professor_two_week_report_2026-08-04_2026-08-17_zh.md`](reports/professor_two_week_report_2026-08-04_2026-08-17_zh.md)：兩週 RNN、Kalman、應用邊界、前後比較與教授 demo。
- [`reports/professor_weekly_report_2026-07-28_2026-08-03_zh.md`](reports/professor_weekly_report_2026-07-28_2026-08-03_zh.md)：精簡週報與前後比較。
- [`reports/professor_complete_experiment_overview_2026-08-03_zh.md`](reports/professor_complete_experiment_overview_2026-08-03_zh.md)：E1–E10 完整實驗總覽（於 2026-08-17 補入 Kalman 受控比較）。
- [`reports/weekly_progress_2026-07-28_2026-08-03_zh.md`](reports/weekly_progress_2026-07-28_2026-08-03_zh.md)：內部完整進度；教授版不需引用個人開發細節。

## 論文與簡報主線

- [`thesis/README.md`](thesis/README.md)：中文論文、簡報大綱與主線文件。
- [`papers/ieee/paper.tex`](papers/ieee/paper.tex)：英文 IEEE 稿正式來源。
- [`papers/thesis/`](papers/thesis/)：中文論文已建置成品與必要資產。
- [`papers/README.md`](papers/README.md)：paper、成品與外部來源的分界。

## 實驗與研究判讀

- [`experiments/`](experiments/)：實驗協定、結果與驗證說明。
- [`experiments/target_holdout_validation_zh.md`](experiments/target_holdout_validation_zh.md)：input／validation 角色分離與受控 holdout 驗證。
- [`research/`](research/)：教授方向與應用範圍判讀。
- [`models/`](models/)：模型設計、參考模型與 Kalman 研究方向。

若要確認「目前可以主張什麼」，優先查看完整實驗總覽與 [`experiments/thesis_result_verification_zh.md`](experiments/thesis_result_verification_zh.md)，不要只讀單一模型筆記。

## 規格與模板

- [`requirements/`](requirements/)：房間設計與 E8 資料契約。
- [`templates/`](templates/)：標準房間、真實房間與介入試驗範本。
- [`hardware/`](hardware/)：input-grade、validation-grade 感測節點與部署規劃。
- [`../openspec/`](../openspec/)：正式研究能力、證據邊界與變更紀錄。

## 系統與展示文件

- [`mcp/`](mcp/)：MCP 與 Gemma bridge。
- [`web/`](web/)：Web demo。
- [`demos/professor_demo_guide_2026-08-17_zh.md`](demos/professor_demo_guide_2026-08-17_zh.md)：教授版離線成果頁與 Live demo 展示順序。
- [`../digital_twin/README.md`](../digital_twin/README.md)：程式模組與依賴方向。
- [`../scripts/README.md`](../scripts/README.md)：腳本分類與建議入口。

## 歷史與外部材料

- [`archive/`](archive/)：不屬於目前論文主線、但仍需保留的課程或歷史材料。
- [`papers/reference_sources/`](papers/reference_sources/)：外部 PDF、文字轉錄與來源輔助檔；它們不是本研究產生的證據。

## 新增文件規則

- 先判斷它是正式來源、結果說明、教授報告、規格，還是外部來源。
- 同一主題只維護一份正式文件；摘要以連結回正式來源，不複製整段內容。
- 舊版本若仍需保存，移入 `archive/`，不要在主線目錄增加 `v2`、`final` 或 `updated` 檔名。
