"""Offline report: cross-plant success must include invalid identification."""
import base64,csv,html,json,os
from run_boptest_cross_plant import ART,ROOT,sha

def main():
    os.environ.setdefault('MPLCONFIGDIR','/tmp/boptest-matplotlib')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    records={n:json.loads((ART/(n+'.json')).read_text()) for n in ['air','hydronic']}
    audit=json.loads((ART/'verification.json').read_text())
    rows='';fitrows=''
    for plant,r in records.items():
        for h,fit in r['fits'].items():
            fitrows+=f'<tr><td>{plant}</td><td>{h}h</td><td>{fit["status"]}</td><td>{fit["coefficients"][0]:.6f}</td><td>{fit["fit_rmse_C"]:.4f}</td></tr>'
        for e in r['evaluations']:
            m=e['metrics'];v=[plant,e['day'],e['budget_h'],e['adaptation_exposure_h'],e['method'],e['q'],f"{m['mae_C']:.4f}",f"{m['max_abs_error_C']:.3f}",f"{m['requested_TV_u']:.3f}"]
            rows+='<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in v)+'</tr>'
        if not r['evaluations']:rows+=f'<tr><td>{plant}</td><td colspan="8">辨識未通過，未進入試調與控制比較；缺失結果不填0。</td></tr>'
    fig,axes=plt.subplots(2,2,figsize=(12,7),constrained_layout=True)
    for i,(name,r) in enumerate(records.items()):
        with (ROOT/r['identification']['trace']).open() as f:data=list(csv.DictReader(f))
        x=[(float(v['time_s'])-86400)/3600 for v in data]
        axes[i,0].plot(x,[float(v['T']) for v in data]);axes[i,0].axhspan(20,30,alpha=.06,color='green')
        axes[i,0].set(title=f'{name}: {r["config"]["measurement_kind"]}',xlabel='Calibration hours',ylabel='Temperature [C]')
        axes[i,1].step(x,[float(v['u']) for v in data],where='post');axes[i,1].set(title=f'{name}: identical normalized excitation rule',xlabel='Calibration hours',ylabel='Normalized supply command [0,1]',ylim=(-.05,1.05))
    plot=ROOT/'docs/reports/boptest_cross_plant_2026-09-08.png';fig.savefig(plot,dpi=140);plt.close(fig)
    image=base64.b64encode(plot.read_bytes()).decode()
    sections=[('先說結果','<p class="lead"><strong>目前尚未達到跨場景少資料適應的目標。</strong>共用算法與設備設定已分離，但水暖系統的2h和6h辨識均被固定檢查拒絕，不能宣稱換設備只要微調即可成功。</p><p>執行流程完成不等於研究假設成立。這輪已完成18組模擬：送風17組、水暖1組校正。水暖原定16組試調／評估因辨識不合格而未執行，沒有用其他算法結果填補。</p>'),
    ('這次怎麼避免情境特例','<p>控制器只接收目標、採樣時間、測得溫度、上一個生效動作，以及固定流程辨識出的參數；不讀設備名称。送風與水暖的FMU訊號、單位、供氣範圍、風扇／泵設定放在獨立JSON，全部在任一新runner模擬之前固定。</p><p>相同正規化u∈[0,1]對應各設備允許供氣溫度：送風12–40°C、水暖20–80°C。風扇0.5與泵1在暖機及控制期間固定，因此交接直接沿用目前輸出，移除舊版空氣側專用比例公式。</p><p>水暖案例量的是室內作用溫度（operative temperature），送風案例量空氣溫度；只在各自設備內比較方法，不把兩者的MAE混成一個總成績。兩者仍屬建築HVAC，並非跨工業領域驗證。</p>'),
    ('輕微調整與少資料的明確預算','<p>兩設備都採同一條6h校正軌跡，分別使用前2h與完整6h。自動辨識l、b、c、d；只允許調整一個公開參數q∈{0.5,1}。每個方法最多2次、每次2h試調，依試調MAE選擇，最後才開第10／40天。</p><p>因此成功的方法是2h辨識＋4h試調＝6h，或6h辨識＋4h試調＝10h的主動適應預算。不是2h內完成全部研究。所有回合另有24h共同暖機，完整24h評估包含暫態。</p><p>基準為使用相同辨識、相同兩次試調的auto-PI；本方法額外使用擾動觀測與平滑。沒有讓基準吃較少資料。觀測率0.2、平滑0.35、回算0.1沿用既有設計，尚未證明為跨設備通用最佳值。</p>'),
    ('辨識結果：預測誤差小，不代表可用來控制','<table><tr><th>設備</th><th>資料</th><th>狀態</th><th>一階損失係數l</th><th>校正一步RMSE °C</th></tr>'+fitrows+'</table><p>原先固定的檢查要求0&lt;l&lt;1、致動增益b&gt;0。水暖擬合得到l&lt;0，對應離散極點1−l&gt;1，因此拒絕計算PI參數。這是辨識模型的問題，不代表真實設備不穩定。</p><p>水暖的一步校正RMSE仍只有約0.025–0.026°C，卻無法通過可用性檢查。可能涉及短激勵、蓄熱／多時間常數與一階模型不足；這輪未證實唯一原因，也未用強制改係數來通過。</p>'),
    ('完整已執行的控制比較','<div class="scroll"><table><tr><th>設備</th><th>日序</th><th>辨識h</th><th>辨識＋試調h</th><th>方法</th><th>q</th><th>MAE °C</th><th>最大誤差 °C</th><th>正規化指令TV</th></tr>'+rows+'</table></div><p>只在事先選定的冬季日期檢查供暖適應；水暖為供暖系統，不宣稱有夏季主動冷卻能力。所有能源分項、域外筆數、飽和與前30min／其後MAE保留在JSON。</p>'),
    ('兩設備的實際辨識軌跡',f'<img alt="Air and hydronic calibration temperatures and normalized excitation" src="data:image/png;base64,{image}"><p>同一正規化激勵規則不保證相同資訊量或實機安全性。原始軌跡與溫度越界都保留，這不是在運轉中精密製程可直接採用的激勵方案。</p>'),
    ('下一步需要解決的問題','<p>下一版應在共用辨識流程中處理延遲／多時間常數，或建立同樣適用各設備的資料不足判斷與擴充預算規則。不能只加一條「水暖專用」分支，也不能把穩定性檢查放寬來換成功數字。</p><p>若使用這輪水暖資料開發新算法，它就成為開發設備；之後仍需另一個未參與開發的設備作外部檢查。目前是跨設備可行性探索的負結果，尚未採納為論文主结論或證明節省人工調參。</p>'),
    ('證據與重現','<p><a href="../../openspec/changes/evaluate-boptest-cross-plant/artifacts/freeze.json">模擬前固定的來源</a> · <a href="../../openspec/changes/evaluate-boptest-cross-plant/artifacts/air.json">送風結果</a> · <a href="../../openspec/changes/evaluate-boptest-cross-plant/artifacts/hydronic.json">水暖結果與拒絕</a> · <a href="../../openspec/changes/evaluate-boptest-cross-plant/evidence.md">研究紀錄</a></p><p>官方BOPTEST v0.9.0模型、本機FMPy0.3.22。沿用上游修訂BSD與依賴授權，FMU及資料雜湊保留。這是自訂runner，未宣稱官方REST/KPI等價。沒有新的神經網路、EUV或濕度驗證。</p>')]
    content=''.join(f'<section id="s{i}"><span>{i:02}</span><h2>{title}</h2>{body}</section>' for i,(title,body) in enumerate(sections,1))
    page=ROOT/'docs/reports/boptest_cross_plant_2026-09-08_zh.html';page.write_text('''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>跨設備少資料適應：首輪結果</title><style>body{font:18px/1.75 system-ui;background:#edf2f7;color:#173047;margin:0}main{max-width:1200px;margin:auto;padding:30px}h1{font-size:36px}h2{font-size:28px}section{padding:35px;background:white;margin:25px 0;border-radius:15px;min-height:55vh}section>span{float:right;color:#778}.lead{font-size:24px}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:10px;border-bottom:1px solid #ccd;text-align:left}th{background:#f1f5fa}.scroll{overflow:auto}img{width:100%}a{color:#08758e}@media print{section{break-before:page;min-height:0}body{background:white}}@media(max-width:600px){main{padding:10px}section{padding:18px}}</style><main><h1>跨場景少資料適應：送風與水暖</h1><p>2026-09-08 · 共用算法／有限調整 · 首輪探索</p>'''+content+'</main></html>')
    page.with_suffix('.json').write_text(json.dumps({'status':'CROSS_PLANT_GOAL_NOT_MET','sections':len(sections),'html_sha256':sha(page),'plot_sha256':sha(plot),'results':{n:sha(ART/(n+'.json')) for n in records}},indent=2)+'\n');print(page)

if __name__=='__main__':main()
