"""First-person offline briefing, with all numbers derived from verified evidence."""
from html import escape
import io
import json
import os
from pathlib import Path
import re
import tempfile

os.environ.setdefault('MPLCONFIGDIR',tempfile.mkdtemp(prefix='enclosure-session-mpl-'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
matplotlib.rcParams['svg.hashsalt']='enclosure-session-20261012'
from enclosure_session_summary import ROOT,ARTIFACTS,summary,LABELS,METHODS
from enclosure_structure_summary import summary as structure_summary, ARTIFACTS as STRUCTURE_ARTIFACTS


def structure_section(data):
    r=data['result']; calibration=data['calibration']
    names={'proportional':'同比例容量','independent_caps':'獨立容量', 'path_variant':'新增傳熱路徑',
           'contact_variant':'接觸／容量變體','path_capacity':'傳熱路徑／容量', 'convection_mismatch':'對流係數失配'}
    selection=''; costs=''; per_rig=''
    for rig,fit in calibration.items():
        s,f=fit['candidates']['S'],fit['candidates']['F']
        selection+=f'<tr><th scope="row">{names[rig]}</th><td>{s["selection_score"]:.4f}</td><td>{f["selection_score"]:.4f}</td><td>{fit["selected_structure"]}</td></tr>'
        for key,v in fit['candidates'].items():
            costs+=f'<tr><th scope="row">{names[rig]}／{key}</th><td>{v["nfev"]}／{v["residual_calls"]}</td><td>{v["wall_time_s"]:.3f}</td><td>{v["jacobian_condition"]:.2f}</td><td>{v["parameter_bound_indices"] or "無"}</td></tr>'
    for rig in ('contact_variant','path_capacity','convection_mismatch'):
        a=rig_metrics(r,rig,'S_corrected'); b=rig_metrics(r,rig,'selected_corrected')
        verdict='相同（保留 S）' if a==b else ('改善' if b<a else '退步')
        per_rig+=f'<tr><th scope="row">{names[rig]}</th><td>{a:.4f}</td><td>{b:.4f}</td><td>{verdict}</td></tr>'
    c=r['aggregates']['closed_loop']['holdout']
    methods={'S_pi':'S＋PI','selected_pi':'選擇模型＋PI','S_rank_h6':'S＋六步','selected_rank_h6':'選擇模型＋六步'}
    closed=''.join(f'<tr><th scope="row">{label}</th>'+''.join(f'<td>{c[m][k]:.4f}</td>' for k in
                      ('tracking_mae_C','source_mae_C','fan_energy_proxy_Wh','overtemp_s','compute_mean_ms'))+'</tr>' for m,label in methods.items())
    maximum=max(e['metrics']['max_source_C'] for e in r['runs'])
    return f'''<section id="structure"><h2>第二階段：可見擬合較好，隱藏熱源仍可能更差</h2>
<p>{escape(data['text'])}</p><p>我把前一階段的容量比例與缺少路徑問題，改成一個事前固定的有限模型選擇。S 是四參數模型，F 是七參數模型；判準只看金屬片、空氣與風扇，不看熱源參考。新增測試與前一階段分開，沒有拿同一批 holdout 調參。</p>
<h3>我如何選擇模型</h3><div class="table-wrap"><table><thead><tr><th>平台</th><th>S 留出分數</th><th>F 留出分數</th><th>選擇</th></tr></thead><tbody>{selection}</tbody></table></div>
<p class="caption">分數為可見三通道誤差除以噪聲標準差後的均方值，無單位，越低越好。只有 F 比 S 低至少 5% 才更換。選擇用的後 60 筆仍是校正資料；下表的熱源結果來自另兩個新 seed。</p>
<h3>新 holdout 的結果</h3><p>{escape(data['decisions'])}</p><div class="table-wrap"><table><thead><tr><th>holdout 平台</th><th>S 校正 MAE °C</th><th>選擇模型校正 MAE °C</th><th>結果</th></tr></thead><tbody>{per_rig}</tbody></table></div>
<p>平均退步主要來自對流係數失配：1.8376→2.7155°C；新增路徑／容量平台則由 0.2711→0.2045°C。接觸／容量平台保留 S，因此兩者相同。這些結果顯示模型選擇有情境差異，不能把三個可見留出改善當成熱源普遍改善。</p>
<details><summary>同一控制器下的模型比較與完整成本</summary><div class="table-wrap numbers"><table><thead><tr><th>方法</th><th>追蹤 MAE °C</th><th>估測 MAE °C</th><th>proxy Wh</th><th>超溫秒／回合</th><th>ms／步</th></tr></thead><tbody>{closed}</tbody></table></div>
<p>新實驗的所有回合最高熱源為 {maximum:.3f}°C；每 5 秒端點的超溫不包含連續尖峰保證。S／選擇模型的 PI 追蹤為 {c['S_pi']['tracking_mae_C']:.4f}／{c['selected_pi']['tracking_mae_C']:.4f}°C。此處只比較 PI 與六步排序下的模型差異，LQR／MPC 仍使用前一階段的完整比較。</p>
<div class="table-wrap numbers"><table><thead><tr><th>平台／模型</th><th>nfev／完整呼叫</th><th>秒</th><th>局部条件數</th><th>碰界索引</th></tr></thead><tbody>{costs}</tbody></table></div>
<p>每個模型 max_nfev=40、單一起點，完整呼叫包含數值 Jacobian。F 的參數索引為接觸熱導、片對流增益、源容量倍率、片容量倍率、氣容量倍率、風扇延遲、源—氣熱導。對流失配平台的索引 2 與 4 碰界；局部條件數只作數值診斷。</p>
<pre>F 額外加入：G_ha(T_h−T_a)
熱源方程扣除此熱流，空氣方程加回此熱流；內部交換保持總能量平衡。
三個容量倍率分別辨識；其他對流／旁路係數仍是假設。</pre></details>
<p>{escape(data['boundary'])}</p><p>因此我保留這次改進的實作與反例，但不把 F 說成已驗證較佳的熱源模型。下一階段應先用新的功率激励與獨立參考檢查容量／熱導的區分能力，再制定新的驗證規則。</p>
<p>{escape(data['integrity'])}</p><p><a href="../../openspec/changes/select-enclosure-structure-20261012/protocol.md">第二階段事前規則</a> · <a href="../../openspec/changes/select-enclosure-structure-20261012/artifacts/result.json">完整結果</a> · <a href="../../openspec/changes/select-enclosure-structure-20261012/artifacts/calibration.json">模型選擇與成本</a> · <a href="../../openspec/changes/select-enclosure-structure-20261012/artifacts/verification.json">逐筆核對</a></p></section>'''


def rig_metrics(result,rig,method,task='open_loop',key='source_mae_C'):
    values=[r['metrics'][key] for r in result['runs'] if r['rig']==rig and r['method']==method and r['task']==task]
    return sum(values)/len(values)


def figure(result):
    hold=result['aggregates']['closed_loop']['holdout']
    labels=['Fixed','PI','PID','LQR','Linear MPC','H=1','H=6','H=6, no correction']
    fig,axis=plt.subplots(figsize=(10,4.2),layout='constrained')
    values=[hold[m]['tracking_mae_C'] for m in METHODS]
    bars=axis.bar(labels,values,color=['#8293a1','#248278','#248278','#8262a1','#315f87','#c38c3e','#315f87','#a6b2bd'])
    axis.bar_label(bars,fmt='%.3f',padding=4)
    axis.set_ylabel('Tracking MAE (degrees C)')
    axis.set_title('Synthetic holdout: 2 assumed rigs x 2 seeds; equal episode weighting')
    axis.set_ylim(0,max(values)*1.25)
    axis.tick_params(axis='x',labelsize=8)
    axis.spines[['right','top']].set_visible(False)
    out=io.StringIO()
    fig.savefig(out,format='svg',metadata={'Date':None})
    path=ROOT/'docs/reports/assets/enclosure_session_2026-10-12.svg'
    path.write_text('\n'.join(line.rstrip() for line in out.getvalue().splitlines())+'\n')
    fig.savefig(path.with_suffix('.png'),dpi=180,metadata={'Software':'matplotlib'})
    plt.close(fig)
    svg=out.getvalue()[out.getvalue().index('<svg'):]
    return svg.replace('<svg ','<svg role="img" aria-label="新合成holdout八種控制方法追蹤誤差" ',1)


def build():
    data=summary(); result=data['result']; closed=result['aggregates']['closed_loop']['holdout']
    second=structure_summary()
    old=(ROOT/'docs/reports/professor_research_2026-10-06_zh.html').read_text()
    # Preserve source-checked historical device and LQR explanations.
    devices=re.search(r'<section id="devices">.*?</section>',old,re.S).group()
    devices=devices.replace('三組模擬係數','前次三組及本輪四組模擬係數')
    lqr=re.search(r'<section id="lqr">.*?</section>',old,re.S).group()
    lqr=lqr.replace('下週介紹：','本週介紹：').replace('備稿完成，尚未向教授報告。','備稿完成；口頭報告是否完成尚無紀錄。')
    lqr=lqr.replace('</section>','<p>本輪實作採離散模型與離散代數 Riccati 方程；上面的連續時間公式只用來介紹主線。實際 Q=diag(1,0.25,0.1,0.02)、R=0.15，狀態為熱源、金屬片、空氣與風扇比例相對平衡點的偏差；共同的 PWM／變化率限制另套用。</p></section>')
    script=re.search(r'<script>(.*?)</script>',old,re.S).group(1)
    table=''.join('<tr><th scope="row">'+LABELS[m]+'</th>'+''.join(f'<td>{closed[m][key]:.4f}</td>' for key in
                  ('tracking_mae_C','source_mae_C','fan_energy_proxy_Wh','overtemp_s','command_variation','compute_mean_ms'))+'</tr>' for m in METHODS)
    rig_names={'contact_capacity':'接觸／容量變體','extra_path':'額外傳熱路徑'}
    per_rig=''.join(f'<tr><th scope="row">{rig_names[rig]}</th><td>{rig_metrics(result,rig,"calibrated_physics"):.4f}</td>'
                   f'<td>{rig_metrics(result,rig,"sparse_corrected"):.4f}</td><td>{"改善" if rig_metrics(result,rig,"sparse_corrected")<rig_metrics(result,rig,"calibrated_physics") else "退步"}</td></tr>'
                   for rig in ('contact_capacity','extra_path'))
    calibration=json.loads((ARTIFACTS/'calibration.json').read_text())
    calrows=''.join(f'<tr><th scope="row">{rig}</th><td>{fit["parameters"]["contact"]:.4f}</td>'
                    f'<td>{fit["parameters"]["plate_fan"]:.4f}</td><td>{fit["parameters"]["capacities"][0]/20:.4f}</td>'
                    f'<td>{fit["parameters"]["fan_tau"]:.3f}</td><td>{fit["nfev"]}／{fit["residual_calls"]}</td>'
                    f'<td>{fit["wall_time_s"]:.3f}</td></tr>' for rig,fit in calibration.items())
    maximum=max(r['metrics']['max_source_C'] for r in result['runs'])
    fallbacks=sum(r['metrics']['fallbacks'] for r in result['runs'] if r['task']=='closed_loop')
    cpu_max=max(r['metrics']['compute_max_ms'] for r in result['runs'] if r['task']=='closed_loop')
    reading='''<div class="table-wrap"><table><thead><tr><th>來源與查閱日期</th><th>實際範圍</th><th>如何用於研究</th></tr></thead><tbody>
<tr><th>TI 熱設計指南／Noctua 風管，10/6</th><td>前次閱讀筆記的指定 PDF 頁與產品說明。</td><td>區分接觸導熱與入口／對流；實際裝置效果待量測。</td></tr>
<tr><th>Kalman 1960，10/6</th><td>18 頁原文重點問題與定理、p.112–113 公式核對，未逐行重證全部證明。</td><td>LQR 代表論文，原文頁碼見閱讀筆記。</td></tr>
<tr><th><a href="https://docs.scipy.org/doc/scipy-1.14.1/reference/generated/scipy.linalg.solve_discrete_are.html">SciPy DARE</a>，10/12</th><td>離散 Riccati 定義、解存在與數值條件；本輪官方來源已核對。</td><td>求離散 LQR 增益；失敗使用相同六步排序回退。</td></tr>
<tr><th><a href="https://docs.scipy.org/doc/scipy-1.14.1/reference/optimize.minimize-slsqp.html">SciPy SLSQP</a>，10/12</th><td>bounds、constraints、ftol 和 maxiter；本輪官方來源已核對。</td><td>六步線性 MPC 的命令／變化率限制；溫度代價為軟限制。</td></tr>
<tr><th><a href="https://docs.scipy.org/doc/scipy-1.14.1/reference/generated/scipy.optimize.least_squares.html">SciPy least_squares</a>，10/12</th><td>有限參數、單一起點與 nfev 的計數範圍；本輪官方來源已核對。</td><td>S／F 各一次有限辨識，另記錄數值 Jacobian 的完整殘差呼叫。</td></tr>
</tbody></table></div>'''
    talk='''<p><strong>研究進度約十分鐘，LQR 與代表論文約五分鐘，共十五分鐘。</strong>正文可依下列主線朗讀，技術細節另行展開。</p>
<h3>前兩分鐘 我如何回應傳熱場景的交辦</h3><p>我先整理金屬片、接觸介面與風管的作用。金屬片主要改變固體導熱與接觸熱阻，風管主要改變入口和對流。我選擇可控熱源、金屬片與風扇作候選平台，但目前沒有设备或資料，所以先把軟體和量測程序完成。</p>
<h3>第三到第五分鐘 我改進了什麼</h3><p>我把物理主模型、有限辨識、稀疏校正和動作選擇接成一個流程。熱源參考只交給評分，不給模型或控制器。第一階段辨識共同容量與風扇延遲，第二階段再測試獨立容量與新增熱導。新模型只用前 120 筆辨識、後 60 筆選擇，規則固定後才開啟新的測試。</p>
<h3>第六到第八分鐘 我遇到的反例</h3><p>第一階段平均估測有下降，但四組只有兩組改善，六步排序也未達門檻。第二階段的可見擬合較好，卻讓熱源誤差由 1.0764 增至 1.3468°C，六步追蹤誤差增加約 2.95%。退步主要在對流係數失配平台，熱容量還碰到搜尋邊界。我因此保留兩階段的不支持判定：增加模型自由度不能保證熱源估測或控制更好。</p>
<h3>第九到第十分鐘 我如何準備實機驗證</h3><p>我已準備輸入、校正與獨立參考三種資料模板，以及離線分析和獨立評分。下一步要先確認感測精度、初始條件、功率與 RPM 尺度，再凍結設備的實驗程序。軟體目前產生操作提案，沒有直接控制硬體。</p>
<h3>最後五分鐘 LQR 與 Kalman 1960</h3><p>我介紹的 LQR 是線性二次調節器：用線性狀態模型描述變化，用 Q 與 R 表達狀態偏差和操作代價，再透過 Riccati 方程求回授增益。Kalman 1960 提供理論基礎，但原文控制部分假設狀態精確已知，穩定定理也有條件。我現在把它接在稀疏估測後，另處理限幅；不能因此說真實機箱已經安全或最優。原文問題、核心式與限制可配合上面的頁碼筆記說明。</p>'''
    document=f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>教授交辦進度與 LQR 論文報告 2026-10-12</title><style>
:root{{color-scheme:light;--ink:#233545;--muted:#596b78;--accent:#315f87;--line:#d8e2e9}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:#f4f6f8;color:var(--ink);font:17px/1.85 system-ui,"PingFang TC",sans-serif;overflow-wrap:anywhere}}
main{{max-width:1100px;margin:auto;padding:36px 24px 70px}}header,section{{background:white;padding:30px;margin:20px 0;border:1px solid var(--line);border-radius:14px;scroll-margin-top:20px}}
h1{{font-size:clamp(28px,4vw,42px);line-height:1.35}}h2{{font-size:25px;line-height:1.5}}h3{{font-size:19px}}p{{margin:15px 0}}a{{color:var(--accent)}}
.meta,.caption{{font-size:14px;color:var(--muted)}}.lead{{font-size:20px}}nav{{display:flex;flex-wrap:wrap;gap:8px}}nav a{{text-decoration:none;padding:4px 11px;background:#eaf0f5;border-radius:7px}}
.table-wrap{{max-width:100%;overflow-x:auto;margin:20px 0}}table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{padding:11px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}thead th{{background:#edf3f8}}.numbers th,.numbers td{{white-space:nowrap}}
.flow{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}.flow div{{padding:16px;background:#edf3f8;border-radius:8px}}.flow strong{{display:block}}figure{{margin:25px 0;max-width:100%;overflow-x:auto}}figure svg{{display:block;width:100%;min-width:720px;height:auto}}
details{{padding:13px 0;border-top:1px solid var(--line)}}summary{{cursor:pointer;font-weight:600}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;background:#f2f5f7;padding:16px;font:14px/1.8 ui-monospace,monospace}}
.controls{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}label,input{{display:block;width:100%}}output{{display:block;padding:16px;background:#edf3f8;margin-top:14px}}:focus-visible{{outline:3px solid #bf8b35;outline-offset:3px}}
@media(max-width:650px){{main{{padding:12px 10px 40px}}header,section{{padding:20px 16px}}.flow,.controls{{grid-template-columns:1fr}}th,td{{padding:9px}}}}
@media print{{html{{scroll-behavior:auto}}body{{background:white;font-size:10.5pt;line-height:1.65}}main{{max-width:none;padding:0}}header,section{{padding:12px 0;margin:12px 0;border:0;border-radius:0}}nav,.controls{{display:none}}h2,h3,summary{{break-after:avoid}}figure,tr,pre{{break-inside:avoid}}figure{{overflow:visible}}figure svg{{min-width:0}}.table-wrap{{overflow:visible}}table{{font-size:8pt}}th,td{{padding:5px}}.numbers th,.numbers td{{white-space:normal}}a{{color:inherit}}.flow{{grid-template-columns:repeat(2,1fr)}}details{{break-inside:auto}}@page{{size:A4;margin:16mm}}}}
</style></head><body><main><header>
<p class="meta">報告整理 2026-10-12｜涵蓋 10/5–10/12｜前次文獻／原型 10/6；本輪新模擬 10/12｜口頭報告尚無完成紀錄</p>
<h1>我把機箱溫度模型接成可驗證流程<br>並準備 LQR 代表論文報告</h1>
<p class="lead">我完成了場景查證、量測資料介面、稀疏估測、控制比較與第二階段模型選擇。兩階段都保留未達判準的結果；可見感測擬合較好仍不保證熱源更準，實機待設備到位。</p>
<nav aria-label="報告目錄"><a href="#assignment">交辦進度</a><a href="#devices">傳熱場景</a><a href="#model">模型流程</a><a href="#experiment">第一階段</a><a href="#results">結果</a><a href="#problems">問題</a><a href="#structure">第二階段</a><a href="#lqr">LQR 論文</a><a href="#hardware">實機準備</a><a href="#talk">十五分鐘講稿</a><a href="#sources">來源</a></nav>
</header>
<section id="assignment"><h2>教授交代我的三件事</h2><div class="table-wrap"><table><thead><tr><th>交辦</th><th>這次交付</th><th>完成範圍</th></tr></thead><tbody>
<tr><th>找金屬片與風管場景</th><td>場景比較、传熱路徑、量測配置。</td><td>資料整理完成；實體效果未量測。</td></tr>
<tr><th>借用控制方法，改進自己的模型</th><td>量測 CSV → 有限辨識 → 稀疏估測 → 可限制的動作；新模擬比較。</td><td>溫度軟體整合完成；跨情境反例保留，完整機箱三因子尚未遷移。</td></tr>
<tr><th>介紹 LQR 與代表論文</th><td>Kalman 1960 原文頁碼、LQR 解說與本週講稿。</td><td>材料完成；實際口頭報告尚無紀錄。</td></tr>
</tbody></table></div><p>10/12 已確認目前沒有設備或資料，本次先完成軟體與實驗準備。<a href="../research/professor_meeting_actions_2026-10-06_zh.md">原交辦紀錄</a></p></section>
{devices}
<section id="model"><h2>我改进的是同一條研究流程</h2><div class="flow" aria-label="機箱溫度流程"><div><strong>① 物理主模型</strong>熱源、金屬片、空氣与風扇；分開接觸熱導、對流與容量。</div><div><strong>② 有限辨識</strong>相同 900 秒校正，辨識四個參數，固定其他假設。</div><div><strong>③ 稀疏估測</strong>金屬片、空氣、風扇、入口、功率；熱源參考僅作驗證。</div><div><strong>④ 操作選擇</strong>PI／PID、LQR、線性 MPC、單步／六步排序；共用限制與警告。</div></div>
<p>我將原本分開的候選元件接進正式套件中的機箱介面。輸入必須每 5 秒一筆，缺資料、非有限值、重複或亂序時間會被拒絕，沒有默默補值。CSV 分析只輸出 PWM 提案，沒有硬體連線。</p>
<details><summary>模型方程、狀態與方法邊界</summary><pre>C_h dT_h/dt = P − G_hp(T_h−T_p) − G_b(T_h−T_in)
C_p dT_p/dt = G_hp(T_h−T_p) − (G_p+k_p f)(T_p−T_a)
C_a dT_a/dt = (G_p+k_p f)(T_p−T_a) − (G_a+k_a f)(T_a−T_in)
τ_f df/dt = u−f</pre><p>這是我的模型整理；多步排序只評估有限候選 constant request，與最佳化整段控制序列的線性 MPC 分開。MPC 以目前估測做四狀態線性化，預測六步，命令與每步變化是硬限制，溫度是軟代價。原室內濕度、照度、八角點與空間殘差方法保留於原場景，這次沒有把它們改稱已在機箱驗證。</p></details></section>
<section id="experiment"><h2>我用新的資料檢查熱容量與方程失配</h2><p>{escape(data['text'])}</p>
<p>validation 為兩個容量／風扇變體；holdout 為不同容量比例與額外熱源—空氣直接傳熱的平台。每個平台先用相同校正程序，測試是有限調適後的遷移，不能稱零樣本。所有控制器共用同一負載、初始條件與噪聲抽樣；操作不同時，閉迴路溫度也會不同。</p>
<details><summary>固定校正預算與實際成本</summary><div class="table-wrap numbers"><table><thead><tr><th>平台</th><th>接觸 G W/K</th><th>對流增益 W/K</th><th>容量倍率</th><th>τ 秒</th><th>nfev／完整殘差呼叫</th><th>秒</th></tr></thead><tbody>{calrows}</tbody></table></div><p>max_nfev=40，單一起點；完整呼叫含數值 Jacobian。容量只辨識共同倍率，不保證三個獨立容量可辨識。額外路徑平台的接觸熱導落在上界 1.5，不能因 fit.success=True 就認定物理參數正確。</p></details>
<p>模擬的真值由另一個積分器算出，模型使用 RK4；未將熱源真值交給校正或控制。每回合 600 秒，先凍結再評估，沒有用新結果調參重跑。<a href="../../openspec/changes/integrate-enclosure-session-20261012/protocol.md">完整事前規則</a></p></section>
<section id="results"><h2>我得到的結果與兩個未達門檻的判定</h2><p>{escape(data['decisions'])}</p><figure>{figure(result)}<figcaption class="caption">新合成 holdout：兩個假設平台 × 兩個 seed，等權回合平均。圖顯示追蹤誤差，不代表估測精度或真實散熱效果。</figcaption></figure>
<p class="caption">手機可左右捲動圖表，查看完整比較。</p><div class="table-wrap numbers"><table><thead><tr><th>方法</th><th>追蹤 MAE °C</th><th>估測 MAE °C</th><th>風扇 proxy Wh</th><th>超溫秒／回合</th><th>Σ|ΔPWM|</th><th>計算 ms／步</th></tr></thead><tbody>{table}</tbody></table></div>
<p>全部評估回合最高熱源溫度為 {maximum:.3f}°C。取樣超溫只看每 5 秒端點，不保證捕捉連續尖峰。本輪求解回退合計 {fallbacks} 步，閉迴路單步計算最高 {cpu_max:.3f} ms，這是目前主機的紀錄，沒有在嵌入式設備測試。</p>
<h3>平均改善沒有涵蓋每一個平台</h3><div class="table-wrap"><table><thead><tr><th>新 holdout 平台</th><th>辨識物理 MAE °C</th><th>稀疏校正 MAE °C</th><th>結果</th></tr></thead><tbody>{per_rig}</tbody></table></div>
<p>接觸與容量變體從 0.2123 變成 0.3326°C，反而退步；額外路徑平台從 0.7238 降到 0.4051°C。我的結論因此是「部分情境平均有改善」，不是稀疏校正普遍更好。</p>
<details><summary>前次結果與本次結果如何區分</summary><p>10/6 的三組指定同方程平台，稀疏估測 0.6580→0.3352°C，六步追蹤相對單步改善 9.03%，仍未優於 PI。本次新增熱容量與路徑失配、不同負載與較短回合，六步改善降至約 0.069%。兩次的研究條件不同，不能直接算成演算法退步百分比；前次正向判定維持原範圍，本次判定另外保留。<a href="professor_research_2026-10-06_zh.html">10/6 完整報告</a></p></details></section>
<section id="problems"><h2>我遇到的問題如何影響下一步</h2><p>我原先只有同方程、部分係數已知的模擬，難以回答換設備是否仍有效。這次把容量倍率與風扇延遲納入有限辨識，並加入模型沒有的傳熱路徑；結果顯示平均與覆蓋判準會給不同結論。</p>
<p>接觸／容量平台在稀疏校正後退步，說明固定噪聲與模型設定不能保證每個情境改善。額外路徑的辨識參數碰到上界，則提醒我搜尋成功不等於方程正確；模型可能用錯誤係數補償缺少的路徑。我保留結果，沒有針對 holdout 加平台例外。</p>
<p>控制方面，PI 的追蹤略好，MPC 或排序的能耗 proxy 較低。下一步需要先決定重視追蹤、超溫還是操作成本，再用新的資料檢查共同程序；不能只因某個方法較複雜就預期它勝出。</p><p>{escape(data['boundary'])}</p></section>
{structure_section(second)}
{lqr}
<section id="hardware"><h2>設備到位後我可以如何開始</h2><p>我已備妥獨立輸入、校正與參考溫度模板，以及離線提案和獨立評分程序。先做感測共址校正、確認熱平衡初始條件、量測功率與 RPM 尺度，再以新的事前規則固定平台可操作範圍、資料切分及停止條件。</p>
<p><a href="../research/enclosure_hardware_execution_2026-10-12_zh.md">完整實機程序</a> · <a href="../templates/enclosure_observations.csv">觀測模板</a> · <a href="../templates/enclosure_commissioning.csv">校正模板</a> · <a href="../templates/enclosure_reference.csv">獨立參考模板</a></p>
<details><summary>離線流程與缺資料處理</summary><pre>觀測／校正 CSV → 已知初始條件檢查 → 有限辨識 → PWM 提案 JSON
獨立參考 CSV + 提案 JSON → 當下估測與下一步預測的獨立評分</pre><p>目前沒有實測資料，所以空白模板不填預期數字。缺感測或時間錯誤不產生新提案；硬體失效保護需要實際設備設計，不能由這個軟體錯誤處理推論已完成。</p></details>
<h3>我想請教授討論</h3><ol><li>先以低功率金屬片平台量測接觸／對流，還是直接研究桌機機箱？兩者的熱路徑與資料可得性不同。</li><li>控制目標要以追蹤為主，還是以超溫與能耗為主？目前 PI 與模型方法呈現不同權衡。</li><li>共同容量倍率是否足以作下一階段，或應先增加容量比例與額外傳熱路徑的辨識證據？</li></ol></section>
<section id="talk"><h2>我向教授報告的十五分鐘主線</h2>{talk}<p><a href="professor_oral_script_2026-10-12_zh.md">完整講稿</a></p></section>
<section id="sources"><h2>實際閱讀來源與可核對結果</h2>{reading}<p>{escape(data['integrity'])}</p>
<details><summary>展開研究證據與歷史資料</summary><p><a href="../../openspec/changes/integrate-enclosure-session-20261012/artifacts/result.json">本輪完整结果</a> · <a href="../../openspec/changes/integrate-enclosure-session-20261012/artifacts/verification.json">逐筆核對</a> · <a href="../../openspec/changes/integrate-enclosure-session-20261012/artifacts/calibration.json">校正與成本</a> · <a href="../../openspec/changes/integrate-enclosure-session-20261012/artifacts/freeze.json">評估前凍結</a> · <a href="../research/enclosure_transfer_sources_2026-10-06_zh.md">前次來源筆記</a> · <a href="professor_catchup_report_2026-10-05_zh.html">10/5 歷史報告</a></p></details></section>
</main><script>{script}</script></body></html>'''
    # Normalize traditional Chinese in newly authored prose only.
    for simplified,traditional in [('改进','改進'),('传熱','傳熱'),('对流','對流'),('与','與'),('热源','熱源'),('设备','設備'),('结果','結果'),('条件','條件'),('激励','激勵')]:
        document=document.replace(simplified,traditional)
    target=ROOT/'docs/reports/professor_research_2026-10-12_zh.html'
    target.write_text('\n'.join(line.rstrip() for line in document.splitlines())+'\n')
    # Talk remains first-person and shares the same evidence as the HTML.
    from html.parser import HTMLParser
    class Text(HTMLParser):
        def __init__(self):
            super().__init__(); self.parts=[]
        def handle_data(self,value):
            self.parts.append(value)
        def handle_endtag(self,tag):
            if tag in ('h3','p'):
                self.parts.append('\n\n')
    parser=Text();parser.feed(talk)
    script_path=ROOT/'docs/reports/professor_oral_script_2026-10-12_zh.md'
    script_path.write_text('# 機箱研究進度與 LQR 代表論文講稿\n\n準備日期 2026-10-12；約十五分鐘。口頭報告尚無完成紀錄。\n\n'+''.join(parser.parts).replace('设备','設備').replace('热源','熱源')+'\n\n[完整 HTML](professor_research_2026-10-12_zh.html)\n')
    return target


if __name__=='__main__':
    print(build())
