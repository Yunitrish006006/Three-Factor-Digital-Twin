# 機箱溫控方向：可移植文獻方法與使用順序

日期：2026-09-08。狀態：`LITERATURE_CANDIDATE`。本次完成文獻篩選及移植設計建議，尚未實作、執行新實驗、納入正式論文方法或更新 3D 圖的已採用方法。

## 選擇結論

優先採「有時間記憶的熱模型 → 工作負載前饋與風扇功率量測 → 有限制的控制比較」，再評估物理一致神經網路及多風扇協調。

目前 [E15](../../openspec/changes/confirm-bmc-temporal-transfer-e15/evidence.md) 的 frozen ridge 已完成同伺服器虛擬感測確認；它不等於已辨識風扇動作對未來溫度的因果響應。機箱溫控適用度應分別檢查：溫度預測、工作負載變化、感測點與風道差異、控制效果、跨機箱轉移。

下列「原文方法」依出版社、作者公開 PDF 或原文索引內容整理；「機箱移植」與優先順序是針對本專案的建議，不是原文已替桌機驗證的結論。並未確認五篇都有可直接執行的公開程式碼。

## 五篇候選論文

### ENC-LIT-01：ARX 動態模型與 model predictive control

**Nevena Lazic et al. (2018), Data center cooling using model-predictive control. NeurIPS 2018.**

