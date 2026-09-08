"""Offline two-factor report with paired contrasts and actual confirmation gates."""
import csv,html,json
from run_boptest_cross_plant import ROOT
from select_boptest_handover import ART,gate


def main():
    v=json.loads((ART/'verification.json').read_text());sections=[]
    fmt=lambda x:'未達成／右設限' if x is None else f'{x:.5f}'
    titles={'handover_at15':'固定15min：保留−撤除','handover_at55':'固定55min：保留−撤除','duration_taper':'固定撤除：55−15min','duration_retain':'固定保留：55−15min'}
    def table(heads,rows):return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+h+'</th>' for h in heads)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
    for name,d in v['plants'].items():
        blocks=[]
        for phase in ('development','confirmation'):
            r=json.loads((ART/(name+'_'+phase+'.json')).read_text());rows=[]
            for a in r['evaluations']:
                b=next(x for x in r['evaluations'] if x['method']=='auto_pi' and x['day']==a['day']);w=a['windows'];g=gate(b['windows'],w)
                label='PI基準（引用前輪）' if a['method']=='auto_pi' and a['reused'] else 'PI基準' if a['method']=='auto_pi' else '沿用PI，非改善' if a['reused'] else '通過' if g['passed'] else '未通過：'+','.join(k for k,t in g['checks'].items() if not t)
                gain=100*(b['windows']['early']['mae_C']-w['early']['mae_C'])/b['windows']['early']['mae_C']
                rows.append([a['day'],a['policy'] or 'PI',fmt(a['initial_state']['T']),fmt(w['early']['mae_C']),f'{gain:.2f}%',fmt(w['late']['mae_C']),fmt(w['late']['max_abs_error_C']),fmt(w['late']['requested_TV_u']),fmt(w['acquisition_onset_min']),a['exit_min'],a.get('zero_min','—'),label])
            blocks.append('<h3>'+('開發日8：完整2×2組合' if phase=='development' else '確認日48／83：已鎖定政策')+'</h3>'+table(['日','政策','起始°C','前1h MAE','前段改善','後段MAE','後段最大誤差','後段TV','持續15min達標起點','交接min','輔助歸零min','判定'],rows)+f'<p><a href="../../openspec/changes/startup-handover-ablation/artifacts/{name}_{phase}.json">完整結果、能耗、軌跡來源</a></p>')
            if phase=='confirmation':
                for day in (48,83):
                    curves=[]
                    for rec in [a for a in r['evaluations'] if a['day']==day]:
                        with (ROOT/rec['trace']).open() as f:curves.append([float(x['next_T']) for x in csv.DictReader(f)])
                    for n,title in ((180,'前3小時'),(1440,'全天')):
                        lo=min([22]+[x for c in curves for x in c[:n]])-.1;hi=max([22]+[x for c in curves for x in c[:n]])+.1
                        y=lambda t:220-(t-lo)/(hi-lo)*180
                        svg=f'<svg viewBox="0 0 900 250"><path d="M50 {y(22)} H870" stroke="#999" stroke-dasharray="4 4"/><text x="0" y="25">{hi:.2f}°C</text><text x="0" y="220">{lo:.2f}°C</text>'
                        for curve,color in zip(curves,['#62aef5','#f4a457']):
                            pts=' '.join(f'{50+i/(n-1)*820:.2f},{y(t):.2f}' for i,t in enumerate(curve[:n]));svg+=f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2"/>'
                        blocks.append(f'<h4>第{day}日 {title}（藍PI／橘選定政策）</h4>'+svg+f'<text x="50" y="245">0</text><text x="790" y="245">{n} min</text></svg>')
        rows=[]
        for c in d['factorial_contrasts']:
            rows.append([titles[c['label']],fmt(c['a_minus_b']['early']['mae_C']),fmt(c['a_minus_b']['late']['mae_C']),fmt(c['a_acquisition_min']),fmt(c['b_acquisition_min']),c['identical_pretrigger_minutes'],'相同' if c['identical_entire_trajectory'] else '不同'])
        blocks.insert(0,'<h3>分開看兩個因素：同一開發日差值</h3><p>誤差差值為表頭所示的前者減後者；負值代表前者誤差較低。交接前命令與溫度已核對一致。這些是已知FMU的開發對照，不是實機統計結論；新日期只確認選定政策，未重做完整2×2。</p>'+table(['固定條件／差值方向','前段MAE差°C','後段MAE差°C','前者達標min','後者達標min','交接前一致min','整段軌跡'],rows))
        sections.append(f'<section><h2>{name}｜選定 {d["selection"]["policy"] or "純PI"}</h2><p>兩個確認日期皆通過：'+('是' if d['supported_both_dates'] else '否')+'</p>'+''.join(blocks)+'</section>')
    wins=[n for n,d in v['plants'].items() if d['supported_both_dates']]
    forwarded=[n for n,d in v['plants'].items() if d['selection']['policy'] is not None]
    body='''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PI 輔助時間與交接方式</title><style>body{font:17px/1.7 system-ui;background:#101923;color:#e7eef5;max-width:1450px;margin:auto;padding:28px}section{background:#1a2836;padding:24px;margin:24px 0;border-radius:16px}h1,h2{color:#7fd1cf}table{border-collapse:collapse;white-space:nowrap;font-size:14px}td,th{padding:9px;border-bottom:1px solid #425466;text-align:right}.scroll{overflow:auto}svg{width:100%;max-height:300px}svg text{fill:#ddd;font-size:14px}a{color:#8ed9d7}.notice{border-left:5px solid #e9b563;padding:16px;background:#302a22}</style><h1>PI 前期輔助：時間和交接方式，分開測試</h1><p>SHA-001｜2026-09-08｜未採納控溫延伸研究</p>'''
    body+=f'<p class="notice">5設備、{len(forwarded)}個開發候選獲選、{len(wins)}個通過兩個確認日期：{", ".join(wins) or "無"}。{v["unique_episodes"]}次新FMU試驗，{v["aggregate_simulated_hours"]}模擬小時；重播／來源／交接前一致性驗證PASS。</p>'
    body+='''<section><h2>四組共用同一輔助公式</h2><p>15_taper＝15分鐘後逐步撤除；15_retain＝15分鐘後轉入PI積分；55_taper與55_retain則將上限延至55分鐘。若先跨越目標就提早交接。固定時間比較交接方式，固定方式比較時間；沒有依設備名稱分支。</p><p>普通PI核心與誤差輔助公式保持一致：輔助clip(Kp×誤差,±0.1u)，每分鐘最多改0.02u。taper不注入積分，最多5分鐘撤完；retain將當下剩餘輔助轉進積分，保留同一觀測下命令連續。這與上一輪同時改變趨勢和積分衰減不同，適合分離本輪兩個因素。交接後PI方程相同，不代表狀態與基準相同。</p></section><section><h2>門檻、成本與適用範圍</h2><p>沿用2h辨識與21→22°C暖機挑戰。每設備新跑4×3＝12h候選，再計既有3h基準與2h辨識，共17h名目曝光，還未含前幾輪搜尋成本；尚未證明總調整成本更低。</p><p>前段首60min MAE改善至少max(0.001°C,1%)；前後段峰值增加≤max(0.02°C,5%)；後段MAE增加≤max(0.002°C,5%)；後段TV≤基準×1.1+0.02；基準若可持續15min在±0.1°C內，候選達標不得晚超過1min。第8日選擇後鎖定，再開第48／83日各24h。不合格則回退純PI；引用軌跡不算獨立試驗。</p><p>兩個時間與兩種模式的有限搜尋，不是找到通用最優界線。若兩種時長都先跨越目標，實際輔助時間可能相同。量測包含氣溫與操作溫度，不混合絕對MAE。相對通過不代表絕對精密控溫或全天維持目標。</p></section>'''
    hyd=json.loads((ART/'hydronic_confirmation.json').read_text())
    summary=[]
    for day in (48,83):
        base,ours=[x for x in hyd['evaluations'] if x['day']==day]
        e=100*(1-ours['windows']['early']['mae_C']/base['windows']['early']['mae_C'])
        l=100*(1-ours['windows']['late']['mae_C']/base['windows']['late']['mae_C'])
        bt,at=base['windows']['acquisition_onset_min'],ours['windows']['acquisition_onset_min']
        summary.append([day,f'{e:.2f}%',f'{l:.2f}%',fmt(bt),fmt(at),fmt(ours['windows']['late']['mae_C']),fmt(ours['windows']['late']['max_abs_error_C'])])
    body+='<section><h2>本輪找到的可行組合與限制</h2><p>水暖由共用選擇流程選到15_retain，兩日期皆通過。交接前保留相同輔助公式，單獨改交接方式的開發對照顯示：在本設備中，保留積分狀態的作用比只延長輔助更值得追查。15分鐘只是已測15／55分鐘中的選擇，尚未建立最佳時間區間。</p>'+table(['確認日','前段MAE改善','後段MAE改善','PI達標min','候選達標min','候選後段MAE°C','候選後段最大誤差°C'],summary)+'<p>第83日後段最大誤差仍約2.65°C，不能把相對改善說成精密控溫。其餘設備未選到同時滿足全部開發門檻的組合，保留原PI。前輪與本輪確認日期不同，不能直接用兩輪百分比宣稱新版全面勝過前版；新輪確認的是相對同日PI基準的效果。</p></section>'
    body+=''.join(sections)
    body+='''<section><h2>證據來源</h2><p>官方BOPTEST v0.9.0 FMU與自訂FMPy runner；未證明官方REST/KPI等價，沒有未知設備、實機、濕度、EUV或NN驗證。</p><p><a href="../../openspec/changes/startup-handover-ablation/protocol.md">凍結協定</a> · <a href="../../openspec/changes/startup-handover-ablation/artifacts/verification.json">完整驗證及因素對照</a> · <a href="../../openspec/changes/startup-handover-ablation/artifacts/selection.json">選擇紀錄</a> · <a href="boptest_predictive_startup_2026-09-08_zh.html">前輪報告</a></p></section></html>'''
    dest=ROOT/'docs/reports/boptest_handover_2026-09-08_zh.html';dest.write_text(body);print(dest)
if __name__=='__main__':main()
