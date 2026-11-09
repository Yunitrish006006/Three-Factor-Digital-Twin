#!/usr/bin/env python3
"""Generate the result-derived offline five-method professor comparison."""
import argparse,base64,csv,hashlib,json,shutil,sys,zipfile
from html import escape
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from enclosure_unified_summary import data,paragraphs,LABELS,ART
OUT=ROOT/'docs/reports/unified_enclosure_2026-10-26'
DEL=Path('/Users/yunitrish/Documents/ChatGPT/論文/同環境五方法比較_2026-10-26/delivery')
COLORS={'fixed':'#7c8793','pi':'#2878b5','pid':'#55a868','lqr':'#dd8452','mpc':'#8865a9'}
SPLITS=['validation','holdout','plant_holdout','overload']
def load(n):return json.loads((ART/n).read_text())
def table(headers,rows):return '<div class="table-wrap" tabindex="0"><table><thead><tr>'+''.join('<th>'+escape(str(h))+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+escape(str(x))+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def rows_for(split):
 a=data()['aggregates'][split]
 return [[LABELS[m]]+[f'{a[m][k]:.4f}' for k in ['tracking_mae_C','tracking_rmse_C','fan_energy_proxy_Wh']]+[f"{a[m]['overtemp_s']:.1f}",sum(r['metrics']['fallback_n'] for r in data()['runs'] if r['split']==split and r['method']==m)] for m in LABELS]
HEADERS=['方法','追蹤 MAE °C','RMSE °C','能耗代理 Wh/回合','超溫秒/回合','回退步數合計']

def figures():
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 import numpy as np
 d=data();(OUT/'figures').mkdir(parents=True,exist_ok=True)
 plt.rcParams.update({'font.size':10,'svg.fonttype':'path','axes.spines.top':False,'axes.spines.right':False})
 def save(fig,name):
  for ext in ['svg','png']:fig.savefig(OUT/'figures'/f'{name}.{ext}',dpi=150,bbox_inches='tight')
  plt.close(fig)
 fig,axs=plt.subplots(2,2,figsize=(11,8),layout='constrained')
 for ax,split in zip(axs.flat,SPLITS):
  vals=[d['aggregates'][split][m]['tracking_mae_C'] for m in LABELS]
  bars=ax.bar(list(LABELS),vals,color=[COLORS[m] for m in LABELS]);ax.set_title(f'{split}: 3 paired episodes/method');ax.set_ylabel('Tracking MAE (deg C)');ax.set_ylim(0,max(vals)*1.2);ax.bar_label(bars,fmt='%.4f',padding=3,fontsize=8)
 fig.suptitle('Five methods in the same assumed CPU/GPU environment');save(fig,'tracking_by_split')
 fig,axs=plt.subplots(2,2,figsize=(11,8),layout='constrained')
 for ax,split in zip(axs.flat,SPLITS):
  label_offsets={
   'validation':{'pi':(-24,8),'pid':(5,8),'lqr':(-24,8),'mpc':(5,8)},
   'holdout':{'pi':(-24,8),'pid':(5,8),'lqr':(-24,-13),'mpc':(5,7)},
   'plant_holdout':{'pi':(-24,10),'pid':(5,10),'lqr':(-27,15),'mpc':(6,2)},
   'overload':{'pi':(-24,8),'pid':(5,8),'mpc':(5,-13)},
  }
  for m in LABELS:
   v=d['aggregates'][split][m];ax.scatter(v['fan_energy_proxy_Wh'],v['tracking_mae_C'],c=COLORS[m],s=55);ax.annotate(m,(v['fan_energy_proxy_Wh'],v['tracking_mae_C']),xytext=label_offsets[split].get(m,(4,5)),textcoords='offset points',fontsize=9)
  ax.set_title(split);ax.set_xlabel('Fan energy proxy (Wh/episode)');ax.set_ylabel('Tracking MAE (deg C)');ax.margins(.2)
 fig.suptitle('Trade-off within each split; energy is assumed 10 x PWM^3 W');save(fig,'energy_tradeoff')
 for seed in load('freeze.json')['config']['seeds']['holdout']:
  fig,axs=plt.subplots(4,1,figsize=(10,9),sharex=True,layout='constrained')
  for m in LABELS:
   run=next(r for r in d['runs'] if r['split']=='holdout' and r['seed']==seed and r['method']==m)
   with (ART/run['trace_path']).open() as f:rs=list(csv.DictReader(f))
   v=lambda k:np.array([float(r[k]) for r in rs]);t=v('time_s')
   axs[0].plot(t+10,v('next_cpu_C'),color=COLORS[m],label=m);axs[1].plot(t+10,v('next_gpu_C'),color=COLORS[m]);axs[2].step(t,v('pwm'),where='post',color=COLORS[m])
  axs[0].axhline(60,color='black',ls=':',lw=1);axs[1].axhline(60,color='black',ls=':',lw=1)
  axs[0].set_ylabel('CPU (deg C)');axs[1].set_ylabel('GPU (deg C)');axs[2].set_ylabel('Applied PWM');axs[2].set_ylim(.15,1.05);axs[0].legend(ncol=5,fontsize=9)
  axs[3].step(t,v('cpu_W'),where='post',label='CPU power');axs[3].step(t,v('gpu_W'),where='post',label='GPU power');axs[3].set_ylabel('Load (W)');axs[3].set_xlabel('Simulated time (s)');axs[3].legend(fontsize=9,ncol=2)
  fig.suptitle(f'All five methods, identical holdout inputs, seed {seed}\nTemperature at t+10 s; command/load at interval start t');save(fig,f'holdout_seed_{seed}')

CAUSES=[
['名義模型 LQR 的平均 MAE 最低','LQR 在此批以目前名義參數計算可達穩態與局部回授，PI/PID 使用固定偏置且無模型前饋。這些結構差異可以描述，但尚未單獨識別各因素的因果貢獻。','增加共同前饋的 PI/PID 消融，保留原 plain PI/PID 結果；用新的保留資料比較。'],
['PI 與 PID 的差距很小','目前平滑且慢變的熱模型中，這組低通微分與三候選預算未形成較大額外效益；不能外推微分項永遠無效。','事前固定更快速負載與量測雜訊強度，配對比較微分項及濾波參數，統一候選預算。'],
['指定參數失配組改由 MPC 取得最低平均 MAE','各方法使用同一個名義模型；該組的真實容量、熱導、風扇效應與延遲改變。這只是三組指定同族壓力測試的彙總。','分別介入單一物理參數，再以新組合檢查；避免把混合失配排名當成普遍穩健性證明。'],
['過載下五方法均超溫','440/580W 負載及名義最大風扇的穩態熱平衡高於目標與限制；控制器無法額外產生散熱能力。MPC 一步殘差超過 gate 而回退。','先檢查散熱能力及可行目標，另行評估降載／提高散熱能力；求解殘差與超溫分開記錄。'],
['不同方法的能耗與控溫取捨不同','固定 PWM holdout 的代理能耗最低，但 MAE 最大；LQR/MPC較低 MAE 伴隨更高代理值。Wh 來自假設10×PWM³，不是量測。','先指定可接受代價範圍或等能耗比較，再以風扇電壓／電流校準代理公式。']]

def build():
 OUT.mkdir(parents=True,exist_ok=True);d=data();freeze=load('freeze.json');c=freeze['config'];v=load('verification.json');ps=paragraphs()
 fig=lambda name,caption:'<figure><img alt="'+escape(caption)+'" src="data:image/svg+xml;base64,'+base64.b64encode((OUT/'figures'/f'{name}.svg').read_bytes()).decode()+'"><figcaption>'+escape(caption)+'</figcaption></figure>'
 b='<section><h2>我完成的共同環境比較</h2>'+''.join('<p>'+escape(p)+'</p>' for p in ps[:3])+table(HEADERS,rows_for('holdout'))+'<p>本表每方法為相同三個 holdout seeds、每回合1200秒；各回合與節點等權。回退列為三回合總步數，其他指標為每回合平均。排序只針對追蹤 MAE，未將代價合併成單一勝負。</p></section>'
 b+='<section><h2>完整實驗環境與公平性條件</h2>'+table(['項目','本批實際設定與性質'],[
 ['Plant','假設 CPU/GPU 熱節點與單一風扇狀態；未使用實體機箱尺寸、CFD、感測器或實測熱導。'],['方程','Cᵢ dTᵢ/dt=Pᵢ−(Gᵢ+kᵢ f)(Tᵢ−Tin)；df/dt=(PWM−f)/τ。'],['熱參數',str(c['parameters'])+'；容量J/K、G/k W/K、τ秒、RPM為模型設定。'],['目標與限制',str(c['settings'])+'；MPC horizon=12步=120秒。'],['時間與初始狀態','每10秒控制，120步=1200秒；plant熱積分1秒Euler、fan精確更新；Tcpu=58+seed%3、Tgpu=59+seed%3°C，fan/PWM=.5。'],['量測資訊','所有方法收到相同完整當下溫度與fan狀態、入口、功率；無量測雜訊、無未來負載、無獨立估測器。'],['負載時序','i*段數//120決定負載段；每步CPU±5W、GPU±8W均勻擾動。完整各split序列如下。'],['入口溫度','29+(seed%3−1)+1.5·I(step≥40)+.5·I(step≥80)+Uniform[−.2,.2]°C。'],['plain PI/PID',str(c['feedback'])+'；PI kd=0；PID derivative alpha=.25；anti-windup=.2。'],['LQR','名義模型 gain-scheduled local ZOH/DARE；Q=diag(.04,.04,0)；候選 R=.1/1/10。限制後不宣稱全域穩定性或最優。'],['MPC','名義 affine ZOH；OSQP1.0.4；Qthermal=1/25，Δu權重5，slack=10000；eps_abs/rel=1e−7，max_iter=100000，rho=1；只接受solved及primal/dual residual≤1e−5。'],['校準與選參','每方法3候選×3seed，共45回合；score=mean(error²/25)+.01mean(PWM³)+10000mean(positive_limit_violation²)；索引tie-break；正式評估前凍結。'],['公平性限制','候選回合數與可用資訊相同；模型式方法與plain回授內部利用資訊不同，候選品質及CPU計算量不等。這是明定實作的比較，非方法族群全域最優排名。'],['能耗與超溫','10×PWM³ W按10秒積分成Wh；超溫=10秒末端任何節點超80/85°C步數×10；非精確連續超溫積分或實測功率。'],['版本',str(freeze['environment'])+'；來源HEAD='+freeze['git_head']+'；研究來源在工作樹內凍結（dirty='+str(freeze['git_dirty'])+'），完整雜湊隨附。']])+table(['分組','seeds','CPU負載段 W','GPU負載段 W'],[[s,str(c['seeds'][s]),str(c['schedules'][s][0]),str(c['schedules'][s][1])] for s in c['seeds']])+table(['失配seed','C倍率','G倍率','fan gain倍率','τ秒'],[[seed,str(vr['capacity_factors']),str(vr['conductance_factors']),str(vr['fan_gain_factors']),vr['fan_tau_s']] for seed,vr in zip(c['seeds']['plant_holdout'],c['variants'])])+table(['方法','候選集合','凍結選定參數'],[[LABELS[m],str(c['candidates'][m]),str(freeze['selected'][m])] for m in LABELS])+'</section>'
 b+='<section><h2>四種情境的完整比較</h2>'+fig('tracking_by_split','四個分組分別評比；各方法各有三回合，不跨組合併排名。')+fig('energy_tradeoff','每個split內MAE與能耗代理值比較；圖上相近點可能重疊，精確值見表。')
 for split in SPLITS:b+='<h3>'+split+'</h3>'+table(HEADERS,rows_for(split))+'<p>MAE次序：'+escape(' → '.join(d['mae_rankings'][split]))+'。三指標Pareto集合（MAE、能耗代理、超溫皆最小）：'+escape(', '.join(d['pareto'][split]))+'。Pareto判定使用未四捨五入值，不代表統計或實務差異顯著。</p>'
 b+='<p>'+escape(ps[3])+'</p></section><section><h2>各seed的完整追蹤與命令</h2>'
 for seed in c['seeds']['holdout']:b+=fig(f'holdout_seed_{seed}',f'holdout seed {seed}；全部五種方法，同一組入口與CPU/GPU負載；未挑選有利案例。')
 b+='<details><summary>60 個正式回合完整指標</summary>'+table(['split','seed','方法','MAE°C','CPU MAE','GPU MAE','能耗代理Wh','超溫秒','回退步數'],[[r['split'],r['seed'],LABELS[r['method']]]+[f"{r['metrics'][k]:.5f}" for k in ['tracking_mae_C','cpu_mae_C','gpu_mae_C','fan_energy_proxy_Wh','overtemp_s','fallback_n']] for r in d['runs']])+'</details></section>'
 b+='<section><h2>結果解釋及改善驗證方案</h2>'+table(['觀察結果','現有證據與可能解釋','後續方案（尚未執行）'],CAUSES)+'<p>名義最大風扇在過載時的穩態公式為 Tin+P/(G+k)。CPU約為 Tin+58.67°C、GPU約為 Tin+58°C，依本批入口範圍可見其高於目標且多數高於限制。這是模型熱平衡計算，不能取代動態實驗或硬體量測。</p><p>下一步應先凍結新測試組、校準預算、主要MAE指標及代價上限，逐一介入前饋、權重、限制或模型參數。實體機箱、NTC、風扇實測電功率及硬體安全均為 NOT_EVALUATED。</p></section><section><h2>核對及資料來源</h2><p>'+escape(ps[4])+'</p><pre>'+escape(json.dumps(v,ensure_ascii=False,indent=2))+'</pre><details><summary>完整可重現設定 JSON</summary><pre>'+escape(json.dumps(freeze,ensure_ascii=False,indent=2))+'</pre></details><p>隨附 result.json、config.json、freeze、verification、protocol、完整105個校準及正式CSV、來源快照與SHA-256。時間欄為模擬秒。當方法求解失敗時保留共同受限回退，該步仍納入指標。</p></section>'
 css='''*{box-sizing:border-box}body{margin:0;background:#edf2f5;color:#20323d;font:16px/1.75 system-ui,-apple-system,"PingFang TC",sans-serif}header{padding:34px max(20px,calc((100vw - 1100px)/2));background:#183e4d;color:white}h1{font-size:clamp(25px,4vw,38px);line-height:1.3}main{max-width:1140px;margin:auto;padding:18px}section{padding:24px;margin:20px 0;background:white;border:1px solid #d3e0e6;border-radius:12px}h2{color:#18586e}table{width:100%;border-collapse:collapse;font-size:14px;min-width:650px}th,td{padding:9px;border:1px solid #d4e0e6;text-align:left;vertical-align:top}th{background:#edf4f7}.table-wrap{overflow-x:auto;width:100%;margin:18px 0}figure{margin:18px 0}img{max-width:100%;height:auto}figcaption{font-size:14px;color:#4b6372}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px}summary{cursor:pointer;color:#18586e;font-weight:600}details{border:1px solid #d4e0e6;padding:12px;margin:15px 0}@media(max-width:600px){main{padding:8px}section{padding:14px}}@media print{body{background:white;font-size:10pt}header{background:white;color:black;padding:0}main{padding:0;max-width:none}section{border:0;padding:0;break-before:page}section:first-child{break-before:auto}figure{break-inside:avoid}.table-wrap{overflow:visible}table{min-width:0;font-size:8pt}td,th{padding:4px}details>*{display:block!important}summary{display:none}pre{font-size:8pt}}'''
 doc='<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>同環境五種機箱控制方法比較</title><style>'+css+'</style><header><p>教授審閱用｜2026-10-26｜指定假設熱模型模擬</p><h1>同環境五種機箱控制方法比較</h1><p>固定PWM、PI、PID、LQR、MPC；共同控制條件與有限調參預算。</p></header><main>'+b+'</main></html>'
 (OUT/'report_zh.html').write_text(doc)
 # The markdown file is deliberately a clearly labelled executive summary;
 # the offline HTML is the complete professor report with all settings/runs.
 d=data();md=['# 同環境五種機箱控制方法比較｜執行摘要',
 '完整教授報告為同資料夾 `report_zh.html`：包含完整環境與候選設定、四組結果、60個正式回合、三組holdout圖及可重現證據。此Markdown僅供快速閱讀，不取代HTML。',
 '## 研究範圍',ps[0],ps[1],
 '## 保留測試組（3個配對seed平均）',
 '| 方法 | MAE (°C) | RMSE (°C) | 能耗代理 (Wh/回合) | 超溫 (秒/回合) |',
 '|---|---:|---:|---:|---:|']
 for m in LABELS:
  v=d['aggregates']['holdout'][m];md.append(f"| {LABELS[m]} | {v['tracking_mae_C']:.4f} | {v['tracking_rmse_C']:.4f} | {v['fan_energy_proxy_Wh']:.4f} | {v['overtemp_s']:.1f} |")
 md += ['','## 四分組 MAE (°C)','| 分組 | 固定PWM | PI | PID | LQR | MPC |','|---|---:|---:|---:|---:|---:|']
 for split in SPLITS:
  md.append('| '+split+' | '+' | '.join(f"{d['aggregates'][split][m]['tracking_mae_C']:.4f}" for m in LABELS)+' |')
 md += ['',ps[2],ps[3],ps[4],
 '## 重要限制','本研究為完全狀態可見的假設雙節點熱模型模擬；不是實體電腦機箱、感測器、風扇功耗或安全驗證。PI/PID未加前饋；LQR/MPC使用名義模型。每方法候選數相同不代表搜尋品質或計算成本相同。']
 (OUT/'report_zh.md').write_text('\n\n'.join(md)+'\n')
 flat=[]
 cal=load('calibration.json')
 for m,choices in cal['candidates'].items():
  for candidate in choices:flat+=candidate['runs']
 flat+=d['runs']
 with (OUT/'runs.csv').open('w',newline='',encoding='utf-8-sig') as f:
  keys=['id','split','method','seed','candidate_index','n','trace_path','trace_sha256','parameters']+list(d['runs'][0]['metrics']);w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
  for r in flat:w.writerow({**{k:json.dumps(r[k]) if k=='parameters' else r[k] for k in keys if k in r},**r['metrics']})
 (OUT/'message_to_professor_zh.md').write_text('老師您好，我新增了同一個假設CPU/GPU熱模型下的固定PWM、PI、PID、LQR及MPC比較。五方法共用每回合初始條件、負載、完整當下狀態與風扇限制，各用相同候選回合預算校準後凍結，完成60正式回合。\n\n'+'\n\n'.join(ps[2:4])+'\n\n隨附完整設定、逐回合數據與原因分析。以上為模擬結果，尚未完成實體機箱與實測功耗驗證。\n')
 print('Built',OUT/'report_zh.html')

def pdf():
 from reportlab.pdfbase import pdfmetrics
 from reportlab.pdfbase.ttfonts import TTFont
 from reportlab.lib.styles import ParagraphStyle
 from reportlab.lib import colors
 from reportlab.lib.pagesizes import A4
 from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak
 font=Path('/System/Library/AssetsV2/PreinstalledAssetsV2/InstallWithOs/com_apple_MobileAsset_Font7/66746e61b4dbfa104b24e08fd5cdadcea3816e57.asset/AssetData/BiauKai.ttf')
 pdfmetrics.registerFont(TTFont('CJK',str(font)));normal=ParagraphStyle('body',fontName='CJK',fontSize=10,leading=15,wordWrap='CJK',spaceAfter=9)
 heading=ParagraphStyle('head',parent=normal,fontSize=15,leading=20,spaceAfter=14)
 small=ParagraphStyle('small',parent=normal,fontSize=8,leading=11)
 ps=paragraphs();c=load('freeze.json')['config'];story=[]
 P=lambda text,style=normal:Paragraph(escape(text),style)
 def T(headers,rows,widths):
  vals=[[P(str(x),small) for x in row] for row in [headers]+rows];t=Table(vals,colWidths=widths,repeatRows=1);t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#b6c8d1')),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e9f0f4')),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]));return t
 story+=[P('同環境五種機箱控制方法比較',heading),P('教授審閱用　2026年10月26日　假設熱模型模擬'),P(ps[0]),P(ps[2]),T(HEADERS,rows_for('holdout'),[65,75,65,85,85,65]),P('同組三回合等權平均；回退為步數合計。風扇能耗為10×PWM³W假設公式，非實測節電。'),PageBreak()]
 story+=[P('共同環境與凍結設定',heading),P(ps[1]),P('入口溫度：29 + (seed mod 3 - 1) + 1.5°C when step is at least 40 + 0.5°C when step is at least 80 + uniform random value from -0.2 to 0.2°C. 每步CPU/GPU負載均勻擾動範圍分別為±5/±8 W。'),T(['分組','Seeds','CPU功率段W','GPU功率段W'],[[s,str(c['seeds'][s]),str(c['schedules'][s][0]),str(c['schedules'][s][1])] for s in c['seeds']],[75,110,130,125]),P('每段長度由120步均分。校準、validation為4段各300秒；holdout/失配為5段各240秒；overload單段1200秒。'),T(['方法','凍結選定參數'],[[LABELS[m],str(load('freeze.json')['selected'][m])] for m in LABELS],[80,360]),P('同一候選回合數不代表全域最佳或相同運算時間。LQR/MPC使用名義模型；plain PI/PID未採模型前饋。'),PageBreak()]
 story+=[P('全部分組結果',heading)]
 for s in SPLITS:story+=[P(s),T(HEADERS,rows_for(s),[65,75,65,85,85,65]),Spacer(1,8)]
 # Keep the interpretation paragraph with the following analysis section;
 # otherwise ReportLab stranded its final two lines on an almost empty page.
 story+=[PageBreak(),P('原因解釋與後續驗證',heading),P(ps[3])]
 for obs,ex,action in CAUSES:story+=[P(obs),P(ex),P('後續：'+action)]
 story+=[P('上述改善方案尚未執行，需在新資料前固定規則。'),P(ps[4]),PageBreak()]
 for ix,seed in enumerate(c['seeds']['holdout']):
  story+=[P(f'共同holdout輸入與追蹤　seed {seed}',heading),Image(str(OUT/'figures'/f'holdout_seed_{seed}.png'),width=470,height=440),P('溫度在區間末端t+10秒，命令及負載標於區間起點t。所有五方法使用同一個功率／入口序列；圖中保留全部holdout seeds。')]
  if ix<len(c['seeds']['holdout'])-1:story.append(PageBreak())
 def footer(canvas,doc):canvas.setFont('CJK',9);canvas.drawString(40,25,'假設模型模擬　實體機箱與功耗未評估');canvas.drawRightString(A4[0]-40,25,str(doc.page))
 SimpleDocTemplate(str(OUT/'report_zh.pdf'),pagesize=A4,leftMargin=35,rightMargin=35,topMargin=35,bottomMargin=42,title='同環境五種機箱控制方法比較').build(story,onFirstPage=footer,onLaterPages=footer)
 print('Built',OUT/'report_zh.pdf')

def package():
 DEL.mkdir(parents=True,exist_ok=True)
 for n in ['report_zh.html','report_zh.md','report_zh.pdf','runs.csv','message_to_professor_zh.md']:
  if (OUT/n).exists():shutil.copy2(OUT/n,DEL/n)
 if (OUT/'figures').exists():shutil.copytree(OUT/'figures',DEL/'figures',dirs_exist_ok=True)
 qa=ART/'reporting'/'professor_qa.md'
 if qa.exists():shutil.copy2(qa,DEL/'QA_RECORD.md')
 dest=DEL/'evidence';dest.mkdir(exist_ok=True)
 for name in ['result.json','freeze.json','calibration.json','verification.json','preregistration.json','historical_hashes.json','calibrate_attempt.json','evaluate_attempt.json']:
  shutil.copy2(ART/name,dest/name)
 shutil.copy2(ART.parent/'protocol.md',dest/'protocol.md');shutil.copy2(ART.parent/'config.json',dest/'config.json')
 shutil.copy2(ART.parent/'evidence.md',dest/'evidence.md')
 shutil.copytree(ART/'traces',dest/'traces',dirs_exist_ok=True);shutil.copytree(ART/'source_snapshots',dest/'source_snapshots',dirs_exist_ok=True)
 hashes={str(p.relative_to(DEL)):hashlib.sha256(p.read_bytes()).hexdigest() for p in DEL.rglob('*') if p.is_file() and p.name!='sha256.json'};(DEL/'sha256.json').write_text(json.dumps(hashes,ensure_ascii=False,indent=2)+'\n')
 zpath=DEL.parent.parent/(DEL.parent.name+'.zip')
 with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(DEL.rglob('*')):
   if p.is_file():z.write(p,p.relative_to(DEL.parent))
 with zipfile.ZipFile(zpath) as z:
  if z.testzip():raise ValueError('Bad ZIP')
 print('Delivery',DEL,'ZIP',zpath)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--figures',action='store_true');p.add_argument('--pdf',action='store_true');p.add_argument('--package',action='store_true');args=p.parse_args()
 if args.figures:figures();build()
 if args.pdf:pdf()
 if args.package:package()
