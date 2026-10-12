"""Read-only synthesis of frozen studies; no new experiment or adopted claim."""
from html import escape
import hashlib
import json
import math
from pathlib import Path
import re
from statistics import mean

from enclosure_session_summary import summary, LABELS, METHODS
from enclosure_structure_summary import summary as structure_summary

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / 'docs/reports'
QA = REPORTS / 'qa/professor_comparison_2026-10-12'


def table(headers, rows):
    return '<div class="table-wrap" tabindex="0" role="region" aria-label="比較表，可左右捲動"><table><thead><tr>' + ''.join('<th scope="col">'+escape(str(x))+'</th>' for x in headers) + '</tr></thead><tbody>' + ''.join('<tr>'+''.join(('<th scope="row">' if i == 0 else '<td>')+escape(str(x))+('</th>' if i == 0 else '</td>') for i,x in enumerate(row))+'</tr>' for row in rows) + '</tbody></table></div>'


def page(title, body):
    css = re.search(r'<style>(.*?)</style>', (REPORTS/'professor_research_2026-10-12_zh.html').read_text(), re.S).group(1)
    return '<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+escape(title)+'</title><style>'+css+' p,li{overflow-wrap:anywhere}.table-wrap table{min-width:640px}.method{border-left:4px solid #315f87;padding:12px 20px;margin:20px 0;background:#f5f8fb}@media print{.table-wrap table{min-width:0}details{display:block}}</style></head><body><main><header><p class="meta">2026-10-12｜既有證據整理，非新一輪實驗</p><h1>'+escape(title)+'</h1><nav><a href="professor_research_2026-10-12_zh.html">完整報告與 LQR</a><a href="professor_comparison_2026-10-12_zh.html">方法比較</a><a href="conference_shortlist_2026-10-12_zh.html">投稿候選</a></nav></header>'+body+'</main></body></html>\n'


def inline(text):
    value = escape(text)
    value = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', value)
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', value)


def markdown(text):
    """Small explicit subset for the checked-in conference note."""
    parts = []; lines = text.splitlines(); i = 0
    while i < len(lines):
        s = lines[i]; i += 1
        if not s.strip() or s.startswith('# '): continue
        if s.startswith('## '): parts.append('<h2>'+inline(s[3:])+'</h2>'); continue
        if s.startswith('|'):
            rows = [s]
            while i < len(lines) and lines[i].startswith('|'): rows.append(lines[i]); i += 1
            cells = [[inline(c.strip()) for c in r.strip('|').split('|')] for r in rows]
            parts.append('<div class="table-wrap" tabindex="0" role="region" aria-label="研討會比較表，可左右捲動"><table><thead><tr>'+''.join('<th>'+c+'</th>' for c in cells[0])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+c+'</td>' for c in r)+'</tr>' for r in cells[2:])+'</tbody></table></div>'); continue
        if s.startswith('- '):
            items = [s[2:]]
            while i < len(lines) and lines[i].startswith('- '): items.append(lines[i][2:]); i += 1
            parts.append('<ul>'+''.join('<li>'+inline(x)+'</li>' for x in items)+'</ul>'); continue
        parts.append('<p>'+inline(s)+'</p>')
    return ''.join(parts)


