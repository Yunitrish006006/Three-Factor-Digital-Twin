# Research questions and decisions

- RQ-CTRL-01：專用 QP、ZOH 與共同保護規則能否改善求解可靠性？
- H-CTRL-01：四方法所有正式回合 bounds/slew 零違例、每回合外部完整控制計時 p95 <10s、numeric fallback <=5%。超載也納入；超溫不屬此假設。
- H-CTRL-02：新版 nominal synthetic holdout，MPC macro MAE 比 PID+feedforward 至少低5%，每 seed 取樣超溫時間不增加。
- H-CTRL-03：同上，相對經限制的 gain-scheduled LQR 至少低5%且取樣超溫時間不增加。
- CLM-CTRL-SIM：只支持明定假設熱模型、合成負載與有限候選預算。比較均探索性，不做推論統計；三 seed 不是设备樣本。

競爭解釋：完整狀態可見、PID+FF/LQR/MPC 知道名義參數、能耗 proxy 假設、不等 CPU 計算量。指定未見假設 plant variants 不是跨實體機箱泛化。熱能力不足與數值失敗分開。無個資、無硬體致動。E8/NTC/throttling/整機功耗 NOT_EVALUATED。
