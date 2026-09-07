# 程式模組導覽

`digital_twin` 只放可重用的程式邏輯；一次性執行入口留在 `scripts/`。

| 模組 | 責任 |
| --- | --- |
| `core/` | 實體、sensor/node roles、情境、holdout validation、共用服務與公開資料任務對齊 |
| `physics/` | reduced-order 場模型、校正、影響學習、baseline 與動作排序 |
| `neural/` | 可選的 hybrid residual 模型 |
| `evaluation/` | E8、次日預測、pure RNN 3-D 場、時序 RNN、Kalman 與公開方法比較的可測試評估邏輯 |
| `mcp/` | MCP runtime 與 Gemma/Ollama bridge |
| `web/` | 本地 Web API、頁面與視覺化輸出 |
| `agent/` | 共用工具 runtime 包裝 |

## 依賴方向

```text
entities/scenarios
      -> physics + neural
      -> evaluation
      -> core service
      -> web / mcp / scripts
```

核心模型不應反向依賴 Web、MCP 或簡報建置程式。新的模型比較先放入 `evaluation/`，再由 `scripts/run_*.py` 提供可重現入口。

## 維護規則

- 資料結構優先共用 `core/entities.py`，避免在各 runner 重複定義。
- input、validation、target 與 pseudo roles 必須在 fitting 前分離；holdout evaluator 使用 `core/validation.py`。
- 評估切分、指標與 hash 應放在可測試模組，不只寫在腳本內。
- `physics`、`neural` 與 comparator 必須取得同一批資料與切分後才能宣稱公平比較。
- Web/MCP 只能呼叫共用 service，不另建一套研究模型。

可執行入口與驗證命令見 [`../scripts/README.md`](../scripts/README.md)。
