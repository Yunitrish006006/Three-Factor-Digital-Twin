"""Offline professor briefing generated from retained development evidence."""
import base64
import csv
import hashlib
import html
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'openspec/changes/pilot-boptest-rapid-pi/artifacts'
REPORT = ROOT / 'docs/reports/boptest_rapid_pi_2026-09-08_zh.html'


def main():
    os.environ.setdefault('MPLCONFIGDIR', '/tmp/boptest-matplotlib')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    v1 = json.loads((ART / 'result.json').read_text())
    v2 = json.loads((ART / 'result_v2.json').read_text())
    assert v1['status'] == v2['status'] == 'COMPLETED_DEVELOPMENT_ONLY'
    records = v1['evaluations'] + v2['evaluations']
    lookup = {(r['day'], r['controller']): r for r in records}
    names = ['fixed_pi', 'grid_pi', 'auto_2h', 'auto_2h_ff', 'auto_6h', 'auto_6h_ff', 'auto_2h_v2', 'embedded']
    labels = {'fixed_pi': '固定 PI', 'grid_pi': '9 組搜尋 PI', 'auto_2h': '2h 自動 PI v1',
              'auto_2h_ff': '2h PI＋環境前饋', 'auto_6h': '6h 自動 PI v1',
              'auto_6h_ff': '6h PI＋環境前饋', 'auto_2h_v2': '2h 自動 PI v2（補強）',
              'embedded': '內建控制器（僅參考）'}
    table = ''
    for name in names:
        a, b = [lookup[(d, name)] for d in (3, 180)]
        values = [labels[name], a['calibration_hours']]
        for r in (a, b):
            m = r['metrics']
            values.extend([f"{m['mae_C']:.4f}", f"{m['max_abs_error_C']:.3f}", f"{m['within_0_5_C_pct']:.1f}%"])
        table += '<tr>' + ''.join('<td>' + html.escape(str(v)) + '</td>' for v in values) + '</tr>'
    fig, axes = plt.subplots(2, 1, figsize=(11, 6), constrained_layout=True)
    for day, ax in zip((3, 180), axes):
        for name in ('fixed_pi', 'grid_pi', 'auto_2h_v2'):
            with (ROOT / lookup[day, name]['trace']).open() as f:
                rows = list(csv.DictReader(f))
            ax.plot([(float(r['time_s']) - day * 86400 + 60)/3600 for r in rows],
                    [float(r['next_T']) for r in rows], label=name, linewidth=1.2)
        ax.axhspan(21.5, 22.5, color='green', alpha=.08)
        ax.axhline(22, color='black', linestyle=':', linewidth=.8)
        ax.set(title=f'Day {day}: development evaluation (60 s sampling)', ylabel='Room temperature [C]', xlabel='Hours')
        ax.legend(ncol=3, fontsize=9)
    figure = ROOT / 'docs/reports/boptest_rapid_pi_2026-09-08.png'
    fig.savefig(figure, dpi=150)
    plt.close(fig)
    img = base64.b64encode(figure.read_bytes()).decode()
    passed = v2['within_exploratory_grid_margin_both_dates']
    verdict = ('兩個日期皆落在本輪事後制定、執行 v2 前寫下的實用差距範圍內。'
               if passed else '尚未在兩個日期都達到本輪探索性的搜尋基準差距門檻。')
    best1, best2 = [lookup[d, 'auto_2h_v2']['metrics']['mae_C'] for d in (3, 180)]
    sections = [
        ('問題與目前結論', f'''<p class="lead">2 小時資料自動整定的補強版，冬／夏日期平均控溫誤差分別為 <strong>{best1:.4f}°C／{best2:.4f}°C</strong>。</p>
<p>{verdict}這是開發可行性結果，<strong>尚未完成論文的調整成本主張</strong>。</p>
<p>問題：換環境後，能否用更少現場辨識與試調，達到足夠好的控溫？本輪先驗證動作確實改變模型中的下一步室溫。</p>'''),
        ('原方法缺口與補強', f'''<ol><li>原有 h=0 空間估測無法直接驗證控制：另加 RC 形式的動態辨識。</li>
<li>增加有輸出限制、積分防飽和的 PI，並依辨識到的時間常數自動算參數。</li>
<li>第一版反應設定過慢：第二版採 λ=max(3Δt, τ/2)，本案為 {v2['response_s']:.0f} 秒；Kp={v2['kp']:.3f}、Ti={v2['ti']:.1f} 秒。</li>
<li>夜間資料無法辨識日照：不啟用這組不完整資料學到的靜態環境前饋。神經網路尚未加入，也没有神經網路增益的證據。</li></ol>'''),
        ('公平條件與資料來源', '''<p>官方 BOPTEST v0.9.0 的 bestest_air 模型；直接以 FMPy 0.3.22 執行 FMI2 Co-Simulation。室溫目標 22°C、每分鐘控制、供氣限制 12–40°C，外接控制器都固定風量 0.5。每組重新建立 FMU，先跑相同 24 小時暖機。</p>
<p>外氣與日照來自模型天氣檔，不是半導體廠資料。第 1 天校正，第 3／180 天各評估 24 小時。內建控制器保留自己的變風量，僅列參考。這不是官方 REST/KPI 完全等價測試。</p>
<p>2h 方法只使用 6h 校正軌跡的前 2h；整輪研究實際跑過完整 6h，另含搜尋、暖機、驗證與失敗重跑。表中列的是各方法可用的主動校正資料／試調時數，不是本研究總工時或人工節省時間。</p>
<p>辨識激勵確實會擾動溫度：前 2h 有 40/120 筆下一步室溫低於原有 20–30°C 範圍；完整 6h 為 159/360 筆。這是另建動態模型的模擬資料，不能聲稱原有估測器已通過此範圍，也不能把這種激勵直接套到運轉中的精密製程。</p>'''),
        ('全部結果，包含負結果', '''<div class="scroll"><table><thead><tr><th rowspan="2">方法</th><th rowspan="2">校正 h</th><th colspan="3">第 3 天</th><th colspan="3">第 180 天</th></tr><tr><th>MAE °C</th><th>最大誤差 °C</th><th>±0.5°C</th><th>MAE °C</th><th>最大誤差 °C</th><th>±0.5°C</th></tr></thead><tbody>''' + table + '''</tbody></table></div>
<p>9 組搜尋：Kp ∈ {0.5, 2, 6}，Ti ∈ {300, 1200, 3600} 秒，每組試 6h。固定 PI 為 Kp=2、Ti=1200 秒；0h 代表預先指定參數，不能解讀成沒有專家知識成本。</p>
<p>環境前饋在夏季反而退步；更長的校正也未必更好。兩者都保留，不能挑最好的一列當結論。</p>'''),
        ('閉迴路溫度軌跡', f'<img alt="Two development dates with fixed, grid and automatic PI temperature trajectories" src="data:image/png;base64,{img}"><p>綠色帶為目標 ±0.5°C。全時段都計分，沒有刪除啟動暫態。數據為理想化建築模型；不能用小數位數推論真實感測精度。</p>'),
        ('能主張什麼、還缺什麼', '''<p>可以說：已建立可重現的動態辨識與控制閉迴路，並找出環境補償的資料不足問題。不能說：已證明無需人工調參、比所有自動整定法好、首次提出環境 PID，或可控制 EUV 製程。</p>
<p>v2 看過 v1 結果後才修改，重用相同評估日期。它是開發改進，不是獨立確認。新增的探索門檻是 MAE 不超過搜尋基準 +0.05°C、最大誤差不超過 +0.5°C，不能事後當作預註冊論文成功標準。</p>
<p>下一個正式實驗應固定算法，再加入多設備／多季節、相同試調預算的強基準、感測雜訊與致動延遲，最後以未使用情境確認。這一輪沒有濕度、良率或真人調參工時；原有 20–30°C 空間估測範圍也未擴張。</p>'''),
        ('證據與重現', '''<p><a href="../../openspec/changes/pilot-boptest-rapid-pi/artifacts/result.json">v1 完整結果</a> · <a href="../../openspec/changes/pilot-boptest-rapid-pi/artifacts/result_v2.json">v2 完整結果</a> · <a href="../../openspec/changes/pilot-boptest-rapid-pi/evidence.md">研究紀錄</a></p>
<p><a href="https://github.com/ibpsa/project1-boptest/tree/v0.9.0">BOPTEST 原始碼與授權</a> · <a href="https://github.com/CATIA-Systems/FMPy/tree/v0.3.22">FMPy</a></p>
<p>所有分項能源、越界筆數、飽和比例、矩陣秩、係數、每分鐘 CSV 與 SHA-256 都保留。暖機與辨識成本分開。未更動既有 E15 確認資料，也未把探索結果升格到論文主結論。</p>''')]
    content = ''.join(f'<section id="s{i}"><span class="number">{i:02}</span><h2>{title}</h2>{body}</section>'
                      for i, (title, body) in enumerate(sections, 1))
    nav = ''.join(f'<a href="#s{i}">{i}</a>' for i in range(1, len(sections)+1))
    REPORT.write_text('''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BOPTEST 快速整定 PI｜教授報告</title><style>
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#edf2f7;color:#142739;font:19px/1.75 system-ui,sans-serif}main{max-width:1200px;margin:auto;padding:40px 22px}h1{font-size:40px;line-height:1.3}h2{font-size:30px;margin-top:0}.lead{font-size:25px}section{min-height:70vh;background:white;padding:42px;margin:30px 0;border-radius:18px;box-shadow:0 8px 30px #1231;scroll-margin-top:50px}.number{float:right;color:#8aa0b2;font-weight:700}nav{position:sticky;top:0;background:#142739;padding:8px;text-align:center;z-index:1}nav a{color:white;text-decoration:none;padding:5px 18px}table{border-collapse:collapse;font-size:15px;width:100%}th,td{padding:10px;text-align:left;border-bottom:1px solid #d7e0e7}th{background:#edf5fa}.scroll{overflow:auto}img{width:100%}a{color:#056b8e}@media(max-width:650px){section{padding:22px}body{font-size:17px}h1{font-size:30px}nav a{padding:5px 12px}}@media print{nav{display:none}section{box-shadow:none;break-before:page;min-height:0;margin:0}body{background:white}main{padding:0}}</style>
<nav aria-label="報告章節">''' + nav + '''</nav><main><h1>用更少的調整時間，達到足夠好的控溫</h1><p>2026-09-08 · 第一輪開發試驗 · 官方 BOPTEST 模型，非半導體實機</p>''' + content + '''</main><script>document.addEventListener('keydown',e=>{if(!['ArrowRight','ArrowLeft','PageDown','PageUp'].includes(e.key))return;e.preventDefault();const a=[...document.querySelectorAll('section')];let i=a.reduce((best,s,j)=>Math.abs(s.getBoundingClientRect().top-50)<Math.abs(a[best].getBoundingClientRect().top-50)?j:best,0);i=Math.max(0,Math.min(a.length-1,i+(['ArrowRight','PageDown'].includes(e.key)?1:-1)));a[i].scrollIntoView();});</script></html>''')
    def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
    REPORT.with_suffix('.json').write_text(json.dumps({'status':'DEVELOPMENT_ONLY', 'sections':len(sections),
        'v1_sha256':sha(ART/'result.json'),'v2_sha256':sha(ART/'result_v2.json'),
        'html_sha256':sha(REPORT),'plot_sha256':sha(figure)},indent=2)+'\n')
    print(REPORT)


if __name__ == '__main__':
    main()
