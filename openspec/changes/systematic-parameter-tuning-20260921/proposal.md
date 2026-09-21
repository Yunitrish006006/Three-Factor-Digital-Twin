# Proposal

教授要求參數調教具備系統性；目前的 API 探索若沒有固定切分、搜尋預算與停止規則，容易把試到的最好結果誤當成證據。本 change 將候選平台比較與參數調教拆成可重現的 protocol，先驗證介面與資料紀錄，再產出小型 pilot。

## Scope

- 比較 BOPTEST、TCLab、OpenHumidistat、SECOM 的可互動性與證據邊界。
- 固定 calibration／validation／holdout、參數層級、搜尋與 tie-break 規則。
- 每次 run 保存設定、trace、指標與 hash；失敗也保存原因。

## Non-goals

- 不重跑 E15。
- 不把模擬結果寫成真實設備控制或因果證據。
- 不在今天宣稱任何應用已通過 intervention。
