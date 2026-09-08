"""Build offline exploratory report from frozen delayed-model experiment artifacts."""
import base64
import csv
import hashlib
import html
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'openspec/changes/improve-portable-dynamics/artifacts'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def table(headers, rows):
    return '<div class="scroll"><table><tr>' + ''.join('<th>'+html.escape(str(x))+'</th>' for x in headers) + '</tr>' + ''.join('<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in row)+'</tr>' for row in rows) + '</table></div>'

def main():
    os.environ.setdefault('MPLCONFIGDIR', '/tmp/boptest-matplotlib')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    records = {n: json.loads((ART / (n+'.json')).read_text()) for n in ('air','hydronic')}
    audit = json.loads((ART / 'verification.json').read_text())
    assert audit['status'] == 'PASS' and audit['sources_match']
    rows, models = [], []
    fig, axes = plt.subplots(4, 2, figsize=(12, 12), constrained_layout=True)
    for pi, (plant, r) in enumerate(records.items()):
        for hi, h in enumerate((2, 6)):
            b = r['banks'][str(h)]; m = b['selected']
            models.append([plant,h,m['order'],m['delay_steps'],f"{m['validation_rollout_rmse_C']:.4f}",b['offline_fit_count']])
            for di, day in enumerate((20,50)):
                ax=axes[pi*2+hi,di]
                pair={e['method']: e for e in r['evaluations'] if e['day']==day and e['budget_h']==h}
                for method, e in pair.items():
                    with (ROOT/e['trace']).open() as f: data=list(csv.DictReader(f))
                    t0=float(data[0]['time_s'])-60
                    ax.plot([(float(v['time_s'])-t0)/3600 for v in data], [float(v['T']) for v in data],label=method,linewidth=1.2)
                ax.axhline(22,color='black',ls='--',lw=.7)
                ax.set(title=f'{plant} | ID {h}h | day {day}',xlabel='Evaluation hours',ylabel='Temperature [C]',xlim=(0,24));ax.legend(fontsize=8)
                a,p=pair['auto_pi']['metrics'],pair['proposed']['metrics']
                rows.append([plant,h,day,f"{a['mae_C']:.4f}",f"{p['mae_C']:.4f}",f"{a['max_abs_error_C']:.4f}",f"{p['max_abs_error_C']:.4f}",'改善' if p['mae_C']<a['mae_C'] else '退步'])
    page=ROOT/'docs/reports/boptest_delayed_dynamics_2026-09-08_zh.html'
    plot=page.with_suffix('.png');fig.savefig(plot,dpi=140);plt.close(fig)
    fits=sum(b['offline_fit_count'] for r in records.values() for b in r['banks'].values())
    fit_seconds=sum(b['fit_wall_seconds'] for r in records.values() for b in r['banks'].values())
    run_seconds=sum(e['wall_seconds'] for r in records.values() for e in r['trials']+r['evaluations'])
    sections=[('辨識突破，控制改善仍有例外','<p class="lead">同一套模型選擇流程已讓送風與水暖的 2h／6h 資料全部通過辨識。但水暖 6h 的本方法在兩個日期都未勝過相同預算的 auto-PI，因此尚未達到穩定跨場景改善的目標。</p><p>32 次新增模擬全部完成；原本的一階模型拒絕結果完整保留。這是獨立探索報告，尚未採納為論文主線確認成果。</p>'),
    ('共用流程如何適應設備','<p>每組資料都比較同一個模型庫：一階／二階 × 0、1、3、5、10 分鐘輸入延遲，共 10 個候選。前 70% 可用端點訓練，後段以不重疊 10 分鐘自由推演評分；不逐步餵入真實室溫，室外溫度固定為每段起點可見值。最後不足 10 分鐘的尾段不評分。</p><p>依推演 RMSE 排序後，用完整資料前綴重新擬合，必須再次通過穩定極點、正致動增益檢查。沒有手動修係數或水暖專用控制分支。ARX 模型用於估算 PI 增益與時間尺度；不是完整狀態預測控制，也不是物理參數的唯一真值。</p><p>兩方法共用辨識與 q∈{0.5,1}，各做兩次 2h 試調再選取；這輪所有 q 都自動選 0.5。本方法額外沿用觀測率 0.2、平滑 0.35、回算 0.1，並使用歷史實際指令處理辨識延遲。這些共用常數尚未證明普遍最佳。</p>'),
    ('自動選到的模型',table(['設備','辨識h','階數','延遲min','校正分段推演RMSE °C','含重擬合次數'],models)+'<p>這裡的推演分數屬於校正資料內的模型選擇，不能當成獨立控制驗證分數；不同資料預算也有不同的驗證區段。</p>'),
    ('全部 16 次新日期控制結果',table(['設備','辨識h','日序','auto-PI MAE °C','本方法 MAE °C','auto-PI最大誤差 °C','本方法最大誤差 °C','MAE判讀'],rows)+'<p>相同目標 22°C、60 秒採樣、24h 暖機與 24h 評估。送風量空氣溫度，水暖量作用溫度；只在設備內比較，不混成總 MAE。模型與試調選擇均在開啟第 20／50 天結果前固定。</p><p>預先門檻：每個日期 MAE 不高於基準 +0.02°C、最大誤差不高於 +0.2°C，且平均 MAE 有改善。送風 2h／6h、水暖 2h 通過；水暖 6h 未通過。這不是多次隨機重複試驗，沒有統計顯著性結論。</p>'),
    ('完整日軌跡', '<img alt="All eight paired 24-hour temperature comparisons" src="data:image/png;base64,'+base64.b64encode(plot.read_bytes()).decode()+'"><p>水暖 6h 的本方法比自身 2h 結果更準，但 auto-PI 受益更多。不能解讀成資料增加本身使控制變差；目前問題是額外補償未持續提供增益。</p>'),
    ('少資料與調整成本',f'<p>沿用上一輪兩條 6h 校正軌跡，沒有新增激勵資料。每方法主動適應預算為 2h＋4h＝6h，或 6h＋4h＝10h；不能只報辨識時間。</p><p>本輪共 {fits} 次離線擬合，記錄的擬合耗時合計 {fit_seconds:.3f} 秒；16 次試調＋16 次評估，記錄的 FMU 回合執行耗時合計 {run_seconds:.1f} 秒（回合耗時加總，不是整個研究牆鐘工時）。新增模擬時間合計 1184h：768h 暖機、32h 試調、384h 評估。</p><p>目前支持有限資料下的可行性，尚未以人工整定工時或同品質所需總時間作公平對照，不能宣稱已證明節省人工成本。</p>'),
    ('可以主張與尚待驗證','<p>兩個設備都已參與開發，新的日期只是設備內檢查，不是未見設備的泛化證據。它們同屬 HVAC；仍需凍結下一版後，用未參與開發的設備確認。下一個候選改進是共用、有限預算的補償強度／啟用選擇，必須先訂規則，不能看到測試結果後替某設備手動關閉。</p><p>本輪未證明神經網路效益、濕度控制、EUV 適用性或實機安全性。水暖只有供暖能力。本機使用官方 BOPTEST v0.9.0 FMU 與 FMPy 0.3.22 自訂 runner，未宣稱等同官方 REST／KPI 流程；資料與模型沿用前輪授權追溯。</p>'),
    ('驗證與可追溯證據','<p>250 項單元測試通過（282.204 秒）；32 條新軌跡、來源雜湊、模型重擬合與指標核對通過。</p><p><a href="../../openspec/changes/improve-portable-dynamics/evidence.md">完整研究紀錄</a> · <a href="../../openspec/changes/improve-portable-dynamics/artifacts/freeze.json">凍結來源</a> · <a href="../../openspec/changes/improve-portable-dynamics/artifacts/air.json">送風原始結果</a> · <a href="../../openspec/changes/improve-portable-dynamics/artifacts/hydronic.json">水暖原始結果</a> · <a href="../../openspec/changes/improve-portable-dynamics/artifacts/verification.json">驗證結果</a></p>')]
    body=''.join(f'<section><small>{i:02}</small><h2>{title}</h2>{text}</section>' for i,(title,text) in enumerate(sections,1))
    page.write_text('''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>共用動態辨識：送風與水暖</title><style>body{font:18px/1.8 system-ui;background:#eef3f6;color:#193548;margin:0}main{max-width:1200px;margin:auto;padding:28px}section{background:white;padding:30px;margin:24px 0;border-radius:14px}h1{font-size:36px}h2{font-size:27px}.lead{font-size:24px}small{float:right;color:#678}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:9px;border-bottom:1px solid #ccd;text-align:left}th{background:#eef5f7}.scroll{overflow:auto}img{width:100%}a{color:#006e85}@media print{section{break-before:page}body{background:white}}@media(max-width:600px){main{padding:10px}section{padding:15px}}</style><main><h1>少資料控溫：共用延遲／二階模型</h1><p>2026-09-08 · 教授報告 · 開發探索，尚未採納為論文確認成果</p>'''+body+'</main></html>')
    page.with_suffix('.json').write_text(json.dumps({'status':'IDENTIFICATION_RECOVERED_CONTROL_MIXED','html_sha256':sha(page),'plot_sha256':sha(plot),'builder_sha256':sha(Path(__file__)),'results':{n:sha(ART/(n+'.json')) for n in records},'offline_fit_count':fits,'offline_fit_seconds':fit_seconds,'aggregate_run_wall_seconds':run_seconds},indent=2)+'\n')
    print(page)

if __name__=='__main__':
    main()
