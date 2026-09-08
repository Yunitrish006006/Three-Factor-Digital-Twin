"""Build the offline professor briefing; no dependencies or external assets."""
from pathlib import Path
import hashlib
import html
import json

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'openspec/changes/confirm-bmc-temporal-transfer-e15/artifacts/bmc_confirmation_e15_result.json'
TARGET = ROOT / 'docs/reports/application_targets_2026-09-08_zh.html'


def build():
    evidence = json.loads(EVIDENCE.read_text())
    baseline = evidence['aggregate']['baseline']['mae_c']
    ridge = evidence['aggregate']['ridge']['mae_c']
    slides = []

    def add(title, kicker, body, notes):
        slides.append(dict(title=title, kicker=kicker, body=body, notes=notes))

    add('從環境估測，走向可驗證的應用品質', '研究方向討論｜2026.09.08｜約 10–12 分鐘', '''
<p class="lead">三個候選目標，優先探索 <strong>3D 列印線材</strong>。</p>
<div class="cards"><article class="priority"><span class="tag">優先探索 · APP-FIL-01</span><h2>線材溫濕度管理</h2><p>先做防潮保存與供料，再評估加熱乾燥。</p></article><article><span class="tag">保留候選 · APP-WOOD-01</span><h2>木材溫濕度管理</h2><p>常溫調濕、含水狀態估測與乾燥進度。</p></article><article><span class="tag">保留候選 · APP-PC-01</span><h2>機箱溫度管理</h2><p>以既有估測證據為起點，另補風扇介入。</p></article></div>
<p class="callout">本次目的：比較應用價值與可行性。三個控制應用均尚未驗證，沒有新增良率或節能結果。</p>''',
        '開場：目前已有環境估測成果，想把應用終點從「預測準不準」延伸到「是否幫助產品或設備」。不是同時開三條完整實驗線；個人優先意願是線材，仍需確認設備與資料。')

    add('已經有什麼證據？', '01｜既有成果與可轉移的經驗', f'''
<div class="metric"><span>E15 同伺服器凍結確認 · MAE</span><strong>{baseline:.4f} → {ridge:.4f} °C</strong><span>{evidence['file_count']} 檔 · {evidence['row_count']:,} 筆 · {evidence['ridge_run_wins']}/{evidence['file_count']} 次改善；另 2 次退步保留</span></div>
<div class="cards two"><article><h2>可以沿用</h2><ul><li>物理結構、稀疏感測與殘差修正的研究流程。</li><li>短期校正、凍結測試、來源與單位稽核。</li><li>AAU 已有同 campaign 的空間校正驗證。</li></ul></article><article><h2>需要新增</h2><ul><li>材料含水狀態、溫濕度動態及參考量測。</li><li>控制動作的實際效果與產品品質。</li><li>新材料／新設備／新溫域的獨立測試。</li></ul></article></div>
<p class="foot">E15 模型是 load-aware ridge，不是神經網路控制器；AAU 不支持任意 3D 熱場、跨機箱或因果控制。GRU／LSTM 的既有負向結果仍保留。</p>
<p class="sources"><a href="../../openspec/changes/confirm-bmc-temporal-transfer-e15/evidence.md">E15 原始證據紀錄</a> · <a href="../thesis/thesis_draft_zh.md">主論文／AAU 證據邊界</a></p>''',
        'E15 是隱藏目標的 CPU 溫度估測，不是預測改變風扇後的反事實溫度。確認集已開封，不會重新用來選新模型。AAU 同 campaign 的日期重疊限制也必須保留。')

    add('三個目標：要改善的事情不同', '02｜候選應用比較', '''
<div class="table-wrap"><table><thead><tr><th>候選</th><th>使用者真正需要</th><th>關鍵比較</th><th>缺少的證據</th></tr></thead><tbody>
<tr><td><strong>線材</strong><br>目前優先</td><td>列印品質穩定；減少失敗與不必要加熱</td><td>密封＋乾燥劑、既有乾燥流程、一般控制</td><td>獨立批次列印品質、含水量參考、能耗</td></tr>
<tr><td><strong>木材</strong></td><td>含水率達標，避免不均或變形</td><td>固定環境／固定程序與自適應程序</td><td>木種、厚度、重量／全乾真值、長時間紀錄</td></tr>
<tr><td><strong>機箱</strong></td><td>不超溫、不降效能下節能</td><td>全速、原廠策略、一般 PID</td><td>可控風扇、同步負載、實際功率、重複介入</td></tr>
</tbody></table></div><p class="callout">三者都是 PROPOSED。研究價值需由相對於簡單基線的額外改善決定，並非採用神經網路就成立。</p>''',
        '教授若問為何不一直全速：機箱要比較熱限制與能源。線材則要證明相對於密封乾燥劑的新增價值。木材重點是材料水分，不能只報空氣預測誤差。')

    add('線材先做保存，乾燥另設階段', '03｜20–30°C 的邊界', '''
<div class="cards two"><article class="priority"><span class="tag">階段 A · 優先 pilot</span><h2>20–30°C 防潮保存／供料</h2><p>相同乾燥前處理後，比較暴露環境、密封＋乾燥劑與主動管理。</p><p>問題：保存一段時間後，列印品質是否仍可維持？</p></article><article><span class="tag">階段 B · 需新溫域驗證</span><h2>加熱乾燥與停止時機</h2><p>Prusa 特定產品指引：PLA 45°C、PETG 55°C。均超出原空氣模型範圍。</p><p>問題：達到同等品質時，是否可縮短處理或降低耗電？</p></article></div>
<p class="callout">落在原溫度範圍不代表材料／濕度模型已驗證。前處理烘乾可用廠商流程，但不列為模型已控制的成果。</p>
<p class="sources"><a href="https://help.prusa3d.com/article/drying-filament_332086">Prusa：產品乾燥指引</a> · <a href="https://wiki.polymaker.com/printing-tips/post-processing/moisture-conditioning">Polymaker：線材乾燥與成品調濕不同</a></p>''',
        '這裡的溫濕度控制是線材保存／乾燥設備，不是印表機噴嘴溫度控制。PETG 或尼龍尚未選定，依可用機器決定。沒有設定所有線材都不能太乾的通用假說。')

    add('線材用固定設定就夠了嗎？', '核心質疑｜先證明研究必要性', '''
<p class="lead"><strong>可能夠，而且應該先拿固定設定當基準。</strong></p>
<div class="cards two"><article><h2>固定目標可以合理工作</h2><p>防潮保存可先比較密封＋乾燥劑、固定濕度目標的一般開關／PID 控制。</p><p>目標固定，不代表設備出力固定；一般回授已能補償一部分擾動。</p></article><article class="priority"><h2>模型必須證明額外用途</h2><p>候選問題：不同初始吸濕量或裝載量下，能否可靠判定乾燥完成？</p><p>或在相同品質下減少耗電與處理時間？目前均未證明。</p></article></div>
<p class="callout">若簡單固定策略已達標，就不需要為了使用神經網路而增加控制複雜度。線材是個人優先探索意願，學術適配性待驗證。</p>''',
        '把固定設定拆成固定目標與固定輸出。固定 RH 目標可以搭配傳統回授，不能假設它無法應付擾動。可先做比較或終點估測，不必先提出動態溫濕度配方。若沒有額外價值，轉為監測或重新選題。')

    add('物理與神經網路，各自負責什麼？', '04｜候選方法架構 · 尚未實作', '''
<div class="flow"><div>環境與操作<br><small>溫度、RH、設備狀態、材料與時間</small></div><b>→</b><div>熱量／水分平衡<br><small>可解釋的基本動態</small></div><b>＋</b><div>小型殘差網路<br><small>學習材料與装載差異</small></div><b>→</b><div>預測與決策<br><small>先驗證，再閉迴路比較</small></div></div>
<div class="cards two"><article><h2>先驗證估測</h2><p>純物理、簡單線性、純小型網路、物理＋殘差，使用相同批次切分。</p><p>材料含水率只有在具參考量測時才能作監督目標。</p></article><article><h2>再驗證控制</h2><p>一般 PID 與候選方法用相同硬體、限制及目標。</p><p>離線紀錄或模擬的改善，分開標示，不能直接當成實機良率。</p></article></div>''',
        '目前的空氣 RH 並不等於材料含水率。不能只在神經網路多加一個輸出就認為量到水分；若沒有水分真值，先將任務限定為空氣狀態與品質結果的關聯。')

    add('良率：先定義「合格」再開始列印', '05｜APP-FIL-01 的主要終點', '''
<p class="formula">試件合格率 ＝ 完成且通過全部必要門檻的件數 ／ 全部啟動列印件數</p>
<div class="table-wrap"><table><thead><tr><th>層級</th><th>怎麼量</th><th>能支持的主張</th></tr></thead><tbody>
<tr><td>完成率</td><td>記錄斷料、堵塞、脫落、中止與完整完成</td><td>能否穩定完成；不等於品質合格</td></tr>
<tr><td>尺寸與表面</td><td>卡尺；固定光照／倍率照片；盲化計數缺陷</td><td>指定尺寸與可見缺陷合格率</td></tr>
<tr><td>機械品質（選配）</td><td>借用拉伸試驗機，採適用程序與試件</td><td>強度／延伸率；不能由外觀推論</td></tr>
</tbody></table></div>
<p class="callout">允收公差與缺陷門檻依試件用途，pilot 後、正式測試前凍結。目前沒有捏造「良率提升 X%」。</p>''',
        '先選一個有尺寸與表面要求的小試件。所有列印失敗保留在分母；事前界定的停電等外部無效事件另記，報全部啟動數與有效分析數。照片不能冒充 Ra、內部孔隙率或強度。')

    add('有先例可借用量測，不能直接借用結果', '06｜線材品質的文獻依據', '''
<article class="wide"><h2>Gong 等，SFF 2022</h2><p><em>Impact of Moisture Absorption on 3D Printing Nylon Filament</em></p><ul><li>Experiment：含水量量測，並製作擠出物、薄壁件及拉伸試件。</li><li>Surface finish / Mechanical testing：多種品質量測互相核對。</li><li>可借用：先量材料狀態，再評估列印結果的設計。</li></ul></article>
<p class="callout">原文調理為 40°C、80% RH，超出本案原溫域；目前也未確認可下載的原始資料與再使用授權。不能把論文圖表當成本案訓練集。</p>
<p class="sources"><a href="https://utw10945.utweb.utexas.edu/sites/default/files/2022/Impact%20of%20Moisture%20Absorption%20on%203D%20Printing%20Nylon.pdf">原文 PDF：Experiment 第 2 頁；品質測試第 4–5 頁</a></p>''',
        '注意英文 yield strength 是降伏強度，不是生產良率。這篇提供品質量測方法，不等於已經證明我們的模型或控制有效；實驗材料與濕度條件也不同。')

    add('最小實驗：先判斷差異量不量得到', '07｜建議 pilot · 尚未執行', '''
<div class="steps"><article><span>1</span><h2>固定起點</h2><p>同品牌、顏色與批次；相同乾燥前處理。固定噴嘴、切片、列印方向與供料路徑。</p></article><article><span>2</span><h2>保存組比較</h2><p>暴露、密封＋乾燥劑、主動管理。記錄溫濕度、保存時長與再吸濕。</p></article><article><span>3</span><h2>獨立批次</h2><p>建議每組 3 個獨立調理批次、每批 2 件；只作可行性與變異估計。</p></article><article><span>4</span><h2>正式確認</h2><p>依 pilot 規劃樣本數與門檻；新批次測試，報合格率差及不確定性。</p></article></div>
<p class="foot">區塊內隨機化組別／列印順序，試件盲化評分；同一盤多件不是多個獨立處理。保存 pilot 不能替代相同箱體下的演算法對照。</p>''',
        '3×2 是資源估計用的 pilot 建議，不是足夠樣本數的保證。如果大家都合格，先看尺寸與缺陷的連續指標是否可量測；不能事後挑有利門檻。不要用反覆濕乾的同一線軸當獨立重複。')

    add('設備與資料：哪些是必要，哪些可後補？', '08｜啟動前的可行性門檻', '''
<div class="table-wrap"><table><thead><tr><th>項目</th><th>第一階段</th><th>限制</th></tr></thead><tbody>
<tr><td>印表機＋相容材料</td><td>必要；型號與材料待確認</td><td>不先假定機器可印尼龍</td></tr>
<tr><td>溫濕度紀錄＋參考校正</td><td>必要；含環境與保存箱</td><td>先核對 RH 範圍及感測器誤差</td></tr>
<tr><td>卡尺＋固定拍攝</td><td>必要；低成本品質量測</td><td>無法代替強度與含水率</td></tr>
<tr><td>含水量參考</td><td>水分模型必要；可先借儀器</td><td>重量法需核對解析度、揮發物與熱分解；不能連線軸稱重便當水分真值</td></tr>
<tr><td>功率紀錄／拉伸機</td><td>節能主張必要／機械品質選配</td><td>沒有相應設備就縮小主張</td></tr>
</tbody></table></div><p class="foot">目前公開資料：BMC 已有，但不支援材料任務。線材／木材仍需核對授權、原始欄位與控制紀錄，預期需補自採資料。</p>''',
        '不是一定要先买所有設備。只有基本量測時，可以研究保存方式對尺寸／外觀的影響，但不要宣稱量到真實含水率或強度。節能比較要包含前處理、保存設備與列印耗電。')

    add('研究推進的判準', '09｜保留失敗結果，逐階段決定', '''
<div class="cards two"><article class="priority"><h2>值得繼續的條件</h2><ul><li>品質差異大於量測噪聲，且能重複。</li><li>相較密封＋乾燥劑，有額外需求。</li><li>新批次上，估測或控制改善仍成立。</li><li>同等品質下，每合格件耗電有改善。</li></ul></article><article><h2>需要縮小或停止的情況</h2><ul><li>簡單保存已足夠，主動控制沒有收益。</li><li>缺少水分真值卻想主張含水率預測。</li><li>神經網路不優於簡單物理／線性模型。</li><li>改善只出現在一個線軸或一盤試件。</li></ul></article></div>
<p class="callout">木材與機箱繼續保留候選；是否切換依可用設備與 pilot 結果決定，不為了模型複雜度強行找效果。</p>''',
        '每合格件耗電的分子是固定邊界內的全部能源，分母是合格件數；零合格時不是零耗電。正式評估用批次層級不確定性，不把每一秒的量測當成獨立樣本。')

    add('本次希望與教授確認的三件事', '10｜討論與下一步', '''
<ol class="questions"><li><strong>應用優先順序</strong><p>線材為優先探索；木材與機箱保留候選，是否合理？</p></li><li><strong>第一個可完成的終點</strong><p>先做 20–30°C 保存後的尺寸／表面合格率，是否需要一開始加入拉伸強度？</p></li><li><strong>可用設備與研究規模</strong><p>確認印表機、材料、含水量參考及機械量測設備，再凍結 pilot。</p></li></ol>
<p class="lead small">預計交付：可追溯的環境紀錄、品質量測表、基線比較，以及是否值得進入閉迴路控制的判斷。</p>
<p class="sources"><a href="../research/application_goals_2026-09-08_zh.md">完整候選目標與驗證方案</a> · <a href="../../openspec/changes/propose-application-targets-filament-first/protocol.md">研究規劃與啟動條件</a></p>''',
        '收尾：現在不是宣稱發明全新的線材乾燥器，而是先確認既有方法能否解決可量測的品質問題。相關工作與資料可用性審查仍需完成，才會採用新方法。')

    add('是否應該停止延伸控制題目？', '最後討論｜先確認問題，再決定方法', '''
<p class="lead">停止追逐新控制場景，是合理選項；既有研究成果仍可保留。</p>
<div class="cards two"><article><h2>目前沒有證明的事情</h2><ul><li>三個應用都尚未證明簡單策略不足。</li><li>溫度估測改善不直接構成控制、品質或節能改善。</li><li>更換材料並不自動產生新穎性。</li></ul></article><article class="priority"><h2>與教授討論的兩條路</h2><ul><li>收斂既有研究：界定稀疏校正在哪些條件有用、何時不如簡單基線。</li><li>延伸前先取得具體使用痛點與可用資料，再決定是否需要新的方法。</li></ul></article></div>
<p class="callout">這份報告不承諾完成三套控制系統。先請教授判斷既有貢獻的定位與缺口，再決定補哪一個最小實驗，或是否轉題。</p>''',
        '承認目前方法導向找應用碰到瓶頸，不把研究負向結果等同失敗。也不保證現有內容必然足夠畢業或投稿；這需要教授依研究問題與要求評估。')

    sections = []
    for i, slide in enumerate(slides):
        sections.append(f'<section class="slide" id="slide-{i+1}" aria-labelledby="title-{i+1}"><p class="kicker">{html.escape(slide["kicker"])}</p><h1 id="title-{i+1}">{html.escape(slide["title"])}</h1>{slide["body"]}<aside class="notes"><strong>口頭報告提示</strong><p>{html.escape(slide["notes"])}</p></aside><footer>候選應用討論 · 尚無新控制／良率實驗<span>{i+1:02d} / {len(slides):02d}</span></footer></section>')
    page = '''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>候選應用與線材品質驗證｜教授報告 2026-09-08</title><style>
:root{--bg:#f2f4f2;--ink:#18332f;--muted:#526760;--accent:#087e70;--line:#d7e0dc}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:"Noto Sans CJK TC","Microsoft JhengHei",sans-serif;line-height:1.6}nav{position:sticky;top:0;z-index:10;background:#16342f;color:white;display:flex;gap:10px;align-items:center;padding:10px 3vw;flex-wrap:wrap}nav strong{margin-right:auto;font-size:14px}button,select{font:inherit;font-size:14px;padding:7px 11px;border:1px solid #93aaa1;border-radius:6px;background:white;color:#18332f;cursor:pointer}button:disabled{opacity:.4;cursor:default}button:focus-visible,a:focus-visible,select:focus-visible{outline:3px solid #e8b857;outline-offset:3px}select{max-width:32vw}.slide{position:relative;max-width:1440px;margin:28px auto;padding:40px 52px 60px;background:white;border:1px solid var(--line);border-radius:12px;min-height:740px}.kicker{font-size:14px;letter-spacing:.08em;color:var(--accent);font-weight:700;margin:0 0 12px}h1{font-size:clamp(26px,3vw,43px);line-height:1.3;margin:0 0 28px;letter-spacing:-.02em}h2{font-size:23px;margin:12px 0}p{margin:10px 0}.lead{font-size:27px;margin-bottom:30px}.lead.small{font-size:21px}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}.cards.two{grid-template-columns:repeat(2,1fr)}article{padding:24px;background:#f5f7f5;border:1px solid var(--line);border-radius:10px;font-size:19px}.priority{background:#e9f5ef;border-top:4px solid var(--accent)}.tag{font-size:13px;color:var(--accent);font-weight:700}.callout{padding:17px 20px;background:#fff4dd;border-left:4px solid #d59e38;margin-top:26px;font-size:18px}.foot{font-size:16px;color:var(--muted);margin-top:22px}.sources{font-size:14px;margin-top:18px}a{color:#08766b;text-underline-offset:3px}ul{padding-left:23px}li{margin:10px 0}.metric{background:#163d35;color:white;border-radius:10px;padding:22px 28px;margin-bottom:22px;display:flex;flex-direction:column}.metric strong{font-size:38px}.metric span{font-size:17px}table{width:100%;border-collapse:collapse;font-size:18px}th,td{text-align:left;vertical-align:top;padding:17px 15px;border-bottom:1px solid var(--line)}th{background:#eaf2ee;font-size:16px}.table-wrap{overflow-x:auto}.formula{font-size:24px;padding:20px;background:#e9f5ef;border-radius:8px}.flow{display:flex;align-items:center;gap:12px;margin:35px 0;flex-wrap:wrap}.flow div{flex:1;min-width:170px;padding:18px;background:#e9f5ef;border-radius:8px;font-size:21px;font-weight:700}.flow small{font-size:15px;font-weight:400}.flow b{font-size:25px}.steps{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}.steps article{padding:20px;font-size:18px}.steps span{display:inline-grid;place-items:center;background:var(--accent);color:white;width:35px;height:35px;border-radius:50%}.questions{font-size:22px;padding-left:28px}.questions p{font-size:20px;color:var(--muted)}footer{position:absolute;bottom:18px;left:52px;right:52px;font-size:12px;color:var(--muted);display:flex;justify-content:space-between;border-top:1px solid var(--line);padding-top:10px}.notes{display:none;margin:25px 0;background:#eff0fb;padding:18px;border-radius:8px;font-size:17px}.show-notes .notes{display:block}.present .slide{display:none}.present .slide.active{display:block}#status{font-size:13px;min-width:42px}@media(max-width:760px){.slide{margin:12px;padding:25px 20px 70px;min-height:0}.cards,.cards.two,.steps{grid-template-columns:1fr}h1{font-size:28px}.lead{font-size:22px}article,table{font-size:16px}footer{left:20px;right:20px}.metric strong{font-size:29px}select{max-width:90vw}nav strong{width:100%}}@media print{@page{size:A4 landscape;margin:9mm}body{background:white}nav,.notes{display:none!important}.slide,.present .slide{display:block!important;border:0;border-radius:0;margin:0;padding:10mm 8mm 14mm;min-height:180mm;break-after:page;break-inside:avoid;max-width:none}h1{font-size:26px;margin-bottom:15px}h2{font-size:19px}article,table{font-size:14px}article{padding:13px}.callout,.foot{font-size:13px;margin-top:12px}.lead{font-size:21px}.sources{font-size:11px}.metric strong{font-size:29px}.steps article{font-size:14px}.formula{font-size:19px}.questions,.questions p{font-size:18px}footer{left:8mm;right:8mm;bottom:3mm}.slide:last-child{break-after:auto}}
</style></head><body><nav aria-label="簡報控制"><strong>研究方向｜線材・木材・機箱</strong><button id="prev" aria-label="上一頁">←</button><select id="jump" aria-label="跳至投影片"></select><button id="next" aria-label="下一頁">→</button><span id="status" role="status" aria-live="polite"></span><button id="mode">逐頁簡報</button><button id="notes" aria-pressed="false">講稿提示</button><button id="print">列印／PDF</button></nav><main>''' + ''.join(sections) + r'''</main><script>
const slides=[...document.querySelectorAll('.slide')],jump=document.getElementById('jump');let index=0;slides.forEach((s,i)=>{let o=document.createElement('option');o.value=i;o.textContent=`${i+1}. ${s.querySelector('h1').textContent}`;jump.appendChild(o)});
function show(n,scroll=true){index=Math.max(0,Math.min(slides.length-1,n));slides.forEach((s,i)=>s.classList.toggle('active',i===index));jump.value=index;document.getElementById('status').textContent=`${index+1}/${slides.length}`;document.getElementById('prev').disabled=index===0;document.getElementById('next').disabled=index===slides.length-1;history.replaceState(null,'',`#slide-${index+1}`);if(scroll)slides[index].scrollIntoView({block:'start'});}
document.getElementById('prev').onclick=()=>show(index-1);document.getElementById('next').onclick=()=>show(index+1);jump.onchange=()=>show(Number(jump.value));document.getElementById('mode').onclick=function(){document.body.classList.toggle('present');this.textContent=document.body.classList.contains('present')?'總覽全部':'逐頁簡報';show(index)};document.getElementById('notes').onclick=function(){document.body.classList.toggle('show-notes');this.setAttribute('aria-pressed',String(document.body.classList.contains('show-notes')))};document.getElementById('print').onclick=()=>window.print();document.addEventListener('keydown',e=>{if(['SELECT','INPUT','TEXTAREA','BUTTON','A'].includes(e.target.tagName)||e.ctrlKey||e.metaKey||e.altKey)return;if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();show(index+1)}else if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();show(index-1)}else if(e.key==='Home'){e.preventDefault();show(0)}else if(e.key==='End'){e.preventDefault();show(slides.length-1)}});const match=location.hash.match(/^#slide-(\d+)$/);document.body.classList.add('present');document.getElementById('mode').textContent='總覽全部';show(match?Number(match[1])-1:0,false);
</script></body></html>'''
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(page, encoding='utf-8')
    manifest = dict(status='PROPOSAL_ONLY', date='2026-09-08', slides=len(slides),
                    preferred_application='APP-FIL-01', applications=['APP-FIL-01','APP-WOOD-01','APP-PC-01'],
                    evidence_file=str(EVIDENCE.relative_to(ROOT)), evidence_sha256=hashlib.sha256(EVIDENCE.read_bytes()).hexdigest(),
                    html_sha256=hashlib.sha256(TARGET.read_bytes()).hexdigest())
    TARGET.with_suffix('.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    print(f'Built {TARGET} ({len(slides)} slides, offline HTML)')


if __name__ == '__main__':
    build()
