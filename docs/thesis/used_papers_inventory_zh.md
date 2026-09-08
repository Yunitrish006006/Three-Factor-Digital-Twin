# 主稿實際使用論文清單

盤點日期：2026-09-08。此文件盤點中英文正式來源的既有引用，不更動研究結論。

合計 **36 篇外部論文**（含 2 篇資料集描述論文），另有 **6 筆資料集、1 份網站文件**。中文書目涵蓋 34 篇外部論文；英文稿另引用 Tao 2019 與 Fuller 2020。主論文本身不計入外部文獻。

原 3D 視圖的 35 篇＝主論文 1 篇＋中文書目中的外部論文 34 篇；因此不能當成中英文合併後的外部論文總數。

以下「用途」是對主稿引用方式的整理；不代表已重新閱讀外部全文，也不代表原論文的章節、頁碼或實驗結果已核實。DOI 沿用現有書目。

## 閱讀索引

| 類別 | 論文編號 |
| --- | --- |
| 建築數位孿生與研究定位 | [7] |
| 室內熱模型、空間估測與感測器配置 | [1], [2], [3], [4], [5], [6], [8], [9], [10] |
| 房間環境、舒適度與現地實驗 | [18], [19], [20], [21], [22], [23], [24], [25] |
| Residual、RNN 與 Kalman 方法 | [26], [27], [28], [31], [32] |
| 候選植物生長應用 | [29], [30] |
| 機箱、資料中心與局部插值 | [33], [34], [37], [38], [39], [40], [41] |
| 資料集描述論文 | [12], [17] |
| 英文稿獨有的數位孿生文獻 | Tao 2019、Fuller 2020 |

## 逐篇清單

### 建築數位孿生與研究定位

#### [7] A review of building digital twins to improve energy efficiency in the building operational stage

