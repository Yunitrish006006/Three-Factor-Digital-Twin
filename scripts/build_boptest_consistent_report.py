"""Offline report for full-model bounded compensation, including exact fallbacks."""
import base64,json,os,re
from pathlib import Path
from run_boptest_consistent import ROOT,ART,sha
from build_boptest_delayed_dynamics_report import table
NAMES={'air':'送風','hydronic':'水暖散熱器','heat_pump':'熱泵地板供暖','apartment':'公寓日間區','commercial':'商用散熱器'}

def main():
    os.environ.setdefault('MPLCONFIGDIR','/tmp/boptest-matplotlib')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    records={n:json.loads((ART/(n+'.json')).read_text()) for n in NAMES};audit=json.loads((ART/'verification.json').read_text());assert audit['status']=='PASS'
    tests=(ROOT/'outputs/boptest_consistent_tests.log').read_text();test=re.search(r'Ran (\d+) tests in ([\d.]+)s\s+OK',tests);assert test
    rows=[];gates=[];counts={'BETTER':0,'WORSE':0,'TIE':0};episodes=[];fallbacks=0
    fig,axes=plt.subplots(5,2,figsize=(12,14),constrained_layout=True)
    for pi,(name,r) in enumerate(records.items()):
        episodes+=r['evaluations']
        for hi,h in enumerate([2,6]):
            d=next(d for d in audit['plants'][name]['decisions'] if d['budget_h']==h);ax=axes[pi,hi]
            valid=r['banks'][str(h)]['status']=='FITTED'
            gates.append([NAMES[name],h,'通過' if d['gate'] else '未通過' if valid else '辨識拒絕',sum(x['correction_nonzero_rows']>0 for x in d['pairs'])])
            ax.set(title=f'{name} | ID {h}h',ylabel='24h MAE [C]',xticks=[0,1],xticklabels=['day 25','day 60'])
            if not valid:ax.text(.5,.5,'Identification rejected',ha='center',transform=ax.transAxes);continue
            values=[[],[]]
            for day in [25,60]:
                es={e['method']:e for e in r['evaluations'] if e['day']==day and e['budget_h']==h};a,b=es['auto_pi']['metrics'],es['consistent']['metrics']
                outcome='BETTER' if b['mae_C']<a['mae_C'] else 'WORSE' if b['mae_C']>a['mae_C'] else 'TIE';counts[outcome]+=1
                diag=next(x for x in d['pairs'] if x['day']==day);off=diag['correction_nonzero_rows']==0;fallbacks+=off
                values[0].append(a['mae_C']);values[1].append(b['mae_C'])
                rows.append([NAMES[name],h,day,f"{a['mae_C']:.5f}",f"{b['mae_C']:.5f}",f"{a['max_abs_error_C']:.3f} / {b['max_abs_error_C']:.3f}",f"{a['requested_TV_u']:.2f} / {b['requested_TV_u']:.2f}",'停用／同基準' if off else {'BETTER':'改善','WORSE':'退步','TIE':'持平'}[outcome]])
            ax.bar([-.18,.82],values[0],.36,label='auto-PI');ax.bar([.18,1.18],values[1],.36,label='consistent');ax.legend(fontsize=8)
    page=ROOT/'docs/reports/boptest_consistent_2026-09-08_zh.html';plot=page.with_suffix('.png');fig.savefig(plot,dpi=130);plt.close(fig)
    runtime=sum(e['wall_seconds'] for e in episodes)
    sections=[('有改善，也有明確失敗',f'<p class="lead">18 組有效比較：{counts["BETTER"]} 組 MAE 改善、{counts["WORSE"]} 組退步、{counts["TIE"]} 組持平。9 組可辨識設備／資料預算中，{audit["passed_budgets"]} 組通過完整門檻。</p><p>公寓 6h 仍無可用辨識模型。整体跨設備改善假設仍未支持；不能把停用補償後與 auto-PI 持平算成方法勝出。</p>'),
    ('這次改了什麼','<p>舊版只從溫度變化扣除致動影響；新版以完整 ARX 的溫度歷史、實際延遲指令、上一時刻室外溫度與截距預測，再用觀測誤差估算補償。二階模型的正常蓄熱動態不再被公式直接省略。</p><p>使用固定 10 分鐘反應尺度與誤差尺度做正則化；補償最多 ±0.1 正規化指令，每分鐘最多變動 0.01。可信度低時停用補償。這些是跨設備共用的工程規則，不是校準過的機率，也沒有構成閉迴路穩定性保證。</p><p>文獻背景：<a href="https://arxiv.org/abs/1902.09032">擾動觀測器綜述</a>、<a href="https://arxiv.org/abs/1912.06331">設計限制</a>、<a href="https://arxiv.org/abs/2101.02859">基準控制與名義模型的角色</a>。目前核對摘要，不宣稱重現原文公式或提出全新控制理論。</p>'),
    ('固定規則如何避免情境特例','<p>五種已看過的設備均列為開發設備；沿用原模型與安装設定，不修補公寓拒絕。控制器不讀設備名稱，所有補償常數在模擬前固定。新開第 25／60 天只算設備內檢查，不是獨立設備確認。</p><p>兩方法都固定 q=0.5、使用相同 2h／6h 校正前綴、無額外試調。基準的每一步輸出另外與原始 auto-PI 公式比對。不能將此結果與前輪選過 q 的其他日期當成同條件前後差值。</p>'),
    ('完整門檻與停用情況',table(['設備','辨識h','整體門檻','兩天中補償啟用天數'],gates)+f'<p>{fallbacks} 次補償回合完全停用，按相同 PI 控制。固定 10 分鐘視窗對辨識延遲至少 10 分鐘的模型沒有可用的短期輸入反應；這是方法限制，不是公寓專用分支。</p><p>每日期 MAE≤基準＋0.02°C、最大誤差≤基準＋0.2°C、指令TV≤1.25×基準＋0.1，且兩天平均 MAE 確實改善才通過。停用持平不通過改善門檻。</p>'),
    ('逐日結果',table(['設備','辨識h','日序','auto-PI MAE °C','新版 MAE °C','最大誤差 基準／新版 °C','TV 基準／新版','判讀'],rows)+'<p>作用溫度與空氣溫度只在各設備內比較，不混成總 MAE。所有 24h 評估均包含交接暫態；完整能耗、飽和與域外資料保留在 JSON。</p>'),
    ('全部設備比較圖','<img alt="All five development plants, two budgets and two dates including rejection" src="data:image/png;base64,'+base64.b64encode(plot.read_bytes()).decode()+'">'),
    ('資料與時間成本',f'<p>完成 {len(episodes)} 次模擬；無新增校正、辨識搜尋或試調。每方法名義校正需求仍為 2h／6h。所有回合另有 24h 暖機，總計 {len(episodes)*48} 模擬小時（暖機與評估各半）。回合執行耗時加總 {runtime:.1f}s，並行執行時不能當成整體牆鐘時間。</p><p>這輪尚未做人工整定、同品質所需最少資料量、或實機暖機成本對照，所以未證明總調整成本比較低。縮短試調流程不能代替控溫品質門檻。</p>'),
    ('結論與下一個問題','<p>全模型補償與限幅能在部分設備改善，弱反應設備則可退回基準；但水暖 2h 仍明顯退步。原始的一階模型不完整可能只是原因之一，並非已由這輪實驗單獨證明。</p><p>下一步需要檢查模型可識別性、短期誤差是否能代表長期閉迴路品質，以及共用的補償效益判斷。不能看到個別設備結果後手動關閉補償來宣稱通用。五種設備已全部參與開發，後續確認還需要未見條件或設備。</p><p>這是未採納的控制研究延伸，沒有新增神經網路、濕度、EUV、實機或線材良率證據。官方 BOPTEST v0.9.0 FMU 經自訂 FMPy runner 執行，未宣稱 REST/KPI 等價。</p>'),
    ('驗證與 3D 研究圖',f'<p>{test[1]} 項測試通過（{test[2]} 秒）。完整來源、軌跡、模型沿用、每步指令及補償診斷均經重播核對。</p><p><a href="../../openspec/changes/model-consistent-compensation/evidence.md">研究紀錄</a> · <a href="../../openspec/changes/model-consistent-compensation/artifacts/verification.json">全部驗證與門檻</a> · <a href="../../docs/research/boptest_graph_sources.json">3D 圖來源註冊</a></p><p>ResearchWorkspace 保持論文為第一層：主論文 → 未採納控溫研究 → 輪次／設備 → 演算法、資料模型、辨識、逐日結果。引用、比較、論證均保留端點定位；外部論文摘要與本地基準實驗不混為同一種比較。</p>')]
    body=''.join(f'<section><small>{i:02}</small><h2>{title}</h2>{text}</section>' for i,(title,text) in enumerate(sections,1))
    page.write_text('''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>完整模型與有限補償控溫</title><style>body{font:18px/1.8 system-ui;background:#eef3f7;color:#17374b;margin:0}main{max-width:1280px;margin:auto;padding:28px}section{background:white;padding:30px;margin:25px 0;border-radius:14px}h1{font-size:36px}h2{font-size:27px}.lead{font-size:24px}small{float:right;color:#678}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:9px;border-bottom:1px solid #ccd;text-align:left}th{background:#eef5f7}.scroll{overflow:auto}img{width:100%}a{color:#00728a}@media print{section{break-before:page}body{background:white}}@media(max-width:600px){main{padding:10px}section{padding:15px}}</style><main><h1>控溫研究：完整模型與有限補償</h1><p>2026-09-08 · 五設備開發／固定規則 · 未採納主論文確認成果</p>'''+body+'</main></html>')
    page.with_suffix('.json').write_text(json.dumps(dict(status=audit['hypothesis'],counts=counts,fallback_episodes=fallbacks,passed_budgets=audit['passed_budgets'],completed_episodes=len(episodes),simulated_hours=len(episodes)*48,aggregate_episode_wall_seconds=runtime,tests=int(test[1]),html_sha256=sha(page),plot_sha256=sha(plot),builder_sha256=sha(Path(__file__)),results={n:sha(ART/(n+'.json')) for n in NAMES}),indent=2)+'\n');print(page)
if __name__=='__main__':main()
