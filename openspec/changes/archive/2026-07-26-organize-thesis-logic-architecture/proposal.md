# Change Proposal: organize-thesis-logic-architecture

## Summary

建立一張跨越「研究缺口、研究問題、方法、驗證與結論邊界」的論文整體邏輯架構圖，補足目前圖 3-1 只描述系統責任分層、尚未直接呈現整篇論文論證鏈的缺口。

## Why

目前架構圖能說明系統由情境觀測、估測學習、服務決策三層組成，但讀者仍需自行把 RQ1--RQ4、方法模組、E1--E9 與可下結論串起來。口試與投稿情境需要一張先行總覽，讓後續章節與圖表都有共同主線。

## Change Map

### 論文整體邏輯總覽

- **From:** 圖 3-1 從系統責任域開始，沒有直接畫出研究問題與證據鏈。
- **To:** 新增「研究整體邏輯架構圖」，明確連結研究限制、RQ1--RQ4、方法核心、分層驗證與 claim boundary。
- **Reason:** 降低讀者在緒論、方法與實驗章之間自行拼接邏輯的負擔。
- **Impact:** 非破壞性；不新增方法、數據或主張，但會更新論文、IEEE 稿、簡報、圖表來源與生成輸出。

## Scope

### In scope

- 新增研究邏輯架構 Mermaid 語意來源與 16:9 SVG renderer。
- 在中文論文緒論、英文 IEEE 稿與兩版簡報中使用一致的總覽。
- 保留既有系統分層圖與執行資料流作為方法層細化圖。
- 重建並視覺驗證 SVG、DOCX、PDF、PPTX 與 IEEE PDF。

### Out of scope

- 不改變 RQ、方法公式、實驗數字或結論強度。
- 不把 E8 從 protocol-only 改成已完成證據。
- 不重新設計所有既有架構圖。

## Research and Claim Impact

| ID | Current status | Intended effect | Evidence needed |
| --- | --- | --- | --- |
| `RQ1`--`RQ4` | 已定義 | 中立；改善對應關係可讀性 | 圖中文字與現有來源一致 |
| `E1`--`E9` | 分層證據 | 中立；改善證據鏈可讀性 | 圖與驗證規格一致 |
| `CLM-ARCH-01` | 新增呈現契約 | 不增加 claim strength | 同步與視覺 QA |

## Affected Capabilities and Artifacts

- Current specs: `artifact-synchronization`
- Code and tests: `scripts/build_architecture_diagrams.py`, architecture tests
- Data and evidence: 無新實驗資料
- Chinese thesis: Markdown、DOCX builder、DOCX/PDF outputs
- English IEEE paper: `paper.tex` 與 `paper.pdf`
- Presentation: PPTX builder、兩版 outline、兩個 PPTX outputs
- Figures and generated outputs: `outputs/figures/architecture/`、thesis PNG assets

## Risks and Rollback

- Risks: 圖中文字過密、章節編號變動、PDF 或投影片縮放後不可讀。
- Stop or rollback condition: 圖在論文寬度或投影片半頁尺寸下無法清楚閱讀，或同步建置出現無法修復的版面問題。

## Completion Criteria

- [x] 圖中每條主線都能追溯到現有 RQ、方法與證據項目。
- [x] 中文論文、IEEE 稿與簡報使用一致的邏輯與 claim boundary。
- [x] 所有適用輸出重建並通過視覺 QA。
- [x] OpenSpec、測試與結果驗證通過。