- 書目：Andres Sebastian Cespedes-Cubides, Muhyiddine Jradi, A review of building digital twins to improve energy efficiency in the building operational stage, Energy Informatics, vol. 7, article 11, 2024. DOI: 10.1186/s42162-024-00313-7
- 本論文用途：建築數位孿生研究背景與本研究定位。
- 實際引用位置：2.3 數位孿生與智慧建築（[thesis_draft_zh.md L370](thesis_draft_zh.md#L370)）；2.7 與相似研究之差異定位（[thesis_draft_zh.md L403](thesis_draft_zh.md#L403)）；Related Work（[paper.tex L60](../papers/ieee/paper.tex#L60)）
- 原文入口：[DOI](https://doi.org/10.1186/s42162-024-00313-7)。
- 比較邊界：此處記錄引用用途，未建立與原文相同資料／任務的直接優劣比較。

### 室內熱模型、空間估測與感測器配置

#### [1] Identifying suitable models for the heat dynamics of buildings

- 書目：Per Bacher, Henrik Madsen, Identifying suitable models for the heat dynamics of buildings, Energy and Buildings, vol. 43, no. 7, pp. 1511-1522, 2011. DOI: 10.1016/j.enbuild.2011.02.005
- 本論文用途：簡化熱動態與 grey-box 建模依據。
- 實際引用位置：2.1 室內環境建模（[thesis_draft_zh.md L362](thesis_draft_zh.md#L362)）；Related Work（[paper.tex L60](../papers/ieee/paper.tex#L60)）
- 原文入口：[DOI](https://doi.org/10.1016/j.enbuild.2011.02.005)。
- 比較邊界：此處記錄引用用途，未建立與原文相同資料／任務的直接優劣比較。

#### [2] A Dynamic Model for Indoor Temperature Prediction in Buildings

- 書目：Petri Hietaharju, Mika Ruusunen, Kauko Leiviska, A Dynamic Model for Indoor Temperature Prediction in Buildings, Energies, vol. 11, no. 6, 1477, 2018. DOI: 10.3390/en11061477
- 本論文用途：室內溫度動態預測與低參數模型依據。
- 實際引用位置：2.1 室內環境建模（[thesis_draft_zh.md L362](thesis_draft_zh.md#L362)）；Related Work（[paper.tex L60](../papers/ieee/paper.tex#L60)）
- 原文入口：[DOI](https://doi.org/10.3390/en11061477)。
- 比較邊界：此處記錄引用用途，未建立與原文相同資料／任務的直接優劣比較。

#### [3] Physics informed neural networks for control oriented thermal modeling of buildings

- 書目：Gargya Gokhale, Bert Claessens, Chris Develder, Physics informed neural networks for control oriented thermal modeling of buildings, Applied Energy, vol. 314, 118852, 2022. DOI: 10.1016/j.apenergy.2022.118852
- 本論文用途：物理導向與神經網路結合的建模背景。
- 實際引用位置：2.1 室內環境建模（[thesis_draft_zh.md L362](thesis_draft_zh.md#L362)）
- 原文入口：[DOI](https://doi.org/10.1016/j.apenergy.2022.118852)。
- 比較邊界：此處記錄引用用途，未建立與原文相同資料／任務的直接優劣比較。

#### [4] Zonal Models for Indoor Air Flow - A Critical Review

- 書目：E. J. Teshome, F. Haghighat, Zonal Models for Indoor Air Flow - A Critical Review, International Journal of Ventilation, vol. 3, no. 2, pp. 119-129, 2004. DOI: 10.1080/14733315.2004.11683908
- 本論文用途：zonal model 的方法背景與適用範圍。
- 實際引用位置：2.2 空間插值與場估計（[thesis_draft_zh.md L366](thesis_draft_zh.md#L366)）；Related Work（[paper.tex L60](../papers/ieee/paper.tex#L60)）
- 原文入口：[DOI](https://doi.org/10.1080/14733315.2004.11683908)。
- 比較邊界：此處記錄引用用途，未建立與原文相同資料／任務的直接優劣比較。

#### [5] Hybrid models for simulating indoor temperature distribution in air-conditioned spaces

- 書目：Boris Huljak, Juan A. Acero, Zin H. Kyaw, Francisco Chinesta, Hybrid models for simulating indoor temperature distribution in air-conditioned spaces, Frontiers in Built Environment, vol. 11, 1690062, 2025. DOI: 10.3389/fbuil.2025.1690062
- 本論文用途：hybrid 空間溫度模型的相似研究及差異定位。
- 實際引用位置：2.2 空間插值與場估計（[thesis_draft_zh.md L366](thesis_draft_zh.md#L366)）；2.5 非連網裝置影響學習（[thesis_draft_zh.md L382](thesis_draft_zh.md#L382)）；2.7 與相似研究之差異定位（[thesis_draft_zh.md L390](thesis_draft_zh.md#L390)）；2.7 與相似研究之差異定位（[thesis_draft_zh.md L399](thesis_draft_zh.md#L399)）；Related Work（[paper.tex L60](../papers/ieee/paper.tex#L60)）
- 原文入口：[DOI](https://doi.org/10.3389/fbuil.2025.1690062)。
- 比較邊界：此處記錄引用用途，未建立與原文相同資料／任務的直接優劣比較。

#### [6] A new dynamic zOnal model with air-diffuser (DOMA) - Application to thermal comfort prediction

- 書目：Ahmed Megri, Yao Yu, Rui Miao, Xiaoou Hu, A new dynamic zOnal model with air-diffuser (DOMA) - Application to thermal comfort prediction, Indoor and Built Environment, vol. 31, no. 7, pp. 1738-1757, 2022. DOI: 10.1177/1420326X211060486
- 本論文用途：動態 zonal／送風模型的相似研究及差異定位。
- 實際引用位置：2.2 空間插值與場估計（[thesis_draft_zh.md L366](thesis_draft_zh.md#L366)）；2.7 與相似研究之差異定位（[thesis_draft_zh.md L390](thesis_draft_zh.md#L390)）；2.7 與相似研究之差異定位（[thesis_draft_zh.md L401](thesis_draft_zh.md#L401)）
- 原文入口：[DOI](https://doi.org/10.1177/1420326X211060486)。
- 比較邊界：此處記錄引用用途，未建立與原文相同資料／任務的直接優劣比較。

#### [8] Estimating indoor air temperature and humidity distributions by data assimilation with finite observations: Validation using an actual residential room

- 書目：Weixin Qian, Chenxi Li, Hu Gao, Lei Zhuang, Yanyu Lu, Site Hu, Jing Liu, Estimating indoor air temperature and humidity distributions by data assimilation with finite observations: Validation using an actual residential room, Building and Environment, vol. 269, 112495, 2025. DOI: 10.1016/j.buildenv.2024.112495
- 本論文用途：有限觀測、資料同化與室內溫濕度場重建的相似研究。
- 實際引用位置：2.5 非連網裝置影響學習（[thesis_draft_zh.md L382](thesis_draft_zh.md#L382)）；2.7 與相似研究之差異定位（[thesis_draft_zh.md L390](thesis_draft_zh.md#L390)）；2.7 與相似研究之差異定位（[thesis_draft_zh.md L398](thesis_draft_zh.md#L398)）；Related Work（[paper.tex L60](../papers/ieee/paper.tex#L60)）
- 原文入口：[DOI](https://doi.org/10.1016/j.buildenv.2024.112495)。
- 比較邊界：此處記錄引用用途，未建立與原文相同資料／任務的直接優劣比較。

#### [9] Application of zonal model on indoor air sensor network design

- 書目：Y. Lisa Chen, Jin Wen, Application of zonal model on indoor air sensor network design, Proceedings of SPIE, vol. 6529, 652911, 2007. DOI: 10.1117/12.716356
- 本論文用途：感測器配置與 zonal model 的方法背景。
- 實際引用位置：2.5 非連網裝置影響學習（[thesis_draft_zh.md L382](thesis_draft_zh.md#L382)）；2.7 與相似研究之差異定位（[thesis_draft_zh.md L402](thesis_draft_zh.md#L402)）；Related Work（[paper.tex L60](../papers/ieee/paper.tex#L60)）
- 原文入口：[DOI](https://doi.org/10.1117/12.716356)。
- 比較邊界：此處記錄引用用途，未建立與原文相同資料／任務的直接優劣比較。

#### [10] A Two-Dimensional Interpolation Function for Irregularly-Spaced Data

- 書目：D. Shepard, A Two-Dimensional Interpolation Function for Irregularly-Spaced Data, Proceedings of the 1968 ACM National Conference, pp. 517-524, 1968.
- 本論文用途：IDW baseline 的文獻依據；中文列入書目但未找到編號引用，英文有明確引用。
- 實際引用位置：Related Work（[paper.tex L60](../papers/ieee/paper.tex#L60)）
- 比較邊界：方法引用與本地 baseline／實驗比較須分開記錄；本地數值不等同原論文數值。

### 房間環境、舒適度與現地實驗

#### [18] Influence of indoor temperature and daylight illuminance on visual perception

- 書目：G. Chinazzo, J. Wienold, M. Andersen, Influence of indoor temperature and daylight illuminance on visual perception, Lighting Research and Technology, vol. 52, no. 8, pp. 998-1020, 2020. DOI: 10.1177/1477153519859609
- 本論文用途：室溫與日光照度聯合實驗的文獻背景。
- 實際引用位置：2.4 房間尺度室內因子實驗研究（[thesis_draft_zh.md L374](thesis_draft_zh.md#L374)）
- 原文入口：[DOI](https://doi.org/10.1177/1477153519859609)。
- 比較邊界：此處記錄引用用途，未建立與原文相同資料／任務的直接優劣比較。

#### [19] Daylight affects human thermal perception

- 書目：G. Chinazzo, J. Wienold, M. Andersen, Daylight affects human thermal perception, Scientific Reports, vol. 9, article 13695, 2019. DOI: 10.1038/s41598-019-48963-y
- 本論文用途：日光與熱感知交互作用的文獻背景。
- 實際引用位置：2.4 房間尺度室內因子實驗研究（[thesis_draft_zh.md L374](thesis_draft_zh.md#L374)）
- 原文入口：[DOI](https://doi.org/10.1038/s41598-019-48963-y)。
- 比較邊界：此處記錄引用用途，未建立與原文相同資料／任務的直接優劣比較。

#### [20] Experimental study on the impact of indoor lighting and thermal environment on university students' learning performance in summer

- 書目：Lan et al., Experimental study on the impact of indoor lighting and thermal environment on university students' learning performance in summer, Energy and Buildings, vol. 331, 115774, 2025. DOI: 10.1016/j.enbuild.2025.115774
- 本論文用途：熱環境、照明與學習表現的房間尺度實驗背景。
- 實際引用位置：2.4 房間尺度室內因子實驗研究（[thesis_draft_zh.md L374](thesis_draft_zh.md#L374)）
- 原文入口：[DOI](https://doi.org/10.1016/j.enbuild.2025.115774)。
- 比較邊界：此處記錄引用用途，未建立與原文相同資料／任務的直接優劣比較。

#### [21] Studying the Indoor Environment and Comfort of a University Laboratory: Air-Conditioning Operation and Natural Ventilation Used as a Countermeasure against COVID-19

- 書目：K. Kuwahara et al., Studying the Indoor Environment and Comfort of a University Laboratory: Air-Conditioning Operation and Natural Ventilation Used as a Countermeasure against COVID-19, Buildings, vol. 12, no. 7, 953, 2022. DOI: 10.3390/buildings12070953
- 本論文用途：冷氣與自然通風操作的現地量測背景。
- 實際引用位置：2.4 房間尺度室內因子實驗研究（[thesis_draft_zh.md L376](thesis_draft_zh.md#L376)）
- 原文入口：[DOI](https://doi.org/10.3390/buildings12070953)。
- 比較邊界：此處記錄引用用途，未建立與原文相同資料／任務的直接優劣比較。

#### [22] Indoor environmental quality and energy use evaluation of a three-star green office building in China with field study

- 書目：Yan Zhou, Jianmin Cai, Yiwen Xu, Indoor environmental quality and energy use evaluation of a three-star green office building in China with field study, Journal of Building Physics, vol. 45, no. 2, pp. 163-190, 2021. DOI: 10.1177/1744259120944604
- 本論文用途：綠建築辦公室 IEQ 與能源使用的現地研究背景。
- 實際引用位置：2.4 房間尺度室內因子實驗研究（[thesis_draft_zh.md L376](thesis_draft_zh.md#L376)）
- 原文入口：[DOI](https://doi.org/10.1177/1744259120944604)。
- 比較邊界：此處記錄引用用途，未建立與原文相同資料／任務的直接優劣比較。

#### [23] Indoor environment quality in a low-energy residential building in winter in Harbin

- 書目：Z. Wang, Q. Xue, Y. Ji, Z. Yu, Indoor environment quality in a low-energy residential building in winter in Harbin, Building and Environment, vol. 135, pp. 194-201, 2018. DOI: 10.1016/j.buildenv.2018.03.012
- 本論文用途：住宅冬季 IEQ 的現地量測背景。
- 實際引用位置：2.4 房間尺度室內因子實驗研究（[thesis_draft_zh.md L376](thesis_draft_zh.md#L376)）
- 原文入口：[DOI](https://doi.org/10.1016/j.buildenv.2018.03.012)。
- 比較邊界：此處記錄引用用途，未建立與原文相同資料／任務的直接優劣比較。

#### [24] Comparative study on indoor environment quality of green office buildings with different levels of energy use intensity

- 書目：Y. Geng, B. Lin, Y. Zhu, Comparative study on indoor environment quality of green office buildings with different levels of energy use intensity, Building and Environment, vol. 168, 106482, 2020. DOI: 10.1016/j.buildenv.2019.106482
- 本論文用途：辦公室能源使用與 IEQ 的比較背景。
- 實際引用位置：2.4 房間尺度室內因子實驗研究（[thesis_draft_zh.md L378](thesis_draft_zh.md#L378)）
- 原文入口：[DOI](https://doi.org/10.1016/j.buildenv.2019.106482)。
- 比較邊界：此處記錄引用用途，未建立與原文相同資料／任務的直接優劣比較。

#### [25] A Comparative Field Study of Indoor Environment Quality and Work Productivity between Job Types in a Research Institute in Korea

- 書目：J. Lee et al., A Comparative Field Study of Indoor Environment Quality and Work Productivity between Job Types in a Research Institute in Korea, International Journal of Environmental Research and Public Health, vol. 19, no. 21, 14332, 2022. DOI: 10.3390/ijerph192114332
- 本論文用途：工作型態、IEQ 與生產力的比較背景。
- 實際引用位置：2.4 房間尺度室內因子實驗研究（[thesis_draft_zh.md L378](thesis_draft_zh.md#L378)）
- 原文入口：[DOI](https://doi.org/10.3390/ijerph192114332)。
- 比較邊界：此處記錄引用用途，未建立與原文相同資料／任務的直接優劣比較。

### Residual、RNN 與 Kalman 方法

#### [26] Hybrid modeling based on integrating simulation and operational data to improve indoor air temperature predictions, a controlled variable in digital twin models

- 書目：Ju-Hong Oh, Stefano Sfarra, Eui-Jong Kim, Hybrid modeling based on integrating simulation and operational data to improve indoor air temperature predictions, a controlled variable in digital twin models, Energy and Buildings, vol. 324, 114898, 2024. DOI: 10.1016/j.enbuild.2024.114898
- 本論文用途：物理基線加 learned residual 的方法啟發，並有本地移植比較。
- 實際引用位置：2.7 與相似研究之差異定位（[thesis_draft_zh.md L392](thesis_draft_zh.md#L392)）；2.7 與相似研究之差異定位（[thesis_draft_zh.md L400](thesis_draft_zh.md#L400)）；3.8 Hybrid Residual Neural Network 延伸（[thesis_draft_zh.md L886](thesis_draft_zh.md#L886)）；5.9.3 Oh et al. (2024) 方法移植比較（[thesis_draft_zh.md L1318](thesis_draft_zh.md#L1318)）；Related Work（[paper.tex L60](../papers/ieee/paper.tex#L60)）
- 原文入口：[DOI](https://doi.org/10.1016/j.enbuild.2024.114898)。
- 比較邊界：有 Oh2024-inspired 本地方法移植；不等於原文 CNN–LSTM、物理模擬器或原始 BEMS 資料的重現，不能直接宣稱勝過原論文。

#### [27] Finding Structure in Time

- 書目：Jeffrey L. Elman, Finding Structure in Time, Cognitive Science, vol. 14, no. 2, pp. 179-211, 1990. DOI: 10.1207/s15516709cog1402_1
- 本論文用途：Vanilla Elman RNN 的方法依據；本地同資料 RNN 比較。
- 實際引用位置：5.9.3.2 Vanilla RNN 同資料公平比較（[thesis_draft_zh.md L1348](thesis_draft_zh.md#L1348)）
- 原文入口：[DOI](https://doi.org/10.1207/s15516709cog1402_1)。
- 比較邊界：方法引用與本地 baseline／實驗比較須分開記錄；本地數值不等同原論文數值。

#### [28] A New Approach to Linear Filtering and Prediction Problems

- 書目：R. E. Kalman, A New Approach to Linear Filtering and Prediction Problems, Journal of Basic Engineering, vol. 82, no. 1, pp. 35-45, 1960. DOI: 10.1115/1.3662552
- 本論文用途：Kalman 狀態估測架構依據；本地受控濾波比較。
- 實際引用位置：2.9 動態精準環境應用與 Kalman Filter 方向（[thesis_draft_zh.md L438](thesis_draft_zh.md#L438)）
- 原文入口：[DOI](https://doi.org/10.1115/1.3662552)。
- 比較邊界：方法引用與本地 baseline／實驗比較須分開記錄；本地數值不等同原論文數值。

#### [31] Improving climate monitoring in greenhouse cultivation via model based filtering

- 書目：Simon van Mourik, Peter J. M. van Beveren, Irineo L. López-Cruz, Eldert J. van Henten, Improving climate monitoring in greenhouse cultivation via model based filtering, Biosystems Engineering, vol. 181, pp. 40-51, 2019. DOI: 10.1016/j.biosystemseng.2019.03.001
- 本論文用途：模型濾波的限制與負向結果背景，約束 Kalman 效益主張。
- 實際引用位置：2.9 動態精準環境應用與 Kalman Filter 方向（[thesis_draft_zh.md L438](thesis_draft_zh.md#L438)）
- 原文入口：[DOI](https://doi.org/10.1016/j.biosystemseng.2019.03.001)。
- 比較邊界：此處記錄引用用途，未建立與原文相同資料／任務的直接優劣比較。

#### [32] Towards an adaptive model for greenhouse control

- 書目：S. L. Speetjens, J. D. Stigter, G. van Straten, Towards an adaptive model for greenhouse control, Computers and Electronics in Agriculture, vol. 67, no. 1-2, pp. 1-8, 2009. DOI: 10.1016/j.compag.2009.01.012
- 本論文用途：溫室 EKF 線上參數調整的候選方法背景。
- 實際引用位置：2.9 動態精準環境應用與 Kalman Filter 方向（[thesis_draft_zh.md L438](thesis_draft_zh.md#L438)）
- 原文入口：[DOI](https://doi.org/10.1016/j.compag.2009.01.012)。
- 比較邊界：此處記錄引用用途，未建立與原文相同資料／任務的直接優劣比較。

### 候選植物生長應用

#### [29] Reaching Natural Growth: The Significance of Light and Temperature Fluctuations in Plant Performance in Indoor Growth Facilities

- 書目：Camilo Chiang, Daniel Bånkestad, Günter Hoch, Reaching Natural Growth: The Significance of Light and Temperature Fluctuations in Plant Performance in Indoor Growth Facilities, Plants, vol. 9, no. 10, 1312, 2020. DOI: 10.3390/plants9101312
- 本論文用途：植物生長環境的動態溫濕度／光照設定值候選應用。
- 實際引用位置：2.9 動態精準環境應用與 Kalman Filter 方向（[thesis_draft_zh.md L436](thesis_draft_zh.md#L436)）
- 原文入口：[DOI](https://doi.org/10.3390/plants9101312)。
- 比較邊界：此處記錄引用用途，未建立與原文相同資料／任務的直接優劣比較。

#### [30] Preventing Overgrowth of Cucumber and Tomato Seedlings Using Difference between Day and Night Temperature in a Plant Factory with Artificial Lighting

- 書目：Young Ho Kim et al., Preventing Overgrowth of Cucumber and Tomato Seedlings Using Difference between Day and Night Temperature in a Plant Factory with Artificial Lighting, Plants, vol. 12, no. 17, 3164, 2023. DOI: 10.3390/plants12173164
- 本論文用途：植物工廠日夜溫差及光週期的候選應用。
- 實際引用位置：2.9 動態精準環境應用與 Kalman Filter 方向（[thesis_draft_zh.md L436](thesis_draft_zh.md#L436)）
- 原文入口：[DOI](https://doi.org/10.3390/plants12173164)。
- 比較邊界：此處記錄引用用途，未建立與原文相同資料／任務的直接優劣比較。

### 機箱、資料中心與局部插值

#### [33] Model and data driven transient thermal system modelings for contained data centers

- 書目：Yewan Wang, Yiru Zhang, David Nörtershäuser, Stéphane Le Masson, Jean-Marc Menaud, Model and data driven transient thermal system modelings for contained data centers, Energy and Buildings, vol. 258, 111790, 2022. DOI: 10.1016/j.enbuild.2021.111790
- 本論文用途：E11A thermal-balance 與 data-driven 模型分工的設計參考。
- 實際引用位置：5.9.3.4 機箱 BMC 公開資料轉移比較（[thesis_draft_zh.md L1391](thesis_draft_zh.md#L1391)）
- 原文入口：[DOI](https://doi.org/10.1016/j.enbuild.2021.111790)。
- 比較邊界：此處記錄引用用途，未建立與原文相同資料／任務的直接優劣比較。

#### [34] Thermal Elasticity-Aware Host Resource Provision for Carbon Efficiency on Virtualized Servers

- 書目：Da Zhang, Haojun Xia, Xiaotong Wang, Yanchang Feng, Haohao Liu, Bibo Tu, Thermal Elasticity-Aware Host Resource Provision for Carbon Efficiency on Virtualized Servers, IEEE Transactions on Computers, vol. 74, no. 11, pp. 3682-3695, 2025. DOI: 10.1109/TC.2025.3603698
- 本論文用途：BMC 公開資料所對應的伺服器研究背景。
- 實際引用位置：5.9.3.4 機箱 BMC 公開資料轉移比較（[thesis_draft_zh.md L1391](thesis_draft_zh.md#L1391)）
- 原文入口：[DOI](https://doi.org/10.1109/TC.2025.3603698)。
- 比較邊界：此處記錄引用用途，未建立與原文相同資料／任務的直接優劣比較。

#### [37] Energy efficiency enhancement in two European data centers through CFD modeling

- 書目：Onur Muhammed Sarikaya et al., Energy efficiency enhancement in two European data centers through CFD modeling, Scientific Reports, vol. 15, 24952, 2025. DOI: 10.1038/s41598-025-11048-0
- 本論文用途：交叉確認 AAU 機房設備及量測背景。
- 實際引用位置：5.9.3.5 AAU 伺服器機房空間轉移比較（[thesis_draft_zh.md L1407](thesis_draft_zh.md#L1407)）；Bounded AAU Enclosure Transfer（[paper.tex L256](../papers/ieee/paper.tex#L256)）
- 原文入口：[DOI](https://doi.org/10.1038/s41598-025-11048-0)。
- 比較邊界：此處記錄引用用途，未建立與原文相同資料／任務的直接優劣比較。

#### [38] Fast inverse distance weighting-based spatiotemporal interpolation: A web-based application of interpolating daily fine particulate matter PM2.5 in the contiguous U.S. using parallel programming and k-d tree

- 書目：L. Li, T. Losser, C. Yorke, R. Piltner, Fast inverse distance weighting-based spatiotemporal interpolation, International Journal of Environmental Research and Public Health, vol. 11, pp. 9101-9141, 2014. DOI: 10.3390/ijerph110909101
- 本論文用途：E11C 局部 IDW／時空插值的方法依據。
- 實際引用位置：5.9.3.6 E11C 局部鄰域獨立確認（[thesis_draft_zh.md L1419](thesis_draft_zh.md#L1419)）
- 原文入口：[DOI](https://doi.org/10.3390/ijerph110909101)。
- 比較邊界：方法引用與本地 baseline／實驗比較須分開記錄；本地數值不等同原論文數值。

#### [39] Fast k-nearest-neighbors calculation for interpolation of radar reflectivity field

- 書目：F. Gao, Fast k-nearest-neighbors calculation for interpolation of radar reflectivity field, Journal of Atmospheric and Oceanic Technology, vol. 26, pp. 1410-1414, 2009. DOI: 10.1175/2009JTECHA1234.1
- 本論文用途：E11C 最近鄰搜尋／局部插值的方法依據。
- 實際引用位置：5.9.3.6 E11C 局部鄰域獨立確認（[thesis_draft_zh.md L1419](thesis_draft_zh.md#L1419)）
- 原文入口：[DOI](https://doi.org/10.1175/2009JTECHA1234.1)。
- 比較邊界：方法引用與本地 baseline／實驗比較須分開記錄；本地數值不等同原論文數值。

#### [40] Inverse distance weighting and kriging spatial interpolation for data center thermal monitoring

- 書目：E. Oktavia, Widyawan, I. W. Mustika, Inverse distance weighting and kriging spatial interpolation for data center thermal monitoring, ICITISEE, pp. 69-74, 2016. DOI: 10.1109/ICITISEE.2016.7803050
- 本論文用途：資料中心 IDW／kriging 的相關方法與研究邊界。
- 實際引用位置：5.9.3.6 E11C 局部鄰域獨立確認（[thesis_draft_zh.md L1419](thesis_draft_zh.md#L1419)）
- 原文入口：[DOI](https://doi.org/10.1109/ICITISEE.2016.7803050)。
- 比較邊界：方法引用與本地 baseline／實驗比較須分開記錄；本地數值不等同原論文數值。

#### [41] A time-varying state-space model for real-time temperature predictions in rack-based cooling data centers

- 書目：X. Tong et al., A time-varying state-space model for real-time temperature predictions in rack-based cooling data centers, Applied Thermal Engineering, vol. 230, 120737, 2023. DOI: 10.1016/j.applthermaleng.2023.120737
- 本論文用途：機架冷卻的動態 state-space 溫度預測方法參考。
- 實際引用位置：5.9.3.6 E11C 局部鄰域獨立確認（[thesis_draft_zh.md L1419](thesis_draft_zh.md#L1419)）
- 原文入口：[DOI](https://doi.org/10.1016/j.applthermaleng.2023.120737)。
- 比較邊界：方法引用與本地 baseline／實驗比較須分開記錄；本地數值不等同原論文數值。

### 資料集描述論文

#### [12] CU-BEMS, smart building electricity consumption and indoor environmental sensor datasets

- 書目：Gopal Chitalia, Manisa Pipattanasomporn, CU-BEMS, smart building electricity consumption and indoor environmental sensor datasets, Scientific Data, vol. 7, article 290, 2020. DOI: 10.1038/s41597-020-00582-3
- 本論文用途：CU-BEMS 資料集描述論文；公開 task-aligned benchmark 的資料來源。
- 實際引用位置：2.8 公開資料與訓練資料適用性（[thesis_draft_zh.md L411](thesis_draft_zh.md#L411)）；E5 Window Matrix and E9 Public Benchmarks（[paper.tex L229](../papers/ieee/paper.tex#L229)）
- 原文入口：[DOI](https://doi.org/10.1038/s41597-020-00582-3)。
- 比較邊界：此處記錄引用用途，未建立與原文相同資料／任務的直接優劣比較。

#### [17] Development of the ASHRAE Global Thermal Comfort Database II

- 書目：V. Foldvary Licina, T. Cheung, H. Zhang, R. de Dear, T. Parkinson, E. Arens, et al., Development of the ASHRAE Global Thermal Comfort Database II, Building and Environment, vol. 142, pp. 502-512, 2018. DOI: 10.1016/j.buildenv.2018.06.022
- 本論文用途：熱舒適資料庫描述論文；主稿用於候選資料適用性與舒適目標參考。
- 實際引用位置：2.8 公開資料與訓練資料適用性（[thesis_draft_zh.md L416](thesis_draft_zh.md#L416)）
- 原文入口：[DOI](https://doi.org/10.1016/j.buildenv.2018.06.022)。
- 比較邊界：此處記錄引用用途，未建立與原文相同資料／任務的直接優劣比較。

### 英文稿獨有文獻

#### tao2019digitaltwin Digital Twin in Industry: State-of-the-Art

- 書目：F. Tao and H. Zhang and A. Liu and A. Y. C. Nee, Digital Twin in Industry: State-of-the-Art, IEEE Transactions on Industrial Informatics, 2019.
- 本論文用途：英文稿 Related Work 的數位孿生定義、技術及研究挑戰背景。
- 實際引用位置：Related Work（[paper.tex L60](../papers/ieee/paper.tex#L60)）
- 比較邊界：此處記錄引用用途，未建立與原文相同資料／任務的直接優劣比較。

#### fuller2020digitaltwin Digital Twin: Enabling Technologies, Challenges and Open Research

- 書目：A. Fuller and Z. Fan and C. Day and C. Barlow, Digital Twin: Enabling Technologies, Challenges and Open Research, IEEE Access, 2020.
- 本論文用途：英文稿 Related Work 的數位孿生定義、技術及研究挑戰背景。
- 實際引用位置：Related Work（[paper.tex L60](../papers/ieee/paper.tex#L60)）
- 比較邊界：此處記錄引用用途，未建立與原文相同資料／任務的直接優劣比較。

## 資料集與網站文件

| 編號 | 來源 | 用途／引用位置 |
| --- | --- | --- |
| [11] | Model Context Protocol Documentation | MCP 服務介面文件；屬網站文件。 Related Work（[paper.tex L60](../papers/ieee/paper.tex#L60)） |
| [13] | Appliances Energy Prediction | 候選公開資料的適用性盤點；不能據此認定已投入實驗。 2.8 公開資料與訓練資料適用性（[thesis_draft_zh.md L412](thesis_draft_zh.md#L412)） |
| [14] | SML2010 [Dataset] | SML2010 公開比較的資料集來源。 2.8 公開資料與訓練資料適用性（[thesis_draft_zh.md L413](thesis_draft_zh.md#L413)）；E5 Window Matrix and E9 Public Benchmarks（[paper.tex L229](../papers/ieee/paper.tex#L229)） |
| [15] | Occupancy Detection | 候選公開資料的適用性盤點；不能據此認定已投入實驗。 2.8 公開資料與訓練資料適用性（[thesis_draft_zh.md L414](thesis_draft_zh.md#L414)） |
| [16] | Dataset of room-level indoor environmental quality measurements and occupancy ground truth for five residential apartments in Denmark [Dataset] | 住宅 IEQ 候選資料適用性盤點；不能據此認定已投入實驗。 2.8 公開資料與訓練資料適用性（[thesis_draft_zh.md L415](thesis_draft_zh.md#L415)） |
| [35] | bmcdata: A dataset collected from server's Baseboard Management Controller | E11A 與 BMC 後續實驗的資料來源。 5.9.3.4 機箱 BMC 公開資料轉移比較（[thesis_draft_zh.md L1391](thesis_draft_zh.md#L1391)）；Related Work（[paper.tex L60](../papers/ieee/paper.tex#L60)） |
| [36] | Data from the AAU Server Room | AAU 空間估測及 commissioning 系列的資料來源。 5.9.3.5 AAU 伺服器機房空間轉移比較（[thesis_draft_zh.md L1407](thesis_draft_zh.md#L1407)）；Bounded AAU Enclosure Transfer（[paper.tex L256](../papers/ieee/paper.tex#L256)） |

## 只在 BibTeX 中、未在兩份主稿找到引用的其他項目

- `ashrae55`：ANSI/ASHRAE Standard 55: Thermal Environmental Conditions for Human Occupancy。不計入已使用清單。
- `iso7730`：ISO 7730: Ergonomics of the Thermal Environment -- Analytical Determination and Interpretation of Thermal Comfort Using Calculation of the PMV and PPD Indices and Local Thermal Comfort Criteria。不計入已使用清單。
- `ieeeauthorcenter`：IEEE Article Templates and Conference Templates。不計入已使用清單。

## 後續對應到 3D 視圖的資料

同名 JSON 保存逐筆引用的原始段落、章節、行號、BibTeX key、DOI 與來源 SHA-256。可用於補入英文稿獨有論文與修正論文計數；本輪只完成清單，尚未變更 3D 視圖。

外部原文論點與頁碼仍需逐篇核對，不能把本清單的「主稿引用段落」當作對方原文的定位。

重建：`python3 scripts/build_used_papers_inventory.py`。
