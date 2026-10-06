#!/usr/bin/env python3
"""Cumulative offline professor report, continuing the September 21 artifact."""
from html import escape
import json
from pathlib import Path
import re
from enclosure_control_v2_summary import ROOT,ARTIFACTS,METHODS,LABELS,summary
from build_enclosure_control_v2_report import scientific_chart
from professor_report_reading import reading_section

OUTPUT=ROOT/'docs/reports/professor_catchup_report_2026-10-05_zh.html'


def build():
    data=summary()
    if data is None:raise FileNotFoundError('Completed evidence required')
    r=data['result'];hold=r['aggregates']['holdout'];verify=json.loads((ARTIFACTS/'verification.json').read_text())
    if verify['status']!='PASS':raise ValueError('Independent audit not passed')
    old=(ROOT/'docs/reports/professor_catchup_report_2026-09-21_zh.html').read_text()
    css=re.search(r'<style>(.*?)</style>',old,re.S).group(1)
    historical=[]
    for name in ('timeline','research-questions','journey','problems','core','enclosure','control','tuning','architecture'):
        section=re.search(r'<section id="'+name+r'">.*?</section>',old,re.S).group(0)
        section=re.sub(r'id="([^"]+)"',lambda m:'id="history-'+m.group(1)+'"',section)
        section=re.sub(r'href="#([^"]+)"',lambda m:'href="#history-'+m.group(1)+'"',section)
        section=section.replace('這週','9月中下旬').replace('本週','9月中下旬').replace('今天','當時')
        historical.append(section)
    historical='\n'.join(historical)
    cols=('tracking_mae_C','tracking_rmse_C','fan_energy_proxy_Wh','pwm_total_variation','control_p95_s')
    rows=''
    for m in METHODS:
        a=hold[m]
        rows+='<tr><td>'+LABELS[m]+'</td>'+''.join(f'<td>{a[k]:.4f}</td>' for k in cols)+f'<td>{a["overtemp_s"]:.0f}</td></tr>'
    stress=''
    for split,label in (('plant_holdout','事先指定假設參數變體'),('overload','超載')):
        for m in METHODS:
            a=r['aggregates'][split][m]
            stress+=f'<tr><td>{label}</td><td>{LABELS[m]}</td><td>{a["tracking_mae_C"]:.4f}</td><td>{a["overtemp_s"]:.1f}</td><td>{a["fallback_n"]:.2f}</td><td>{a["safety_override_n"]:.1f}</td></tr>'
    v1=json.loads((ROOT/'openspec/changes/implement-enclosure-mpc-20261005/artifacts/result.json').read_text())
    cpu,gpu=(80.,85.)
    frozen_config=json.loads((ARTIFACTS/'freeze.json').read_text())['config']
    settings=frozen_config['settings'];pars=frozen_config['parameters']
    band=[f'{LABELS[m]}：'+str(hold[m]['band_entry_60s_achieved_n'])+'/3 回合達成' for m in METHODS]
    key_message=(f'MPC holdout MAE 為 {hold["mpc"]["tracking_mae_C"]:.4f}°C，比 PID＋前饋高 '
                 f'{-r["decisions"]["holdout_relative_mae_gain_vs_pid"]*100:.2f}%，比 LQR 高 '
                 f'{-r["decisions"]["holdout_relative_mae_gain_vs_lqr"]*100:.2f}%。')
    all_runs=''
    for run in r['runs']:
        a=run['metrics'];entry='未達' if a['band_entry_60s_s'] is None else f'{a["band_entry_60s_s"]:.0f}'
        all_runs+=f'<tr><td>{run["split"]}</td><td>{run["seed"]}</td><td>{LABELS[run["method"]]}</td><td>{a["tracking_mae_C"]:.4f}</td><td>{a["cpu_mae_C"]:.4f}/{a["gpu_mae_C"]:.4f}</td><td>{a["max_cpu_C"]:.2f}/{a["max_gpu_C"]:.2f}</td><td>{a["overtemp_s"]:.0f}</td><td>{a["fan_energy_proxy_Wh"]:.4f}</td><td>{a["fallback_n"]}</td><td>{a["control_p95_s"]:.6f}</td><td>{entry}</td></tr>'
    prefix='../../openspec/changes/validate-enclosure-four-controllers-20261005/'
    reading=reading_section(ROOT)
    html=f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>我的研究進度與探索過程｜近期研究整理</title><style>{css}
