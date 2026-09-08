# Single-Room Sparse-Sensing Spatial Digital Twin

本專案是單房間空間數位孿生的 Python 研究原型。核心問題是在只有少量角落感測器、設備本身沒有遙測介面的條件下，估計房內的溫度、相對濕度與照度，並學習冷氣、窗戶及照明對環境的影響。

目前研究邊界如下：

- 單一房間、8 顆角落感測器、三因子空間場。
- 物理啟發的 reduced-order model 是主模型；稀疏校正與 hybrid residual 是後續修正層。
- 目前溫度研究範圍限定在 `20–30 °C`。
- Web 與 MCP 是展示／服務層，不是主要科學貢獻。
- E8 真實介入尚未完成，不把反事實推薦寫成已證實的控制效益。

## 從哪裡開始

目前接續研究的應用方向是**電腦機箱稀疏測溫與虛擬感測**，先以公開伺服器資料驗證方法，再銜接桌機機箱 NTC 多點量測。2026-09-07 的 E15 已完成一次性凍結確認：14 檔、3,112 rows，MAE 1.6939→0.9744°C，12/14 runs 勝出，10 個閘門全部通過。這只支持同一伺服器的時間／工作負載轉移；桌機機箱、NTC、完整空間場及跨伺服器仍未驗證。完整紀錄見 [`E15 evidence`](openspec/changes/confirm-bmc-temporal-transfer-e15/evidence.md)。

| 需求 | 入口 |
| --- | --- |
| 查看教授版進度與完整實驗 | [`docs/reports/`](docs/reports/) |
| 開啟兩週教授成果與 Demo 指南 | [`docs/reports/professor_two_week_report_2026-08-04_2026-08-17_zh.md`](docs/reports/professor_two_week_report_2026-08-04_2026-08-17_zh.md)／[`docs/demos/professor_demo_guide_2026-08-17_zh.md`](docs/demos/professor_demo_guide_2026-08-17_zh.md) |
| 閱讀中文論文主線 | [`docs/thesis/README.md`](docs/thesis/README.md) |
| 找研究、模型或實驗文件 | [`docs/README.md`](docs/README.md) |
| 查看感測節點與驗證級硬體 | [`docs/hardware/README.md`](docs/hardware/README.md) |
| 理解程式模組 | [`digital_twin/README.md`](digital_twin/README.md) |
| 找可執行腳本 | [`scripts/README.md`](scripts/README.md) |
| 查看研究規格與變更流程 | [`openspec/README.md`](openspec/README.md) |

## 快速驗證

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[research,artifacts]"
.venv/bin/python scripts/validate_research_openspec.py
.venv/bin/python scripts/verify_thesis_results.py
.venv/bin/python -m unittest discover -s tests
```

`verify_thesis_results.py` 在任何 `FAIL` 或 `MISSING` 時會以非零狀態結束；乾淨 clone 必須先依報告中的 `suggested_script` 重建被忽略的 `outputs/data/` 證據。

執行完整研究實驗：

```bash
python3 scripts/run_all_thesis_experiments.py
```

執行 input／validation 角色分離的受控 holdout 檢查：

```bash
python3 scripts/run_target_holdout_validation.py
python3 scripts/run_kalman_filter_comparison.py
```

執行本地展示：

```bash
python3 scripts/run_demo.py
python3 scripts/build_professor_demo.py
python3 scripts/run_web_demo.py
```

## 專案結構

```text
digital_twin/   可重用的模型、評估與服務程式碼
scripts/        實驗、驗證、建置與展示入口
tests/          單元測試與研究行為檢查
docs/           論文、實驗、模型、報告與規格說明
openspec/       研究能力契約、變更與證據治理
outputs/        可重建輸出、公開資料中介檔與本地原始資料
```

`outputs/` 預設不納入版本控制；大型公開資料與正規化中介檔維持本地保存。正式論文成品依 [`AGENTS.md`](AGENTS.md) 的同步規則重建。

## 常用工作流程

研究變更依序進行：

```text
OpenSpec proposal/protocol
  -> 實作與實驗
  -> actual evidence
  -> 論文／IEEE／簡報同步
  -> 重建與驗證
  -> archive
```

重建正式文件：

```bash
python3 scripts/build_architecture_diagrams.py
python3 scripts/build_thesis_docx.py
python3 scripts/build_thesis_pdf.py
python3 scripts/build_thesis_pptx.py
cd docs/papers/ieee && tectonic --keep-logs --keep-intermediates paper.tex
```

房間設計必須符合 [`docs/requirements/room_design_format_requirements_zh.md`](docs/requirements/room_design_format_requirements_zh.md)，並以 [`docs/templates/room_design_template.json`](docs/templates/room_design_template.json) 建立。

## 維護原則

- 正式來源只維護一份；產生檔由指定 builder 重建。
- 模擬、真實房間快照、公開 task-aligned benchmark 與真實介入證據分開陳述。
- 不新增 `final_v2`、`new_updated`、`agent_version` 等平行版本；需要保留的歷史材料移至 `docs/archive/`。
- 任何研究方法、數字或結論變更，都要遵守 [`AGENTS.md`](AGENTS.md) 的同步範圍。

- [本週研究進度與報告入口（2026-09-08）](docs/reports/weekly_progress_2026-09-08_zh.html)
