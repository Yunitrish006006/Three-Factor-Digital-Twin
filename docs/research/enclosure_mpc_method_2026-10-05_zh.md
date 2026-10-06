# 機箱受限制 MPC 方法與參數

2026-10-05；已完成假設模型的探索性模擬，實體機箱 NOT_EVALUATED。

## 來源與選擇

我查到 [OSQP 官方範例](https://osqp.org/docs/examples/mpc.html) 用有限 horizon、狀態／輸入限制與逐步重求解描述 MPC。我選擇 [SciPy SLSQP](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-slsqp.html) 求解本輪小型問題，另檢查求解狀態、有限值及限制殘差。這兩份是方法／實作文件；機箱方程為下列自行數學化整理，沒有原文方程編號。

## 狀態與模型

`x=[T_cpu,T_gpu,f]`；控制是 `u=PWM/100`；擾動是 `d=[T_in,P_cpu,P_gpu]`。溫度為 °C，功率為 W，f 為有效風扇 0–1，RPM=6000f。

\[
C_i\dot T_i=P_i-(G_i+k_{f,i}f)(T_i-T_{in}),\qquad \tau_f\dot f=u-f.
\]

CPU：C=1200 J/K、G=1.5 W/K、k_f=6 W/K；GPU：1800、2、8；風扇 tau=20 s。這些是事前假設值，沒有從實機辨識，也不沿用先前單節點示範的 C=12000。預測器每次於目前 x 線性化：`A=I+dt*Jacobian`、`B=dt*[0,0,1/tau]`、`c=dt*(F-Jacobian*x-B_cont*u)`；因此 `x_next=A*x+B*u+c`。plant 用 1 s 子步積分與 exact fan lag，提供獨立於 affine 預測器的合成結果。

## 目標、限制與流程

| 設定 | 固定值 | 解釋 |
| --- | --- | --- |
| 取樣／horizon | 10 s／12 步（120 s） | 每步重新線性化和求解 |
| CPU/GPU 目標 | 60/60°C | 追蹤誤差與預測誤差分開計算 |
| CPU/GPU 溫度上限 | 80/85°C | 預測以 2°C margin、非負 slack 的軟限制表示 |
| 警告溫度 | 75/80°C | 三方法共用提高至最大風扇的安全覆寫，仍遵守 slew |
| PWM／變化率 | 20–100%／每步最多 10 百分點 | 硬限制 |
| Q／terminal Q | diag(1,1)，誤差以 5°C 正規化 | 溫度偏離代價 |
| R_u／R_delta | calibration 選 R_u=1；R_delta=5 | PWM 平方與相鄰動作變化代價 |
| slack penalty | 10000*sum(slack²) | 保留無法達成預測溫度限制的程度 |

目標函數為所有預測步的 `sum(((T-target)/5)^2) + R_u*sum(u^2) + R_delta*sum(delta_u^2) + 10000*sum(slack^2)`。預測軟限制 `T≤T_limit-2+slack`。它不保證硬體安全，過載可以超溫。模型使用當下擾動 persistence，没有未來負載資訊。

流程：讀取當下狀態與負載；形成 affine prediction；求解 input/slack 序列；檢查解；只執行第一動作；plant advance；記錄預測與結果；下步重新估算。求解不成功或殘差超過 1e-5 時回退為向 100% PWM 漸增，明確記錄 fallback。此版本只接模擬器。

## 比較與目前結果

| 方法 | 模型資訊與選參方式 | 狀態 |
| --- | --- | --- |
| fixed fan | calibration 4 候選選 40%；警告時仍有共用覆寫 | 已模擬比較 |
| PID | calibration 18 候選選 Kp=0.06、Ki=0.0001、Kd=0.05；max CPU/GPU error、back-calculation=0.2 | 已模擬比較 |
| constrained MPC | calibration 3 個 R_u 候選；同當下觀測、同限制 | 已模擬比較 |
| LQR | 尚待狀態空間 Q/R 比較與限制處理 | TODO |

三方法的候選數不同，因此結果是固定的各自搜尋預算比較，不能聲稱等額運算預算。所有方法都可見當下負載／風扇；PID 的此版本未使用負載前饋，也未完成 PID 所有可能配置的全面搜索。

完整 protocol、所有候選及正式結果見 [研究規格](../../openspec/changes/implement-enclosure-mpc-20261005/protocol.md)、[freeze](../../openspec/changes/implement-enclosure-mpc-20261005/artifacts/freeze.json)、[result](../../openspec/changes/implement-enclosure-mpc-20261005/artifacts/result.json)。預測器的較小 one-step error 來自已知假設參數，不能和先前 BOPTEST replay 的 1.6073°C 直接比較。