[會議原文 PDF](https://papers.neurips.cc/paper_files/paper/2018/file/059fdcd96baeb75112f09fa1dcc740cc-Paper.pdf)

- 原文定位：§4.1、Eq. (1)、Table 1（PDF 第 4 頁）；§4.2 與 §5.1（PDF 第 5–6 頁）。已取得 PDF 文字。
- 原文方法：用 ARX 表達歷史狀態、控制輸入及擾動，先辨識再作滾動預測控制；原文也比較刻意激勵與既有 PID 紀錄的辨識效果。
- 機箱移植：輸入改為歷史溫度、風扇 PWM／RPM、CPU／GPU 功率及入口溫度，預測負載或轉速改變後的溫度軌跡。
- 建議用途：**第一優先的動態預測 baseline**。先在現有 development traces 檢查取樣時間與變化量；不足以辨識風扇效果時，需新增受控動作資料。
- 限制：原文為機房 AHU 控制。移植到桌機需要重新辨識，原文節能結果不能直接沿用。
- 主稿對應：§3.3 溫度模型、§3.9 控制排序、§5.9.3.4／§5.9.3.7 機箱比較；尚未加入這些章節。

### ENC-LIT-02：工作負載感知風扇策略與預測誤差裕量

**Jinzhu Chen, Rui Tan, Guoliang Xing, Xiaorui Wang (2014), PTEC: A System for Predictive Thermal and Energy Control in Data Centers.**

[作者公開 PDF](https://personal.ntu.edu.sg/tanrui/pub/control-rtss14.pdf)

- 原文定位：§IV-A 風扇功率模型、§V-A／Eq. (2) 溫度限制與誤差分布（PDF 第 3–4 頁）、§V-C Dynamic Fan Speed Control（PDF 第 5 頁起）。已取得 PDF 文字。
- 原文方法：風扇策略同時考慮入口溫度與 CPU 負載，預測控制則把溫度上限與預測誤差納入限制。
- 機箱移植：增加工作負載前饋，避免只等高溫才升轉速；依開發／校正資料估計的誤差保留溫度裕量，並實测整機及風扇耗電。
- 建議用途：**第一優先的控制設計參考**，可與簡單 PID 組成容易解釋的對照策略。
- 限制：原文協調 CRAC 與伺服器風扇；本案只移植機箱部分。原文的誤差分布假設須重新檢查，不能將裕量視為必然安全保證。
- 主稿對應：§3.9 控制排序、機箱實驗與第六章限制。

### ENC-LIT-03：伺服器風扇功率曲線與 PIDNN

**Chengming Lee, Rongshun Chen (2015), Optimal Self-Tuning PID Controller Based on Low Power Consumption for a Server Fan Cooling System. Sensors 15, 11685–11700. DOI: 10.3390/s150511685.**

[原文](https://www.mdpi.com/1424-8220/15/5/11685)／[原文全文鏡像](https://pmc.ncbi.nlm.nih.gov/articles/PMC4481903/)

- 原文定位：§2 的 1U mockup 與 Eqs. (1)–(2) 風扇功率模型；§3.1–3.2 的 PID 及自調整方法。已取得原文索引的相關段落；直接開啟全文端點遇到存取限制。
- 原文方法：以三次多項式擬合風扇功率，結合 PID neural network 調整控制增益，在負載變化實驗中評估暫態與耗電。
- 機箱移植：先量自己的 PWM–RPM–W 曲線，建立固定轉速、原廠策略與一般 PID 基準；資料充分後，再比較 PIDNN。
- 建議用途：**第一優先借用功率量測與比較設計；PIDNN 列第二階段候選**。
- 限制：不能沿用作者的係數；PWM 不等於 RPM，RPM 也不等於耗電。原文允許的 overshoot 不能自動套用至本機硬體。
- 主稿對應：§3.9 控制方法及待建立的機箱實際介入評估。

### ENC-LIT-04：物理一致的自適應熱模型

**Dong Chen, Chee-Kong Chui, Poh Seng Lee (2025), Adaptive physically consistent neural networks for data center thermal dynamics modeling. Applied Energy 377, 124637. DOI: 10.1016/j.apenergy.2024.124637.**

[出版社原文頁](https://www.sciencedirect.com/science/article/pii/S0306261924020208)

- 原文定位：Abstract、Introduction 的 PCNN／A-PCNN 方法及貢獻說明；已取得出版社索引內容，尚未核對完整方程與逐頁原文。
- 原文方法：以 Softplus 神經網路取代預設固定係數，保留 PCNN 的物理約束結構。
- 機箱移植：保留 reduced-order 熱交換骨架，先以正值熱容量／熱導係數及風扇相關散熱項建模；再比較固定係數與小型網路預測係數。
- 建議用途：**第二階段候選**，檢查跨負載、入口溫度與散熱條件的適用性。
- 限制：正係數本身不等於整個模型物理一致；殘差路徑、離散時間穩定性與輸入依賴仍需檢查。這是簡化移植構想，尚不能稱完整 A-PCNN 重現。
- 主稿對應：§3.3 溫度模型、§3.8 hybrid residual 及機箱轉移實驗。

### ENC-LIT-05：多感測點、多風扇的耦合控制

**Zhen Zhang, Cheng Ma, Rong Zhu (2016), Self-Tuning Fully-Connected PID Neural Network System for Distributed Temperature Sensing and Control of Instrument with Multi-Modules. Sensors 16, 1709. DOI: 10.3390/s16101709.**

[出版社原文](https://www.mdpi.com/1424-8220/16/10/1709)／[全文鏡像](https://pmc.ncbi.nlm.nih.gov/articles/PMC5087497/)

- 原文定位：§2.2 MIMO Temperature Sensing and Control System、Figure 1；已取得原文索引的相關段落。
- 原文方法：在多個 PIDNN 與冷卻風扇間加入全連接層，處理多輸入、多輸出的溫控關係。
- 機箱移植：先量測前進氣、後排氣、CPU／GPU 區域對各風扇動作的響應；比較獨立 PID 與耦合控制。
- 建議用途：**取得多風扇獨立控制能力後再做**。第一步可只估計交互作用矩陣，再決定是否需要 FCPIDNN。
- 限制：本案若只有一組可調 PWM，就不足以驗證多致動器優勢；風道、位置與響應延遲不能由幾何距離替代。
- 主稿對應：§3.2 感測器／設備設定、§3.9 控制方法及多區域機箱評估。

## 本案建議的最小整合方式

以下為移植設計建議，並非任一原文的原樣公式或已完成方法：

```text
入口溫度＋NTC 空氣測點＋可用的元件遙測＋功率＋PWM/RPM
    → 動態 ARX／簡化熱模型
    → 多步溫度預測與誤差裕量
    → 工作負載前饋＋PID baseline
    → 資料足夠後比較受限制 MPC
```

可先採簡化熱節點模型：

\[
C_i\dot T_i=P_i+\sum_jG_{ij}(T_j-T_i)-G_{i,\mathrm{in}}(u)(T_i-T_\mathrm{in}).
\]

`T_i` 需明確指定是空氣、元件表面或晶片接面溫度；`P_i` 為對應熱節點的熱輸入近似，不能把整機 PSU 功率直接視為每個節點的獨立功率。係數與取樣間隔均需重新辨識。先使用固定係數，經比較後才考慮 A-PCNN-inspired 自適應係數。

## 驗證如何對準「適用度」

| 要改善的能力 | 建議比較 | 必須報告 |
| --- | --- | --- |
| 負載變化後的預測 | persistence、具相同可用輸入的静態模型、ARX、簡化熱模型 | 不同 horizon 的 MAE／RMSE／P95、升溫低估、逐 run 退步 |
| 未量測目標點估測 | 現有虛擬感測基準、短期 commissioning、動態狀態估測 | 未參與擬合的目標點誤差、測點失效、可用資料條件 |
| 風扇控制效益 | 固定轉速、原廠策略、PID、前饋＋PID、後續 MPC | 超溫峰值與持續時間、settling、風扇 Wh、整機 Wh、運算效能／throttling、控制抖動 |
| 跨情境 | 留出工作負載、日期、入口溫度；之後另留機箱 | 分情境結果及不確定性；不以同機箱跨 run 代替跨機箱 |
| 多風扇協調 | 獨立 PID 與耦合模型／控制 | 每個目標點與熱點的改善／退步，不能只報平均溫度 |

建議優先順序：①動態資料契約與 baseline；②功率曲線及前饋＋PID；③相同工作量下的受限制 MPC；④A-PCNN-inspired 與多風扇協調。不是一次把五套方法全部堆進主模型。

## 執行前的資料與判讀條件

- 把「有真實目標溫度回授的預測／控制」與「部署後沒有目標感測器的虛擬感測」分成兩個任務。後者不能把留出目標的真實歷史值餵給 ARX；需以可用測點、校正後狀態估計及開迴路 rollout 評估。
- PWM 是控制指令、RPM 是致動器回應；兩者應各自記錄。既有風扇閉迴路紀錄可能只反映控制器與溫度的相關性，不足以識別改變風扇的效果。
- 資料量不足時先做離線預測比較；要證明溫控與節能，需實際風扇介入及可比較工作量。不能直接用觀察性 BMC trace 宣稱新的控制策略節能。
- E15 的一次性確認已完成且資料已開封；本輪不得重訓／重跑 E15，或把它重新當獨立確認集。新模型調整只使用指定開發資料，最終主張另留新資料確認。
- 室內 20–30°C、機箱空氣溫度與 CPU/GPU 遙測是不同目標及操作域。實測範圍、溫度限制與回退策略須依選定硬體另外登錄；NTC 不直接作未校正參考真值。
- 正式採用任何候選前，依 `research-first` 建立 proposal／protocol／specs／design／reproducibility，固定 splits、指標、接受門檻與停止條件；取得結果後再同步中文、英文、簡報與成品。本次未改動已完成實驗或正式論文主張。
