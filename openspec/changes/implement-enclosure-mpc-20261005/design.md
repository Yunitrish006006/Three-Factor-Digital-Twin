# Design

CTRL-101/RQ-MPC-01：新增 digital_twin/control/enclosure_mpc.py，保持 PWM 工程單位於公共模型層；CPU/GPU 組態由 dataclasses 提供，不以 testcase 名稱分支。
CTRL-102/H-MPC-01：每步在当前 T/f/u 線性化雙熱節點与風扇，condense 到 input/slack variables；SLSQP 求解有限 horizon 的 convex quadratic approximation，顯式梯度与線性限制。warm-start 是上一步序列位移，不是未來真值。
CTRL-103/H-MPC-02：共用 CommandLimits、safety override、初態與場景，獨立 plant 積分；PID/fixed 与 MPC 可見相同當下狀態。安全 override/solver fallback 都保存 reason。
EVD-101：freeze 的 config、源碼及 protocol hash 在 calibration 後保存；只用 calibration 選參數。正式 runner 不搜尋，verifier 從原始 CSV 重算。CLI 預設不覆寫已有 artifact。
SYN-101：新結果作独立 exploratory 補充，不更新既有室內估測與 E15 主張。使用共用同步段落讀取 actual result.json；不能只改 generated outputs。
