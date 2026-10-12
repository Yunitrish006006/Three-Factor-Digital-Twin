# LQR 詳細整理：推導、機箱對應與原始論文

整理日期：2026-10-12。內容同步放在 [HTML 的 LQR 區](../reports/professor_research_2026-10-12_zh.html#lqr)，供我閱讀、口頭介紹與回答教授追問。下列推導是**現代記號的教學整理**；機箱矩陣由報告既有方程自行微分，一維例題由我選定數字計算，均不冒稱 Kalman 原文逐字公式或新增機箱實驗。

**論文本體已附上：**R. E. Kalman (1960), **Contributions to the Theory of Optimal Control**, Boletín de la Sociedad Matemática Mexicana, second series, 5, pp.102–119。[完整原始 PDF，18 頁](../papers/reference_sources/kalman_1960_optimal_control_original.pdf) · [出版來源](https://boletin.math.org.mx/pdf/2/5/BSMM%282%29.5.102-119.pdf) · [來源與檔案指紋](../papers/reference_sources/kalman_1960_optimal_control_original.source.json)。原始位元組未修改；不是《A New Approach to Linear Filtering and Prediction Problems》那篇濾波論文。

## 1. 我先把 L、Q、R 和三個角色講清楚

LQR 是 Linear Quadratic Regulator：L 指線性動態，Q 指二次成本，R 指調節器。成本中的矩陣 Q、R 另外表示狀態與操作權重，不是把縮寫逐字對應到兩個矩陣。

我用一句話介紹它：**給定動態模型、可用狀態和成本，LQR 算出狀態偏差應如何轉成操作修正。** 最優性相對於指定的模型與成本，不等於物理散熱最好、真實能耗最低，或所有工況都安全。

| 角色 | 解決的問題 | 在機箱中的例子 |
|---|---|---|
| 熱模型／辨識 | 操作與擾動如何改變狀態 | 熱容量、接觸熱導、對流增益、風扇時間常數 |
| 狀態估測器 | 由部分量測推估內部狀態 | 由金屬片、空氣、風扇等訊息估測熱源 |
| LQR 控制器 | 如何用偏差選擇操作 | 四個狀態偏差轉成 PWM 修正 |

LQR 不自動完成前兩件事。LQR、Kalman filter 和 LQG 是不同角色與設定。基本現代形式可對照 [MIT LQR 課程筆記](https://underactuated.mit.edu/lqr.html)。

## 2. 符號、維度、單位與我真正量得到的量

本稿選四狀態、一個控制輸入。討論時將熱功率 P_heat 與 Riccati 矩陣 P_cost 分開，避免兩種 P 混淆。

| 符號 | 維度 | 定義／單位 |
|---|---|---|
| x | 4×1 | [T_h,T_p,T_a,f]ᵀ；前三項 °C，f 為 0–1 風扇比例 |
| u | 1×1 | 0–1 PWM 命令；不是瞬時 RPM |
| d | 2×1 | [P_heat,T_in]ᵀ，單位 W／°C；已知輸入或擾動 |
| y | 2×1 | 例：金屬片與空氣溫度；風扇量測可另外加入 |
| e、v | 4×1、1×1 | 狀態與操作相對平衡點的偏差 |
| A、A_d | 4×4 | 連續／離散狀態動態；連續元素單位隨狀態尺度不同 |
| B、B_d | 4×1 | 控制對各狀態的動態影響 |
| C | 2×4 | 狀態轉成兩個溫度量測 |
| Q、R | 4×4、1×1 | 成本權重；Q 對稱半正定，R 對稱正定 |
| P_cost、K | 4×4、1×4 | 最優未來成本矩陣與狀態回授增益 |

若探頭讀到自身溫度，探頭延遲與偏差也要處理，不能直接當物體真溫。熱源參考只供獨立評分，不直接給稀疏控制器。控制、估測與評分使用的資訊必須列清楚。

LQR 的 Q／R 是設計成本；Kalman 濾波常用的 Q／R 是噪聲共變異數。即使字母相同，也要用 Q_cost／R_cost、Q_noise／R_noise 等名稱分開記錄。

## 3. 第一步是可達的平衡點，不是先調 Q／R

將非線性熱動態寫成 F(x,u,d)。固定功率、入口和設定值後，先找四個變化率都為零的 x_eq、u_eq，且 u_eq 在平台可提供的範圍。令 e=x−x_eq、v=u−u_eq、δd=d−d_eq，工作點附近的一階模型為：

```math:workpoint
F(x_eq,u_eq,d_eq)=0
de/dt ≈ Ae+Bv+Eδd
A=∂F/∂x|eq；B=∂F/∂u|eq；E=∂F/∂d|eq
```

全速風扇仍無法達標時，問題是可達性與散熱能力。增加 Q 不會產生超過設備能力的冷卻。功率／入口改變後，原平衡點可能不再成立；持續 δd 需要前饋、擾動估測或追蹤擴充。

線性化只保留工作點附近的一階效應。風扇對流乘上溫差有非線性耦合；遠離工作點或更換接觸／風道後，不能拿同一 K 延伸局部保證。此映射依 [MIT 局部 LQR 說明](https://underactuated.mit.edu/lqr.html#local-stabilization-of-nonlinear-systems)整理。

## 4. 我的四狀態熱方程如何得到 A、B、C

以下由報告既有 S 熱模型自行微分，不是原文機箱公式，也不代表已辨識出各物理參數。設 g=G_p+k_p f_eq、h=G_a+k_a f_eq、Δ_pa=T_p,eq−T_a,eq、Δ_ai=T_a,eq−T_in,eq：

```math:thermal-jacobian
A=[−(G_hp+G_b)/C_h, G_hp/C_h, 0, 0;
    G_hp/C_p, −(G_hp+g)/C_p, g/C_p, −k_pΔ_pa/C_p;
    0, g/C_a, −(g+h)/C_a, (k_pΔ_pa−k_aΔ_ai)/C_a;
    0, 0, 0, −1/τ_f]
B=[0,0,0,1/τ_f]ᵀ
C=[0,1,0,0; 0,0,1,0]
```

B 只有最後一項非零：PWM 先改變風扇比例，再由對流影響溫度。B_d 可以包含同一取樣期間的間接溫度效應，不等於連續 B。若風扇比例可量測，C 增加 [0,0,0,1] 一列；入口與功率另送入模型，不偽裝成熱源量測。

F 模型另有源—氣直接熱導，矩陣也需隨方程更改。容量、接觸、對流與風扇延遲影響不同項，不統稱一個導熱係數。對流失配已有估測退步反例，模型項較多不代表 A 較可信。

## 5. 每五秒控制時，離散化與成本要一起定義

假設每個取樣區間保持 v 不變，即 zero-order hold。連續模型的精確離散化為：

```math:zoh
A_d=exp(AΔt)
B_d=∫[0,Δt] exp(Aτ)B dτ
```

可用 [SciPy cont2discrete 的 zoh 方法](https://docs.scipy.org/doc/scipy-1.14.1/reference/generated/scipy.signal.cont2discrete.html)。A 可能奇異，不能一律用 A⁻¹(A_d−I)B。Euler 近似需確認取樣相對最快動態夠小；有風扇延遲時，不能只看溫度很慢。

模型精確離散化不等於成本精確離散化。保留連續成本的區間積分通常得到 Q_d、R_d，甚至交叉項 N_d；直接選離散 Q、R 則是定義每步成本。取樣改變時，要記錄採哪種方式，不混用連續增益與離散矩陣。既有比較採五秒；本稿沒有改取樣或重選權重來改動結果。

**專案目前實作：**`digital_twin/enclosure/session.py` 的 `linearize` 對既有五秒 `advance` 映射做有限差分，取得離散 A_d、B_d；沒有在本次換成 cont2discrete。`advance` 採熱方程 RK4 與風扇解析更新。上面的連續 Jacobian／ZOH 是理解主線，與目前數值實作分開；目標不可達時，`equilibrium` 選操作邊界的平衡狀態，不假稱熱源溫度等於設定值。

## 6. 連續 LQR：為什麼會出現 Riccati 方程

先看定常線性、完整狀態、無操作硬限制的無限時域問題。Q 對稱半正定、R 對稱正定；適當可穩定與成本可偵測條件下，取最優未來成本 V(e)=eᵀPe，P 表示未來累積成本如何依目前狀態變化。

```math:continuous-lqr
de/dt=Ae+Bv
J=∫[0,∞](eᵀQe+vᵀRv)dt
v=−Ke；K=R⁻¹BᵀP
AᵀP+PA−PBR⁻¹BᵀP+Q=0
```

把當下成本加未來成本變化最小化，對 v 微分設為零；R 正定讓當下最小化操作唯一。代回後要求對所有 e 成立，得到 CARE（連續代數 Riccati 方程）。

```math:hjb
V(e)=eᵀPe
0=min_v[eᵀQe+vᵀRv+2eᵀP(Ae+Bv)]
2Rv+2BᵀPe=0
v=−R⁻¹BᵀPe
dV/dt=−eᵀ(Q+KᵀRK)e
```

最後一式連到 Lyapunov；Q 半正定時導數可能只是半負定，還需相應條件，不能只由非正導數宣稱任意系統漸近穩定。這是依 [MIT HJB／LQR 推導](https://underactuated.mit.edu/lqr.html)重述主線，不是逐行重證全部定理。

有限時域有終端成本與終端條件，P 與 K 可能隨時間變動；不是所有 LQR 都只算一次常數 P。本節採定常無限時域的特定設定。

## 7. 離散 LQR：Bellman、DARE 和 K 的關係

五秒操作用 A_d、B_d。Bellman 原理將 V(e)=eᵀPe 拆成當步成本與下一步最優成本；代入下一步狀態，展開並對 v 求導：

```math:bellman
V(e)=min_v[eᵀQe+vᵀRv+(A_de+B_dv)ᵀP(A_de+B_dv)]
(R+B_dᵀPB_d)v+B_dᵀPA_de=0
```

K 的分母多了 B_dᵀPB_d，不能沿用連續公式。把最小化操作代回，即得到 DARE（離散代數 Riccati 方程）：

```math:discrete-lqr
e[k+1]=A_de[k]+B_dv[k]
J=Σ[k=0,∞](e[k]ᵀQe[k]+v[k]ᵀRv[k])
P=A_dᵀPA_d−A_dᵀPB_d(R+B_dᵀPB_d)⁻¹B_dᵀPA_d+Q
K=(R+B_dᵀPB_d)⁻¹B_dᵀPA_d
u[k]=u_eq−K e_hat[k]
```

最後一行換成估測偏差，是稀疏實作的映射；理想推導使用真實偏差，需另驗證估測，不能直接移用最優性。離散形式可核對 [Stanford 無限時域 LQR 講義，3–4 至 3–6](https://ee363.stanford.edu/archive/lectures/dlqr-ss.pdf)、[SciPy DARE](https://docs.scipy.org/doc/scipy-1.14.1/reference/generated/scipy.linalg.solve_discrete_are.html)與 [python-control dlqr](https://python-control.readthedocs.io/en/0.10.2/generated/control.dlqr.html)。

有限步數從終端 P_N 向後遞推 P_k；無限時域解是適當條件下的固定點。含成本交叉項 N 時應用對應形式；本節採 N=0。[Stanford 有限時域講義，1–14 至 1–20](https://ee363.stanford.edu/archive/lectures/dlqr.pdf)

## 8. 一維算例：我能親手算出 P、K 與 PWM

**自選數學教學模型，不是辨識、機箱實測或優越性實驗。** 假定 e[k+1]=0.98e[k]−0.02v[k]，e 為 °C 偏差，v 為 PWM 百分點修正；本例用 0–100 百分數尺度，與專案 0–1 不同。選 Q=1、R=0.1。

標量 DARE 乘開分母為 b²P²+[r(1−a²)−qb²]P−qr=0。代入 a=0.98、b=−0.02、q=1、r=0.1，取非負穩定化根：

```math:scalar-example
0.0004P²+0.00356P−0.1=0
P≈11.975666；K≈−2.239932
a−bK≈0.935201
u≈40+4.479864=44.479864%
```

假定平衡命令 40%、偏差 +2°C，v=−Ke≈+4.479864 百分點，提案約 44.48%。K<0 仍是正確冷卻回授，因 b<0，不能自行改號。另一根約 −20.875666，不是此問題的非負穩定化解。

我用 SciPy 與獨立二次方程求根核對，P=11.9756658921、K=−2.2399318147，理想特徵值 0.9352013637。這只檢查算式與方向，未含飽和、風扇動態、噪聲或未知擾動；不是安全證據，也不把例題權重搬去實際機箱。

## 9. 可控、可穩定、可觀測、可偵測不要混用

| 概念 | 我要問的問題 | 注意事項 |
|---|---|---|
| 可控 | 輸入能影響所有模態嗎？ | 完整 rank 不代表有限 PWM 有足夠冷卻能力 |
| 可穩定 | 不能控制的模態已穩定嗎？ | 較完全可控弱；離散不穩定含單位圓上模態 |
| 感測可觀測／可偵測 | y 能還原哪些模態，未見模態穩定嗎？ | 看 (A_d,C)，涉及感測位置與估測器 |
| 成本可偵測 | 成本未懲罰的模態穩定嗎？ | 看 (A_d,Q^(1/2))，不同於感測 C |

標準無限時域充分條件常用 (A_d,B_d) 可穩定、(A_d,Q^(1/2)) 可偵測，加上 Q 半正定、R 正定。PBH 針對不穩定模態檢查輸入／輸出方向的 rank；還需奇異值、尺度與條件數，不能只報 rank=4。

兩個感測點可能利用時間序列估四狀態，感測數少不直接等於不可觀測。rank 完整也不保證噪聲、弱耦合與短觀察窗下估得準。設計 Q 與感測 C 是不同角色。

## 10. Q／R 如何選、如何正規化

先選可接受狀態偏差與操作尺度，再選無量綱重要性。S 是狀態尺度對角矩陣，T 是操作尺度矩陣；W_x、W_u 是無量綱權重：

```math:normalization
ẽ=S⁻¹e；ṽ=T⁻¹v
Q=S⁻ᵀW_xS⁻¹；R=T⁻ᵀW_uT⁻¹
```

溫度、風扇比例與 PWM 尺度不同，權重都設 1 不代表同樣重要；PWM 改百分數也需換算 R。這是自行代入成本的量尺整理，背景可看 [Caltech 的 LQR 權重章節](https://www.cds.caltech.edu/~murray/books/AM05/wiki/OBC%3AMain_Page.html)。

- Q 相對 R 較大通常更重視偏差，但多變數暫態不保證每項指標單調改善，也可能更常飽和。
- 同正倍率放大 Q、R，標準無限制最佳操作不變；成本與 P 同倍率變化。
- R=0 不能仍套標準公式；正定也不等於數值條件良好。
- vᵀRv 不是實際 Wh，需功率模型／量測；與報告風扇 proxy 分開。
- 既有 Q=diag(1,0.25,0.1,0.02)、R=0.15 是當次固定設定，本稿沒有證明它跨平台最佳。

跨場景調適仍需共同程序與資料／試算預算，不看完 holdout 後為每台設備挑漂亮結果。

## 11. 求解器成功後，我還要檢查什麼

用 [SciPy solve_discrete_are](https://docs.scipy.org/doc/scipy-1.14.1/reference/generated/scipy.linalg.solve_discrete_are.html)求 P，再用線性求解取得 K，避免顯式求逆。以下是教學骨架，不是已驗證的新控制器：

```python
P = scipy.linalg.solve_discrete_are(Ad, Bd, Q, R)
S = R + Bd.T @ P @ Bd
K = numpy.linalg.solve(S, Bd.T @ P @ Ad)
residual = Ad.T @ P @ Ad - P - Ad.T @ P @ Bd @ K + Q
symmetry_error = numpy.linalg.norm(P - P.T)
relative_residual = numpy.linalg.norm(residual) / max(
    1.0, numpy.linalg.norm(P), numpy.linalg.norm(Q))
eigenvalues = numpy.linalg.eigvals(Ad - Bd @ K)
proposal = u_eq - K @ estimated_error
```

檢查維度、有限值、Q／R 對稱性、Q 半正定與 R 正定；再看 P 對稱／半正定、DARE 殘差，以及理想閉迴路特徵值模長<1。容差依量尺、條件數與求解器選定，沒有一個小數保證實機安全。

這只驗證理想線性計算。估測、負載階躍、入口、延遲、飽和、失配與感測異常仍需動態驗證；命令可行、數值穩定、物理不超溫是不同結果。

## 12. 估測、追蹤、限幅與 PI／MPC 邊界

**估測回授：**估測誤差進入實際閉迴路。適當線性、Gaussian 噪聲、模型／成本假設下，LQR 加 Kalman 濾波可形成 LQG；任意校正器接 LQR 不自動有相同最優／分離原理保證。[Stanford 部分觀測 LQG 講義，10–2 至 10–5](https://ee363.stanford.edu/archive/lectures/lqg.pdf) 原文 p.104 將控制與估測分開。

**追蹤：**非零設定值先求可達工作點與前饋。持續未知功率／模型偏差可能有穩態誤差；LQI 把輸出誤差積分加入狀態再設計 LQR，仍需增廣可穩定性、可達目標與 anti-windup。[dlqr integral_action](https://python-control.readthedocs.io/en/0.10.2/generated/control.dlqr.html)只是接口，不代替設計。

**限幅：**原始提案套共同 PWM／slew 限制後，實際命令才是 plant 輸入。它不再是原無限制問題的最優回授；保留風扇狀態也不等於涵蓋通訊、排程或感測延遲。

| 方法 | 可借用優點 | 我需保留的限制 |
|---|---|---|
| PI／PID | 誤差回授、積分、實作簡單 | windup、延遲、噪聲、參數需共同規則 |
| LQR | 模型統整多狀態與操作代價；線上矩陣乘法 | 模型／估測、工作點有效範圍；標準版無硬限制 |
| MPC | 預測窗中處理操作／變化率限制 | 計算、可行性、模型失配；不增加設備能力 |

公平比較共用外部 plant、初始條件、負載、感測、擾動先驗、校正預算與限制。完整真值版只能標 oracle／不同資訊條件，不直接與稀疏版宣稱公平。估測、追蹤、超溫、操作變化、能耗／proxy、計算時間分別報告，不用單一成本概括全部優劣。

## 13. 原始論文導讀：我先帶教授看哪些頁

PDF 第 1 頁為紙本 p.102，PDF 頁序＝紙本頁碼−101。下表可直接跳到原 PDF。

| 原文位置 | PDF 頁序 | 內容與邊界 |
|---|---|---|
| p.102，Introduction | [1](../papers/reference_sources/kalman_1960_optimal_control_original.pdf#page=1) | 調節器、存在／穩定性，不是熱控制實驗 |
| p.103，(2.1)、(2.2) | [2](../papers/reference_sources/kalman_1960_optimal_control_original.pdf#page=2) | 狀態、輸入、輸出用 F(t)、G(t)、H(t) |
| p.104，(A)/(B)、(3.3) | [3](../papers/reference_sources/kalman_1960_optimal_control_original.pdf#page=3) | 分開估測／控制；控制部分精確知道狀態 |
| p.108，(5.5)、(5.6) | [7](../papers/reference_sources/kalman_1960_optimal_control_original.pdf#page=7) | 定常完全可控 rank 判準，與現代較弱條件分開 |
| p.111，(5.23)、(A1) | [10](../papers/reference_sources/kalman_1960_optimal_control_original.pdf#page=10) | 一致完全可觀測；原文 Hx 的輸出成本 |
| p.112，(6.3)、(6.4) | [11](../papers/reference_sources/kalman_1960_optimal_control_original.pdf#page=11) | 微分 Riccati／存在，不是直接列出現代 DARE |
| p.113，(6.7)、(6.8) | [12](../papers/reference_sources/kalman_1960_optimal_control_original.pdf#page=12) | 無限時域與回授主線 |
| p.114，(6.10) | [13](../papers/reference_sources/kalman_1960_optimal_control_original.pdf#page=13) | 一致完全可控／可觀測、Q(t)／R(t) 正定上下界，條件下穩定 |
| p.117，(7.7) | [16](../papers/reference_sources/kalman_1960_optimal_control_original.pdf#page=16) | 定常情形與反向時間計算 P 的穩定性；現代 CARE 的定常整理另說明 |

原文 F／G 對應現代 A／B，H 是輸出映射；成本有 1/2 因子與 HᵀQH 結構。本稿 Q 是狀態成本，且另外選離散每步成本。回授符號／命名需連同定義看，不能只換字母就稱逐字轉錄。

文章以狀態空間、可控／可觀測、Riccati 分析最優調節的存在與穩定。它沒有證明我的非線性、估測、受限 PWM 機箱已最優或安全。本次核對原始 18 頁的首尾頁碼／文字，實際目視 p.104／114；[歷史原文閱讀定位](lqr_kalman1960_reading_2026-10-06_zh.md)保留，不聲稱全部證明逐行驗證。

## 14. 教授可能追問的十二題

| 追問 | 我的回答主線 |
|---|---|
| 為什麼選 LQR？ | 把可信模型、多狀態與操作代價合成可解釋基準；比較仍看結果。 |
| 狀態全部量得到嗎？ | 理論先用完整狀態；我只有部分量測，要估測與驗證。 |
| 為什麼加入風扇狀態？ | PWM 到散熱有動態，不能假設立即生效。 |
| Q／R 如何選、什麼單位？ | 以可接受偏差／操作尺度正規化，再固定重要性與調參預算。 |
| P 是濾波共變異數嗎？ | 本節是未來成本矩陣；估測共變異數另定義。 |
| K 為什麼可能為負？ | 由 B、狀態與輸入定義決定，冷卻 b<0 時負 K 可產生正修正。 |
| Riccati 算得出來就穩定嗎？ | 檢查穩定化解、條件、殘差與特徵值；受限／失配另驗證。 |
| 兩個感測怎麼估四狀態？ | 用動態時間資訊；查可偵測／數值條件，再獨立參考驗證。 |
| 限幅後還最優嗎？ | 不再是原無限制最優解；記錄實際命令、飽和與溫度。 |
| 設定值／功率變動呢？ | 先求可達工作點；前饋、擾動估測或 LQI 另設計。 |
| 和 PI／MPC 公平嗎？ | 需共享資訊、校正、限制與負載；真值上界另標。 |
| 和原論文差在哪？ | 原文線性、精確狀態、指定成本與定理條件；我需驗證模型、估測、限制與新工況。 |

## 15. 五分鐘與十分鐘口頭主線

**五分鐘：**第一分鐘講模型／估測／控制；第二分鐘講平衡點與 Q／R；第三分鐘以 Riccati → K → PWM 說回授；第四分鐘帶看 p.104／114；第五分鐘講稀疏估測、限制與下一階段驗證。

**十分鐘：**前兩分鐘講四狀態、可達工作點；第三、四分鐘講 A／B 和離散化；第五、六分鐘講 HJB／Bellman；第七分鐘算例與負 K；第八分鐘講權重、估測／飽和；第九分鐘看原文；第十分鐘交代公平比較與證據範圍。

我帶去的是離線 HTML、詳細筆記與原始 PDF。設備與資料仍未到位；本次增加教學、排版與附件，沒有新增實機結果或改動既有模擬結論。
