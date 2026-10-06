# Research

- RQ-MPC-01：假設機箱熱模型下，有限 horizon MPC 能否持續產生符合 PWM 與變化率限制的命令？
- H-MPC-01：validation 與 holdout 的 nominal episodes 均完成、命令無違例、控制步 p95 求解耗時低於 sample time、fallback 比率不超過 5%，支持模擬可行性。
- H-MPC-02：holdout nominal 中，MPC macro tracking MAE 比 calibration 選出的 PID 至少低 5%，且每回合超溫時間不增加；僅支持此模型的相對追蹤改善。非保證結果。
- CLM-MPC-SIM：只可主張假設模型／固定預算／固定觀測與當下擾動條件下的探索結果。

競爭解釋：MPC 使用正確模型、基準整定預算有限、狀態可見性高、風扇三次方功耗為假設。模型失配與過載另列 stress，不能因不利而排除。seed 是合成負載的隨機重複，不代表實體設備樣本。不涉及個資或硬體致動。E8、實體機箱、NTC、throttling 與整機功耗保持 NOT_EVALUATED。
