# Version 2 protocol

2026-10-05；研究先行、執行前固定。舊 v1 seeds 與 holdout 已開啟，保留歷史。本研究新 sources/config/artifacts，不能把舊結果當未見證據。

## Shared model and information

雙熱節點 C=(1200,1800)J/K、G=(1.5,2)W/K、k=(6,8)W/K、fan tau20s、RPM6000；plant 1s Euler thermal/exact fan。dt10s、120steps、target60/60、limit80/85、warning75/80、margin2、PWM[.2,1]、slew .1/step、初始PWM/f .5、溫度[58+seed%3,59+seed%3]。每方法只見當下state/inlet/powers，不提供未來。MPC/LQR 使用 shared affine ZOH。

PID+FF/LQR 共用 scalar equilibrium allocation：在 PWM 範圍 min sum((Tin+P/(G+k*u)-60)/5)^2+u^2，minimize_scalar bounded xatol1e-10/maxiter100 並比較端點。兩溫度目標通常不可同時到達。失配時 controller 只用 nominal parameters，不取得真 plant 參數。

## Controllers and calibration

fixed PWM .4/.6/.8；PID+FF 三候選(kp,ki,kd)=(.01,0,0)/(.03,.0001,0)/(.06,.0003,.05)，max thermal error、backcalculation .2、bias 使用共同 equilibrium feedforward。LQR Qdiag(.04,.04,0)、R .1/1/10；allocation 決定可達 x_eq，DARE normalized residual <=1e-5、closed-loop spectral radius <1；限制後不宣稱全域最優/穩定。MPC R .1/1/10、Qthermal1/25、delta5、slack1e4、horizon12、terminal同Q；OSQP1.0.4，scaled slack=sqrt(1e4)*s、eps_abs/rel1e-7、max_iter100000、rho1、eps_prim_inf/eps_dual_inf1e-10、adaptive_rho_interval25、polishing=True、objective scale1。只接受 solved 且直接未縮放約束及 primal/dual residual <=1e-5。

每方法3候選×3calibration seeds111/112/113，共36回合，全保存不提前停。相同候選回合預算不是相同計算時間。selection=mean(error²/25)+.01mean(u³)+1e4mean(positive_limit_violation²)，候選序 tie-break，不逐 plant 重調。freeze 含 source snapshots/hashes、config/candidates/selected/seeds/schedules、environment/calibrationhash；freeze 後禁止改研究輸入來源。

## Splits and assumed variants

validation121/122/123；holdout131/132/133；plant_holdout141/142/143；overload151/152/153。正式48回合/5760步。schedules/config.json 完整固定：cal CPU[80,160,110,190]/GPU[120,220,170,260]，val[140,60,210,100]/[190,110,280,150]，hold/plant[160,90,205,65,175]/[230,140,275,105,245]，overload[450]/[600]。同組 shared seed ±5/8W uniform jitter，Tin=29+(seed%3-1)+1.5*(step>=40)+.5*(step>=80)+Uniform[-.2,.2]。

plant_holdout 預先固定三組：C factors(.8,1.1)/(1.25,.75)/(.65,1.4)，G factors(.9,1.1)/(1.15,.85)/(1,1)，fan gain factors(.8,.75)/(1.1,.85)/(.6,.7)，tau30/15/40s。僅正式評估，不校準或給 controller 真參數；有限假設模型壓力測試而非實體跨設備。

## Durability, metrics and audit

全方法 runner 外部完整計時；超10s使用同 ramp-to-max fallback並記deadline。記狀態/當下擾動/commands/next/firstprediction、solver reason/status、accepted-plan slack（失敗/非MPC null）、applied cap exceedance、fallback/override、solver與total time、primal/dual residual。報各node/aggregate MAE/RMSE、prediction error、peak、sampled overtemp seconds（10s末端取樣×dt，不是精確積分）、PWM TV、u³fan-energy假設proxy、bounds/slew、fallback/override、timingp50/p95/max、deadline、首次連續60s誤差帶時間（null與達成數保留）、selection score。所有不利結果公開，缺失不當零。

calibrate/evaluate 在任何 episode 前 exclusive attempt receipt，失敗/中斷也消耗，禁止同目錄覆寫/重試；CSV x模式；JSON拒絕非有限。獨立 verifier 不匯入 runner/controller 計算，重算全指標/candidate×seed/selection/aggregate/H01..03、freeze chronology/source snapshots/config、seed scenario、plant equation、initial/continuity、warning/fallback；明確 raise 非 assert，python -O 有效。負測試包含 timing/decision/missingrun/duplicate/plant/scenario/override/marker。

不因結果修改規則。如需修正保留失敗版本另立 protocol/目錄。多步診斷固定 x=[60,60,.5]、Tin30、P200/280、12step rampup/down，和 nonlinear plant比較；屬診斷非實測。

## Pre-calibration numerical diagnostic amendment

正式 calibration/evaluation 前，單點 nominal/overload 單元測試發現原10000iter無法收斂，且default infeasibility tolerance在無上限slack的可行問題誤停。全情境同一規則改 max_iter100000、rho1、infeasibility tolerances1e-10；success/residual gate仍不放寬，objective scale仍1。測試 x=[60,61,.5]/[91,91,1]/[105,110,1], Tin30, P450/600；不使用正式seeds或結果選參。保留此修訂原因。
