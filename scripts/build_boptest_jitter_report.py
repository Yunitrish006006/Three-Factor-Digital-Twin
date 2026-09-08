"""Offline report of smoothing and delayed-actuator validation."""
import base64,csv,json,os,html
from run_boptest_jitter import ART,ROOT,sha

def main():
    os.environ.setdefault('MPLCONFIGDIR','/tmp/boptest-matplotlib')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    d=json.loads((ART/'development.json').read_text());t=json.loads((ART/'transfer.json').read_text());v=json.loads((ART/'verification.json').read_text())
    assert v['transfer_sha256']==sha(ART/'transfer.json')
    names={'v4':'v4 原觀測器','aware1':'實際致動回授','smooth06':'回授＋α=0.6 平滑','smooth035':'回授＋α=0.35 平滑','grid':'搜尋 PI＋交接'}
    selected=v['selected']
    def table(records):
        text='<div class="scroll"><table><tr><th>日序</th><th>雜訊σ</th><th>延遲步</th><th>方法</th><th>MAE °C</th><th>最大誤差 °C</th><th>±0.5°C內</th><th>送出指令總變動 °C</th><th>生效指令總變動 °C</th></tr>'
        for r in records:
            m=r['metrics'];values=[r['day'],r['noise_sd_C'],r['delay_steps'],names[r['controller']],f"{m['mae_C']:.4f}",f"{m['max_abs_error_C']:.3f}",f"{m['within_0_5_C_pct']:.1f}%",f"{m['command_total_variation_C']:.1f}",f"{r['applied_total_variation_C']:.1f}"]
            text+='<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in values)+'</tr>'
        return text+'</table></div>'
    summary={}
    for noise in (0,.05):
        summary[str(noise)]={}
        for name in t['controllers']:
            records=[r for r in t['records'] if r['noise_sd_C']==noise and r['controller']==name]
            summary[str(noise)][name]={k:sum(r['metrics'][k] for r in records)/len(records) for k in ['mae_C','command_total_variation_C']}
    noisy=[r for r in t['records'] if r['noise_sd_C']>0]
    days=sorted(set(r['day'] for r in noisy));fig,axes=plt.subplots(2,3,figsize=(15,7),constrained_layout=True)
    for i,day in enumerate(days):
        for r in noisy:
            if r['day']!=day:continue
            with (ROOT/r['trace']).open() as f:rows=list(csv.DictReader(f))
            x=[(float(a['time_s'])-day*86400+60)/3600 for a in rows]
            axes[0,i].plot(x,[float(a['next_T']) for a in rows],label=r['controller'],linewidth=.9)
            axes[1,i].plot(x[:120],[float(a['command']) for a in rows[:120]],label=r['controller'],linewidth=.8)
        axes[0,i].axhspan(21.5,22.5,alpha=.08,color='green');axes[0,i].set(title=f'Day {day}: SD 0.05 C, delay 60 s',xlabel='Hours',ylabel='True room temperature [C]')
        axes[1,i].set(title='First 2 hours: requested supply',xlabel='Hours',ylabel='Requested supply [C]')
        for ax in axes[:,i]:ax.legend(fontsize=7)
    plot=ROOT/'docs/reports/boptest_jitter_2026-09-08.png';fig.savefig(plot,dpi=130);plt.close(fig)
    img=base64.b64encode(plot.read_bytes()).decode()
    summary_rows=''
    for group,group_label in [('0','3個新日期：無雜訊／無延遲'),('0.05','3個新日期：雜訊0.05°C／延遲60秒')]:
        for name,m in summary[group].items():summary_rows+=f'<tr><td>{group_label}</td><td>{names[name]}</td><td>{m["mae_C"]:.4f}</td><td>{m["command_total_variation_C"]:.1f}</td></tr>'
    reduction=100*(1-v['noisy_requested_variation_ratio'])
    sections=[('本輪結論',f'<p class="lead">新版本：{names[selected]}。新日期含雜訊／延遲組的平均送出指令變動量降低 <strong>{reduction:.1f}%</strong>。</p><p>事先制定的「每個情境控溫不明顯退步＋抖動降低至少20%」門檻：<strong>{"通過" if v["improvement_gate"] else "未通過"}</strong>。三個乾淨情境的MAE均略增（0.0029–0.0045°C），最大誤差增量最高0.0915°C；完整代價保留如下。</p><table><tr><th>情境</th><th>方法</th><th>平均MAE °C</th><th>平均指令總變動 °C</th></tr>'+summary_rows+'</table>'),
    ('這次算法改了什麼','<ol><li>擾動觀測器使用上一個區間真正生效的供氣指令，避免把尚未到達致動器的命令當成已生效。</li><li>以指數平滑減少指令跳動；比較α=0.6和0.35，沒有改辨識增益。積分器以0.1比例回算平滑造成的指令差。</li><li>保留交接初值、12–40°C供氣限制、固定風量0.5及積分防飽和。控制與評分每分鐘一次，目標22°C。</li></ol><p>α由已看過的開發情境選擇，不能說整套設計完全免調參。沒有新增辨識激勵，也沒有加入或驗證神經網路。指令平滑是通用控制技巧，不是新穎性證明。</p>'),
    ('先選版本，再開新日期','<p>開發：第95／245天，固定雜訊σ=0.05°C，分別測0／60秒延遲，四個候選共16組。每個案例MAE最多比v4增加0.02°C、最大誤差最多增加0.2°C，且平均指令變動需降低至少20%，才可被選取。</p><p>選定後固定程式、參數、協定及舊資料雜湊，再測未使用過的第65／155／275天，各做無雜訊無延遲，以及雜訊加60秒延遲。所有方法共用初始狀態、雜訊序列與輸出限制；真實FMU室溫用於評分。暖機24h，完整評分24h，沒有刪暫態。</p><p>這是合成的離散指令傳輸延遲，不是實測致動器動態。傳送／生效指令逐筆記錄並核對佇列。新日期仍是同一FMU／天氣年，不能推論跨設備可靠性。</p>'),
    ('所有開發候選',table(d['records'])),('固定版本後的新日期',table(t['records'])),
    ('雜訊與延遲下的真實溫度和控制指令',f'<img alt="True temperature and requested supply for all three noisy delayed transfer days" src="data:image/png;base64,{img}"><p>上排為整天室溫，下排為前2h供氣命令。全部24h指令變動都計入表格，圖中截段僅為觀察抖動。無雜訊情境完整結果也保留在表格中。</p>'),
    ('限制、成本與下一輪','<p>平滑會降低反應速度：乾淨量測的微小誤差可能增加，不能把通過允許差距門檻說成每個案例都更準。指令總變動量是動作平順度的代理指標，不能直接稱為節能或延長壽命。能源通道、飽和比例、域外筆數、前30min／之後MAE都保留在JSON。高負載仍可能碰到設備出力上限。</p><p>下一輪應加入更長／變動延遲、不同雜訊種子與第二個設備模型，並加入同樣平滑的強PI基準。當前grid比較器沒有相同平滑器，主要結論是相對舊v4的改進，不能宣稱超越所有PID方案。</p><p>自動方法沿用2h資料前綴，原研究實際收集6h；原9組搜尋使用54h試調。這輪模擬、暖機、平滑係數選擇都是額外研究成本；沒有測量人工調參工時。既有論文主結論與20–30°C空間估測範圍未擴張。</p>'),
    ('可重現證據','<p><a href="../../openspec/changes/reduce-boptest-command-jitter/artifacts/development.json">開發結果</a> · <a href="../../openspec/changes/reduce-boptest-command-jitter/artifacts/selection.json">固定版本</a> · <a href="../../openspec/changes/reduce-boptest-command-jitter/artifacts/transfer.json">新日期結果</a> · <a href="../../openspec/changes/reduce-boptest-command-jitter/evidence.md">研究紀錄</a> · <a href="boptest_transfer_2026-09-08_zh.html">前一輪</a></p><p>沿用官方BOPTEST v0.9.0 bestest_air FMU、FMPy0.3.22與本機相容函式庫；授權及版本紀錄均保留。這是自訂FMU runner，不宣稱官方REST/KPI等價、半導體實機或濕度驗證。</p>')]
    content=''.join(f'<section id="s{i}"><span>{i:02}</span><h2>{title}</h2>{body}</section>' for i,(title,body) in enumerate(sections,1))
    page=ROOT/'docs/reports/boptest_jitter_2026-09-08_zh.html'
    page.write_text('''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BOPTEST 抖動與延遲改進</title><style>body{font:18px/1.75 system-ui;background:#edf2f7;color:#172d3e;margin:0}main{max-width:1250px;margin:auto;padding:30px}h1{font-size:36px}h2{font-size:28px}section{background:white;padding:35px;margin:25px 0;border-radius:15px;min-height:55vh}section>span{float:right;color:#668}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:10px;border-bottom:1px solid #ccd;text-align:left}th{background:#f0f5fa}.scroll{overflow:auto}.lead{font-size:24px}img{width:100%}a{color:#086981}@media print{section{break-before:page;margin:0;min-height:0}body{background:white}}@media(max-width:600px){main{padding:10px}section{padding:18px}}</style><main><h1>繼續改進：降低指令抖動，處理致動延遲</h1><p>2026-09-08 · 模擬探索 · 固定版本後新日期檢查</p>'''+content+'</main></html>')
    page.with_suffix('.json').write_text(json.dumps({'status':'EXPLORATORY','sections':len(sections),'summary':summary,'html_sha256':sha(page),'plot_sha256':sha(plot),'transfer_sha256':sha(ART/'transfer.json')},indent=2)+'\n');print(page)

if __name__=='__main__':main()
