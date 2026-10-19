# 控制理論代表性原始論文與推薦選讀（2026-10-19）

## 目的及證據界線

這份文件盤點與 LQR 並列討論的 **PI／PID、MPC（含 DMC）、Kalman Filter** 是否有適合教授報告的經典代表文獻，並補充受限 MPC 與常見基準法的定位。每個條目標明「經典早期論文／技術發展／綜述」，避免將後人的教學版公式誤稱原文發明。書目信息和摘要要點依出版商、學術機構或文獻索引可查頁面核對；除另行註明，並未宣稱逐頁細讀全文或可自由轉存受版權保護 PDF。

**與原本 LQR 單篇報告分開**：Kalman（1960）最優控制導讀仍以 `docs/reports/lqr_kalman1960_paper_only_2026-10-19_zh.md` 為主，本清單是另外的後續選讀建議。

## 一、代表文獻總覽

| 方法 | 代表文獻（類型） | 核心問題 | 為什麼值得報告 |
|---|---|---|---|
| PI / PID 早期整定 | Ziegler & Nichols (1942), *Optimum Settings for Automatic Controllers*（經典整定論文） | 如何由實際製程特徵取得控制器設定 | 可由 P/I/D 控制效果、整定公式及適用範圍切入；不應稱此文「發明 PID」 |
| PID 自動整定 | Åström & Hägglund (1984), *Automatic Tuning of Simple Regulators with Specifications on Phase and Amplitude Margins*（技術研究） | 如何自動估計臨界增益／頻率並整定 PID | 數學與工程程序並重，且可取得學校公開版 PDF |
| MPC 早期工業研究 | Richalet et al. (1978), *Model Predictive Heuristic Control: Applications to Industrial Processes*（早期代表論文） | 利用過程模型對未來輸出做預測並求控制動作 | 直接理解預測軌跡、回授修正與工業動機 |
| MPC / DMC | Cutler & Ramaker (1980), *Dynamic Matrix Control—A Computer Control Algorithm*（經典工業技術論文） | 用動態響應矩陣表達過程並設計多變數控制 | 有原始會議 PDF 可直接讀，適合與 PID 的思路做比較 |
| MPC 概覽 | García, Prett & Morari (1989), *Model Predictive Control: Theory and Practice—A Survey*（綜述，不是最早原論文） | MPC 的共通設計架構和產業實務 | 適合先建立全貌，再深入 1978/1980 |
| 受限 MPC 的理論 | Mayne et al. (2000), *Constrained Model Predictive Control: Stability and Optimality*（理論論文） | 在輸入／狀態約束下如何討論穩定性和最優性 | 適合教授追問：「加入控制限制後為什麼不能直接保證穩定？」 |
| Kalman Filter 狀態估測 | R. E. Kalman (1960), *A New Approach to Linear Filtering and Prediction Problems*（奠基研究） | 利用模型與量測估測系統狀態 | 可以獨立報告，並釐清它不是 LQR 最優控制論文 |

## 二、可追溯書目與原文入口

### 1. PI／PID：Ziegler–Nichols（1942）

