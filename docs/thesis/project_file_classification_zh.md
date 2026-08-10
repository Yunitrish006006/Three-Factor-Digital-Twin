# 專案檔案角色與正式來源

本文件取代容易過期的「逐檔掃描清單」。需要找檔案時，依角色與正式來源定位；實際檔名以 repository 當下內容為準。

## 一、正式來源

| 產物 | 唯一正式來源 | 產生／驗證方式 |
| --- | --- | --- |
| 中文論文內容 | `docs/thesis/thesis_draft_zh.md`、`scripts/build_thesis_docx.py` | `build_thesis_docx.py`、`build_thesis_pdf.py` |
| 英文 IEEE 稿 | `docs/papers/ieee/paper.tex`、`references.bib` | `tectonic paper.tex` |
| 簡報 | `scripts/build_thesis_pptx.py`、兩份 presentation outline | `build_thesis_pptx.py` |
| 架構圖 | `scripts/build_architecture_diagrams.py`、`system_architecture_diagrams_zh.md` | `build_architecture_diagrams.py` |
| 研究契約 | `openspec/specs/` | `validate_research_openspec.py` |
| 實驗證據 | 實驗 runner、result JSON、OpenSpec evidence | `verify_thesis_results.py`、tests |

不要直接修改 DOCX、PDF、PPTX 或自動產生的圖來取代來源修改。

## 二、程式角色

- `digital_twin/`：可重用的模型、評估與服務程式。
- `scripts/`：實驗、驗證、資料準備與建置入口。
- `tests/`：單元測試及研究行為檢查。
- `pyproject.toml`：Python 專案基本中繼資訊。

詳細模組與腳本用途分別見 `digital_twin/README.md` 與 `scripts/README.md`。

## 三、文件角色

- `docs/reports/`：教授版週報、完整實驗總覽與內部進度。
- `docs/thesis/`：中文論文及簡報主線。
- `docs/experiments/`：實驗協定、結果與驗證說明。
- `docs/models/`：模型設計與文獻判讀。
- `docs/research/`：研究範圍與教授方向。
- `docs/hardware/`：input-grade、validation-grade 節點與部署規劃。
- `docs/requirements/`、`docs/templates/`：資料與房間設計契約。
- `docs/mcp/`、`docs/web/`：次要服務與展示文件。
- `docs/archive/`：非目前論文主線的歷史或課程材料。

## 四、輸出與外部資料

- `outputs/data/`：實驗 JSON/CSV、原始公開資料與正規化中介檔。
- `outputs/figures/`：可重建視覺化。
- `outputs/papers/`：正式 DOCX、PDF、PPTX 交付檔。
- `docs/papers/reference_sources/`：外部論文及文字轉錄，不是本研究證據。

大型 `outputs/` 預設不進版本控制。刪除本地 raw data 前必須先確認是否可重新下載，以及相關結果是否已有重現資訊。

## 五、不應保留的平行版本

以下檔名模式容易造成正式來源不明，不再新增：

- `*_updated.*`
- `*_final_v2.*`
- `*_agent.*`
- 同內容只改中文／英文檔名的重複圖片

需要修改正式產物時，更新 canonical builder；需要保存歷史材料時，移至 `docs/archive/` 並補一份簡短 README。

## 六、快取與中繼檔

下列檔案不屬於研究成果，應由 `.gitignore` 排除：

- `.DS_Store`
- `__pycache__/`、`*.pyc`、`.pytest_cache/`
- LaTeX `*.aux`、`*.log`、`*.bbl`、`*.blg`、`*.out`
- Quick Look 暫存目錄

整理檔案時不得刪除 OpenSpec evidence、原始量測、已登錄結果 JSON 或 AGENTS.md 指定的正式交付成品。
