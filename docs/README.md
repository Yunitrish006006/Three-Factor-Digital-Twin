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
- [`research/enclosure_temperature_control_method_selection_zh.md`](research/enclosure_temperature_control_method_selection_zh.md)：機箱溫控的五篇候選方法、原文定位與移植順序（尚未採用／驗證）。
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

## BOPTEST 自動整定 PI 開發初測（2026-09-08）

- [教授報告：離線 HTML](reports/boptest_rapid_pi_2026-09-08_zh.html)：2h／6h 辨識、固定 PI、9 組搜尋、環境前饋的負結果與 v2 補強。
- [完整研究紀錄](../openspec/changes/pilot-boptest-rapid-pi/evidence.md)：26 個完成的模擬回合、資料／授權追溯、控制品質與成本界線。這是開發探索，尚未採納為論文確認成果。

- [第二輪演算法改進與新日期／雜訊檢查（HTML）](reports/boptest_transfer_2026-09-08_zh.html)：v3 交接與 v4 擾動觀測、26 組新增模擬、版本固定後的完整結果與動作抖動代價。

- [第三輪：降低指令抖動與致動延遲測試（HTML）](reports/boptest_jitter_2026-09-08_zh.html)：34 組新增模擬；平滑收益、乾淨情境與最大誤差代價完整保留。

- [情境特化審查（先讀）](reports/boptest_generality_audit_2026-09-08_zh.html)：確認存在單一模型開發選參；尚未排除情境特化，暫停繼續單情境微調。

- [跨設備少資料適應：送風與水暖（HTML）](reports/boptest_cross_plant_2026-09-08_zh.html)：共用算法與有限試調；水暖辨識拒絕，跨場景目標尚未達成。

- [共用延遲／二階辨識：完整 32 次模擬（HTML）](reports/boptest_delayed_dynamics_2026-09-08_zh.html)：兩設備均通過辨識；水暖 2h 改善、6h 未勝 auto-PI，成本與負結果完整保留。

- [新增三設備：熱泵、公寓與商用散熱器（HTML）](reports/boptest_more_devices_2026-09-08_zh.html)：固定演算法的新增 FMU 檢查，涵蓋辨識拒絕、控制退步與完整適應成本。

- [完整模型與有限補償（HTML）](reports/boptest_consistent_2026-09-08_zh.html)：36 次新日期模擬；7 組改善、5 組退步、6 組停用持平，並同步論文層級 3D 圖。

- [進步與退步裝置的共同特徵（HTML）](reports/boptest_device_groups_2026-09-08_zh.html)：補償碰限幅、模型反應與同設備資料量反例；事後描述性分析，不作因果推論。

- [PI 前期輔助／退出界線研究（2026-09-08）](reports/boptest_startup_2026-09-08_zh.html)：五設備、32次FMU試驗；水暖前段約20%改善，誤差界線尚不可辨認，非總調整成本或實機證據。

- [PI 趨勢預估退出與積分接手研究](reports/boptest_predictive_startup_2026-09-08_zh.html)：27次新FMU試驗；水暖仍有前段改善但一確認日達標延遲，未取代前版。

- [PI 輔助時間 × 交接方式研究](reports/boptest_handover_2026-09-08_zh.html)：32次新FMU試驗；水暖15min轉入積分通過兩確認日，前段MAE約改善22%，非通用最優或成本優勢證明。

- [本週研究進度與報告入口（2026-09-08）](reports/weekly_progress_2026-09-08_zh.html)
