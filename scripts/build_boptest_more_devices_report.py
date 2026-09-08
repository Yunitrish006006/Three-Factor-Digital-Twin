"""Offline report with every registered new FMU and all negative outcomes."""
import base64
import csv
import html
import json
import os
import re
from pathlib import Path
from run_boptest_more_devices import ROOT, ART, sha
from build_boptest_delayed_dynamics_report import table

LABELS={'heat_pump':'熱泵地板供暖','apartment':'雙區公寓（日間區）','commercial':'商用建築散熱器'}

def main():
    os.environ.setdefault('MPLCONFIGDIR','/tmp/boptest-matplotlib')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    records={n:json.loads((ART/(n+'.json')).read_text()) for n in LABELS}
    audit=json.loads((ART/'verification.json').read_text())
    assert audit['status']=='PASS'
    tests=(ROOT/'outputs/boptest_more_devices_tests.log').read_text()
    summary=re.search(r'Ran (\d+) tests in ([\d.]+)s\s+OK',tests)
    assert summary,'Tests have not completed successfully'
    fitrows=[];evalrows=[];gaterows=[];device_rows=[];calrows=[];episodes=[]
    fig,axes=plt.subplots(2,3,figsize=(13,7),constrained_layout=True)
    for col,(name,r) in enumerate(records.items()):
        c=r['config'];episodes += [r['identification']]+r['trials']+r['evaluations']
        with (ROOT/r['calibration_trace']).open() as f: calibration=list(csv.DictReader(f))
        temperatures=[float(x[k]) for x in calibration for k in ['T','next_T']]
        calrows.append([LABELS[name],f'{min(temperatures):.3f}–{max(temperatures):.3f}',f"{r['identification']['metrics']['saturation_pct']:.1f}%",' / '.join(f"{day}: {next(e for e in r['evaluations'] if e['day']==day)['initial_state']['T']:.3f}°C" for day in [20,50])])
        device_rows.append([LABELS[name],c['case'],c['measurement_kind'],f"{c['actuator_min']}–{c['actuator_max']} {c['actuator_unit']}"])
        for row,h in enumerate((2,6)):
            bank=r['banks'][str(h)];m=bank.get('selected');ax=axes[row,col]
            fitrows.append([LABELS[name],h,bank['status'],m['order'] if m else '—',m['delay_steps'] if m else '—',f"{m['validation_rollout_rmse_C']:.5f}" if m else '—'])
            decision=next(d for d in audit['plants'][name]['decisions'] if d['budget_h']==h)
            gaterows.append([LABELS[name],h,'通過' if decision['gate'] else '未通過'])
            ax.set(title=f'{name} | ID {h}h',ylabel='24h MAE [C]',xticks=[0,1],xticklabels=['day 20','day 50'])
            if not m:
                ax.text(.5,.5,'Identification rejected',ha='center',transform=ax.transAxes);continue
            values={'auto_pi':[],'proposed':[]}
            for day in (20,50):
                es={e['method']:e for e in r['evaluations'] if e['budget_h']==h and e['day']==day}
                a,p=es['auto_pi']['metrics'],es['proposed']['metrics']
                for method in values:values[method].append(es[method]['metrics']['mae_C'])
                evalrows.append([LABELS[name],h,day,f"{a['mae_C']:.4f}",f"{p['mae_C']:.4f}",f"{a['max_abs_error_C']:.3f}",f"{p['max_abs_error_C']:.3f}",f"{p['saturation_pct']:.1f}%",f"{a['requested_TV_u']:.2f} / {p['requested_TV_u']:.2f}",'改善' if p['mae_C']<a['mae_C'] else '退步'])
            ax.bar([-.18,.82],values['auto_pi'],.36,label='auto-PI');ax.bar([.18,1.18],values['proposed'],.36,label='proposed');ax.legend(fontsize=8)
    n=len(episodes);warmup=sum(e['warmup_hours'] for e in episodes);scored=sum(e['scored_hours'] for e in episodes)
    fit_count=sum(b['offline_fit_count'] for r in records.values() for b in r['banks'].values())
    model_success=sum(b['status']=='FITTED' for r in records.values() for b in r['banks'].values())
    gate_success=sum(d['gate'] for p in audit['plants'].values() for d in p['decisions'])
    page=ROOT/'docs/reports/boptest_more_devices_2026-09-08_zh.html';plot=page.with_suffix('.png');fig.savefig(plot,dpi=145);plt.close(fig)
    sections=[('增加設備後，能否維持效果？',f'<p class="lead">新增三個 FMU，累計測試五種設備模型。本輪 {model_success}/6 組辨識成功，{gate_success}/6 組設備／資料預算通過預先控制門檻。</p><p>完成 {n} 次新模擬。演算法沿用上一輪凍結版本，新增設備沒有參與控制器開發或人工選參；它們仍須使用相同規則取得校正資料與有限試調，不是零資料移植。</p><p>整體三設備目標：'+('通過本輪門檻，仍限於這些模擬條件。' if audit['all_six_budgets_pass'] else '<strong>未通過；缺失或不利結果不能用平均改善掩蓋。</strong>')+'</p>'),
    ('五種模型的研究位置','<p>既有送風、水暖散熱器：開發設備，前輪結果保持不變。新加入熱泵地板供暖、雙區公寓與商用建築散熱器：固定演算法的新增 FMU 檢查。模型數量不等於獨立實體設備數；都屬建築 HVAC，也可能共用上游物理元件。</p>'+table(['設備','官方 testcase','溫度量測','主致動器原生範圍'],device_rows)+'<p>公寓只控制日間區的溫度，夜間區沿用原生控制；商用建築只接管散熱器閥，AHU 原生控制持續運作。結果不是完整多區或全設備聯合最佳化。</p>'),
    ('可調什麼、花多少成本','<p>控制器不接收設備名稱。固定模型庫為一／二階 × 五種延遲；相同穩定性檢查、相同 q∈{0.5,1} 的兩次 2h 試調，再固定選擇後開第 20／50 天。補償、平滑與回算常數全部沿用，沒有因新設備結果而修改。</p><p>設備安裝設定事先固定：熱泵風扇／泵開啟；公寓日間閥全開、兩區設定 22°C；商用泵 25000Pa、供水 45°C、室溫設定 22°C。其餘迴路原生運作。這些設定也是適用條件，不能把它們隱藏成完全免設定。</p>'+f'<p>辨識成功後，每方法的主動適應預算為 2h／6h 辨識＋4h 試調＝6h／10h；辨識拒絕的組合不支出後續試調時數。新收三條 6h 校正資料；本輪 {fit_count} 次離線擬合。完成回合的模擬時間合計 {warmup+scored:g}h，其中暖機 {warmup:g}h、校正／試調／評估 {scored:g}h。沒有人工整定工時對照，尚不能主張總調整成本已較低。</p>'),
    ('校正與初始狀態',table(['設備','校正溫度範圍 °C','校正指令飽和','各評估日暖機後溫度'],calrows)+'<p>相同正規化激勵可能有不同飽和程度，因此不保證相同資訊量。公寓日間閥全開的安裝條件下，暖機後已高於目標；這是本輪固定測試條件，不是已證實的普遍設備能力限制。所有方法從各日期相同初始狀態出發，沒有排除初始偏差來美化結果。</p>'),
    ('完整辨識與門檻',table(['設備','辨識h','狀態','階數','延遲min','校正推演RMSE °C'],fitrows)+table(['設備','辨識h','控制門檻'],gaterows)+'<p>每個日期 MAE ≤ auto-PI＋0.02°C、最大誤差 ≤ auto-PI＋0.2°C，且兩天平均 MAE 有改善才算通過；辨識拒絕時不進行控制評估。推演 RMSE 是校正內模型選擇，不能取代閉迴路驗證。</p>'),
    ('全部閉迴路比較',table(['設備','辨識h','日序','auto-PI MAE °C','本方法 MAE °C','auto-PI最大 °C','本方法最大 °C','本方法飽和','指令TV 基準／本方法','MAE'],evalrows)+'<p>目標 22°C、60 秒採樣；所有回合均含 24h 暖機，評估涵蓋完整 24h 暫態。空氣溫度與作用溫度只在各設備內比較，不混成總 MAE。</p><img alt="All new-device MAE comparisons including rejected identification" src="data:image/png;base64,'+base64.b64encode(plot.read_bytes()).decode()+'">'),
    ('怎麼看待這些結果','<p>熱泵四組日期／預算的本方法 MAE 均高於 auto-PI，且指令總變化量也較大。公寓 6h 十個訓練候選全被拒絕，沒有用缺失控制結果填零。短資料能擬合不代表控制一定受益；小推演誤差、正增益與穩定辨識極點也不是閉迴路穩定保證。控制退步、致動飽和、原生迴路交互影響都需要分開檢查。供暖設備沒有保證能消除日間過熱，不能直接把誤差全歸因於算法。</p><p>這輪只擴大固定方法的測試範圍，沒有看到結果後改算法再重測同一份資料。若後續用新設備失敗結果改進，它們將成為開發資料，下一版需要另設未見設備／條件。</p><p>這是未採納為主論文確認成果的獨立研究延伸。沒有實機、EUV、濕度、線材良率或神經網路效益的新增證據。</p>'),
    ('驗證與可重現資料',f'<p>{summary[1]} 項測試通過（{summary[2]} 秒）。驗證程式檢查來源雜湊、每條軌跡、指標重算、模型選擇與控制器逐步重播。官方 BOPTEST v0.9.0 FMU 搭配 FMPy 0.3.22，自訂 runner，不宣稱官方 REST／KPI 等價。</p><p><a href="../../openspec/changes/evaluate-more-boptest-devices/evidence.md">研究紀錄與成本</a> · <a href="../../openspec/changes/evaluate-more-boptest-devices/artifacts/verification.json">完整驗證</a> · <a href="../../openspec/changes/evaluate-more-boptest-devices/artifacts/freeze.json">執行前固定來源</a> · <a href="../../scripts/boptest_more_devices.json">設備設定</a></p>'+''.join(f'<p><a href="../../openspec/changes/evaluate-more-boptest-devices/artifacts/{n}.json">{label}全部原始結果</a></p>' for n,label in LABELS.items()))]
    body=''.join(f'<section><small>{i:02}</small><h2>{title}</h2>{text}</section>' for i,(title,text) in enumerate(sections,1))
    page.write_text('''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>少資料控溫：新增三種設備</title><style>body{font:18px/1.8 system-ui;background:#edf3f7;color:#193348;margin:0}main{max-width:1280px;margin:auto;padding:28px}section{background:white;padding:30px;margin:25px 0;border-radius:14px}h1{font-size:36px}h2{font-size:27px}.lead{font-size:24px}small{float:right;color:#678}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:9px;border-bottom:1px solid #ccd;text-align:left}th{background:#edf4f6}.scroll{overflow:auto}img{width:100%}a{color:#00728a}@media print{section{break-before:page}body{background:white}}@media(max-width:600px){main{padding:10px}section{padding:15px}}</style><main><h1>少資料控溫：新增三種設備</h1><p>2026-09-08 · 固定算法／有限適應 · 離線教授報告</p>'''+body+'</main></html>')
    manifest={'status':'BOUNDED_GATE_PASSED' if audit['all_six_budgets_pass'] else 'GENERALITY_GATE_NOT_MET','html_sha256':sha(page),'plot_sha256':sha(plot),'builder_sha256':sha(Path(__file__)),'results':{n:sha(ART/(n+'.json')) for n in records},'completed_episodes':len(episodes),'simulated_hours':warmup+scored,'offline_fit_count':fit_count,'tests':int(summary[1])}
    page.with_suffix('.json').write_text(json.dumps(manifest,indent=2)+'\n');print(page)

if __name__=='__main__':main()
