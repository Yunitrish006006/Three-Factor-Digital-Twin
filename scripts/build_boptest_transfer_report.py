"""Offline report for frozen controller transfer checks."""
import base64
import csv
import html
import json
import os
from pathlib import Path
from run_boptest_transfer import ROOT, ART, sha


def main():
    os.environ.setdefault('MPLCONFIGDIR','/tmp/boptest-matplotlib')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    dev=json.loads((ART/'development.json').read_text())
    t=json.loads((ART/'transfer.json').read_text())
    audit=json.loads((ART/'verification.json').read_text())
    assert audit['transfer_sha256']==sha(ART/'transfer.json')
    selected=audit['selection']
    labels={'v2':'上一版自動 PI','v3_handover':'v3 銜接交接','v4_observer':'v4 交接＋擾動觀測','grid_handover':'9 組搜尋＋相同交接'}

    def table(records):
        body=''
        for r in records:
            m=r['metrics']
            row=[r['day'],r['noise_sd_C'],labels[r['controller']],f"{m['mae_C']:.4f}",f"{m['max_abs_error_C']:.3f}",
                 f"{m['within_0_5_C_pct']:.1f}%",f"{r['initial_30min_mae_C']:.4f}",f"{r['after_30min_mae_C']:.4f}",f"{m['command_total_variation_C']:.1f}"]
            body+='<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in row)+'</tr>'
        return '<div class="scroll"><table><tr><th>日序</th><th>雜訊 σ °C</th><th>控制器</th><th>MAE °C</th><th>最大誤差 °C</th><th>±0.5°C 內</th><th>前 30min MAE</th><th>其後 MAE</th><th>供氣指令總變動 °C</th></tr>'+body+'</table></div>'

    macro={}
    for noise in (0,.05):
        macro[noise]={}
        for name in t['controllers']:
            subset=[r for r in t['records'] if r['noise_sd_C']==noise and r['controller']==name]
            macro[noise][name]=sum(r['metrics']['mae_C'] for r in subset)/len(subset)
    fig,axes=plt.subplots(3,2,figsize=(14,10),constrained_layout=True)
    for ax,(day,noise) in zip(axes.flat,t['cases']):
        for r in t['records']:
            if r['day']!=day or r['noise_sd_C']!=noise:continue
            with (ROOT/r['trace']).open() as f:rows=list(csv.DictReader(f))
            ax.plot([(float(x['time_s'])-day*86400+60)/3600 for x in rows],[float(x['next_T']) for x in rows],label=r['controller'],linewidth=.9)
        ax.axhspan(21.5,22.5,color='green',alpha=.07)
        ax.axhline(22,color='black',linestyle=':',linewidth=.7)
        ax.set(title=f'Day {day}; measurement noise SD {noise} C',xlabel='Hours',ylabel='True temperature [C]')
        ax.legend(fontsize=7)
    plot=ROOT/'docs/reports/boptest_transfer_2026-09-08.png'
    fig.savefig(plot,dpi=130);plt.close(fig)
    image=base64.b64encode(plot.read_bytes()).decode()
    verdict='通過' if audit['protocol_improvement_gate'] else '未通過'
    summary=''.join(f'<tr><td>{"無雜訊，4 個新日期" if noise==0 else "σ=0.05°C，2 個日期"}</td>'+''.join(f'<td>{macro[noise][name]:.4f}</td>' for name in ('v2',selected,'grid_handover'))+'</tr>' for noise in (0,.05))
    sections=[('這輪改善了什麼',f'''<p class="lead">固定候選版本後，在新日期／雜訊共六個情境的改善門檻：<strong>{verdict}</strong>。</p><p>從原本的自動 PI，加入熱輸出銜接與因果擾動觀測。選定版本為 {labels[selected]}，沿用前一輪的 2h 辨識係數，沒有增加校正激勵。</p>
<table><tr><th>新情境</th><th>舊自動 PI MAE</th><th>本輪選定 MAE</th><th>搜尋＋交接 MAE</th></tr>{summary}</table><p>單位 °C。四個乾淨日期與兩個雜訊日期分開平均；同一建築模型與天氣年，不是跨地區實驗。</p>'''),
('算法與比較公平性','''<ol><li><strong>交接</strong>：接手前讀取室溫、供氣溫度與風量，換算固定風量下近似等效的顯熱輸出，避免 PI 從零積分突然接手。</li><li><strong>擾動觀測</strong>：用剛完成的溫度變化，扣除已知致動輸出影響，以 0.2 更新率追蹤剩餘擾動，再補償下一次指令。沒有讀取未來資料。</li><li><strong>控制限制</strong>：每分鐘操作，22°C 目標、供氣 12–40°C、風量 0.5，保留積分防飽和。觀測器沿用辨識得到的致動增益。</li><li><strong>公平基準</strong>：9 組搜尋的 PI 也得到相同的交接改善，不能把通用交接技巧都算成自動辨識的優勢。</li></ol><p>這不是新的神經網路模型，也不是新穎性證明。感測、交接資訊、模型增益及預先設計的規則都有成本；尚未測量人工調參時間。</p>'''),
('開發與新日期分開','''<p>先在已看過的第 3／180 天比較四種版本，按事先寫下的門檻選擇；接著固定程式、參數、協定與資料雜湊，才打開第 35／95／245／305 天。第 95／245 天另加入 σ=0.05°C 的共同高斯量測雜訊。</p><p>所有比較器使用相同初始模擬狀態與相同雜訊序列。控制器看到含雜訊的室溫，評分使用 FMU 真值。每組皆有 24h 暖機，完整 24h 評估包含初始暫態。這輪沒有根據新日期結果再調參。</p><p>選擇門檻：每個開發日的 MAE 不得比 v2 差超過 0.01°C、最大誤差不得差超過 0.1°C，合格者依平均 MAE 選擇。新情境使用同樣非退步界線，且總平均必須改善。</p>'''),
('開發結果：每個候選都保留',table(dev['records'])+'<p>v3 是交接修正的消融比較；v4 另加擾動觀測。搜尋 PI 使用前一輪選好的 Kp=6、Ti=300 秒，本輪沒有重搜。</p>'),
('新日期與雜訊：完整結果',table(t['records'])+'<p>供氣指令總變動量表示動作頻繁程度，不能只看溫度誤差。完整能源分項、飽和比例與 20–30°C 越界筆數保存在 JSON；沒有把不同能源通道直接相加當總效率。</p>'),
('所有新情境的控制軌跡',f'<img alt="True temperature for all six transfer scenarios" src="data:image/png;base64,{image}">'),
('結論界線與下一輪','''<p><strong>保留的難例：</strong>第 245 天乾淨量測的新版本 MAE 仍為 0.2349°C，293 個室溫超過 22.5°C 的分鐘，全部已到最低供氣 12°C。這與目前固定風量／供氣限制下的冷卻能力不足相符，不能只靠增大 PI 增益就假定可解。</p><p><strong>雜訊的代價：</strong>兩個含雜訊情境的平均供氣指令總變動量，舊版為 312.4°C、新版為 508.4°C，搜尋基準為 666.1°C。新版比舊版增加約 62.8%；控溫改善不等於動作更平順，也不能把此指標直接當成磨耗或能源。</p>
<p>這一輪支持的是同一官方 FMU 的日期／季節與量測雜訊檢查，仍是模擬探索，未採納成論文主結論。四個新日期不足以代表所有設備；也沒有驗證感測偏移、控制延遲、設備老化或另一棟建築。</p><p>2h 是方法可用的辨識資料前綴；原研究實際採集了 6h。9 組搜尋的主動試調資料為 54h，並不是最強自動整定方法的普遍成本。暖機、開發和這輪 26 組模擬都是額外開銷。</p><p>下一輪應優先處理雜訊下的指令抖動，再加入致動延遲與跨設備測試，檢查觀測器是否仍穩定，並比較動作變動與能源成本。夜間辨識資料的越界與日照不可辨識限制仍保留；不能直接在運轉中的精密製程做相同激勵。</p>'''),
('證據與授權','''<p><a href="../../openspec/changes/improve-boptest-transfer/artifacts/development.json">開發結果</a> · <a href="../../openspec/changes/improve-boptest-transfer/artifacts/selection.json">開啟新日期前固定的版本</a> · <a href="../../openspec/changes/improve-boptest-transfer/artifacts/transfer.json">新情境結果</a> · <a href="../../openspec/changes/improve-boptest-transfer/evidence.md">研究紀錄</a> · <a href="boptest_rapid_pi_2026-09-08_zh.html">前一輪報告</a></p><p>來源為 BOPTEST v0.9.0 bestest_air 官方 FMU，透過 FMPy 0.3.22 本機執行；沿用前一輪版本、授權與相容函式庫紀錄。不是官方 REST/KPI 等價測試，也不是 EUV、濕度或良率驗證。</p>''')]
    content=''.join(f'<section id="s{i}"><span>{i:02}</span><h2>{title}</h2>{body}</section>' for i,(title,body) in enumerate(sections,1))
    page=ROOT/'docs/reports/boptest_transfer_2026-09-08_zh.html'
    page.write_text('''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BOPTEST 演算法改進與新情境檢查</title><style>body{font:18px/1.75 system-ui;background:#edf2f7;color:#172d3e;margin:0}main{max-width:1250px;margin:auto;padding:30px}h1{font-size:36px}h2{font-size:28px}section{background:white;padding:35px;margin:25px 0;border-radius:15px;min-height:55vh}section>span{float:right;color:#668}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:10px;border-bottom:1px solid #ccd;text-align:left}th{background:#f0f5fa}.scroll{overflow:auto}.lead{font-size:24px}img{width:100%}a{color:#086981}@media print{section{break-before:page;margin:0;min-height:0}body{background:white}main{padding:0}}@media(max-width:600px){main{padding:10px}section{padding:18px}}</style><main><h1>持續改進：從自動 PI 到交接與擾動補償</h1><p>2026-09-08 · 開發候選固定後的新情境檢查 · 模擬探索</p>'''+content+'</main></html>')
    page.with_suffix('.json').write_text(json.dumps({'status':'EXPLORATORY_TRANSFER','sections':len(sections),
        'html_sha256':sha(page),'plot_sha256':sha(plot),'development_sha256':sha(ART/'development.json'),
        'transfer_sha256':sha(ART/'transfer.json'),'macro_mae_C':macro},indent=2)+'\n')
    print(page)


if __name__=='__main__':main()