- J. G. Ziegler and N. B. Nichols, “Optimum Settings for Automatic Controllers,” *Transactions of the ASME* / 典藏索引 *Journal of Fluids Engineering*, **64**(8), 759–765, 1942。
- DOI: https://doi.org/10.1115/1.4019264
- [出版／索引及摘要](https://cir.nii.ac.jp/crid/1360861295470097280?lang=en)
- 原文摘要涉及控制器各種作用、製程反應特徵與快速調整控制器的公式；**不是**所有 PI/PID 行為的穩定性普遍證明，也不是硬體或任何一個應用的最優保證。
- **PI 沒有必要硬找一篇獨立的「唯一創始論文」**：PI 是比例／積分控制組合，可用這篇 P-I-D 整定代表作來導讀，但要明確交代選文原因。

### 2. PID：Åström–Hägglund（1984）

- K. J. Åström and T. Hägglund, “Automatic Tuning of Simple Regulators with Specifications on Phase and Amplitude Margins,” *Automatica*, **20**(5), 645–651, 1984。
- DOI: https://doi.org/10.1016/0005-1098(84)90014-1
- [Lund University 學術典藏](https://portal.research.lu.se/en/publications/automatic-tuning-of-simple-regulators-with-specifications-on-phas/)
- [Lund University 可讀 PDF](https://lup.lub.lu.se/search/ws/files/6340936/8509157.pdf)
- 論文摘要描述用測試訊號估計臨界增益和頻率，依相位裕度／增益裕度要求自動整定 PID。這是**整定策略**的經典，而不是整體 PID 所有理論的起源。

### 3. MPC：Richalet 等人（1978）

- J. Richalet, A. Rault, J.-L. Testud, and J. Papon, “Model Predictive Heuristic Control: Applications to Industrial Processes,” *Automatica*, **14**(5), 413–428, 1978。
- DOI: https://doi.org/10.1016/0005-1098(78)90001-8
- [出版商書目與摘要](https://www.sciencedirect.com/science/article/pii/0005109878900018)
- 摘要可確認：以過程脈衝響應表示多變數模型、作較長距離的輸出預測、採用參考軌跡與控制計算程序。是早期工業預測控制的重要代表，**不能**把現代完整 QP/MPC 最佳化程式直接視為論文的原式。

### 4. MPC / DMC：Cutler–Ramaker（1980）

- C. R. Cutler and B. L. Ramaker, “Dynamic Matrix Control—A Computer Control Algorithm,” *Proceedings of the Joint Automatic Control Conference*, 1980, WP5.B1–WP5.B6。
- [日本 JST J-GLOBAL 書目紀錄](https://jglobal.jst.go.jp/en/detail?JGLOBAL_ID=200902055067084269)
- [NTNU 封存原始會議 PDF](https://skoge.folk.ntnu.no/puublications_others/1980_Cutler-Ramaker_Dynamic-matrix-control_JACC1980.pdf)
- 作者以製程動態響應係數及最小平方型計算建立 DMC，強調多變數與延遲系統的處理。這比背「每次解一次 MPC 最佳化」更能說明原始工業動機。

### 5. MPC 全貌：García–Prett–Morari（1989）

- C. E. García, D. M. Prett, and M. Morari, “Model Predictive Control: Theory and Practice—A Survey,” *Automatica*, **25**(3), 335–348, 1989。
- DOI: https://doi.org/10.1016/0005-1098(89)90002-2
- [出版商摘要](https://www.sciencedirect.com/science/article/abs/pii/0005109889900022)
- 建議作為理解「什麼方法都算 MPC」的總覽；**類型是綜述**，適合補充背景，不應稱為最早提出 MPC 的論文。

### 6. 約束與穩定性：Mayne 等人（2000）

- D. Q. Mayne, J. B. Rawlings, C. V. Rao, and P. O. M. Scokaert, “Constrained Model Predictive Control: Stability and Optimality,” *Automatica*, **36**(6), 789–814, 2000。
- DOI: https://doi.org/10.1016/S0005-1098(99)00214-9
- [出版書目紀錄](https://cir.nii.ac.jp/crid/1363951795880364800)
- 與本次問答的「控制幅度限制後仍會穩定嗎？」高度對應；**不是說所有使用 MPC 的系統都有無條件穩定保證**，需看具體可行性、約束與終端設計等條件。

### 7. 狀態估測：Kalman（1960）的另一篇論文

- R. E. Kalman, “A New Approach to Linear Filtering and Prediction Problems,” *Journal of Basic Engineering*, **82**(1), 35–45, 1960。
- DOI: https://doi.org/10.1115/1.3662552
- [出版索引與原文入口](https://cir.nii.ac.jp/crid/1360855570047666048)
- 此文研究濾波與預測問題，將最優估測誤差的共變異矩陣和差分／微分方程相連，並討論估測與調節器問題的對偶性。這才是 Kalman Filter 的代表作；**不是**目前報告的 *Contributions to the Theory of Optimal Control*。

### 8. 更早的控制史：Minorsky（1922，可選）

- N. Minorsky, “Directional Stability of Automatically Steered Bodies,” *Journal of the American Society for Naval Engineers*, **34**(2), 280–309, 1922。
- DOI: https://doi.org/10.1111/j.1559-3584.1922.tb04958.x
- [出版商原始書目](https://onlinelibrary.wiley.com/doi/10.1111/j.1559-3584.1922.tb04958.x)
- 可當自動操舵與早期控制史補充，但若想報告「怎麼整定 PI/PID」，1942 Ziegler–Nichols 通常更直接；不要將此控制史文本與 1942 年整定法混為一談。

## 三、怎麼選擇下一篇最容易講給教授聽

| 閱讀目的 | 首選 | 原因 |
|---|---|---|
| 要能解釋 PI、PID 怎麼運作／整定 | **Ziegler & Nichols 1942** | P、I、D 與整定規則是中心問題；與 LQR 很不一樣，適合練習比較概念 |
| 想要公開可讀的完整論文 | **Åström & Hägglund 1984** | 學校典藏公開 PDF，便於逐頁閱讀和驗算 |
| 想先建立 MPC 全貌 | **García、Prett、Morari 1989** | 綜述架構完整，但不是原創方法論文 |
| 要找和 Kalman 1960 類似的「早期代表原論文」 | **Richalet 1978** 或 **Cutler–Ramaker 1980** | 兩篇均是 MPC/DMC 初期重要研究，後者有可讀原始 PDF |
| 要釐清 LQR vs Kalman Filter | **Kalman 1960 filtering** | 兩篇同作者同年份，但研究問題不同 |
| 要深入控制限制和穩定性 | **Mayne et al. 2000** | 約束 MPC 穩定／最優性的理論重點較深，建議最後再讀 |

建議**第一步讀 PID 的 Ziegler–Nichols（1942）或 Åström–Hägglund（1984），第二步讀 Cutler–Ramaker（1980）的 DMC，第三步才讀 Mayne 等人的約束 MPC 理論**。若目的是更純粹的經典原始文獻導讀，選 1942 PID + 1980 DMC 的組合即可。

## 四、其他常見基準法的書目定位

- **Persistence（前值維持）**：是時間序列預測的基準規則；通常沒有像 LQR/Riccati 一樣單一、普遍公認的「發明此規則」代表論文。宜選與比較資料條件相符的預測方法／基準定義論文，而非硬指派一篇創始作。
- **純物理熱模型**：可追溯到熱傳導、對流及集中參數模型的不同脈絡，不宜硬把它們合併成一篇「純物理模型的創始論文」。若需研究應用，應依實際採用的 RC／熱阻熱容／CFD 形式選典型建模文獻。
- **PI 與 PID**：兩者有共同的控制器及整定文獻，應解釋各自省略／保留的項，不必為了湊數將相同方法說成不同原始論文。

## 五、下一次若做獨立論文導讀，建議採一致的審查流程

1. 取得原始 PDF 或出版商摘要，核對作者、年份、期刊／會議、原文頁碼；**沒有原文 PDF 時先標註未全文核對**。
2. 先講論文自己的研究問題、假設、方程與結果，再另用一頁現代教科書表示法比較；不要把現代公式放回原文口中。
3. 做至少一個可以手算的簡化範例，但註明是**教學例題**。
4. 把主要貢獻與適用限制分開報告；不要把「經典」等同於任何條件都最優。
5. 若做 PI/PID/MPC 等不同方法的論文報告，**每一份保持單篇獨立**，不要插入其他研究專案的實驗資料或宣稱具備未驗證的效果。

## 六、已完成的獨立論文導讀與簡報

可由 [論文導讀索引](../reports/control_theory_paper_guides_2026-10-19_zh.md) 進入 Kalman 1960 LQR、Ziegler–Nichols 1942 PID、Cutler–Ramaker 1980 DMC 的獨立 Markdown 講稿和 HTML 簡報。