def build():
    first = summary(); second = structure_summary()
    r = first['result']; c = r['aggregates']['closed_loop']['holdout']
    runs = [x for x in r['runs'] if x['task']=='closed_loop' and x['split']=='holdout']
    metrics = ('tracking_mae_C','source_mae_C','fan_energy_proxy_Wh','overtemp_s','command_variation','compute_mean_ms')
    # Independent aggregation from episode entries prevents transcription drift.
    for m in METHODS:
        selected = [x for x in runs if x['method']==m]
        assert len(selected) == 4
        for k in metrics:
            assert math.isclose(mean(x['metrics'][k] for x in selected), c[m][k], abs_tol=1e-12)
    rows = [[LABELS[m]]+[f'{c[m][k]:.4f}' for k in metrics] for m in METHODS]
    reduction = (c['pi']['fan_energy_proxy_Wh']-c['linear_mpc']['fan_energy_proxy_Wh'])/c['pi']['fan_energy_proxy_Wh']*100
    penalty = (c['linear_mpc']['tracking_mae_C']/c['pi']['tracking_mae_C']-1)*100
    body = '''<section id="comparison"><h2>我如何比較，才能解釋每個方法</h2><p>我把第一階段的八種控制方法、三種估測配置，以及第二階段的模型結構分開比較。先說實際數據，再說可能原因，最後交代能下的結論。以下延伸既有結論的說明，沒有重新調參或重跑實驗。</p><p>第一階段 holdout 為兩種平台 × 兩個 seed，每個方法四回合；每回合 120 步、每步 5 秒。各方法共用同一校正預算、外部負載與噪聲抽樣，熱源真值只用於評分。除了明確標示的無校正消融，估測器相同；不同控制輸出會改變溫度軌跡。</p><p><strong>共同條件不代表各方法已經過同等最佳化調參。</strong>這是固定設定的系統比較：PI/PID 沿用固定增益，LQR 用固定 Q/R，MPC 與排序沿用固定代價。不能由一次排名推論方法家族的普遍優劣。</p></section><section id="numbers"><h2>第一階段：八方法的數值比較</h2>'''
    body += table(['方法','追蹤 MAE °C','估測 MAE °C','風扇 proxy Wh／回合','取樣超溫 秒／回合','PWM 總變化／回合','平均 ms／步'],rows)
    body += f'''<p>各數值為四回合等權平均。追蹤 MAE 是實際熱源與 28°C 的絕對差；低於目標也計入，所以它與只避免過熱的目標不同。估測 MAE 是熱源估測相對真值的誤差。proxy 依假設風扇功率積分，並非量測用電。</p><p>這批設定中，PI 的平均追蹤誤差最低；MPC 相對 PI 的風扇 proxy 低 {reduction:.2f}%，追蹤 MAE 高 {penalty:.2f}%。這是取捨，不是所有指標同時改善。PI/PID 的差只有 {c['pid']['tracking_mae_C']-c['pi']['tracking_mae_C']:.8f}°C，沒有足夠證據主張實質差異或統計顯著。</p><p>超溫以 5 秒取樣端點高於 30°C 計算；零秒不代表連續時間或真實機箱安全。全部方法的 PWM／變化率命令違例為零。運算時間含此主機與目前求解方式，不能直接推成嵌入式裝置的延遲。</p></section>'''
    notes = [
      ('固定風扇','固定請求 PWM 0.6，另有共同警告與限速；因此不是完全開迴路恆速。','追蹤誤差及風扇 proxy 均高於 PI；可作簡單基準。','固定輸出不依目標誤差調整，可能在低負載時過度冷卻、高負載時反應不足。需看逐時負載／溫度才能定位是哪一段造成誤差。','我保留它作基線，不能由其結果代表所有固定轉速。'),
      ('PI','以估測熱源誤差的比例與積分調整 PWM，使用反算式 anti-windup。','本批平均追蹤最低、計算量低，取樣超溫為零。','積分可處理持續偏差；本批慢變熱負載下可能已足夠。這是機制解釋，尚未以關閉積分等消融證實。','我把 PI 視為必須超越的強基線；仍不能宣稱跨設備最佳。'),
      ('PID','PI 再加低通濾波後的誤差微分；其餘條件相同。','與 PI 幾乎相同；微小 proxy／追蹤差異不構成穩健優勢。','慢變熱動態、微分權重及濾波可能使額外效果很小；尚未量化各控制項貢獻。','目前沒有增加微分項能帶來明顯收益的證據；噪聲與快速擾動需新實驗。'),
      ('LQR','依當前功率與入口求可達平衡點，線性化並解 DARE，再加共同限幅／限速。','追蹤、proxy 和 PWM 總變化均高於 PI；平均計算約 1 ms／步。','固定 Q/R 未按狀態容許範圍正規化、局部模型失配、限幅，以及每步重算平衡點／增益，都可能影響表現。它也未加入積分狀態；不能直接判定其中某項是主因。','LQR 是理論清楚的狀態回授基線；此實作未勝過 PI，限幅後也不能主張無限制 LQR 的全域最優性。'),
      ('線性 MPC','目前估測附近的仿射模型，六步＝30 秒；最佳化整段 PWM，負載假設保持目前值。','相對 PI，proxy 較低、追蹤稍差；本批取樣超溫為零。','代價同時處罰追蹤、輸入、變化率與超溫，允許控制量／溫度的折衷。較低 proxy 與此機制相容，但仍需固定預算的權重敏感度檢查。','適合進一步研究限制與取捨；溫度只是軟代價，不能保證不過熱。'),
      ('單步排序','在九個固定請求中，預測一步後排序選擇，另套用共同限制。','proxy 低，但平均有 6.25 秒取樣超溫，不能只看省能數字。','短視野與有限候選可能忽略風扇延遲／未來熱累积；需要新的視野消融和事件追蹤，才能判定具體原因。','可作低成本候選搜尋基準，不可視為完整 MPC。'),
      ('六步排序','仍是九個固定請求；把每個請求推進六步，並非最佳化六個獨立動作。','相對單步追蹤改善 0.069%，未達事前 5% 門檻；超溫平均 3.75 秒，計算量增加。','多看 30 秒但不增加候選動作自由度，可能使兩者首步選擇接近；模型失配也可能抵銷視野收益，均尚未完成原因消融。','H-ENC-52 不支持；保留較低取樣超溫這一描述性現象，不升格為安全或普遍優勢。'),
      ('六步無校正','關閉稀疏觀測校正，保留辨識後物理預測與六步排序。','相對有校正版本，估測與追蹤變差，平均超溫增至 12.5 秒；proxy 反而更低。','較低風扇輸出可能與未修正的估測偏差相關，造成少冷卻；需檢查逐時誤差正負與動作才能確立原因。','這是估測器消融，不是獨立控制方法；低 proxy 可能伴隨溫度代價，不能解讀成節能成功。'),
    ]
    body += '<section id="reasons"><h2>每個方法：機制、原因與結論</h2><p>「可能原因」是根據實作與結果提出的待驗證解釋，沒有當成已證明的因果。各方法都受到共同的 29.5°C 警告介入，因此目前比較的是含警告與限制的完整配置。</p>'
    for name,mechanism,observed,reason,conclusion in notes:
        body += '<article class="method"><h3>'+escape(name)+'</h3>'+''.join('<p><strong>'+label+'：</strong>'+escape(text)+'</p>' for label,text in [('實作機制',mechanism),('數據現象',observed),('可能原因，待驗證',reason),('目前結論',conclusion)])+'</article>'
    body += '</section><section id="per-rig"><h2>逐平台：平均值不能取代情境分析</h2><p>下表每格為同一平台兩個 seed 的平均追蹤 MAE；它仍不是大量獨立重複，沒有顯著性保證。</p>'
    rigs = [('contact_capacity','接觸／容量變體'),('extra_path','額外傳熱路徑')]
    body += table(['方法']+[name+' °C' for _,name in rigs],[[LABELS[m]]+[f'{mean(x["metrics"]["tracking_mae_C"] for x in runs if x["method"]==m and x["rig"]==rig):.4f}' for rig,_ in rigs] for m in METHODS])
    body += '<details><summary>展開四個配對回合的原始追蹤與超溫數字</summary>'+table(['平台','seed','方法','追蹤 MAE °C','取樣超溫 s'],[[x['rig'],x['seed'],LABELS[x['method']],f'{x["metrics"]["tracking_mae_C"]:.4f}',f'{x["metrics"]["overtemp_s"]:.0f}'] for x in runs])+'</details></section>'
    opened = r['aggregates']['open_loop']['holdout']
    body += '<section id="models"><h2>估測與模型結構：另外回答兩個問題</h2><h3>同一軌跡下，有限辨識與稀疏校正是否改善熱源估測？</h3>'+table(['估測配置','熱源 MAE °C'],[[label,f'{opened[m]["source_mae_C"]:.4f}'] for m,label in [('nominal_physics','名義物理'),('calibrated_physics','有限辨識物理'),('sparse_corrected','有限辨識＋稀疏校正')]])+'<p>平均校正改善 21.19%，但四組僅兩組改善，H-ENC-51 不支持。這裡使用相同開迴路資料，較適合隔離估測器差異；不能拿上面的不同閉迴路估測誤差直接當作純估測器排名。</p><h3>第二階段，增加模型自由度是否比較好？</h3><p>'+escape(second['decisions'])+'</p>'
    sc = second['result']['aggregates']['closed_loop']['holdout']
    body += table(['第二階段配置','追蹤 MAE °C','proxy Wh','取樣超溫 s'],[[label]+[f'{sc[m][k]:.4f}' for k in ('tracking_mae_C','fan_energy_proxy_Wh','overtemp_s')] for m,label in [('S_pi','S＋PI'),('selected_pi','選擇模型＋PI'),('S_rank_h6','S＋六步'),('selected_rank_h6','選擇模型＋六步')]])
    body += '<p>'+escape(second['boundary'])+'</p><p>兩階段的平台與資料不同，因此我只在各階段內比較，沒有把兩表串成所有方法的新總排名。第二階段 S＋六步的追蹤低於 S＋PI，也提醒我第一階段的 PI 排名不能外推。</p></section><section id="conclusion"><h2>我目前能下的實驗結論</h2><p>第一，方法選擇取決於追蹤、耗能估計、超溫與計算成本；單看最低 MAE 或最低 proxy 都不足以決策。第二，第一階段 PI 是強基線，LQR 沒有展示優勢，MPC 展現輸入成本與追蹤之間的取捨，延長排序視野未達原先改善門檻。第三，稀疏校正與更複雜模型都不保證跨情境改善；可見感測擬合不能替代隱藏熱源驗證。</p><p>以上限於固定設定、有限校正後的合成溫度實驗。沒有實機能耗、安全或任意設備泛化的證據；原先未支持的研究假設保持不變。</p><h3>如何把可能原因變成可驗證的解釋</h3>'+table(['待驗證問題','候選後續實驗（尚未執行）','避免混淆的條件'],[
    ['LQR 是否受權重與限制影響','記錄各狀態成本、未限幅／實際 PWM、限幅比例；比較固定預算的正規化權重','新開發資料選參；凍結後使用新 holdout，不由舊結果挑參'],
    ['六步為何收益小','在新場景比較相同候選、不同視野；記錄首步動作相同率與預測誤差','分開視野長度和動作自由度；共同負載與校正預算'],
    ['MPC 的低 proxy 是否可持續','固定候選權重與試驗預算，報追蹤／proxy／超溫取捨','不用不同方法各自最好看的單一指標宣稱勝出'],
    ['模型結構为何在對流失配失敗','新功率激勵與獨立熱源參考，檢查熱導／容量補償','參考只作評分；不要以可見擬合分數代替熱源準確度'],
    ['結果是否跨平台成立','擴充未見平台、噪聲／延遲與配對重複，先固定分析規則','以回合／平台作獨立單位，不把相鄰時間點當獨立樣本']])+'<p>这些是後續候選，尚未執行、尚未成為新增結論。下一輪需先固定研究問題、預算與驗證规则。</p></section>'
    body += '<section id="evidence"><h2>可核對來源</h2><p><a href="../../openspec/changes/integrate-enclosure-session-20261012/protocol.md">第一階段事前規則</a> · <a href="../../openspec/changes/integrate-enclosure-session-20261012/artifacts/result.json">第一階段完整結果</a> · <a href="../../openspec/changes/select-enclosure-structure-20261012/evidence.md">第二階段既有結論</a> · <a href="../../openspec/changes/select-enclosure-structure-20261012/artifacts/result.json">第二階段完整結果</a></p><p>原因解釋核對實作：<a href="../../digital_twin/enclosure/session.py">LQR／線性 MPC</a>、<a href="../../digital_twin/control/sparse_enclosure_v2.py">PI／PID 與共同警告</a>、<a href="../../digital_twin/control/sparse_enclosure.py">有限候選排序與估測器</a>。結果整理不涉及重跑研究。</p><p><a href="professor_research_2026-10-12_zh.html#lqr">完整 LQR 推導</a> · <a href="../papers/reference_sources/kalman_1960_optimal_control_original.pdf">Kalman 1960 完整原文</a></p></section>'
    for a,b in [('累积','累積'),('为何','為何'),('这些','這些'),('规则','規則')]: body = body.replace(a,b)
    output = REPORTS/'professor_comparison_2026-10-12_zh.html'
    output.write_text(page('各方法實驗比較、原因與結論',body))
    note = ROOT/'docs/research/conference_shortlist_2026-10-12_zh.md'
    (REPORTS/'conference_shortlist_2026-10-12_zh.html').write_text(page('研討會投稿候選與準備方向','<section>'+markdown(note.read_text())+'</section>'))
    QA.mkdir(parents=True,exist_ok=True)
    sources = [ROOT/'openspec/changes'/name/'artifacts/result.json' for name in ('integrate-enclosure-session-20261012','select-enclosure-structure-20261012')]
    receipt = {'scope':'descriptive reporting of frozen evidence; no experiment or new adopted conclusion','episode_aggregation_checks':len(METHODS)*len(metrics),'episodes_per_method':4,'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},'first_stage_rows':rows,'mpc_vs_pi_proxy_reduction_percent':reduction,'mpc_vs_pi_tracking_increase_percent':penalty}
    (QA/'numeric_verification.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(output)
    print('PASS: 48 independent aggregation checks; prior study decisions preserved')


if __name__ == '__main__':
    build()
