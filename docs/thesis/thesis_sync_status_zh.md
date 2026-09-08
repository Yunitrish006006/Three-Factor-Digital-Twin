# 論文現況整理與同步狀態

## 2026-09-08 GitHub 整理補記

本次已補齊 E15 完成勾選，並成功重建中文 DOCX／PDF 及英文 IEEE PDF；中文 DOCX／PDF 的 outputs 副本一併同步。數值核對 110 PASS、0 FAIL、0 MISSING。依使用者網頁簡報偏好，新增 [本週 HTML 報告](../reports/weekly_progress_2026-09-08_zh.html)，歷史 PPTX 保留。

另將 14 份圖譜所需的衍生結果 JSON 以原位元組快照保存至 docs/research/published_results，來源與 SHA256 位於 published_graph_evidence.json；不含原始資料或 FMU。已驗證沒有 outputs/ 的乾淨副本仍可產生完整論文圖與 960 條控溫比較。控制方法仍屬未採納延伸，未加入正式論文作為已驗證控制主張。

## 2026-09-08 現況盤點

本次整理既有主稿、實驗紀錄與文件入口，不變更研究方法、章節或結論。以下是工作區盤點，不代表已完成投稿前審查；文末保留 2026-07-12 的歷史紀錄，不能把它當成今日待辦。

### 論文目前在說什麼

正式題目仍是「單房間非連網家電環境影響學習之稀疏感測空間數位孿生原型」。主線是以少量感測器，結合物理啟發模型、稀疏校正與殘差學習，估計溫度、濕度及照度。Web／MCP 是展示與服務介面。

目前應用推進方向為電腦機箱稀疏測溫與虛擬感測。公開伺服器資料已提供方法驗證，但桌機機箱與 NTC 實測尚未完成。室內模型的 20–30°C 範圍與 E15 的 CPU 溫度任務應分開解讀，不能把兩者視為同一量測目標。

### 閱讀入口與現有章節

| 用途 | 正式入口 | 閱讀重點 |
| --- | --- | --- |
| 中文主稿 | [thesis_draft_zh.md](thesis_draft_zh.md) | 第 1–2 章問題與文獻；第 3 章方法；第 4 章實作；第 5 章證據；第 6 章結論與限制 |
| 英文稿 | [paper.tex](../papers/ieee/paper.tex) | 英文論述及 E12–E15 證據鏈 |
| 報告準備 | [30 分鐘大綱](presentation_outline_zh_30min.md)、[講稿](presentation_speaker_notes_zh_30min.md) | 口頭報告順序與限制說明 |
| 最新確認結果 | [E15 evidence](../../openspec/changes/confirm-bmc-temporal-transfer-e15/evidence.md) | 一次性執行結果、來源 hash、負向 runs 與主張邊界 |
| 數值核對 | [本地驗證報告](../../outputs/data/thesis_result_verification_report.md) | 本次執行的 PASS／FAIL／MISSING；outputs 未必隨 Git 提供 |

### 成果與證據邊界

| 證據線 | 目前成果 | 論文可主張的範圍 |
| --- | --- | --- |
| E1–E6 受控模擬 | 場重建、IDW 比較、消融、裝置影響與 residual 實驗 | 受控真值下的方法表現；不是完整真實房間驗證 |
| E7 臥室快照 | 7 天、28 筆，未參與校正的 pillow 點誤差改善 | 真實目標點稀疏校正；不是完整 3D 真值 |
| E8 介入 | 尚無完成的實測介入 | 只能說反事實動作排序，不能說已證明控制效益 |
| 公開資料／RNN 系列 | 有任務優勢，也有 persistence 較佳及 RNN 負向結果 | 按相同資料與任務比較，不能總稱所有模型或任務均勝出 |
| AAU E11H／E11F | commissioning 開發及凍結確認已有結果 | 同一 campaign 的校正輔助 unseen-byte transfer；不是跨日期或 NTC 準確度驗證 |
| BMC E12–E14 | E12 未評估；E13 parser-invalidated；E14 修正後作回溯比較 | 必須保留失敗與資料修正歷程；E14C 不是獨立確認 |
| BMC E15 | 14 檔、3,112 rows；MAE 1.6939→0.9744°C，12/14 runs 勝出，十項閘門通過 | 同一伺服器 CPU 目標溫度的時間／工作負載轉移；兩個退步 runs 必須保留 |

E15 的逐 run 等權 MAE 改善為 0.6134°C，95% bootstrap CI 為 [0.2721, 0.9831]°C；它與 pooled MAE 差值是不同統計量。完整數字以 E15 evidence 及封存結果為準。

### 本次核對結果與待整理事項

