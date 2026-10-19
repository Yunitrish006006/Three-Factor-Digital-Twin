# Enclosure Thermal Control — 電腦機箱閉環控溫演算法比較

> **研究方向更新：2026-10-19。** 目前依指導教授要求，優先比較不同控制演算法在機箱熱環境下的閉環控溫效果、研究性能差異原因，並嘗試提出可公平驗證的改善方法。短期交付目標為 **CSME 2026 中文論文候選投稿**與 **2027 年 1 月碩士口試／畢業**。CSME 是否投稿及是否受校方認列，仍需教授與系辦確認。

## 先看這四份

1. **[2027/01 畢業與 2026/10/25 CSME 投稿時程](docs/planning/2027-01-graduation-csme2026-zh.md)**：期限、待辦、接受證明與口試關卡。
2. **[目前機箱控制研究主軸與證據界線](docs/research/current_enclosure_control_scope_2026-10-19_zh.md)**：評比問題、控制器、實機條件及暫停方向。
3. **[CSME 2026 中文稿／投稿準備](docs/papers/conference_review_2026-10-19/readiness_zh.md)**、[完整五頁中文稿](docs/papers/conference_review_2026-10-19/manuscript_zh.md)：**投稿前審閱稿；並非已投稿或已被接受**。
4. **[2026-10-19 LQR 診斷原始證據](openspec/changes/diagnose-enclosure-lqr-20261019/evidence.md)**：四個同族模擬 plant、40 回合與負面結果。

## 研究狀態

- 主要成果是 **模擬機箱／控制環境的閉環演算法比較**。機箱實測、風扇實際電功率與硬體上的公平對照尚未完成，不能稱為真實機箱控溫已驗證。
- 目前已有 PI、PID、LQR、MPC 與控制候選排序的比較資料；不同實驗批次的排名可能不同，不能忽略控制代價及模型失配。
- 研究中的新算法仍為條件式目標，不可先宣稱優於全部 baseline。
- 單房間三因子空間數位孿生、pillow reference、家具與 Google Home、MCP 展示等舊主題支援筆記已移到 [歷史封存區](docs/archive/room-spatial-digital-twin/README.md)。主稿、原始程式與凍結 evidence 仍保留原路徑以免破壞重現性。

## 本日獨立文獻報告（與控制研究分開）

- [Kalman 1960 原始論文導讀（離線 HTML，含 Riccati 推導與逐頁講稿）](docs/reports/lqr_kalman1960_paper_only_2026-10-19_zh.html)／[純文字講稿](docs/reports/lqr_kalman1960_paper_only_2026-10-19_zh.md)。只介紹論文本身，不連結到機箱實驗的推論。

## 入口與保留的研究資產

| 用途 | 位置 |
| --- | --- |
| 活動與期程 | [docs/planning/](docs/planning/README.md) |
| 活躍研究及證據邊界 | [docs/research/current_enclosure_control_scope_2026-10-19_zh.md](docs/research/current_enclosure_control_scope_2026-10-19_zh.md) |
| CSME 中文會議論文 | [docs/papers/conference_review_2026-10-19/](docs/papers/conference_review_2026-10-19/readiness_zh.md) |
| 教授本週說明與離線頁 | [docs/reports/professor_weekly_script_2026-10-19_zh.md](docs/reports/professor_weekly_script_2026-10-19_zh.md) |
| 中文碩論歷史正式來源（**尚待改編為機箱研究**） | [docs/thesis/README.md](docs/thesis/README.md) |
| 模型、程式、測試與研究規格 | [digital_twin/](digital_twin/README.md)、[scripts/](scripts/README.md)、[openspec/](openspec/README.md) |
| 房間三因子舊文件 | [docs/archive/room-spatial-digital-twin/](docs/archive/room-spatial-digital-twin/README.md) |
| 轉向前原始 README | [歷史快照](docs/archive/room-spatial-digital-twin/legacy_root_readme_2026-10-19.md) |

## 檢查／重現

```bash
python3 scripts/validate_research_openspec.py
python3 scripts/verify_thesis_results.py
python3 -m unittest discover -s tests
```

此輪僅整理研究方向、時程及歷史文件，**不改動控制實作、模擬結果、凍結 protocol 或論文數據**。後續科學方法或正式碩論章節改動，仍需遵守 [AGENTS.md](AGENTS.md) 的 OpenSpec、同步與建置規則。
