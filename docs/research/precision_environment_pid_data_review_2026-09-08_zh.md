# 精密環境快速調適：文獻與資料可用性初查

日期：2026-09-08。狀態：LITERATURE_CANDIDATE / NOT_EVALUATED。這是探索性查核，未新增主論文方法、控制結果或半導體適用性主張，未下載大型資料或啟動模型訓練。

## 結論

無塵室自動調參與現場辨識有既有研究，但本輪未找到可直接驗證「EUV 換地區後，溫濕度 PID 調適所需時間」的公開資料。不能由無塵室穩定環境需求推論 EUV 必須在不同國家人工重調 PID。

較可行的候選問題是：在相同控制品質要求下，換邊界條件或設備特性後，能否縮短校正／調參所需的實驗時間？固定設定值是合理目標；需要比較的是調適成本，而非要求動態配方。所有離線模擬、一般熱控制平台及真實無塵室證據必須分開。

## 已有方法與需求證據

| ID | 來源 | 可支持的內容 | 限制 |
| --- | --- | --- | --- |
| PRE-LIT-01 | [Auto-tuned variable structure control of cleanrooms, 1998](https://pure.uj.ac.za/en/publications/auto-tuned-variable-structure-control-of-cleanrooms/)，DOI 10.1016/S0019-0578(98)00029-9 | 作者機構摘要：以 modified relay feedback 在閉迴路加入受控擾動、自動辨識後設計 variable structure controller | 無塵室溫度自動調適不是新概念；不是 EUV 或新方法的調整時間實驗 |
| PRE-LIT-02 | [Multivariable Model Predictive Control of Cleanroom Pressure Cascades, 2025](https://www.mdpi.com/2079-9292/14/16/3296) | 出版社索引說明 commissioning 的 trial-and-error、系統辨識及試驗平台；原 PID 可在無擾動時穩定 | 主問題是壓差串級，不能當作溫濕度調參工時證據。全文存取受限，原始資料下載與授權未確認 |
| PRE-LIT-03 | [Safe Contextual Bayesian Optimization for Sustainable Room Temperature PID Control Tuning, 2019](https://arxiv.org/pdf/1906.12086) | §4–5、§7.3：外溫作 context，自動調 PI 參數，涉及 commissioning | 一般房間研究，不是半導體設備；不能宣稱環境條件化 PID 首創 |
| PRE-LIT-04 | [imec cleanroom introduction](https://www.imec-int.com/en/semiconductor-education-and-workforce-development/microchips/how-are-microchips-made/cleanroom) | 說明穩定溫濕度需求，舉通常 20–22°C | 不是特定機台允收規格，更不提供可直接使用的公差 |
| PRE-LIT-05 | [ASML EUV lab-to-fab](https://www.asml.com/en/company/stories/2022/making-euv-lab-to-fab) | EUV 光路需真空 | 不能將 EUV 真空機內環境視為一般恆溫恆濕空氣箱 |

## 資料／平台候選（必須區分種類）

### PRE-DATA-01：TCLab 實測步階資料 — 可讀，僅適合初步動態辨識

- [原始文字檔](https://apmonitor.com/do/uploads/Main/tclab_dyn_data2.txt)、[官方建模範例](https://apmonitor.com/do/index.php/Main/TCLabA)。本輪已開啟原始檔：Time,H1,H2,T1,T2；開頭時間間隔為 1，Time=10 時 H1 由 0 變 80，有可觀察的加熱指令與後續溫度反應。
- 這比只有溫度／濕度的資料更接近控制導向辨識，但一條既定動作軌跡不能回放成任意新控制器的反事實效果，也不提供人工作業工時。
- 原始檔起始 T1/T2 約 19.29/18.32°C，已不全在原 20–30°C 空氣溫域；平台量的是加熱系統溫度，不是完整空氣溫濕度。需另立任務，不截段後宣稱全域相容。
- [TCLab 軟體](https://github.com/jckantor/TCLab)標示 Apache-2.0，包含資料記錄與 TCLabModel 離線模擬。軟體授權不能自動套到 APMonitor 網站的獨立資料檔；後者明確資料授權本輪未確認，不直接再散布。

### PRE-DATA-02：BOPTEST — 優先考慮的互動控制模擬平台，不是真實資料集

- [官方介紹](https://ibpsa.github.io/project1-boptest/index.html)、[測試案例](https://ibpsa.github.io/project1-boptest/testcases/)、[DOE 說明](https://www.energy.gov/cmei/buildings/boptest-building-operations-testing-framework)。提供建築/HVAC 模型、天氣、既有控制與 API，可施加新控制動作並取得模擬反應。
- 可規劃相同條件下不同調參程序的比較；若做環境／設備轉移，必須固定哪些條件改變、另留測試案例，不把不同 HVAC 架構誤稱同設備跨地區。
- [授權原文](https://raw.githubusercontent.com/ibpsa/project1-boptest/master/license.md)：revised 3-clause BSD 加附加段落，另列相依軟體條款。正式使用需鎖定版本及案例／資料來源。
- 需逐案例核對濕度狀態、加濕／除濕致動器與 override 介面；目前不承諾任一案例可完整驗證雙變數控制。亦未安裝或執行，不能報已可重現的控制成績。
- 只能支持一般 HVAC 模擬調適，不能直接支持 EUV、半導體無塵室精度或現場人工工時節省。

### PRE-DATA-03：SECOM — 半導體資料，但排除為本題主資料

- [UCI 官方資料](https://archive.ics.uci.edu/dataset/179/secom)：1,567 個生產實體，製程量測特徵及 pass/fail 標籤，含缺值；官方頁標示 CC BY 4.0。
- 目標是品質分類與特徵選擇，官方內容沒有提供本題所需的具名 PID 係數、設定值、連續致動器反應與重新調參工時。因此不能因為來自半導體就當作溫濕度控制資料。

### PRE-PLATFORM-04：OpenHumidistat — 自建濕度實驗的備案

- [作者論文](https://arxiv.org/abs/2112.08500)：以乾／濕氣流混合及感測回授控制實驗腔濕度，提出開源裝置。
- 是硬體／方法來源，不是本輪已取得的標準資料集，也不是完整溫濕度雙變數平台。摘要的原發表成本不作目前台灣採購報價。
- 本輪僅核對摘要；組裝檔案、各部分授權、元件與適用 RH 範圍仍需查核。

## 最小可驗證問題

1. 先比較固定原 PID、既有自動調參、物理辨識調參；只有簡單方法不足，再加入小型神經網路。
2. 預先設定相同容許帶、超限上限、驗證負載與連續達標規則；不得事後挑有利時間窗。
3. 成本分開報：取得辨識資料的過程時間、計算牆鐘時間、介入次數與人工操作時間。加速模擬秒數不能當作真實人工工時。
4. 新條件下校正結束後，另用未參與調整的擾動驗證品質。時間終點為「完成調整並通過獨立驗證的成本」，不是只有單次升溫到目標的時間。
5. 暫不採用 EUV 為已驗證應用名稱；若拿不到機台環境與調適資料，使用「精密環境控制快速調適的原理驗證」，產業需求列動機，實驗平台如實列名。

目前決策：TCLab 適合辨識起步；BOPTEST 適合可重複的閉迴路方法比較；SECOM 不適合本題。半導體真實調適資料仍未找到可直接使用的版本。這是有限搜尋結果，不代表此類資料不存在。
