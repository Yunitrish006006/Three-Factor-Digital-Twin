# Design

依既有 protocol 與實際產物補齊研究規格，不新增或重跑實驗。介面契約測試由 `run_parameter_tuning_contract_test.mjs` 實作；TCLab simulation 由 `run_tclab_simulation_pilot.py` 保存候選、切分與重現檢查；BOPTEST locked runner 只使用先前選出的 PI，禁止搜尋。

`validate_parameter_tuning_artifact.mjs` 檢查 artifact 必要欄位、獨立切分與 gate。舊 `validator_report.json` 對照的是 development audit；後續 Linux holdout 另存 artifact，不能覆寫早期失敗或把舊日期重新標為 holdout。E8 與真實介入仍 NOT_EVALUATED。
