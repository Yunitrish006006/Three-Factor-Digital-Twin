# MPC 優先執行計劃表

日期：2026-10-05。範圍：桌機機箱探索性控制模擬；實體機箱與 E8 不列為已完成。

| 順序 | 工作 | 完成條件 | 產物 | 狀態 |
| --- | --- | --- | --- | --- |
| 1 | 方法來源與研究規格 | 固定模型、單位、horizon、限制、切分、搜尋預算及判準 | `openspec/changes/implement-enclosure-mpc-20261005/` | 完成 |
| 2 | 機箱熱模型與可重設模擬器 | CPU/GPU 溫度、PWM、RPM、負載、入口溫度可同步記錄；明確標示假設參數 | `digital_twin/control/enclosure_mpc.py` | 完成 |
| 3 | 受限制 MPC | 每步重求解並只執行第一動作；PWM、變化率、溫度與求解失敗均可稽核 | 同上與單元測試 | 完成 |
| 4 | 公平基準比較 | 固定風扇、PID、MPC 共用模型、觀测、擾動及控制限制；只在 calibration 選參數 | `scripts/run_enclosure_mpc.py` | 完成 |
| 5 | 獨立模擬驗證 | validation／holdout 各三個 seed，保存完整失敗與極端負載；重算指標與 hash | JSON、CSV、verification | 完成 |
| 6 | 報告與同步 | 更新研究待辦、第一人稱 HTML、中文論文、IEEE、既有簡報來源及適用輸出 | 報告、同步產物、檢查紀錄 | 來源與輸出已同步；Office 逐頁視覺 QA 待做 |

## 完成的定義

本階段完成是「受限制 MPC 已實作，且按固定 protocol 完成機箱假設模型的探索性模擬」，不以結果一定優於 PID 作為交付條件。溫度超限、模型失配、求解失敗、增加功耗等都保留。

參數為研究假設，不能視為實機辨識；CPU/GPU 的高溫節點與既有室內 20–30°C 估測域分開。實體 throttling、整機功耗與硬體安全證據仍為 NOT_EVALUATED。

## 後续順序

| 階段 | 工作 | 目前狀態 |
| --- | --- | --- |
| 下一階段 | LQR：相同狀態模型、Q/R、相同限制下的比較 | 待做 |
| LQR 完成後 | 固定風扇／PID／LQR／MPC 四方法統一比較 | 待做 |
| 實驗條件具備後 | 實體機箱校準、介入及獨立確認 | 待硬體與介面；NOT_EVALUATED |

## 方法來源

- [OSQP 官方 MPC 範例](https://osqp.org/docs/examples/mpc.html)：有限 horizon、狀態／輸入限制及每步只執行第一動作。
- [SciPy SLSQP 官方文件](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-slsqp.html)：本次使用的受限制數值求解器；成功旗標與限制殘差另行核對。

上述来源用於方法查證。本研究的機箱能量平衡與線性化是自行數學化整理，沒有借用文獻公式編號。

## 執行結果（2026-10-05）

MPC 核心實作與模擬完成。12 項控制單元測試、286 項 repository tests、36 回合／4,320 步的原始結果核對、75 calibration 回合的選參核對与兩個同 fixture 重現檢查均通過。holdout tracking MAE：fixed 5.4378°C、PID 2.6034°C、MPC 1.4426°C；MPC 的風扇 energy proxy 和 PWM 變化增加。

[完整 HTML](../reports/enclosure_mpc_2026-10-05_zh.html) 與 [執行證據](../../openspec/changes/implement-enclosure-mpc-20261005/evidence.md)。LQR、四方法比較和實機尚未完成。DOCX/PPTX 已依原 builder 重建並核對內容，但缺 bundled LibreOffice 與 runtime loader，逐頁視覺 QA 尚未完成，因此同步檢查仍有一個開放項目。


## 第二階段：三角色審查後完成四方法

2026-10-05 已完成 LQR、PID＋平衡點前饋與 OSQP/ZOH MPC。每方法3候選×3校準回合，36回合後凍結；正式48回合/5760步含3組未調參假設plant。獨立stdlib audit核對84回合/10080步、全指標/決策/動力方程/防覆寫來源。MPC不優於PID＋FF或LQR，H-CTRL-02/03不支持；H-CTRL-01數值健康支持。超載數值回退為零但仍超溫，不能宣稱安全或實測效益。

- [x] MPC數值問題、獨立驗證、phase防覆寫修正
- [x] LQR可達平衡點與Q/R方法整理、實作
- [x] 四方法相同候選回合預算calibration與正式比較
- [x] 獨立指標/動力/研究判準核對與篡改拒絕測試
- [x] 文稿重建與HTML/新增PDF頁QA，見本階段evidence執行紀錄
- [ ] Office全頁render QA：工作區沒有提供bundled LibreOffice/runtime loader
- [ ] 實體辨識／NTC／介入：缺量測與設備連線，NOT_EVALUATED

完整主報告：[2026-10-05教授HTML](../reports/professor_catchup_report_2026-10-05_zh.html)；[新protocol](../../openspec/changes/validate-enclosure-four-controllers-20261005/protocol.md)。舊版本LQR TODO只代表第一階段，不能當作當前狀態。
