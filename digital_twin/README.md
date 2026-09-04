# 程式模組導覽

`digital_twin` 只放可重用的程式邏輯；一次性執行入口留在 `scripts/`。

| 模組 | 責任 |
| --- | --- |
| `core/` | 實體、sensor/node roles、情境、holdout validation、共用服務與公開資料任務對齊 |
| `physics/` | reduced-order 場模型、校正、影響學習、baseline 與動作排序 |
| `neural/` | 可選的 hybrid residual 模型 |
| `evaluation/` | E8、次日預測、RNN 與公開方法比較的可測試評估邏輯 |
| `research/` | Adaptive Orchestration、研究角色、paper/evidence/claim registry、review gate 與 replay |
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

research task
      -> research/orchestration
      -> research/store + validators
      -> scripts/runtime adapters
```

研究流程核心不依賴 Web/MCP，也不把 agent prose 當成 evidence truth。Estimator 與 research orchestration 共享專案治理，但彼此不應形成反向依賴。

## 維護規則

- 資料結構優先共用 `core/entities.py`，避免在各 runner 重複定義。
- input、validation、target 與 pseudo roles 必須在 fitting 前分離；holdout evaluator 使用 `core/validation.py`。
- 評估切分、指標與 hash 應放在可測試模組，不只寫在腳本內。
- `physics`、`neural` 與 comparator 必須取得同一批資料與切分後才能宣稱公平比較。
- Research claim 必須引用 registered evidence；contradiction 不得從 synthesis state 靜默消失。
- Web/MCP 只能呼叫共用 service，不另建一套研究模型。

Research Adaptive Orchestration 架構見 [`../docs/research_orchestration/ARCHITECTURE.md`](../docs/research_orchestration/ARCHITECTURE.md)。可執行入口與驗證命令見 [`../scripts/README.md`](../scripts/README.md)。