已執行 `python3 scripts/verify_thesis_results.py`：**110 PASS、0 FAIL、0 MISSING**。這代表腳本涵蓋的數值與本地證據一致，不等同全部敘述、PDF 排版或簡報成品已審查完成。本次未重跑實驗、下載資料或重建正式文件。

1. **先補進度紀錄。** E15 evidence 已記載 2026-09-07 完成；GitHub 整理時已依實際封存結果補齊 [tasks.md](../../openspec/changes/confirm-bmc-temporal-transfer-e15/tasks.md) 的下載、執行與 evidence 勾選；原有重建勾選對應 NOT_EVALUATED 階段，不能直接當成 E15 執行後完成證明。
2. **釐清歷史與現在的措辭。** 主稿附錄 E11E／E11G 的「E11F 未下載／未存取」是當時開發決策；後面已有 E11H／E11F 完成結果。後續編修宜補上「當時」與階段日期，避免讀者誤認矛盾。
3. **收束研究敘事。** 題目及摘要仍以室內三因子為核心，機箱結果集中在第五章與附錄。下一輪正式編修應交代機箱驗證與原研究問題的關係；本次不擅自改題或改章節。
4. **更新舊導覽。** [實驗驗證流程](../experiments/thesis_result_verification_zh.md) 仍記錄 E1–E9 與 71/71 的歷史狀態；今日核對結果以上方 110 項報告為準。
5. **正式交付前同步建置。** 已在中文主稿、DOCX builder、IEEE 稿及簡報同步 helper 看到 E15 結果；本次未逐份檢查 DOCX／PDF／PPTX 內容，因此成品同步仍列待驗。涉及正式敘述修改時，依 [AGENTS.md](../../AGENTS.md) 一併同步及重建。

節省額度的接續順序：先修狀態紀錄與歷史措辭，再集中一次同步主稿、英文稿及簡報並核對成品；新硬體實驗另依 protocol 推進。E15 已消耗一次性確認集，不可為了整理文件重跑。

---

## 歷史紀錄：2026-07-12 LaTeX 與 OpenSpec 同步

## 同步日期

2026-07-12

## 已同步檔案

- `docs/papers/thesis/thesis_draft_zh.tex`

## 本次同步內容

本次已將中文論文 LaTeX 主檔從舊版「8-corner sparse field reconstruction」定位，改為目前 OpenSpec 的研究邊界：

- 核心主張改為「家具感知自由空間中的可驗證目標點估計」。
- 保留 8-corner 作為 baseline，不再作為唯一正式部署假設。
- 加入 `S_input`、`S_validation`、`V_target`、`V_pseudo` 的資料角色。
- 加入 `Ω_room`、`Ω_occ`、`Ω_free = Ω_room \ Ω_occ` 的自由空間定義。
- 加入 ESP32-C3 + DHT11 + BH1750 sensing node 設計。
- 加入 8–10 顆以上 furniture-aware node deployment。
- 加入 `input_fan_path` 與 `input_fan_shadow_zone` 的電風扇感知部署概念。
- 加入 occupancy 作為 dynamic heat / moisture / obstruction source。
- 加入 Google Home UI operation events 作為 operator-verified operation context。
- 明確區分 synthetic full-field、synthetic target holdout、real target-point、public task-aligned benchmark 與 intervention validation。
- 將控制建議限制為 counterfactual action ranking。

## 已保留但重新標記的既有結果

- Synthetic 8-scenario field MAE：保留為 controlled synthetic full-field evidence。
- Hybrid residual leave-one-scenario-out：保留為 synthetic / controlled robustness evidence。
- 7-day real-bedroom pillow snapshot：改標記為 pillow target-point evidence，不再外推為 complete real 3-D field validation。
- SML2010 / CU-BEMS：保留為 public task-aligned benchmark，不作 dense spatial ground truth。

## 尚未完成同步

以下項目尚未完成，因此不應宣稱全部 thesis artifacts 已完全一致：

- 中文 Markdown 主稿同步。
- IEEE 英文稿 `docs/papers/ieee/paper.tex` 同步。
- PPT 與 speaker notes 同步。
- claim-to-evidence matrix 建立。
- 真實 bedroom_01 node deployment map。
- real target-point validation 的新資料圖表。
- output JSON、figures、LaTeX 數值一致性檢查。
- XeLaTeX 實際編譯確認。

## 使用注意

目前 LaTeX 已是 OpenSpec-aligned draft，但屬於研究主張與章節架構同步，不代表所有實驗輸出與圖表已重新產生。後續應先完成 claim-to-evidence matrix，再同步 IEEE 稿與簡報。
