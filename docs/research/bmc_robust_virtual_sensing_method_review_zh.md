# BMC 虛擬感測資料品質與穩健方法研究筆記

日期：2026-08-24  
狀態：探索性方法研究，尚未納入論文主方法

## 1. 問題重新定義

E13 的數億至數百億度誤差起初看似 sentinel 或重尾 outlier，但原始檔檢查顯示真正原因是 **InfluxDB 多 section schema 錯位**。同一 CSV 在每個 `#group` 後可能重新宣告 header，並混合 `device_id=bmc` 與 `device_id=host`。現行 parser 固定使用第一個 BMC header，因此把 host 的 cache counter、cycles 與 core utilization 錯映射為溫度、風扇及 PSU 欄位。

上游 README 明確說明資料同時包含 BMC 與 host telemetry，且提供 `split.py`；該程式以 `#group` 建立 sections，再依 `bmc`／`host` 選取資料，而不是跨整檔共用一個 header。來源：[BMCDATA repository](https://github.com/arealuser/bmcdata)、[upstream split.py](https://github.com/arealuser/bmcdata/blob/master/scripts/split.py)、[upstream collapse.py](https://github.com/arealuser/bmcdata/blob/master/scripts/collapse.py)。

## 2. 文獻方法整理

### 2.1 資料完整性應先於模型穩健性

Gwerder 等人將建築自動化 plausibility checks 分為 single-signal、similarity 與 reaction tests；這支持先檢查 schema、範圍、跨訊號關係和控制反應，再進入預測模型。[Data Integrity Checks for Building Automation and Control Systems](https://doi.org/10.34641/clima.2022.271)

真實校園感測資料常有異質性、缺值與 temporal pattern 差異，模型是否具代表性必須與資料品質一起評估。[Lillstrang et al., 2022](https://doi.org/10.1016/j.buildenv.2021.108529) 但環境監測研究也警告，純統計 fault detector 可能把重要真實事件誤刪，因此不能依 test residual 清資料。[The Perils of Detecting Measurement Faults](https://arxiv.org/abs/1902.03492)

### 2.2 Robust regression 只能處理污染，不能修復 schema

Huber M-estimation 對近似分布中的污染比 least squares 穩健；Least Median of Squares 可抵抗接近 50% 的污染。[Huber, 1964](https://doi.org/10.1214/aoms/1177703732)、[Rousseeuw, 1984](https://doi.org/10.1080/01621459.1984.10477105) Soft-sensor 研究亦把 noise、outlier 與 missing data 視為核心問題，並比較 OLS、robust regression、PLS 與 Bayesian 方法。[Dealing with Irregular Data in Soft Sensors](https://doi.org/10.1021/ie800386v)

然而 schema 錯位是語意錯誤，不是同一變數分布中的污染。直接套 Huber 可能讓錯誤結果看似穩定，反而掩蓋 parser 缺陷。

### 2.3 分布轉移應輸出不確定性或拒答

Weighted conformal prediction 可處理 covariate shift，但需要可靠的 density ratio 或足夠未標記 target covariates；目前單一伺服器、少量完整 runs 不足以支持複雜 ratio estimation。[Tibshirani et al., 2019](https://papers.neurips.cc/paper_files/paper/2019/hash/8fb21ee7a2207526da55a679f0332de2-Abstract.html)

Selective regression 允許高風險輸入 abstain，代價是降低 coverage；對安全相關溫度估測比無條件輸出點估計合理。[Regression with reject option](https://papers.nips.cc/paper/2020/file/e8219d4c93f6c55c6b10fe6bfe997c6c-Paper.pdf)、[Selective Nonparametric Regression](https://proceedings.mlr.press/v222/noskov24a.html) Soft-sensor 文獻也主張同時輸出 prediction interval 與可信度。[Interval soft sensors](https://doi.org/10.1021/ie201053j)

## 3. 候選方法比較

| 方法 | 本案適用性 | 主要限制 | 決策 |
|---|---|---|---|
| `#group` 分段且只接受 `device_id=bmc` | 直接修復根因 | 必須逐 section 驗證 header | 必做 |
| 固定物理範圍 quarantine | 可攔截單位／感測故障 | 範圍需有硬體或 protocol 依據 | 第二層 |
| median/IQR scaling | 防止少數 leverage points 破壞尺度 | 無法修復欄位錯位 | parser 正確後採用 |
| Huber regression | 對 response contamination 穩健 | 高 leverage input 仍可能有影響 | 候選 baseline |
| Least Median/Trimmed Squares | 高 breakdown point | 小樣本與多特徵時估計不穩、實作較重 | sensitivity only |
| weighted conformal | 可研究 covariate shift interval | density ratio 樣本不足 | 暫不採用 |
| robust support gate + abstention | 可阻止明顯 OOD 硬輸出 | 必須同時報 coverage 與 risk | 推薦 |
| Transformer／深度 domain adaptation | 能力強但參數多 | 31 個 runs 遠不足以支撐 | 不採用 |

## 4. 推薦的下一階段設計

1. 建立 E14A parser-correctness study：每遇到 `#group` 重設 section/header，只接受同 section 中 `_measurement=sdgp`、`device_id=bmc` 且具完整 BMC 欄位的 rows。
2. 以 upstream `split.py` 的 BMC section row count 作 oracle，至少用早期、晚期與多 section 檔案做 parser tests。
3. 保留 E13 原始失敗，但將其標示為 parser-invalidated，不可把修正後重算稱為 confirmation。
4. 在 parser-correct development data 上比較 standard ridge、median/IQR ridge、Huber 與 inlet/outlet offset；所有品質規則只能使用欄位語意或 development data 設定。
5. 以 robust-scaled feature support 建立 abstention gate，報告 coverage、accepted-run MAE、all-run failure rate 和被拒 runs，不只報條件式 MAE。
6. 從 BMCDATA 尚未用過的完整檔案另選新的 final confirmation set；目前 14 個 E13 test runs 已開封，不能再當未見確認資料。

## 5. 研究判斷

最有論文價值的結論不是「換更複雜模型」，而是：**IoT 虛擬感測必須把 source-aware schema integrity、robust estimation 與 abstention 視為三個不同層級**。E13 證明 robust modeling 之前若沒有資料語意隔離，任何準確度數字都可能失效。下一個 confirmatory experiment 必須使用未開封 runs，不能修 parser 後重用 E13 test 並宣稱成功。

## 6. E14A 後續發現：單位 regime

E14A 在 31/31 oracle count、零 host leakage 與已知 host-row 排除均通過，但三個 BMC sections 仍以 raw hwmon/OpenBMC 單位記錄。官方文件指出 Linux `temp*_input` 使用 millidegree Celsius、`power*_input` 使用 microwatt；OpenBMC 亦以 `Scale=-3` 表示溫度。因此下一步不是 outlier deletion，而是預註冊 section-level unit normalization。[Linux hwmon sysfs interface](https://origin.kernel.org/doc/html/v5.15/hwmon/sysfs-interface.html)、[OpenBMC sensor architecture](https://github.com/openbmc/docs/blob/master/architecture/sensor-architecture.md)、[OpenBMC host management](https://github.com/openbmc/docs/blob/master/host-management.md)
