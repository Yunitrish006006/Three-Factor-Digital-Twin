# 機箱傳熱場景與控制機制查證（2026-10-06）

本次實際查閱日期為 2026-10-06。以下整理只支持候選設計；不是實測裝置成效。既有室內模型的 20–30 °C 適用性不因這些案例而擴張。

## 裝置與場景

| 場景／來源 | 查閱範圍與來源支持 | 對模型的啟示（本研究推論） | 需要的量測 |
|---|---|---|---|
| 處理器接觸金屬散熱器／導熱介面：[TI SPRABI3B](https://www.ti.com/lit/an/sprabi3b/sprabi3b.pdf) | PDF 第 3–4 頁 compact model／CM 與 CFD、第 6–7 頁 §5.6–5.6.1。區分固體導熱與空氣對流，並指出接觸與環境條件影響傳熱。 | 熱源與金屬片分為不同熱容量節點，以有效接觸熱導連接；不能只改風扇增益。 | 熱源驗證溫度、金屬片溫度、入口與局部空氣溫度、輸入熱功率 |
| 小型機箱進氣風管：[Noctua NA-FD1](https://www.noctua.at/en/products/na-fd1) | Overview 與 Key features。EVA foam 風管把風扇與穿孔面板連接，減少吸入機箱內熱空氣。此裝置不是金屬導熱風管。 | 導流和回流主要改變入口邊界及對流交換；不能把廠商特定配置降溫幅度當成自己的參數或成果。 | 外部入口與散熱器入口溫度、RPM、PWM、必要時風量／壓差 |
| PCB 金屬散熱路徑：[TI SPRABI3B](https://www.ti.com/lit/an/sprabi3b/sprabi3b.pdf) | PDF 第 10 頁 §7 與 Fig. 4：processor-to-PCB thermal paths。 | PCB／金屬底板可能是平行傳熱路徑，後续應依辨識與量測需求決定是否增加節點。 | PCB／底板溫度、幾何與接觸資料；目前未取得 |

我選擇先研究「可控熱源＋金屬片／散熱片＋風扇／風管」的小型候選平台。這是設計選擇，未購買、未製作；低功率 synthetic rig 用來檢查稀疏感測與動作排序介面，不等於 CPU／GPU 或真實桌機。

## 控制方法可以借用什麼

| 方法與來源 | 實際閱讀範圍 | 可以借用的機制與限制 | 本輪採用狀態 |
|---|---|---|---|
| PI／PID：[University of Michigan control introduction](https://eecs.umich.edu/courses/eecs373.w05/lecture/control.html) | 線上課程控制介紹與 P／I／D 段落 | 誤差回授、積分處理持續偏差、微分反映變化；積分飽和與噪聲代價需處理。不能保证任何非線性受限系統都零誤差。 | PI、PID 作共享稀疏估測輸入的 comparator，具命令限幅與 back-calculation |
| MPC：[OSQP 官方範例](https://osqp.org/docs/examples/mpc.html) | 離散狀態模型、quadratic objective、input/state bounds、receding-horizon loop | 多步評估、共同限制、下一步重算；本輪有限候選 constant-request 排序不是完整 QP MPC。 | 借用多步預測與只執行第一步；用 H=1 消融 |
| LQR：[SciPy DARE](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.solve_discrete_are.html) | DARE 定義、solver 條件與範例 | 溫度與動作二次代價有清楚權衡；代價相似不代表算法是 LQR。 | 借用成本分層思路；LQR 實作比較留在 10/5 v2，不將本輪排序稱為 LQR |
| 擾動補償：[Pannocchia & Rawlings (2003)](https://aiche.onlinelibrary.wiley.com/doi/10.1002/aic.690490213) | 出版者摘要與書目，未查閱全文 | 摘要指出 integrating disturbances 可描述 mismatch，並有可控變數／條件限制；不能直接推論這裡可 offset-free。 | 僅列後續候選，不實作、不稱已完成閱讀全文 |

「LQZ」仍保留會議原文，待使用者確認；本輪不把它解讀成已確認的 LQR。

## 我自己的方法要如何遷移

原有方法是 reduced-order physics → 稀疏觀測校正 → 可選殘差 → 候選動作預測／排序。本轮將此流程轉成獨立溫度候選原型：多節點熱網路 → 金屬片與空氣感測更新 → H 步 PWM 排序 → 下一步重新估測。原室內三因子、八角點與空間殘差網路沒有直接搬用；不宣稱完整三因子遷移已完成。

辨識與控制選參分開。先以同一有限 calibration 程序辨識接觸熱導和對流風扇增益；再固定所有控制設定。所有硬體係數目前均是假設值；以新的 synthetic workload、初始狀態與參數變體執行驗證，不重用 E15 或已開啟 v1／v2 holdout。
