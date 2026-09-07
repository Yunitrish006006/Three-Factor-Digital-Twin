# Change Proposal: execute-equipment-enclosure-transfer

## Summary

啟動機箱／設備櫃轉移研究的第一個可執行階段 `E11A`：以公開 BMC 時序資料比較 persistence、一般線性 readout 與具有進出口溫差、設備功率和風扇對流項的 thermal-balance readout。研究先限於 `20–30 °C` air-state prediction，不把房間證據、CPU 熱點或 PID 控制效果混入機箱適用性主張。

## Why

目前機箱方向只有 `NOT_EVALUATED` 登錄，尚無資料契約、可執行 baseline 或 leakage-resistant protocol。公開 BMC 資料已包含 inlet/outlet temperature、fan speed、PSU power、workload 與固定 PWM/PID trace，適合先回答時序轉移問題；AAU 3-D server-room 資料則保留給後續空間熱場階段。

## Change Map

### Equipment-enclosure transfer

- **From:** 僅登錄為未評估的未來方向。
- **To:** 具有預註冊 protocol、公開資料 adapter、三個同資料 comparator 與機器可讀輸出契約。
- **Reason:** 在討論 GRU/LSTM 或 PID 前，先建立簡單、可解釋且可否證的機箱 baseline。
- **Impact:** 非破壞性；不改變既有房間結果或目前論文 claim。

## Scope

### In scope

- 解析 arealuser/bmcdata 的 InfluxDB-style CSV。
- 預測下一個有效時間點的 `Outlet_Temp`。
- 使用 chronological 60/20/20 train/validation/test split。
- 比較 persistence、linear readout 與 thermal-balance readout。
- 保存資料範圍排除、缺值、gap、adverse case 與 provenance。

### Out of scope

- 不下載或提交大型原始資料。
- 不執行或比較 PID、TEAP、GRU 或 LSTM 控制效果。
- 不宣稱完成 3-D 機箱熱場重建、CFD 驗證或元件溫度預測。
- 不把 `Outlet_Temp` 結果外推到 CPU/GPU hotspot 或 30 °C 以上情境。

## Research and Claim Impact

| ID | Current status | Intended effect | Evidence needed |
| --- | --- | --- | --- |
| `RQ-ENC-01` | `NOT_EVALUATED` | 判斷 reduced-order thermal terms 是否在公開 BMC trace 優於 persistence | 原始 trace、同列 split 與 test metrics |
| `H-ENC-01` | `NOT_EVALUATED` | 可能建立 bounded public-task evidence | 至少三個合格 trace 的預註冊執行 |
| `CLM-ENC-01` | 不存在 | 僅允許公開資料時序 task claim | 可重現 JSON 與 adverse cases |

## Affected Capabilities and Artifacts

- Current specs: `research-governance`, new `equipment-enclosure-transfer` delta。
- Code and tests: `digital_twin/enclosure/`, `scripts/run_enclosure_bmc_baseline.py`, `tests/test_enclosure_bmc_baseline.py`。
- Data and evidence: local-only BMC CSV；planned `outputs/data/enclosure/enclosure_bmc_baseline.json`。
- Chinese thesis: actual evidence accepted 後才同步。
- English IEEE paper: actual evidence accepted 後才同步。
- Presentation: actual evidence accepted 後才同步。
- Figures and generated outputs: 本階段無圖；有 claim 變動時依 root `AGENTS.md` 全部重建。

## Risks and Rollback

- Risks: dataset traces 的控制模式、工作負載、cadence 與裝置可能不平衡；公開資料缺少完整 3-D 機箱幾何。
- Stop or rollback condition: 少於三個 in-scope trace、欄位語意不一致、split contamination，或目標溫度超出 20–30 °C 時，維持 `NOT_EVALUATED` 並保留失敗結果。

## Completion Criteria

- [x] At least three eligible traces are executed under the registered protocol.
- [x] Machine-readable evidence records all exclusions and adverse cases.
- [x] Every hypothesis and claim receives an evidence decision.
- [ ] Applicable thesis, IEEE, presentation, and generated outputs are synchronized.
