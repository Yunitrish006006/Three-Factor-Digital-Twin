# Research OpenSpec

此目錄是論文專案的 OpenSpec source of truth。根目錄的 [`OPEN_SPEC.md`](../OPEN_SPEC.md) 只保留快速入口；正式能力、證據邊界與研究變更都在這裡。

## 結構

```text
openspec/
├── config.yaml
├── schemas/research-first/
├── specs/
├── changes/
│   ├── archive/
│   └── <active-change>/
└── README.md
```

- `specs/`：目前有效的研究與系統契約。
- `changes/`：尚未完成的研究變更；規劃完成不等於有實驗證據。
- `changes/archive/`：已完成、已同步且附實際 evidence 的變更。
- `schemas/research-first/`：研究變更的必要文件與相依順序。

## 目前能力群組

主研究規格包括：

- research governance / research contract
- room and free-space spatial models
- sparse sensing and sensing-node roles
- spatial field estimation and appliance-impact learning
- hybrid residual learning
- evaluation, evidence, reproducibility, and artifact synchronization
- action recommendation and secondary service interfaces

硬體與角色規格明確區分低成本 input-grade node 與 validation-grade node。`DHT11` 可作為輸入節點規劃，不得描述為高精度 reference；真實 holdout evaluation 必須把 validation observation 排除在 calibration、impact learning 與 model selection 之外。

## 目前進行中的變更

[`changes/stabilize-thesis-evidence/`](changes/stabilize-thesis-evidence/) 聚焦：

1. 分離 `S_input`、`S_validation`、`V_target` 與 `V_pseudo`。
2. 建立 target-point holdout 與 leakage-resistant evaluation。
3. 在相同資料及切分下比較 BasePhysics、IDW 與 proposed free-space estimators。
4. 建立 claim-to-evidence traceability，並同步論文、IEEE 稿與簡報。
5. 文件化 sensing-node、風扇條件與真實房間部署需求。

這個 change 仍是 active；未勾選工作與缺少的實驗證據不得被寫成已完成成果。

## Research-first 流程

```text
proposal
  -> research
  -> protocol
  -> delta specs
  -> design
  -> reproducibility
  -> tasks
  -> implementation / experiment
  -> evidence
  -> synchronized rebuild
  -> archive
```

穩定識別碼使用 `RQ`、`H`、`EQ`、`CLM`、`E`，以及 capability-scoped requirement ID。Requirement ID 必須在 `openspec/specs/` 中保持唯一。

## 建立與關閉變更

以 OpenSpec CLI 建立：

```bash
openspec new change <kebab-case-name>
openspec status --change <kebab-case-name>
```

沒有 CLI 時，可從 `schemas/research-first/templates/` 複製模板。只有在 tasks、實際 evidence、claim decision、測試、同步重建與 stale-text 搜尋全部完成後，才能移入 `changes/archive/YYYY-MM-DD-<change-name>/`。

## 驗證

```bash
python3 scripts/validate_research_openspec.py
python3 scripts/verify_thesis_results.py
python3 -m unittest discover -s tests
```

若 OpenSpec CLI 可用，再執行：

```bash
openspec schema validate research-first
openspec validate --all
```
