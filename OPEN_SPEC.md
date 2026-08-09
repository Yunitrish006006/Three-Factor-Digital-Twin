# OpenSpec 快速入口

本檔只保留相容性導覽；正式研究規格的唯一來源是 [`openspec/`](openspec/README.md)。

## 目前應讀的檔案

- [`openspec/config.yaml`](openspec/config.yaml)：專案研究範圍、同步與證據規則。
- [`openspec/specs/`](openspec/specs/)：目前有效的研究與系統能力契約。
- [`openspec/changes/`](openspec/changes/)：進行中的研究變更。
- [`openspec/changes/archive/`](openspec/changes/archive/)：已完成且有證據的歷史變更。
- [`openspec/schemas/research-first/`](openspec/schemas/research-first/)：研究變更模板與相依順序。

## 研究變更流程

```text
proposal -> research -> protocol -> delta specs -> design
         -> reproducibility -> tasks -> implementation/experiment
         -> evidence -> synchronized rebuild -> archive
```

`evidence.md` 只能記錄實際執行結果；預期結果、缺失資料與未評估項目不得改寫成已完成證據。

## 驗證

```bash
python3 scripts/validate_research_openspec.py
python3 scripts/verify_thesis_results.py
python3 -m unittest discover -s tests
```

程式、文件與檔案角色請分別查看 [`digital_twin/README.md`](digital_twin/README.md)、[`docs/README.md`](docs/README.md) 與 [`scripts/README.md`](scripts/README.md)。
