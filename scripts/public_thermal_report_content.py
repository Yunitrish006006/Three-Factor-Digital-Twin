"""Public-scenario and LQR teaching content; no new algorithm-efficacy claims."""
import json
from pathlib import Path
from lqr_guide_html import render_guide

ROOT=Path(__file__).resolve().parents[1]
ARTIFACTS=ROOT/'openspec/changes/discover-public-thermal-scenes-20261012/artifacts'


def scene_section():
    data=json.loads((ARTIFACTS/'readiness.json').read_text())
    rows=data['HotSpot']['rows']; columns=data['HotSpot']['columns']
    return f'''<section id="online"><h2>我先找外部公開場景，不必等設備到位</h2>
<p>我需要能改變熱輸入或散熱操作、再取得溫度的外部場景。只有已記錄的資料不能回答另一個風扇命令的反事實；公開模型、雲端 CFD 與逐步 REST 模擬也不能混為一談。本次查閱與功能檢查日期為 2026-10-12。</p>
<p class="caption">手機可左右捲動下表，查看完整候選、執行狀態與用途。</p><div class="table-wrap" tabindex="0" role="region" aria-label="公開模擬場景比較，可左右捲動"><table class="scenes"><thead><tr><th>公開候選</th><th>能模擬什麼</th><th>實際確認到哪裡</th><th>我如何使用</th></tr></thead><tbody>
<tr><th><a href="https://www.simscale.com/docs/tutorials/thermal-management-cht-analysis-electronics-box/">SimScale 電子盒</a></th><td>發熱元件、散熱器、接觸熱阻、空氣與風扇曲線。</td><td>官方雲端教學與專案匯入入口已查；尚未登入、匯入或求解。</td><td>幾何／傳熱路徑優先候選。此教學是穩態，迭代不是物理時間，不能直接作 LQR 的每步控制。</td></tr>
<tr><th><a href="https://github.com/uvahotspot/HotSpot">UVA HotSpot</a></th><td>晶片 floorplan、功率 trace、封裝與散熱參數 → 瞬態／穩態溫度。</td><td>已編譯並執行原版 example1 一個 block-model 命令，產生 {rows} 筆 × {columns} 欄有限值。</td><td>公開電子熱模型候選。本次固定對流熱阻，詳細風扇／閉迴路未做；不是機箱 CFD。</td></tr>
<tr><th><a href="https://tclab.readthedocs.io/en/latest/notebooks/04_Emulation_of_TCLab_for_Offline_Use.html">TCLab 無設備模擬</a></th><td>雙加熱器、雙溫度感測、熱耦合與感測延遲／量化。</td><td>官方模型固定輸入介面已跑通，沒有連接硬體或比較控制器。</td><td>較快的估測／控制流程練習平台。操作是加熱功率，沒有風扇、風管與機箱幾何。</td></tr>
<tr><th><a href="https://ibpsa.github.io/project1-boptest/docs-userguide/getting_started.html">BOPTEST REST</a></th><td>室內／建築空調模型，可初始化、送控制、推進與取量測。</td><td>本次 /testcases 與核准網路重試皆無法解析主機，未建立實例。</td><td>不同場景的方法驗證候選；目前未接通，不能由一次 DNS 失敗推論永久不可用。</td></tr>
</tbody></table></div>
<p>我先把 SimScale 用於理解機箱的接觸／氣流路徑，把 HotSpot 用於公開電子熱模型，把 TCLab 用於控制介面準備。選擇下一階段前，要先確認要回答的是幾何散熱，還是時序控制；公開範例跑通不代表我的方法已在它上面有效。</p>
<details><summary>使用條件、溫度域與下一階段如何安排</summary>
<p><a href="https://www.simscale.com/product/pricing/">SimScale 官方方案</a>列有免費 Community 與有限定量模擬額度。帳號、特定教學功能與剩餘額度仍未確認；本次沒有啟動雲端計算。文字工具未開啟教學的專案匯入／完成連結，所以不能稱實際匯入已驗證。</p>
<p>HotSpot 原版例子的入口／初始溫度是 318.15 K＝45°C，超過目前方法 20–30°C 的既有驗證範圍；本次僅一秒 trace，也不代表充分暖機。風扇 RPM 與對流的映射、可重設的逐步 adapter 和新溫度域都需另固定。TCLab 的雙加熱輸入則不能直接換名為風扇 PWM。</p>
<p>若選雲端電子盒，先確認瞬態資料與控制接口，再定義感測位置；若先選 HotSpot／TCLab，先固定外部模型版本、初始條件與擾動，再用相同觀測／校正／限制比較。這些是下一階段計畫，本次沒有新增 LQR／MPC 優越性實驗，也沒有重跑 E15 或舊機箱研究。</p>
</details><p><a href="../research/public_thermal_simulation_scenes_2026-10-12_zh.md">完整場景與執行條件</a> · <a href="../../openspec/changes/discover-public-thermal-scenes-20261012/artifacts/readiness.json">本次來源與功能紀錄</a></p></section>'''


def lqr_details():
    content='''<h3>我需要理解與注意的六個重點</h3>
<div class="table-wrap"><table><thead><tr><th>重點</th><th>我在機箱研究中要確認什麼</th></tr></thead><tbody>
<tr><th>平衡點與模型</th><td>先確認功率／入口下，目標有可行 PWM。LQR 在工作點附近使用線性模型；更換風道與接觸後，不能直接沿用同一 K 的保證。</td></tr>
<tr><th>狀態與量測</th><td>x 是熱源、金屬片、空氣與風扇狀態；y 是可量測的部分。熱源參考只作評分。LQR 不會自動辨識或補出狀態；稀疏感測需要估測器。</td></tr>
<tr><th>Q／R 與量尺</th><td>Q 重視哪些偏差，R 重視操作代價；先處理 °C 與 PWM 的尺度。二次操作成本不是量測能耗，較大權重也不是更強的風扇。</td></tr>
<tr><th>離散化與穩定條件</th><td>每 5 秒操作要用對應 A_d／B_d 與離散 Riccati。檢查可穩定／成本可偵測、P 與 DARE 殘差，理想離散閉迴路特徵值模長需小於 1。</td></tr>
<tr><th>限幅、延遲與擾動</th><td>PWM／slew 限制套用後，不能沿用原無限制最優結論。風扇延遲、功率失配與估測偏差仍要測；非零設定值與持續擾動需要前饋或另設計追蹤／積分。</td></tr>
<tr><th>公平比較與原文邊界</th><td>各方法取得相同稀疏資訊、負載、預算與限制。Kalman 原文 p.104 假設狀態精確已知，p.114 穩定定理有條件；不能說任何受限機箱都最優、安全或已驗證。</td></tr>
</tbody></table></div>
<h3>詳細版：推導、機箱對應、算例與原始論文</h3>
<p>以下十五個主題可各自展開；長公式可左右捲動，離線也能閱讀。列印版會展開全部內容。</p><!-- DETAILED LQR GUIDE -->
<p><a href="../research/lqr_practical_guide_2026-10-12_zh.md">完整 LQR 詳細筆記</a> · <a href="../papers/reference_sources/kalman_1960_optimal_control_original.pdf">下載 Kalman 1960 完整原始論文（18 頁）</a></p>'''
    return content.replace('<!-- DETAILED LQR GUIDE -->',render_guide())
