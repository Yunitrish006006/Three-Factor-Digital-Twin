# LQR：我需要理解與注意的內容

整理日期2026-10-12。此稿供理解與口頭報告，配合[原文閱讀定位](lqr_kalman1960_reading_2026-10-06_zh.md)與[HTML 的 LQR 區](../reports/professor_research_2026-10-12_zh.html#lqr)。下列現代記號是教學整理，不冒稱 Kalman1960 原文逐字公式；沒有新增 LQR 實驗或改動既有研究結果。

## 先掌握一句話與三個區別

LQR（Linear Quadratic Regulator，線性二次調節器）用線性狀態模型和二次成本，算出「狀態偏差應如何轉成操作修正」的回授增益。L 是模型形式，Q 是二次成本，R 是 regulator；權重矩陣 Q、R 則分別表示狀態偏差與操作代價。[MIT 原始課程筆記](https://underactuated.mit.edu/lqr.html)

我需要分清楚：**熱模型**負責描述溫度如何改變，**估測器**負責從少量感測還原狀態，**LQR**負責選操作。LQR不會自動辨識熱容量／熱導，不會自動補上缺少的熱源感測，也不能靠改 Q／R 增加風扇的物理散熱能力。

## 和機箱對上：狀態、操作與量測

| 符號／例子 | 我的解釋 | 容易混淆的地方 |
|---|---|---|
| x=[熱源溫度、金屬片溫度、空氣溫度、風扇比例] | 用來預測未來的內部狀態 | 四個狀態不代表四個都量得到 |
| u=PWM 命令 | 我要操控的量 | PWM命令不等於瞬間RPM；風扇有延遲 |
| y=[金屬片溫度、空氣溫度] | 稀疏溫度量測；已量測風扇比例可另送給估測器 | y不等於完整x；熱源參考僅用於評分 |
| 功率與入口溫度 | 此問題的負載／擾動或已知輸入 | 不可給控制器尚未發生的未來負載真值 |
| x_eq、u_eq | 給定負載與入口下可達的平衡點 | 設定值28°C不保證有可行PWM能達到 |

符號是本稿的熱控制映射，並非 Kalman 原文指定機箱狀態。線性化與平衡點的作法參照[MIT 的非線性系統局部 LQR](https://underactuated.mit.edu/lqr.html#local-stabilization-of-nonlinear-systems)。

## 核心式：先選平衡點，再算回授

令 e=x−x_eq、v=u−u_eq。以連續熱模型做局部線性化得到 A、B；使用固定取樣時間 Δt，經適當離散化得到 A_d、B_d。實際控制常用：

```text
e[k+1] = A_d e[k] + B_d v[k]
y[k]   = C e[k] + 量測噪聲
J      = Σ (e[k]ᵀ Q e[k] + v[k]ᵀ R v[k])
P      = A_dᵀ P A_d − A_dᵀ P B_d (R+B_dᵀ P B_d)⁻¹ B_dᵀ P A_d + Q
K      = (R+B_dᵀ P B_d)⁻¹ B_dᵀ P A_d
v[k]   = −K e_hat[k]
u[k]   = u_eq − K e_hat[k]
```

DARE與離散增益形式依[SciPy 官方說明](https://docs.scipy.org/doc/scipy-1.14.1/reference/generated/scipy.linalg.solve_discrete_are.html)及[python-control dlqr](https://python-control.readthedocs.io/en/stable/generated/control.dlqr.html)。標準無限時域成本的最優回授使用真實狀態 e；本研究只能用 e_hat，是實務估測回授，需另外評估估測誤差，不能把理想最優結論直接移過來。

若採四個狀態、一個PWM輸入，A_d／Q／P為4×4、B_d為4×1、R為1×1、K為1×4。此處P是最優未來成本的矩陣，**不是估測器的誤差共變異數**；LQR的Q／R也是成本權重，不能和Kalman濾波的過程／量測噪聲Q／R混成同一組參數。

連續時間的代數 Riccati與增益是另一套式子：

```text
AᵀP + PA − PBR⁻¹BᵀP + Q = 0
K = R⁻¹BᵀP
```

不能把此 K 公式配到離散 A_d、B_d。取樣時間改變時，模型與成本離散化也需保持一致；不能把每次調參後的連續模型與離散控制混著比較。

**回授符號也要和模型一起核對。** 冷卻操作對溫度的有效影響可能帶負號，K的元素不一定全為正。不要因為看到「負回授」就強制改K的符號；應依狀態／輸入定義確認A_d−B_dK與實際命令的方向。

## 我最需要注意的九件事

1. **先確認平衡點可達。** 給定熱功率與入口溫度，全速風扇仍超過目標時，改Q／R不能解決散熱不足。我要先求平衡點或用模型計算可達範圍，才談追蹤。
2. **線性模型有適用範圍。** 在一個工作點附近求K，不代表不同功率、入口、接觸或風道都有效。切換／排程工作點若要使用，需有共同規則與新資料驗證。[MIT 局部線性化](https://underactuated.mit.edu/lqr.html)
3. **不用把完全可控當成唯一條件。** 標準無限時域LQR常用充分條件是(A_d,B_d)可穩定、(Q^(1/2),A_d)可偵測，Q半正定、R正定。較強的完全可控／可觀測可作充分檢查；完整rank不等於輸入有限時有足夠散熱能力。必要時用PBH檢查不穩定模態，避免只有數值rank一個數字。[SciPy DARE條件](https://docs.scipy.org/doc/scipy-1.14.1/reference/generated/scipy.linalg.solve_discrete_are.html)
4. **狀態看不到就先處理估測。** 我應檢查(A_d,C)的可觀測／可偵測性、噪聲和模型失配。Kalman濾波器是估測器，LQR是控制器；符合標準線性隨機假設的組合才可談LQG。把任意估測器接LQR不自動繼承分離原理的保證。
5. **Q／R要按量尺比較。** 可先選可接受偏差尺度，再把溫度°C、風扇比例與PWM正規化，記錄權重定義。單純同倍率放大Q、R通常不改變標準無限時域增益；增加某個Q相對R通常更重視該狀態，但不能保證每個多變數暫態都單調改善。v²是二次操作代價，不是真實風扇Wh。
6. **限幅、slew與延遲另算。** 原始命令可能要求負PWM或超過100%。實施限幅後是受限制的LQR回授，不能仍稱原無限制問題的最優解；也不能由命令合規推論熱源不超溫。若硬限制是研究主題，MPC可明確處理限制，但仍受散熱能力與模型影響。
7. **求解成功後還要驗算。** 檢查P近似對稱、有限值／半正定、DARE殘差及A_d−B_dK的特徵值；離散局部理想閉迴路要求模長<1。還須另外檢查估測器、飽和、延遲與失配，不能只看solve_discrete_are沒拋錯。[SciPy](https://docs.scipy.org/doc/scipy-1.14.1/reference/generated/scipy.linalg.solve_discrete_are.html)
8. **Regulation不等於任意tracking。** 非零設定值需平衡點與前饋；持續未知擾動或模型偏差可能留下穩態誤差。積分增廣／LQI是可考慮的擴充，仍需可穩定性、飽和與anti-windup設計。本次僅整理，沒有把它稱為已完成方法。[dlqr積分選項](https://python-control.readthedocs.io/en/stable/generated/control.dlqr.html)
9. **比較方法時資訊必須公平。** 同一外部plant、負載、初始狀態、感測、校正預算、輸入限制與切分；完整真值LQR不能直接和只有兩個感測點的方法宣稱公平。分別報估測誤差、追蹤、超溫、能耗與成本。較複雜模型已有退步反例，不由形式較複雜推定一定較好。

## 程式檢查的最小主線

以下是教學骨架，沒有填入假造的機箱參數或實驗結果：

```python
P = scipy.linalg.solve_discrete_are(Ad, Bd, Q, R)
K = numpy.linalg.solve(R + Bd.T @ P @ Bd, Bd.T @ P @ Ad)
closed_loop_eigenvalues = numpy.linalg.eigvals(Ad - Bd @ K)
# 檢查對稱性、DARE殘差與 eigenvalues，再做估測／飽和／延遲的動態驗證
proposal = u_eq - K @ estimated_error
# 實際 PWM／slew 限制套用後，另外紀錄飽和比例與溫度結果
```

不能把教學骨架當作已驗證控制器。既有專案實作和結果已在HTML中列明，本次沒有重跑、更改或新增LQR優越性主張。

## 代表論文：我需要能回答的重點

R. E. Kalman (1960), *Contributions to the Theory of Optimal Control*, *Boletín de la Sociedad Matemática Mexicana*, second series5,102–119。[原始論文](https://boletin.math.org.mx/pdf/2/5/BSMM%282%29.5.102-119.pdf)

- **研究問題：**在線性系統中，如何以二次損失嚴格定義最優調節，並處理解存在與穩定性。
- **貢獻：**以狀態空間、可控／可觀測與Riccati連結調節理論；不是一篇CPU散熱實驗。
- **最重要的假設：**紙本p.104（PDF3）控制部分把狀態視為精確已知。我的稀疏量測不直接滿足它。
- **最容易說錯的結論：**原文p.114（PDF13）的穩定定理有一致完全可控／可觀測及權重有界等條件；不能說「只要成本最小，任何系統都穩定」。
- **我和原文的差別：**用離散估測狀態、受限PWM與非線性熱模型的局部線性化；這些需要新的驗證，不能把原定理整套套到實機。

本次重核官方可解析原文的p.104／114；新下載PDF連線逾時，沒有宣稱本次重新目視原頁。10/6原文閱讀與頁面核對範圍維持[原筆記](lqr_kalman1960_reading_2026-10-06_zh.md)記載，未逐行重證全部證明。

## 我可以用的五分鐘講稿

第一分鐘：我介紹LQR是線性二次調節器，把溫度偏差與操作代價放入成本，用模型求回授，而不是由控制器自動得到熱模型。

第二分鐘：我先確認可達的平衡點，以偏差狀態與操作修正描述問題。Q表示哪些偏差重要，R表示操作代價；權重要按單位與量尺設計。

第三分鐘：我介紹Kalman1960的研究問題與貢獻，說明Riccati導出狀態回授；現代教學式與原文記號分開，不聲稱已重證全部定理。

第四分鐘：原文控制部分假設狀態精確已知，而我只有少量溫度感測，需要估測器。原文穩定性也有條件，不能把求解成功或限幅當成真實安全。

第五分鐘：我把它連回機箱：先建立可信的動態模型與工作點，再檢查狀態資訊、離散閉迴路、飽和和延遲。公開場景若只有穩態CFD，就先用來理解熱路徑，另找可逐步操作的動態plant作LQR比較。