main{{overflow-wrap:anywhere}}figure{{margin:20px 0}}figure svg{{width:100%;height:auto;display:block}}figcaption{{color:var(--muted);font-size:14px}}details{{background:white;border:1px solid var(--line);border-radius:15px;padding:18px 20px;margin:16px 0}}summary{{cursor:pointer;font-weight:800;color:var(--navy);font-size:17px}}.formula{{overflow-wrap:anywhere;background:#edf5ff;padding:14px 18px;border-radius:10px;font-family:ui-monospace,monospace}}.status-grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}}.status-grid article{{padding:18px;background:white;border:1px solid var(--line);border-radius:15px}}.status-grid .metric{{font-size:28px}}.table-wrap table{{min-width:640px}}#all-runs table{{min-width:1040px}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px}}.source{{overflow-wrap:anywhere}}@media(max-width:650px){{.status-grid{{grid-template-columns:1fr 1fr}}}}@media print{{details{{break-inside:auto}}nav{{display:none}}.table-wrap{{overflow:visible}}.table-wrap table{{min-width:0;font-size:8pt}}}}
</style></head><body>
<header><p class="eyebrow">PROFESSOR RESEARCH REPORT · RESEARCH PROGRESS</p><h1><span>從稀疏感測到機箱控制</span><span>我的驗證、修正與研究進度</span></h1><p>研究進度分段整理｜從8月中旬的估測驗證、9月上旬的平台探索，到9月中下旬的機箱方向整理，再接續 MPC／LQR 實作、四方法比較與獨立核對。前期成果與後續補充結果分開呈現。</p></header>
<nav aria-label="報告章節"><a href="#overview">本次重點</a><a href="#tasks">教授要求與完成度</a><a href="#story">我如何推進</a><a href="#model">模型與方法</a><a href="#review">問題與改進</a><a href="#results">比較結果</a><a href="#limits">限制與下一步</a><a href="#next-week">下週計畫</a><a href="#reading">查閱論文</a><a href="#background">前期研究脈絡</a><a href="#talk">15分鐘講稿</a><a href="#questions">與教授討論</a><a href="#sources">來源</a></nav>
<main>
<section id="overview"><h2>這次，我完成了什麼</h2><p class="lead">我先建立機箱熱模型與MPC，作為自己的數位孿生方法遷移到機箱的前置研究，再檢查求解可靠性、目標是否可達，以及比較條件是否一致。之後我加入 LQR 與具負載前饋的 PID，重新固定比較條件。結果顯示：求解可靠性改善，但較複雜的 MPC 沒有在本輪保留測試中帶來更好的追蹤。</p>
<div class="status-grid"><article><span class="tag good">方法完成</span><div class="metric">4 種</div><p>固定風扇、PID＋前饋、LQR、MPC</p></article><article><span class="tag good">校準後凍結</span><div class="metric">48 回合</div><p>正式比較／5,760 控制步</p></article><article><span class="tag warn">殘差檢查回退</span><div class="metric">7 步</div><p>validation 5步、參數變體2步；無命令違例或超時</p></article><article><span class="tag warn">比較結論</span><div class="metric">不支持</div><p>MPC 優於 PID＋前饋或 LQR 的預設假設</p></article></div>
<p class="callout"><strong>我目前的判斷：</strong>{key_message}同一測試下，MPC 風扇能耗 proxy 也較高。因此我先保留簡單方法作為基準，下一步需要改善模型與取得量測證據，不能只靠增加控制器複雜度。</p></section>
<section id="tasks"><h2>兩週前的要求，我做到哪裡</h2><p>9/21 會議紀錄寫的是「教授提出 MPC」，LQR 是我另外查到的候選方法。我把兩者和既有 fixed fan／PID 納入相同條件比較；沒有把 LQR 改寫成教授原話。</p><div class="table-wrap"><table><thead><tr><th>工作</th><th>我完成的內容</th><th>目前狀態</th></tr></thead><tbody>
<tr><td>MPC 方法與機箱適用性</td><td>有限 horizon、狀態／負載觀測、PWM／slew 硬限制、溫度軟限制、第一步執行與重新規劃</td><td class="status-good">方法整理與模擬完成</td></tr>
<tr><td>LQR 狀態空間與 Q/R</td><td>可達平衡點分配、ZOH 離散模型、DARE 求增益、相同命令保護</td><td class="status-good">方法整理與模擬完成</td></tr>
<tr><td>可重設模型與 dry run</td><td>雙熱節點＋風扇延遲、獨立連續模型／平衡點／失敗路徑測試</td><td class="status-good">完成，參數為假設</td></tr>
<tr><td>四方法統一比較</td><td>每方法3候選×3校準回合；36回合後凍結，另48正式回合</td><td class="status-good">完成，全部結果保留</td></tr>
<tr><td>操作後預測與控制結果</td><td>分開評估 prediction error、tracking MAE、取樣超溫、能耗proxy與動作變化</td><td class="status-mixed">僅假設模型，不代表實測準確度</td></tr>
<tr><td>NTC、RPM、整機功耗、throttling、實機介入</td><td>沒有新增實體量測或可控制設備紀錄</td><td class="status-no">NOT_EVALUATED</td></tr></tbody></table></div><p class="source">依據：<a href="../research/weekly_research_tasks_2026-09-21_zh.md">9/21會議後清單</a>、<a href="../research/mpc_execution_plan_2026-10-05_zh.md">計劃與實際執行</a>。</p></section>
<section id="story"><h2>我如何從方法探索走到這次比較</h2><div class="timeline">
<article><time>8月中旬：估測與保留點驗證</time><h3>先釐清模擬和真實量測的證據範圍</h3><p>我整理模型 baseline、Kalman 去噪與臥室保留點結果，檢查稀疏感測能支持哪些估測主張。</p></article>
<article><time>9月上旬：公開資料與平台探索</time><h3>從 AAU／BMC 延伸到可互動模型</h3><p>我比較時序模型與公開機櫃資料，接著查找 TCLab、BOPTEST 等平台，處理資料解析、單位與 API 連線問題。</p></article>
<article><time>9月中下旬：機箱方向與會議要求</time><h3>觀測資料無法回答新控制動作的效果</h3><p>公開 BMC／AAU 可以支持估測研究，但不能直接驗證更改風扇後的反應。我因此延續可重設模擬與固定校準／驗證流程，聚焦機箱控制，並依9/21會議要求整理MPC。</p></article>
<article><time>後續補充・第一階段：受限制 MPC</time><h3>我先跑 fixed／PID／MPC</h3><p>v1 的36回合中，holdout MPC MAE 是1.4426°C，PID是2.6034°C。但 MPC 能耗 proxy 比 PID 高40.20%，過載190/360步數值回退。這些結果保留為歷史版本。</p></article>
<article><time>後續補充・問題確認與改進</time><h3>數值可靠性、單風扇目標與驗證獨立性</h3><p>我發現同一風扇通常不能同時讓兩節點穩於60°C；原求解器在可行的軟限制問題中仍失敗；驗證器也未完整重算判準。因此我修正求解流程與核對方式。</p></article>
<article><time>後續補充・第二階段：新版四方法</time><h3>我先凍結，再看新的合成測試</h3><p>我加入可達參考點的 LQR，也讓 PID 使用同一模型的負載前饋；每方法三候選，僅看校準選參。新的48回合包含 nominal、三組假設參數變體及過載，不把新 seed 當成新設備。</p></article></div><p class="source">前期日期依既有報告分段；後續補充按實作順序呈現，實驗實際執行時間保留於來源紀錄。</p></section>
<section id="model"><h2>我固定的模型與控制流程</h2><p>狀態是 CPU 溫度、GPU 溫度與有效風扇比例 f；輸入是 PWM u。入口溫度與當下 CPU／GPU 負載是擾動。所有方法只見當下觀測，不提供未來負載。</p><p class="formula">C<sub>i</sub> · dT<sub>i</sub>/dt = P<sub>i</sub> − (G<sub>i</sub> + k<sub>i</sub>f) · (T<sub>i</sub> − T<sub>in</sub>)<br>τ · df/dt = u − f；RPM = RPM<sub>max</sub> · f = {pars['max_rpm']:g}f</p><p>上式是我的數學化整理，參數是研究假設，沒有宣稱出自文獻的逐字公式或實機辨識。以下數值是名義模型設定；假設參數變體另列於完整設定。</p>
<p class="callout"><strong>研究定位：模型遷移到機箱的前置研究。</strong>我先建立機箱的簡化熱模型，作為原有數位孿生方法遷移到機箱場景的候選物理主模型。目前參數採假設值，後續將以量測資料辨識參數，再接入自己的稀疏感測校正、設備影響學習與殘差修正流程。現階段只涵蓋溫度子問題，尚未完成原本三因子方法的整套遷移。</p>
<p><strong>這組參數實際用在哪裡：</strong>C、G、k、τ與最大RPM描述「CPU、GPU雙熱節點＋風扇延遲」的特性；本輪固定為假設值，沒有從實機資料辨識。模擬plant依此產生反應，作為固定風扇／PID／LQR／MPC比較的測試環境。MPC／LQR使用其名義模型的局部離散形式，PID的負載前饋也使用名義散熱關係。PID增益、LQR的Q/R、MPC的預測步數與權重則是另外設定的控制器參數。</p>
<h3>公式符號、單位與目前設定</h3><div class="table-wrap"><table><thead><tr><th>符號</th><th>意義</th><th>單位</th><th>目前設定／如何解讀</th></tr></thead><tbody>
<tr><td>i</td><td>熱節點索引</td><td>無</td><td>分別代表 CPU、GPU；兩者共用同一風扇狀態 f 與入口溫度。</td></tr>
<tr><td>t</td><td>連續時間</td><td>s</td><td>控制命令每 {settings['dt_s']:g} 秒更新；MPC 預測 {settings['horizon']} 步（{settings['dt_s']*settings['horizon']:g} 秒）。</td></tr>
<tr><td>T<sub>i</sub></td><td>第 i 個節點的模型溫度</td><td>°C</td><td>CPU／GPU 狀態；本輪初始值依seed為CPU 58–60°C、GPU 59–61°C，目標為60／60°C。尚未以實體感測器驗證。</td></tr>
<tr><td>dT<sub>i</sub>/dt</td><td>節點溫度隨時間的變化率</td><td>°C/s</td><td>正值表示升溫，負值表示降溫。</td></tr>
<tr><td>C<sub>i</sub></td><td>節點的等效熱容量</td><td>J/K</td><td>CPU {pars['capacities'][0]:g}、GPU {pars['capacities'][1]:g}；升高1 K所需熱量。數值越大，相同淨熱功率下溫度變化越慢。</td></tr>
<tr><td>P<sub>i</sub></td><td>節點的產熱功率／負載擾動</td><td>W（J/s）</td><td>由各回合的CPU／GPU功率情境給定，隨時間變動；不是CPU使用率，也不是整機實測功耗。</td></tr>
<tr><td>G<sub>i</sub></td><td>不隨風扇比例改變的基礎等效熱導</td><td>W/K</td><td>CPU {pars['conductances'][0]:g}、GPU {pars['conductances'][1]:g}；與入口每差1 K所對應的基礎散熱功率。</td></tr>
<tr><td>k<sub>i</sub></td><td>風扇增加的等效熱導係數</td><td>W/K（f為無因次）</td><td>CPU {pars['fan_gains'][0]:g}、GPU {pars['fan_gains'][1]:g}；風扇貢獻為 k<sub>i</sub>f，總熱導為 G<sub>i</sub>＋k<sub>i</sub>f。</td></tr>
<tr><td>T<sub>in</sub></td><td>機箱入口空氣溫度</td><td>°C</td><td>兩節點共用的外部擾動，由情境給定，約30°C附近變動；與 T<sub>i</sub> 相減得到溫差，1°C溫差等於1 K。</td></tr>
<tr><td>f</td><td>有效風扇比例／正規化轉速狀態</td><td>無因次，0–1</td><td>模擬初始 f=0.5；不是PWM命令本身，會因風扇延遲逐步接近 u。</td></tr>
<tr><td>df/dt</td><td>有效風扇比例的變化率</td><td>s⁻¹</td><td>由 (u−f)/τ 決定；u大於f時加速，小於f時減速。</td></tr>
<tr><td>τ</td><td>風扇一階響應時間常數</td><td>s</td><td>{pars['fan_tau_s']:g}秒；固定u時，經過一個τ約完成63.2%的剩餘變化，並非瞬間到達命令值。</td></tr>
<tr><td>u</td><td>控制器送出的PWM占空比命令</td><td>無因次，0–1</td><td>本輪允許 {settings['pwm_min']:g}–{settings['pwm_max']:g}（20%–100%）；每步變化最多 {settings['max_delta']:g}，即10個百分點。</td></tr>
<tr><td>RPM<sub>max</sub></td><td>假設最大風扇轉速</td><td>rev/min（轉/分鐘）</td><td>{pars['max_rpm']:g}；是模型換算係數，尚未以實際風扇校準。</td></tr>
<tr><td>RPM</td><td>由 f 換算的模型風扇轉速</td><td>rev/min（轉/分鐘）</td><td>RPM={pars['max_rpm']:g}f；例如f=0.5對應3000 RPM。這是線性假設，不代表真實PWM與RPM必然成正比。</td></tr>
</tbody></table></div><p class="callout"><strong>兩個方程式的意思：</strong>第一式表示「儲存熱量的速率＝產熱功率−散熱功率」，各項單位都是W；當產熱大於散熱時溫度上升。第二式描述風扇追隨PWM命令的延遲。此簡化模型未加入CPU與GPU之間的直接熱交換，也未加入感測誤差。</p>
<div class="flow"><div><strong>1. 觀測當下</strong>兩節點溫度、風扇、入口與負載</div><div><strong>2. 形成模型</strong>名義參數與局部 ZOH 離散化</div><div><strong>3. 選擇控制動作</strong>固定／PID＋前饋／LQR／MPC</div><div><strong>4. 套用共同保護</strong>PWM、變化率、警告與失敗回退</div><div><strong>5. 記錄並核對</strong>plant反應、預測、控制代價與判準</div></div>
<div class="table-wrap" style="margin-top:20px"><table><thead><tr><th>方法</th><th>我如何設定</th><th>主要限制</th></tr></thead><tbody><tr><td>固定風扇</td><td>校準選 PWM 0.6</td><td>沒有依負載調整，仍套同一警告保護</td></tr><tr><td>PID＋平衡點前饋</td><td>負載估計穩態PWM＋溫度誤差回授；Kp=.06、Ki=.0003、Kd=.05</td><td>只搜尋三組；是新版前饋PID，不能與v1 PID數字直接混算</td></tr><tr><td>經限制的 gain-scheduled LQR</td><td>先分配可達平衡點；Q=diag(.04,.04,0)，校準選R=1</td><td>套slew／飽和後不宣稱受限最優或全域穩定</td></tr><tr><td>受限制 MPC</td><td>每步QP、thermal slack、horizon12；校準選R=.1</td><td>horizon內固定當下負載；局部線性模型；軟溫度上限不是安全保證</td></tr></tbody></table></div>
<p class="callout"><strong>相同的比較條件：</strong>目標60／60°C，上限80／85°C，警告75／80°C，PWM .2–1，每步變化不超過 .1；每方法3候選×相同3個校準seed。這是相同候選評估回合預算，CPU運算時間並不相等。</p></section>
<section id="review"><h2>我找到的問題與改進方法</h2><p>我在前置研究中找到以下問題，分別調整求解方式、目標設定與比較流程；尚未完成的模型辨識另列為後續工作。</p><div class="table-wrap"><table><thead><tr><th>我找到的問題</th><th>改進方法</th><th>目前結果／待確認</th></tr></thead><tbody>
<tr><td>第一階段超載有190步求解失敗，但軟溫度限制允許可行解，失敗原因需檢查數值求解。</td><td>已改用專用QP求解器OSQP、調整變數尺度、採ZOH離散預測，並檢查收斂與原約束殘差。</td><td>新版超載0回退；其他切分仍有7步未通過殘差檢查而回退。超載依然超溫。</td></tr>
<tr><td>單一風扇通常無法讓CPU／GPU同時穩在60°C。</td><td>已先在允許的風扇範圍內分配可達平衡點，再讓LQR計算回授增益。</td><td>平衡點與增益計算測試通過；尚未驗證實機穩定性。</td></tr>
<tr><td>部分指標與判準原先沒有獨立重算，實驗中斷也可能覆寫紀錄。</td><td>已從原始紀錄獨立重算指標、判準與熱模型步進，保留每次執行紀錄，並測試錯誤資料能否被拒絕。</td><td>84回合、10080步核對通過；6項篡改／失敗測試通過。</td></tr>
<tr><td>第一階段各方法候選數不同，PID也未使用相同的負載前饋。</td><td>已統一為每方法3候選，PID共享名義模型前饋；校準後凍結，再開新的合成測試。</td><td>完成48個正式回合；新版結果不支持MPC優於PID＋前饋或LQR。</td></tr>
<tr><td>熱模型參數仍是假設值，原有稀疏校正與學習流程尚未接入機箱。</td><td>後續先整理同步量測與熱參數辨識程序，再接入自己的校正、設備影響學習與殘差修正。</td><td>列入後續計畫；目前只支持假設模型比較，尚未完成整套方法遷移或實機驗證。</td></tr></tbody></table></div></section>
<section id="results"><h2>我得到的結果：MPC 沒有勝過較簡單的基準</h2><p class="lead">以下是新版 nominal synthetic holdout 的三 seed 等權平均；每回合20分鐘。同一負載、初始條件與保護限制下比較。</p><figure>{scientific_chart(r)}<figcaption>柱：三seed平均；黑點：逐seed結果。左圖追蹤誤差，右圖假設風扇能耗，不是整機耗電或實測節能。</figcaption></figure>
<div class="table-wrap"><table><thead><tr><th>方法</th><th>MAE °C</th><th>RMSE °C</th><th>fan proxy Wh</th><th>PWM TV</th><th>control p95 s</th><th>取樣超溫 s</th></tr></thead><tbody>{rows}</tbody></table></div>
<p>{key_message}MPC的相對改善假設 H-CTRL-02／03 都是 <strong class="status-no">NOT_SUPPORTED</strong>；數值健康 H-CTRL-01 是 <strong class="status-good">SUPPORTED_SIMULATION_ONLY</strong>。三seed沒有做顯著性或設備泛化推論。</p>
<h3 style="margin-top:24px">我把「求解正常」和「散熱能力不足」分開看</h3><div class="table-wrap"><table><thead><tr><th>測試</th><th>方法</th><th>MAE °C</th><th>取樣超溫 s/回合</th><th>數值回退步/回合</th><th>警告覆寫步/回合</th></tr></thead><tbody>{stress}</tbody></table></div><p>過載假設450W／600W，入口約30°C；最大風扇下穩態溫度約90°C，已高於限制。新版超載雖每步正常求解，仍無法保證不超溫。這是模型散熱能力不足，不能由更換求解器消除。</p>
<p>prediction MAE 與 tracking MAE 分開保存；名義 one-step prediction error 低，主要因模型參數已知，不能當成實測預測準確度。首次連續60秒進入±2°C只是進入誤差帶指標，不保證往後負載變動都能維持。{escape('；'.join(band))}。</p>
<details id="all-runs"><summary>展開全部48個正式回合與負面結果</summary><div class="table-wrap"><table><thead><tr><th>切分</th><th>seed</th><th>方法</th><th>MAE °C</th><th>CPU/GPU MAE</th><th>CPU/GPU peak</th><th>超溫 s</th><th>proxy Wh</th><th>回退步</th><th>p95 s</th><th>首次60s誤差帶 s</th></tr></thead><tbody>{all_runs}</tbody></table></div></details>
<details><summary>第一階段歷史結果為何與本輪不同</summary><p>v1 fixed／PID／MPC holdout MAE=5.4378／2.6034／1.4426°C，MPC改善44.59%，但能耗proxy增加40.20%、超載求解回退190/360步。本輪加入前饋PID、不同負載、ZOH與重新固定的候選集合，所以不能把兩版差異解釋為單一演算法改版效應。舊結果和凍結證據完整保留。</p><p><a href="enclosure_mpc_2026-10-05_zh.html">第一階段完整報告</a></p></details></section>
<section id="limits"><h2>我現在能支持什麼，還缺什麼</h2><div class="grid"><article class="card"><span class="tag good">完成</span><h3>假設模型內的可重現比較</h3><p>方法實作、有限校準、凍結、48回合新合成比較與獨立核對已完成。我能交代各方法的誤差、計算與風扇代價，並保留不支持的結果。</p></article><article class="card"><span class="tag warn">仍有限制</span><h3>模型與觀測條件理想</h3><p>完整溫度與fan狀態可見；PID＋FF、LQR、MPC知道名義假設參數。三個plant variants只是指定的合成壓力測試，不是獨立實體設備。</p></article><article class="card"><span class="tag bad">尚未量測</span><h3>實體辨識與介入</h3><p>尚未提供NTC／RPM／負載同步量測、可控制機箱或硬體介入紀錄；整機耗電、throttling與E8仍未評估。公開BMC結果也不能補作風扇介入證據。</p></article><article class="card"><span class="tag">下一步</span><h3>先改善模型證據，再判斷控制必要性</h3><p>先定義資料契約、同步時鐘與量測位置，再用有限校準辨識熱容量／散熱／風扇延遲，鎖定後做獨立負載比較；若簡單方法已足夠，就不強求MPC。</p></article></div></section>
<section id="next-week"><h2>下週計畫：參考既有研究，改進自己的方法</h2><p class="lead">下週我會回到自己的方法，先找出需要改善的問題，再觀察PID／LQR／MPC如何處理回授、代價與多步決策，選擇一項適合的機制進行設計與驗證。</p><p>我的方法包含物理主模型、稀疏感測校正、可選的殘差學習，以及候選動作預測與排序。本輪簡化熱模型是遷移到機箱場景的前置研究，四方法比較尚未納入這套完整流程。下週會先整理機箱量測資料需求與熱參數辨識程序，再規劃原有校正與學習流程如何接入；模型參數辨識與控制器選參分開記錄。</p><div class="table-wrap"><table><thead><tr><th>順序</th><th>預計工作</th><th>交付／完成標準</th></tr></thead><tbody>
<tr><td>第1天</td><td>整理自己的方法與具體問題</td><td>方法流程、輸入／輸出、可調參數與現有證據；選定一項需要改善的問題。</td></tr>
<tr><td>第2天</td><td>查讀PID／LQR／MPC的研究做法</td><td>有來源的方法比較表：誤差回授、狀態／動作代價、多步預測與限制；評估適用條件。</td></tr>
<tr><td>第3天</td><td>選擇一項機制，設計改進</td><td>說清楚借用與自行修改的部分；先固定假設、資料切分、調參預算與驗證判準。多步動作排序暫列候選。</td></tr>
<tr><td>第4天</td><td>最小原型與公平比較</td><td>平台具備時比較原版、改進版及移除新增機制的版本；若加入控制baseline，先對齊任務、動作與觀測資訊。</td></tr>
<tr><td>第5天</td><td>分析結果，整理下週報告</td><td>分開報告估測誤差與決策效果，保留退步與成本；未能執行時交代缺少條件。</td></tr>
</tbody></table></div><p class="callout"><strong>預計工作，尚未執行：</strong>下週至少交付自己的方法流程、文獻借鑑與差異表，以及一項改進設計與事前驗證計畫。選參只看calibration，凍結後才看新的保留測試；不重用已開啟的結果或一次性E15作獨立確認。是否改善，要由比較結果判斷。</p><p class="source"><a href="../research/weekly_research_tasks_2026-09-21_zh.md">完整下週工作清單與比較條件</a> · <a href="../thesis/thesis_draft_zh.md">自己的方法與論文主線</a></p></section>
{reading}
<section id="background"><h2>我的前期研究脈絡（累積背景）</h2><p>以下延續兩週前的報告，涵蓋先前估測、公開資料、API尋找、TCLab與BOPTEST探索。這些不是本次新實驗；不因文件曾存在就假設已向教授口頭報告。E15一次性結果只讀取，沒有為本次報告重跑。</p><details><summary>展開前期研究問題、API探索、既有證據與模型架構</summary><p class="callout"><strong>日期說明：</strong>此區內容來自9/21累積報告；當時的「待做」依上方最新工作表更新。本區的估測資料與本次合成機箱控制不可合併成同一驗證層級。</p>{historical}</details></section>
<section id="talk"><h2>我的報告講稿（約15分鐘）</h2><ol class="talk-track">
<li><strong>1分鐘｜我這次要回答的問題：</strong>老師，兩週前您提到MPC，我也另外查了LQR。我這次先在可重設的機箱假設模型中，把固定風扇、PID＋前饋、LQR與MPC放在相同條件下比較。我想知道複雜控制器是否真的值得。</li>
<li><strong>2分鐘｜我的研究脈絡：</strong>我的主線原本是少量感測下估計未量測位置；臥室保留點與公開AAU/BMC各有不同證據範圍。E15的同伺服器時間／負載確認是既有成果，MAE從1.6939到0.9744°C，不是本次新控制證據。當我想驗證風扇動作，就需要可互動動態模型，不能只拿觀測紀錄推論介入。</li>
<li><strong>3分鐘｜我固定的方法：</strong>我先建立CPU、GPU與風扇延遲的簡化熱模型，作為原有數位孿生方法遷移到機箱場景的前置研究。模型參數目前是研究假設，後續需以量測辨識，再接入自己的稀疏校正、設備影響學習與殘差修正；這次還沒有完成整套方法的遷移。我先在此環境固定60°C目標、PWM範圍與變化率，讓LQR分配可達平衡點、MPC用12步QP與溫度softslack，PID使用同一模型的平衡點前饋。每方法三候選、相同三個校準seed，選完凍結再開新測試。</li>
<li><strong>4分鐘｜我實際比較的結果：</strong>新版48回合中，holdout固定風扇MAE為2.9051°C、PID＋前饋1.7713°C、LQR1.7304°C、MPC1.8071°C。MPC比PID＋前饋高2.02%，比LQR高4.43%，而風扇能耗proxy也較高。因此這次不支持MPC比較好。我保留這個結果，因為它回答了是否有必要增加複雜度。</li>
<li><strong>3分鐘｜我查到的問題與修正：</strong>第一階段過載有190次求解回退，但軟限制本來有可行解。我改用QP求解器與數值檢查，新版超載0回退，其他切分仍有7步未通過殘差檢查而回退。獨立核對也從CSV重算全部指標與熱模型步進，能拒絕被改過的結論或軌跡。不過過載仍超溫，因為假設風扇能力不夠；求解成功不能當成安全保證。</li>
<li><strong>2分鐘｜我的下一步與想請教的事：</strong>目前四方法比較是在已知參數、完整狀態的假設模型上執行，屬於機箱遷移的前置研究，還沒有接入自己的稀疏感測方法。下週我會先整理量測與熱參數辨識需求，規劃原有校正與學習流程如何接入，同時參考PID的誤差回授、LQR的代價取捨，以及MPC的多步預測與限制，選一項機制設計改進，再比較原版、改進版與移除新增機制的版本。我會分開評估估測與決策效果；實體介入與E8仍未評估。</li></ol></section>
<section id="questions"><h2>我想請教授討論的三件事</h2><div class="grid"><article class="card third"><h3>控制問題是否需要MPC？</h3><p>當PID＋前饋/LQR已達較低tracking MAE，我是否應優先研究模型失配、突變負載或真正的約束需求，再決定MPC的角色？</p></article><article class="card third"><h3>下一階段先補哪種量測？</h3><p>入口與熱節點溫度、負載功率、PWM/RPM和時鐘同步，哪些是建立小資料辨識與獨立驗證的最低條件？</p></article><article class="card third"><h3>論文怎麼收斂？</h3><p>機箱控制目前只作探索補充；是否先以稀疏估測與虛擬感測為主，等獨立量測支持後再增加實體控制結論？</p></article></div></section>
<section id="sources"><h2>方法來源與可追溯證據</h2><p><a href="https://osqp.org/docs/examples/mpc.html">OSQP：MPC官方範例</a> · <a href="https://osqp.org/docs/interfaces/solver_settings.html">OSQP：求解設定</a> · <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.solve_discrete_are.html">SciPy：DARE</a></p><p><a href="../research/enclosure_control_v2_method_2026-10-05_zh.md">我的方法整理</a> · <a href="{prefix}protocol.md">事前固定protocol</a> · <a href="{prefix}config.json">完整設定</a> · <a href="{prefix}artifacts/freeze.json">來源與選參freeze</a> · <a href="{prefix}artifacts/result.json">全部結果</a> · <a href="{prefix}artifacts/verification.json">獨立驗證</a> · <a href="enclosure_control_v2_2026-10-05_zh.html">四方法詳細報告</a> · <a href="professor_catchup_report_2026-09-21_zh.html">兩週前原報告</a></p><details><summary>核對範圍與證據摘要</summary><pre>{escape(json.dumps(verify,ensure_ascii=False,indent=2))}</pre><p>來源snapshot、候選trial、正式CSV、不支持的判準与過載結果都保留。這項驗證確認數值與記錄的一致性，沒有把假設模型轉成真實物理證據。</p></details></section>
</main><footer>我的研究進度與探索過程｜近期研究整理。單檔可離線閱讀；引用與完整證據連結需原工作區或網路。</footer></body></html>'''
    OUTPUT.write_text('\n'.join(line.rstrip() for line in html.splitlines()) + '\n')
    return OUTPUT


if __name__=='__main__':print(build())
