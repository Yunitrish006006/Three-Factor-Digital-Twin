# OpenSpec 研究規格導覽

此目錄是 Three-Factor Digital Twin 的 OpenSpec source of truth，用來區分：

- `specs/`：目前已成立的研究與系統行為
- `changes/`：準備實作或驗證的研究變更

根目錄既有的 `OPEN_SPEC.md` 是專案總覽文件；本目錄則遵循 Fission-AI OpenSpec 的 `config + specs + changes` 結構，供後續 agent 依 proposal、specs、design、tasks 執行。

## Current specs

- `specs/research-contract/spec.md`
  - 研究範圍、方法角色、控制推薦與完成狀態
- `specs/spatial-estimation/spec.md`
  - 三因子主模型、家具感知感測器配置、校正與 baseline
- `specs/evidence-and-artifacts/spec.md`
  - 證據分層、資料切分、可重現性與論文產物同步

## Active change

`changes/stabilize-thesis-evidence/`

目標是先解決口試最關鍵的三個風險：

1. 分離 `S_input` 與 `S_validation`，避免 target-point leakage。
2. 在同一介面與 split 下比較 BasePhysics、IDW 與 free-space estimators。
3. 建立 claim-to-evidence matrix，同步論文、IEEE 稿、簡報、圖表與結果檔。

閱讀順序：

1. `proposal.md`：為什麼現在要做
2. `specs/*/spec.md`：行為與驗收條件如何改變
3. `design.md`：資料角色、估計器介面與實驗設計
4. `tasks.md`：實作與研究待辦

## OpenSpec commands

安裝 OpenSpec 後，可在 repository root 執行：

```bash
openspec status --change stabilize-thesis-evidence
openspec validate stabilize-thesis-evidence --strict
```

在支援 OpenSpec slash commands 的 coding agent 中，可依序使用：

```text
/opsx:explore
/opsx:apply
/opsx:archive
```

在所有 tasks 完成、輸出證據齊全並同步論文產物後，才 archive 此 change。
