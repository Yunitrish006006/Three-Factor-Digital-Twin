# Pre-registered Protocol

版本 1；登記日期 2026-10-05；實作與結果之前固定。探索性合成研究。

## Model and inputs

兩個獨立元件熱節點 T_cpu/T_gpu 與共用有效風扇 f。C dT/dt = P - (G + k_f f)(T - T_in)；tau_f df/dt = u - f。PWM u 以 0–1 表示，RPM = 6000 f。自行數學化整理，不是實機物理參數。
假設 CPU C=1200 J/K、G=1.5 W/K、k_f=6 W/K；GPU C=1800、G=2、k_f=8；tau_f=20 s。入口溫度 25–33°C，CPU/GPU 目標 60/60°C，上限 80/85°C。dt=10 s，horizon=12（120 s）。CPU/GPU 高溫不屬室內估測域。
Plant 用分段 1 s Euler 積分；MPC 每步在當下狀態／輸入重新線性化並作 affine Euler prediction。nominal 與 predictor 因數值與線性化不同，不用預測自身作真值。

## Constraints and controller

所有方法 u∈[0.2,1]，每步 |delta u|≤0.1；T_warn=75/80°C 時共用 ramp-to-max safety override。它不保證在過載下無超溫；override 仍受相同 slew limit。初始 f/u=0.5。
MPC Q=diag(1,1)，R_u∈{0.1,1,10}，R_delta=5，terminal=Q；分母温度尺度 5°C。預測 T≤limit-margin+s，margin=2°C，s≥0，slack penalty=1e4 sum(s²)。溫度為軟限制，PWM 與 slew 為硬限制。SLSQP maxiter=80、ftol=1e-7；另核對有限值及硬限制與溫度/slack residual≤1e-5。不通過就 ramp-to-max fallback。只執行第一輸入。
每方法只見當下 T/f、入口與CPU/GPU功率；MPC 以當下擾動持續至 horizon，不能看到未來 trace。PID 使用 max(T_cpu-target,T_gpu-target)，bias=0.5，Kp∈{0.01,0.03,0.06}、Ki∈{0,0.0001,0.0003}、Kd∈{0,0.05}（18 組），back-calculation anti-windup=0.2。fixed u∈{0.4,0.6,0.8,1}。

## Split and search

每回合 120 steps/20 min，不去掉初始過渡。calibration seeds 11/12/13；validation 21/22/23；holdout 31/32/33；stress seeds 41/42/43 各跑 model-mismatch 與 overload。
calibration 負載四段 60/120/180/90 W CPU、90/180/240/120 W GPU；validation 較頻繁四段 100/190/70/160 与 140/260/100/220；holdout 不同五段 70/200/110/180/80 与 100/280/160/250/120，各 seed 加固定有界負載抖動与入口擾動。stress mismatch 參數 C×0.7、k_f×0.65、tau×2，overload CPU=450/GPU=600 W；沒有換控制器或重調。
搜尋 4 fixed +18 PID+3 MPC 候選，各用相同3 calibration seeds，selection score=macro mean[(error/5)² + 0.01 u³ + 1e4 violation²]，以列舉順序 tie-break；選完凍結 JSON 及 source hashes，才可開 validation/holdout。不是跨未見機箱確認。

## Metrics and decisions

保存各節點與 aggregate MAE/RMSE、one-step prediction MAE（模型誤差）、最大溫度、超溫秒數、PWM total variation、slew/bounds violations、假設 fan energy Wh（10 u³ W）、slack、fallback、safety override、求解 p50/p95/max、settling time（進入並持续 60 s 在兩個目標±2°C內，未達為 null）。throttling 與整機功耗為 null。
H-MPC-01 與 H-MPC-02 按 research.md 判準；stress 不納入 nominal 成功率但全部公開。三 seeds 不進行推論統計或泛化宣稱。誤差/能耗/失敗均不隱藏。

## Execution

`scripts/run_enclosure_mpc.py` 先 freeze，再正式 evaluate；`scripts/verify_enclosure_mpc.py` 從 CSV 重算指標與來源/trace hash。結果存本 change 的 artifacts/。實作測試失敗可修正並從 calibration 開始全重跑；開正式 test 後的修改必須記錄版本、原因與先前結果，不覆寫不利研究結果。
