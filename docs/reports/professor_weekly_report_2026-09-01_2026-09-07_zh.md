# 教授週報：2026-09-01 至 2026-09-07

## 本週研究重點

本週將新增的公開資料研究成果納入既有單房間稀疏感測數位孿生主線，並逐項重現其資料、模型與證據邊界。整合後的主要進展是：完成 GRU／LSTM 同資料負向比較的重現，恢復 AAU E11 系列的研究證據，並把 BMC E12–E15 整理為可追溯的資料修正與確認流程。

## 一、GRU／LSTM 同資料比較完成重現

- 比較資料固定為 SML2010 S2、四筆歷史、15／60／1,440 分鐘 horizon 與四個溫濕度 target。
- Vanilla RNN、GRU、LSTM 與三個既有比較方法共用相同 split、endpoint 與 input hash。
- GRU 與 LSTM 的 lowest-MAE 次數均為 0/12；GRU 只在 2/12 案例優於 vanilla RNN，LSTM 為 0/12。
- 中位相對 MAE 改善分別為 -12.880146% 與 -11.368865%，因此 H-RNNGATE-01 不支持，沒有候選送入完整 3-D 場比較。

## 二、AAU 機櫃空間研究證據恢復

- E11B：42 個 PT100、1,641 個一分鐘快照；最近鄰 MAE 1.175°C，優於 3-D IDW 的 1.687°C，H-ENC-02 不支持。
- E11C：local IDW 將 aggregate MAE 由 1.301°C 降至 1.223°C，但只在 21/42 感測器勝出，未達 26/42，H-ENC-03 不支持。
- E11D：角色條件模型 MAE 1.6517°C，勝出 30/42，支持角色語意具有預測資訊，但不代表氣流因果。
- E11E/E11G：平均與尾端指標有改善，但感測器覆蓋門檻未通過，均保留為開發證據。
- E11H/E11F：commissioning-assisted frozen map 在同一 AAU campaign 的 unseen bytes 上維持約 0.40°C MAE；日期與開發資料重疊，因此不能外推為跨日期、跨機箱或 NTC 硬體驗證。

## 三、BMC E12–E15 證據鏈完成整理

1. E12 在 final-test 開啟前因 6 個 development files 未達 30-row 門檻而停止，維持 `NOT_EVALUATED`。
2. E13 的輸出使用未修正的 parser／unit pipeline，保留為 `PARSER_INVALIDATED`。
3. E14A/E14B 在 31 檔、4,038 rows 上完成來源 section 與單位制度稽核；三個 raw-unit files 被正規化，八個資料品質閘門全通過。
4. E14C 回溯敏感度中，load-aware ridge 將 MAE/RMSE/P95 由 4.0882/5.2087/12.0000°C 降至 1.8054/2.8001/7.1146°C，勝出 13/14 runs，bootstrap 95% CI 為 [1.4271, 2.7939]°C。
5. E14C 的檔案先前已開啟，只能支持候選資格；E15 的另 14 個未使用檔案尚未下載與執行，維持 `NOT_EVALUATED`。

## 四、本週可報告的核心結論

本週最重要的成果不是把所有新增模型宣稱為成功，而是建立了更嚴格的證據層級：gated recurrent model 沒有超越簡單基線；AAU 的角色與 commissioning 資訊在限定條件下有預測價值；BMC 候選只有在完成 parser 與單位修正後才顯示回溯改善，而且仍需 E15 未使用檔案確認。這些結果使目前論文可以同時呈現正向、負向與尚未評估的證據，而不混淆開發、回溯分析與獨立確認。

## 下一步

- 在不更動 E15 模型、檔案清單與判準的前提下，另行決定是否執行一次未使用檔案確認。
- 若要主張實體機箱或 NTC 應用，仍需新的硬體、幾何、氣流與跨機箱 protocol；現有公開資料不能替代。
- 持續收集長期真實房間與 E8 intervention 資料，補足目前最主要的實體與因果證據缺口。
