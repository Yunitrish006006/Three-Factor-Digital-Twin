# 教授版報告 QA 紀錄｜2026-10-26

## 報告生成與靜態檢查

- 由凍結結果重新生成 `docs/reports/unified_enclosure_2026-10-26/report_zh.html`、Markdown 執行摘要、PDF、圖表及 `runs.csv`；未重跑校準或評估。
- HTML 為離線單檔：5 張圖以內嵌 SVG 呈現，無外部 script，含 viewport、窄螢幕表格橫向捲動、print CSS；靜態解析共有 129 個表格列，含 60 個正式回合逐回合表格。已檢查分組/seed/方法共60項均在HTML結果資料中；Markdown 清楚標示為執行摘要，HTML 才是完整教授報告。
- HTML 瀏覽器實際響應式、互動及列印預覽未做。先前 Codex 瀏覽器對本機 file URL 遭安全政策拒絕；沒有使用其他 browser、HTTP server 或 CDP 繞過。此限制不影響本紀錄中的靜態檢查聲明。

## 圖表與 PDF

- 檢視 MAE 四分組長條圖、能耗代理/MAE 散點圖，以及全部3個 holdout seed 的追蹤圖；散點圖近似點標籤已調整。精確值仍由表格提供。
- PDF 重新排版後共7頁 A4，以 Poppler 90 dpi 轉頁圖並逐頁目視檢查。第1頁摘要和 holdout表、第2頁共同條件與凍結選參、第3頁四分組表、第4頁原因與限制、第5–7頁三組holdout追蹤圖皆有內容；沒有原先近空白第4頁。公式以一般文字寫出，避免特殊數學符號字型缺字。
- PDF的追蹤曲線溫度標為區間末端，命令/負載為區間起點；三個 seed 全數呈現。

## 研究資料核對

- stored-data verifier PASS：45校準、60正式回合、12,600列、1,995個回合指標；逐步標量狀態最大差異0；371個歷史檔案未變；兩種篡改負面案例皆拒絕。
- 結果 SHA-256：`e9953311d4528786b17b558cca6757db9dd1f1194a3f96c3c52748d689cb7552`。
- OpenSpec validator PASS：14個spec files、130項requirements、251個scenarios、42個active changes。
- 中文 thesis DOCX/PDF 複本與 `outputs/papers/` 對應檔案雜湊一致。DOCX 已 render 74 頁，但未逐頁目視。thesis PDF 93頁、IEEE PDF 9頁、中文審閱稿PDF 6頁有既有 build 紀錄；未宣稱這些整份文件均完成視覺 QA 或符合投稿版型。簡報提綱與建置來源已同步，舊 PPTX 依新教授簡報採 HTML 的專案規則保留。

## 界線

結果均來自完全狀態可見的假設熱模型。實體電腦機箱、感測器、風扇/整機實測能耗、硬體安全與稀疏感測控制效果均為 NOT_EVALUATED。獨立核對不包含重新最佳化 LQR/MPC。改善方案只列為後續待驗證，不當作已證實原因或已完成工作。
