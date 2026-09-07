# Change Proposal: register-gru-lstm-pid-enclosure-directions

## Summary

將 `GRU`、`LSTM`、`PID` 與機箱／設備櫃內熱環境加入後續研究方向，但明確維持 `NOT_EVALUATED`：

1. GRU 與 LSTM 是 vanilla Elman RNN 的後續 recurrent comparator，不覆蓋既有 RNN 負向結果。
2. PID 是閉環控制 baseline，不是 3-D 場估測器；必須先有可執行 plant、setpoint trajectory、actuator 與安全限制。
3. 機箱／設備櫃是候選轉移場景；其動態負載、局部熱點與強迫對流可形成精準動態溫控需求，但現有房間模型不能直接宣稱適用。

## Why

Pure RNN 已在完整 3-D 場取得 0/24 lowest-MAE，SML2010 時序 RNN 亦為 0/12；這只能否定目前固定 Elman 設定的優勢，不能排除具有 gated memory 的 GRU 或 LSTM。另一方面，目前推薦模組仍是 model-based ranking，不是閉環控制，因此 PID 應作為未來控制比較的簡單基準。機箱／設備櫃具有負載快速變化與熱點，但尺度、風道、發熱源與量測變數均不同，必須作為新場景重新建模與驗證。

## Scope

### In scope

- 登錄 GRU/LSTM 的公平比較條件與禁止覆蓋既有負向結果的規則。
- 登錄 PID 的閉環控制 baseline 角色與必要評估指標。
- 登錄 20–30°C 內機箱／設備櫃候選場景的轉移門檻。
- 同步教授週報、論文未來工作與簡報方向。

### Out of scope

- 本次不訓練 GRU 或 LSTM，也不產生其性能數字。
- 本次不實作 PID 或聲稱閉環控制成功。
- 本次不宣稱現有房間模型已適用於機箱、資料中心或超過 30°C 的電子元件熱點。
- 不以後續架構選擇覆蓋 pure RNN 的 0/24 與 temporal RNN 的 0/12。

## Claim Impact

- Claim-neutral：新增研究計畫，不改變任何已完成結果。
- Scope-bounded：機箱僅為需要新幾何、風道、熱源與感測驗證的候選轉移場景。
- Status-explicit：四項方向均為 `NOT_EVALUATED`。

## Affected Artifacts

- `openspec/config.yaml`
- `openspec/specs/research-governance/spec.md`
- `openspec/specs/artifact-synchronization/spec.md`
- `docs/reports/professor_two_week_report_2026-08-04_2026-08-17_zh.md`
- `docs/thesis/thesis_draft_zh.md`
- `scripts/build_thesis_docx.py`
- `docs/papers/ieee/paper.tex`
- `scripts/build_thesis_pptx.py`
- Generated thesis, IEEE, and presentation outputs

## Completion Criteria

- [x] Four directions appear with `NOT_EVALUATED` status and distinct research roles.
- [x] The 20–30°C boundary and enclosure transfer gaps remain explicit.
- [x] Existing RNN negative results remain unchanged.
- [x] Applicable sources and generated artifacts are synchronized and validated.
