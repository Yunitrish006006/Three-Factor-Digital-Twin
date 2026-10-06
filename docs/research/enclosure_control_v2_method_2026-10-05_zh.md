# 機箱控制方法比較與多角色修正

## 我固定的數學模型

以下是自行數學化整理，不是文獻逐字公式或實機辨識：C_i dT_i/dt=P_i−(G_i+k_i f)(T_i−T_in)；tau df/dt=u−f。狀態x=[T_CPU,T_GPU,f]，PWM u，觀測RPM=6000f。局部连续Jacobian J與affine drift作augmented matrix expm(dt*[J,b,c])形成ZOH A/B/c。MPC每步重新線性化，horizon內固定當下擾動；不看未來負載。

## 我如何選基準

|方法|模型/參考|候選/限制|
|---|---|---|
|固定風扇|不用負載前饋|PWM .4/.6/.8，共同slew/warning|
|PID＋前饋|共用bounded equilibrium allocation，max thermal error|3組kp/ki/kd、backcalc .2|
|gain-scheduled LQR|可達x_eq、ZOH、DARE Qdiag(.04,.04,0)|R .1/1/10、限制後不宣稱受限最優|
|MPC|當下線性模型、12步預測、溫度softslack|R .1/1/10、OSQP、u/slew硬限制|

allocation 固定最小化兩節點穩態target error²/25 + u²。單風扇不一定同時達兩target。LQR P解DARE，K=(R+BᵀPB)^−1 BᵀPA，u_raw=u_eq−K(x−x_eq)。MPC成本sum thermal error²/25 + R sum u² +5 sum Δu²+1e4 sum s²；s≥0。兩式屬本研究數學化整理，沒有杜撰方程編號。

## 我查到的來源

[OSQP MPC官方範例](https://osqp.org/docs/examples/mpc.html)、[OSQP求解設定](https://osqp.org/docs/interfaces/solver_settings.html)、[SciPy DARE官方文件](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.solve_discrete_are.html)。當前環境OSQP1.0.4/SciPy1.14.1，官方站最新版本不代替環境版本紀錄。

## 我保留的限制

相同候選回合預算並非等CPU時間；完整狀態與名義參數已知；plant_holdout只涵蓋指定三組假設參數。PID+FF不是v1的PID，負載生成/離散化也不同，所以不能直接把兩版數字當成算法改善率。功耗為10u³W proxy，整機功耗與throttling未測。實體控制/E8未評估。
