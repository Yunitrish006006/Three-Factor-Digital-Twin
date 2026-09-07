# 機箱／設備櫃熱環境文獻與資料來源

## 研究切入點

第一階段應先做「公開 BMC air-state 時序轉移」，再做「具幾何與 airflow 的空間轉移」，最後才評估 PID 或其他閉環控制。這個順序能把估測、空間重建與控制分開驗證。

## 優先文獻

| 來源 | 可借用方法 | 本專案限制 |
| --- | --- | --- |
| Wang et al., *Model and data driven transient thermal system modelings for contained data centers*, 2022, DOI `10.1016/j.enbuild.2021.111790` | lumped-capacitance ODE 與 multivariate LSTM 的同場比較 | 原文結果不能直接當成本專案證據 |
| Tong et al., *A time-varying state-space model for real-time temperature predictions in rack-based cooling data centers*, 2023, DOI `10.1016/j.applthermaleng.2023.120737` | control-oriented state-space、recirculation 與 bypass | rack-based model 不等於單機箱模型 |
| Melgaard et al., *Energy efficiency enhancement in two European data centers through CFD modeling*, 2025, DOI `10.1038/s41598-025-11048-0` | 量測不確定度、inlet/outlet sensor、airflow 與 CFD validation | 場景尺度較大，需另做 spatial transfer contract |
| Zhang et al., *Thermal Elasticity-Aware Host Resource Provision for Carbon Efficiency on Virtualized Servers*, 2025, DOI `10.1109/TC.2025.3603698` | BMC telemetry、工作負載、fan mode 與熱管理 | 控制策略比較須另行預註冊 |

## 候選資料庫

| 優先度 | 資料集 | 內容與用途 | 注意事項 |
| --- | --- | --- | --- |
| 1 | `https://github.com/arealuser/bmcdata` | inlet/outlet、CPU、fan、PSU power、workload 與 PWM/PID traces；適合 `E11A` | MIT；需記錄 commit 與逐檔 checksum；PID 35 °C traces 可能超出目前 air-state 範圍 |
| 2 | `https://doi.org/10.5281/zenodo.19398358` | AAU v4，3-D geometry、air temperature、air speed、server power，1–10 秒量測；適合 `E11B` | 約 757 MB；是 server-room/rack 空間資料，不是 dense single-enclosure truth |
| 3 | `https://doi.org/10.5281/zenodo.10050368` | 3312 nodes 的 inlet/outlet 與 power，2019 全年；適合 large-scale robustness 或 hazard task | 約 1 GB；缺少 fan 與單機箱幾何，不適合第一個 thermal-balance 主實驗 |
| 4 | `https://doi.org/10.1016/j.dib.2022.108587` | air-cooled data center 的實驗與 OpenFOAM thermal/flow distributions | 需先確認下載格式、license 與量測點可映射性 |

## 採用決策

- `E11A`：先使用 BMC dataset，比較 persistence、linear readout、thermal-balance readout。
- `E11B`：另開 OpenSpec，使用 AAU 幾何、溫度、風速與功率資料驗證空間 transfer。
- `E11C`：只有在 plant、setpoint、actuator、disturbance 與安全限制固定後，才比較 PID 與其他 controller。
- GRU/LSTM 必須使用與 `E11A` 相同 endpoints，且不可用 test set 選 architecture。
