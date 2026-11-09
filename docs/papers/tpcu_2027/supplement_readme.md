# 研究資料包說明

本資料包是論文數值的作者核查材料。官方是否接收補充附件尚未確認，因此投稿時不預設一併上傳。

| 檔案 | 內容 | 來源 |
| --- | --- | --- |
| `supplement_45_calibration_runs.csv` | 五方法各三候選、三校準種子的45回合；含候選索引、參數、單回合與三種子平均選參分數、選定標記、MAE、代價、超溫、回退及逐步軌跡SHA-256。 | 凍結`artifacts/calibration.json` |
| `supplement_60_runs.csv` | 四個正式評估分組、每分組五方法各三種子的60回合；含參數、指標及逐步軌跡SHA-256。 | 凍結`artifacts/result.json` |
| `claim_evidence.csv` | 正文表三、表四、改善率及核心環境／方法設定的數值來源對照。 | 同一凍結協定與結果 |

105份逐步軌跡CSV保存在研究根目錄的`openspec/changes/compare-enclosure-five-methods-20261026/artifacts/traces/`，未複製進本投稿工作目錄。每份軌跡的SHA-256可由上述逐回合CSV核對。凍結`verification.json`記錄45校準、60正式、12,600列及1,995個回合指標的稽核範圍；該稽核不等於獨立重新最佳化LQR/MPC。

數據狀態為假設機箱模型的完整狀態可見模擬。`fan_energy_proxy_Wh`使用假設功率`10u³ W`計算，並非實測風扇電耗或整機節能。
