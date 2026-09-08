"""Build an offline evidence-linked HTML briefing from canonical SPB results."""
import csv
import html
import json
from run_boptest_cross_plant import ROOT
from select_boptest_startup import ART,gate


def main():
    v=json.loads((ART/'verification.json').read_text());sections=[]
    labels={'air':'空氣系統','hydronic':'水暖系統','heat_pump':'熱泵','apartment':'公寓','commercial':'商用系統'}
    reasons={1:'未啟用',2:'連續5分鐘進入界線',3:'跨越目標',4:'60分鐘上限'}
    def fmt(x):return '未達成（右設限）' if x is None else f'{x:.4f}'
    for name,decision in v['plants'].items():
        band=decision['selection']['band_C'];blocks=['<p class="notice">'+('三種界線的控制命令與溫度軌跡完全相同：無法辨認最佳誤差界線。' if decision['development_bands_identical_trajectories'] else '三種界線可產生不同軌跡，但沒有同時滿足所有開發門檻的界線。')+'</p>']
        for phase in ('development','confirmation'):
            r=json.loads((ART/(name+'_'+phase+'.json')).read_text());table=[]
            for rec in r['evaluations']:
                w=rec['windows'];base=next(b for b in r['evaluations'] if b['day']==rec['day'] and b['method']=='auto_pi')
                g=gate(base['windows'],w)
                failed='、'.join(k for k,val in g['checks'].items() if not val)
                outcome='基準' if rec['method']=='auto_pi' else '沿用基準，非改善' if rec['reused'] else '通過' if g['passed'] else '未通過：'+failed
                row=[rec['day'],'PI' if rec['band_C'] is None else f"±{rec['band_C']}°C",fmt(rec['initial_state']['T']),fmt(w['early']['mae_C']),fmt(w['late']['mae_C']),fmt(w['early']['max_abs_error_C']),fmt(w['late']['max_abs_error_C']),fmt(w['late']['requested_TV_u']),fmt(w['acquisition_onset_min']),f"{reasons[rec['exit_code']]} / {rec['exit_min']:g} min",outcome]
                table.append('<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in row)+'</tr>')
            title='開發日：界線搜尋（3小時）' if phase=='development' else '新日期確認（24小時；未再調參）'
            blocks.append('<h3>'+title+'</h3><p><a href="../../openspec/changes/startup-pi-boundary/artifacts/'+name+'_'+phase+'.json">完整逐次結果（含能耗與來源軌跡）</a></p><div class="scroll"><table><thead><tr>'+''.join('<th>'+x+'</th>' for x in ['日','政策','起始°C','前1h MAE','後段 MAE','前段最大誤差','後段最大誤差','後段 TV','持續15min達標起點','退出原因／時間','複合判定'])+'</tr></thead><tbody>'+''.join(table)+'</tbody></table></div>')
            if phase=='confirmation':
                for day in (35,70):
                    records=[x for x in r['evaluations'] if x['day']==day]
                    curves=[];all_t=[]
                    for rec in records:
                        with (ROOT/rec['trace']).open() as f:rows=list(csv.DictReader(f))[:180]
                        values=[float(x['next_T']) for x in rows];all_t.extend(values);curves.append(values)
                    lo=min(all_t+[22])-.1;hi=max(all_t+[22])+.1
                    yy=lambda t:220-(t-lo)/(hi-lo)*180
                    svg=f'<svg viewBox="0 0 900 260" role="img" aria-label="前3小時溫度曲線"><path d="M50 {yy(22)} H870" stroke="#999" stroke-dasharray="5 4"/><text x="5" y="25">{hi:.2f}°C</text><text x="5" y="225">{lo:.2f}°C</text>'
                    for values,color in zip(curves,['#4f98e8','#f09b48']):
                        points=' '.join(f'{50+i/179*820:.2f},{yy(t):.2f}' for i,t in enumerate(values))
                        svg+=f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2"/>'
                    svg+='<text x="50" y="250">0</text><text x="790" y="250">180 min</text></svg>'
                    blocks.append(f'<h4>第{day}日：前3小時（藍＝PI；橘＝選定政策）</h4>'+svg)
        sections.append(f'<section><h2>{labels[name]}／{name}</h2><p>開發日自動選擇：'+('純 PI 回退' if band is None else f'±{band}°C')+f"；兩個確認日期皆通過：{'是' if decision['supported_both_dates'] else '否'}。</p>"+''.join(blocks)+'</section>')
    supported=[n for n,d in v['plants'].items() if d['supported_both_dates']]
    selected=[n for n,d in v['plants'].items() if d['selection']['band_C'] is not None]
    body=f'''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PI 前期輔助與退出界線</title><style>body{{font:17px/1.65 system-ui;background:#101923;color:#e7eef5;margin:auto;max-width:1400px;padding:28px}}section{{background:#1a2836;padding:24px;margin:24px 0;border-radius:16px}}h1,h2{{color:#7fd1cf}}table{{border-collapse:collapse;font-size:14px;white-space:nowrap}}td,th{{padding:9px;border-bottom:1px solid #425466;text-align:right}}th{{color:#8ed9d7}}.scroll{{overflow:auto}}svg{{width:100%;max-height:330px}}svg text{{fill:#ddd;font-size:14px}}a{{color:#8ed9d7}}.notice{{border-left:5px solid #e9b563;padding:16px;background:#302a22}}</style>
    <h1>讓 PI 更快接近目標，同時守住後段品質</h1><p>2026-09-08｜SPB-001｜未採納的控溫延伸研究</p>
    <p class="notice">5 個已知設備；{len(selected)} 個在開發日選到輔助政策，{len(supported)} 個在兩個新日期均通過。確認通過設備：{', '.join(supported) or '無'}。這不是跨未知設備或實機的一般性證明。</p>
    <section><h2>方法與界線</h2><p>先以21°C設定暖機24小時，再將目標切到22°C，保留實際起始溫度。基準是既有2小時資料辨識的 PI。前期加上 clip(Kp×誤差, ±0.1) 輔助，每分鐘變化不超過0.02。</p><p>比較 ±0.05、±0.1、±0.2°C。連續5分鐘進入界線、首次跨越目標，或60分鐘到期，即永久退出；起始已在界線內則不啟用。退出時將補償轉入積分狀態，保持同一觀測點的未飽和命令連續；後續使用普通 PI 方程，不代表溫度軌跡必定與基準相同。</p><p>第8日每政策測3小時，依同一規則自動選界線，未通過則回退。選擇及來源雜湊鎖定後，才開啟第35、70日各24小時的確認。若三個界線都由60分鐘上限退出且軌跡相同，無法據此認定最佳誤差界線。</p></section>
    <section><h2>評分與成本</h2><p>前段固定第一小時；後段固定第60分鐘後，不隨退出時間改窗。前段MAE需改善 ≥ max(0.001°C,1%)；前後段最大誤差增加不能超過 max(0.02°C,5%)；後段MAE增加不能超過 max(0.002°C,5%)；後段TV ≤ 原值×1.10+0.02。基準若能持續15分鐘在±0.1°C內，候選達標不得晚超過1分鐘。這是容差內維持，並非後段誤差絕對不能增加。</p><p>每設備沿用2小時資料，另需4×3＝12小時開發試跑，名目適應曝光14小時。基準PI不需要這12小時搜尋，因此尚未證明總調整成本更低。共 {v['unique_episodes']} 次獨立FMU試驗；評分 {v['scored_hours']} 小時、暖機 {v['warmup_hours']} 小時，合計 {v['aggregate_simulated_hours']} 模擬小時。回退軌跡明確重用，不算第二次獨立試驗。各設備量測定義不同，不合併絕對MAE。</p></section>
    {''.join(sections)}
    <section><h2>這輪對界線的回答</h2><p>目前仍未辨認出一條通用的誤差切換界線。水暖系統開發日前1小時MAE由0.9433降至0.7478°C（約20.7%），但三種界線都由60分鐘上限退出；±0.2°C只是同分時偏好較寬界線的既定選擇，不是最佳值的證據。</p><p>空氣系統±0.2°C前段MAE由0.12746降至0.11744°C（約7.9%），持續達標卻由第16分鐘延至第19分鐘；平均更準與更快穩定達標不是同一件事。商用約0.77%、熱泵約0.03%的前段改善未達1%最低門檻；公寓前段沒有改善。</p><p>水暖系統確認日35與70之前段MAE分別改善約20.38%與20.61%；後段分別改善16.38%與1.03%。但第70日後段MAE仍2.099°C，最大誤差5.609°C，不能把相對改善說成已達精密控溫。持續15分鐘達標也不代表其後全天一直維持。</p><p>下一個研究問題是退出時機是否還需考慮溫度變化速度，以及已累積的積分量，而不是繼續只縮小誤差界線。這是由本輪結果提出的待驗證假設，尚未改入演算法，也不能據此宣稱已解決。</p></section>
    <section><h2>證據範圍</h2><p>官方 BOPTEST v0.9.0 FMU，自訂 FMPy runner；未驗證官方 REST/KPI 等價。沒有新增 NN、濕度控制、EUV 或硬體證據。平滑切換是已知控制概念，非本研究新穎性證明；參考 <a href="https://www.mathworks.com/help/simulink/slref/bumpless-control-transfer-between-manual-and-pid-control.html">MathWorks bumpless transfer 文件</a>。</p><p>來源：<a href="../../openspec/changes/startup-pi-boundary/protocol.md">凍結協定</a>、<a href="../../openspec/changes/startup-pi-boundary/artifacts/selection.json">開發選擇</a>、<a href="../../openspec/changes/startup-pi-boundary/artifacts/verification.json">完整驗證</a>。表格未列的能耗、RMSE、飽和率與域外樣本均保留於逐次JSON及CSV。公寓開發日起始約23.69°C，已高於22°C目標，屬降溫方向的挑戰，不可當作與其他設備同幅度的升溫試驗。</p></section></html>'''
    dest=ROOT/'docs/reports/boptest_startup_2026-09-08_zh.html';dest.write_text(body)
    print(dest)
if __name__=='__main__':main()
