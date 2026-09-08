"""Offline presentation, all quantitative conclusions derived from canonical data."""
import csv,html,json
from run_boptest_cross_plant import ROOT
from select_boptest_predictive_startup import ART,gate

def main():
    v=json.loads((ART/'verification.json').read_text());sections=[]
    reasons={0:'仍啟用',1:'未啟用',2:'預估接近目標',3:'跨越目標',4:'55分鐘撤離上限',5:'PI積分接手'}
    fmt=lambda x:'未達成' if x is None else f'{x:.4f}'
    for name,d in v['plants'].items():
        blocks=[]
        for phase in ('development','confirmation'):
            r=json.loads((ART/(name+'_'+phase+'.json')).read_text());trs=[]
            for rec in r['evaluations']:
                w=rec['windows'];b=next(x for x in r['evaluations'] if x['method']=='auto_pi' and x['day']==rec['day']);g=gate(b['windows'],w)
                verdict='基準（舊軌跡引用）' if rec['method']=='auto_pi' and rec['reused'] else '基準' if rec['method']=='auto_pi' else '回退純PI：非改善' if rec['reused'] else '通過' if g['passed'] else '未通過：'+','.join(k for k,t in g['checks'].items() if not t)
                gain=100*(b['windows']['early']['mae_C']-w['early']['mae_C'])/b['windows']['early']['mae_C']
                vals=[rec['day'],rec['horizon_min'] or 'PI',fmt(rec['initial_state']['T']),fmt(w['early']['mae_C']),f'{gain:.2f}%',fmt(w['late']['mae_C']),fmt(w['late']['max_abs_error_C']),fmt(w['late']['requested_TV_u']),fmt(w['acquisition_onset_min']),reasons[rec['exit_code']],rec['exit_min'],rec.get('zero_min','—'),verdict]
                trs.append('<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in vals)+'</tr>')
            title='第8日開發／三種預估時間' if phase=='development' else '第42、77日確認／不再調參'
            heads=['日','預估分鐘','起始°C','前1h MAE','前段改善','後段MAE','後段最大誤差','後段TV','持續15min達標起點','撤離原因','觸發min','完全撤離min','判定']
            blocks.append('<h3>'+title+'</h3><p><a href="../../openspec/changes/predictive-startup-boundary/artifacts/'+name+'_'+phase+'.json">完整結果、能耗與軌跡來源</a></p><div class="scroll"><table><tr>'+''.join('<th>'+x+'</th>' for x in heads)+'</tr>'+''.join(trs)+'</table></div>')
            if phase=='confirmation':
                for day in (42,77):
                    pair=[x for x in r['evaluations'] if x['day']==day];curves=[]
                    for rec in pair:
                        with (ROOT/rec['trace']).open() as f:curves.append([float(x['next_T']) for x in csv.DictReader(f)])
                    for n,label in [(180,'前3小時'),(1440,'全天24小時')]:
                        lo=min([22]+[x for c in curves for x in c[:n]])-.1;hi=max([22]+[x for c in curves for x in c[:n]])+.1
                        y=lambda t:220-(t-lo)/(hi-lo)*180
                        svg=f'<svg viewBox="0 0 900 250"><path d="M50 {y(22)} H870" stroke="#888" stroke-dasharray="4 4"/><text x="0" y="25">{hi:.2f}°C</text><text x="0" y="220">{lo:.2f}°C</text>'
                        for curve,color in zip(curves,['#62aef5','#f4a457']):
                            pts=' '.join(f'{50+i/(n-1)*820:.2f},{y(t):.2f}' for i,t in enumerate(curve[:n]));svg+=f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2"/>'
                        blocks.append(f'<h4>第{day}日 {label}（藍PI／橘選定政策）</h4>'+svg+f'<text x="50" y="245">0</text><text x="790" y="245">{n} min</text></svg>')
        snap=d['posthoc_withdrawal_snapshots']
        if d['selection']['horizon_min'] is not None:
            rows=''.join('<tr>'+''.join('<td>'+html.escape(str(x[k]) if k in ('day','method','minute') else fmt(x[k]))+'</td>' for k in ('day','method','minute','T','u','integral','correction'))+'</tr>' for x in snap)
            blocks.append('<h3>撤離前後觀察（事後描述，非獨立因果檢驗）</h3><div class="scroll"><table><tr><th>日</th><th>政策</th><th>分鐘</th><th>溫度°C</th><th>輸出u</th><th>積分</th><th>輔助</th></tr>'+rows+'</table></div><p>本輪水暖在第60分鐘仍比基準暖，但輸出較低，第120分鐘溫度略落後。這與撤離後進展變慢一致；仍需分開測試撤離時間與積分處理才能確認原因。</p>')
        old_rows=d['old_development_candidates']
        old_text='；'.join(f"±{x['band_C']}°C：前段MAE {x['early_mae_C']:.6f}，達標 {fmt(x['acquisition_onset_min'])}min" for x in old_rows)
        blocks.append('<h3>前輪候選：同一開發日的對照</h3><p>'+old_text+'</p><p>這些是既有第8日開發證據，不是新日期確認，也不代表所有前輪候選都符合門檻。</p>')
        h=d['selection']['horizon_min'];same=d['development_horizons_identical']
        sections.append(f'<section><h2>{name}｜'+('純PI回退' if h is None else f'預估{h}分鐘')+f"</h2><p>兩確認日皆通過：{'是' if d['supported_both_dates'] else '否'}。三種候選軌跡{'完全相同，無法辨認預估時間的差異' if same else '不同；選出的值只代表這個有限搜尋範圍'}。</p>"+''.join(blocks)+'</section>')
    wins=[n for n,d in v['plants'].items() if d['supported_both_dates']];forward=[n for n,d in v['plants'].items() if d['selection']['horizon_min'] is not None]
    body='''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PI 預估退出界線研究</title><style>body{font:17px/1.7 system-ui;background:#101923;color:#e7eef5;margin:auto;max-width:1450px;padding:28px}section{background:#1a2836;padding:24px;margin:24px 0;border-radius:16px}h1,h2{color:#7fd1cf}table{border-collapse:collapse;font-size:14px;white-space:nowrap}td,th{padding:9px;border-bottom:1px solid #425466;text-align:right}.scroll{overflow:auto}svg{width:100%;max-height:300px}svg text{fill:#ddd;font-size:14px}a{color:#8ed9d7}.notice{border-left:5px solid #e9b563;padding:16px;background:#302a22}</style><h1>PI 前期輔助：提前預估退出，讓積分逐步接手</h1><p>PSB-001｜2026-09-08｜未採納控溫延伸研究</p>'''
    body+=f'<p class="notice">五設備，{len(forward)}個在開發日選到候選；{len(wins)}個通過兩確認日期：{", ".join(wins) or "無"}。共{v["unique_episodes"]}次新FMU試验、{v["aggregate_simulated_hours"]}模擬小時。完整重播與來源驗證PASS。</p>'
    body+='''<section><h2>新的退出判斷</h2><p>保留普通PI核心；額外輔助上限0.1u，每分鐘變化≤0.02u。PI朝目標累積的積分量越多，輔助量越少。依過去觀測的平滑溫度斜率，判斷3／10／30分鐘後是否接近±0.1°C；預估接近、跨越目標、PI已接手，或55分鐘上限即開始不可逆撤離，最晚60分鐘歸零。不將補償加入PI積分。</p><p>這是趨勢外推啟發式，不是保證準確的溫度預測。退出後PI狀態受先前溫度影響，不能保證等同基準軌跡。</p></section><section><h2>比較規則與成本</h2><p>沿用先前2h辨識及第8日3h基準軌跡，新跑三候選各3h。每設備新增9h試調；若計既有基準觀測及辨識，名目曝光14h，且尚未包括前幾輪研究成本。不能宣稱整體調參時間已減少。</p><p>前段固定首60分鐘；後段第60分鐘至結束。門檻保持前輪：前段MAE至少改善max(0.001°C,1%)；後段MAE容許增加≤max(0.002°C,5%)；前後段峰值增加≤max(0.02°C,5%)；後段TV≤基準×1.1+0.02；若基準可持續15min在±0.1°C內，達標起點不得晚超過1min。候選皆未過則選純PI。</p><p>鎖定五設備選擇後才開啟第42／77日各24h。純PI回退引用同日基準，不算額外獨立試验；相對改善不等於絕對精度合格，持續15min達標不等於全天維持。氣溫與操作溫度不混合計算總平均。</p></section>'''
    body+=''.join(sections)
    body+='<section><h2>退出界線仍未確認</h2><p>本輪無候選同時通過兩個新日期全部門檻，因此不替換前輪方法。水暖的三種預估時間仍產生相同軌跡，都是55分鐘開始撤離，56分鐘歸零：3分鐘只是同分時既定選擇，不是已找出的最佳預估時間。</p><p>第77日水暖前段改善約16%，但持續達標從576分鐘延到581分鐘，超過容許的1分鐘延遲。後段平均誤差雖仍在事先容差內，也不能遮蓋這個失敗。第42日後段MAE約1.75°C，亦不屬精密控溫。</p><p>同一開發日，水暖前段MAE由前版約0.7478增加至新版0.7888°C；新版沒有超越前版。空氣系統達標延遲消失，但有效前段改善也消失。這輪同時改變撤離判斷與積分處理，無法單憑結果區分哪一項造成變化；下一輪應分開測試固定輔助期間與撤離方式，維持原門檻。</p></section>'
    body+='''<section><h2>研究範圍</h2><p>已知設備上的模擬流程確認；沒有未知設備泛化、實機、濕度、EUV或NN證據。官方BOPTEST v0.9.0 FMU、自訂FMPy runner，非官方REST/KPI等價驗證。前輪開發數據只作事後對照，不當成新獨立驗證。</p><p><a href="../../openspec/changes/predictive-startup-boundary/protocol.md">凍結協定</a> · <a href="../../openspec/changes/predictive-startup-boundary/artifacts/selection.json">自動選擇</a> · <a href="../../openspec/changes/predictive-startup-boundary/artifacts/verification.json">完整驗證與前輪對照</a> · <a href="boptest_startup_2026-09-08_zh.html">前輪報告</a></p></section></html>'''
    p=ROOT/'docs/reports/boptest_predictive_startup_2026-09-08_zh.html';p.write_text(body);print(p)
if __name__=='__main__':main()
