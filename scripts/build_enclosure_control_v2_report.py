#!/usr/bin/env python3
"""Build an offline first-person research report from completed v2 artifacts."""
import argparse
import io
import json
from html import escape
from pathlib import Path

from enclosure_control_v2_summary import (
    ROOT, ARTIFACTS, TITLE, METHODS, LABELS, SPLITS, summary,
)

OUTPUT = ROOT / 'docs/reports/enclosure_control_v2_2026-10-05_zh.html'


def number(value, digits=4):
    return '未達／未提供' if value is None else f'{value:.{digits}f}'


def scientific_chart(result):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    labels = ['Fixed', 'PID + FF', 'LQR', 'MPC']
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.7), layout='constrained')
    colors = ['#667085', '#207966', '#9d6418', '#295ac7']
    hold = result['aggregates']['holdout']
    for ax, metric, title, unit in zip(axes,
            ('tracking_mae_C', 'fan_energy_proxy_Wh'),
            ('Synthetic holdout: tracking error', 'Synthetic holdout: fan-energy proxy'),
            ('MAE (degrees C)', 'Assumed energy (Wh)')):
        values = [hold[m][metric] for m in METHODS]
        bars = ax.bar(labels, values, color=colors, width=.65)
        ax.bar_label(bars, fmt='%.3f', padding=3, fontsize=9)
        for i, method in enumerate(METHODS):
            points = [r['metrics'][metric] for r in result['runs']
                      if r['split'] == 'holdout' and r['method'] == method]
            ax.scatter(np.linspace(i-.1, i+.1, len(points)), points, color='black', s=14, zorder=3)
        ax.set(title=title, ylabel=unit, ylim=(0, max(values)*1.25))
        ax.spines[['top', 'right']].set_visible(False)
        ax.grid(axis='y', alpha=.18)
        ax.set_axisbelow(True)
    stream = io.StringIO()
    fig.savefig(stream, format='svg', metadata={'Date': None})
    plt.close(fig)
    svg = stream.getvalue()
    return '\n'.join(line.rstrip() for line in svg[svg.index('<svg'):].splitlines()) + '\n'


def build():
    data = summary()
    if data is None:
        raise FileNotFoundError('No completed v2 result; no report was produced')
    result = data['result']
    freeze = json.loads((ARTIFACTS / 'freeze.json').read_text())
    selected = freeze.get('selected', {})
    selected_rows = ''.join('<tr><td>' + escape(LABELS[m]) + '</td><td><code>' +
        escape(json.dumps(selected.get(m), ensure_ascii=False)) + '</code></td></tr>' for m in METHODS)
    aggregate_rows = ''
    for split in SPLITS:
        for method in METHODS:
            a = result['aggregates'][split][method]
            values = [split, LABELS[method], number(a['tracking_mae_C']),
                      number(a['tracking_rmse_C']), number(a['overtemp_s'], 1),
                      number(a['fan_energy_proxy_Wh']), number(a['pwm_total_variation'], 3),
                      number(a['fallback_n'], 2)]
            aggregate_rows += '<tr>' + ''.join('<td>'+escape(v)+'</td>' for v in values) + '</tr>'
    per_run_rows = ''
    for run in result['runs']:
        a = run['metrics']
        values = [run['id'], number(a['tracking_mae_C']),
                  number(a['prediction_mae_C']), number(a['max_cpu_C'], 2)+'/'+number(a['max_gpu_C'], 2),
                  number(a['overtemp_s'], 0), number(a['fan_energy_proxy_Wh']),
                  number(a['fallback_n'], 0), number(a.get('safety_override_n'), 0),
                  number(a.get('total_p95_s', a.get('control_p95_s', a.get('solve_p95_s'))), 6),
                  number(a.get('band_entry_60s_s'), 0)]
        per_run_rows += '<tr>' + ''.join('<td>'+escape(v)+'</td>' for v in values) + '</tr>'
    decision_rows = ''.join('<tr><th>'+escape(str(k))+'</th><td>'+escape(str(v))+'</td></tr>'
                            for k, v in result['decisions'].items())
    markers = {}
    for path in sorted(ARTIFACTS.glob('*.json')):
        if any(word in path.stem for word in ('attempt', 'receipt', 'marker')):
            markers[path.name] = json.loads(path.read_text())
    marker_text = (json.dumps(markers, ensure_ascii=False, indent=2) if markers else
                   '未找到 attempt／receipt／marker；凍結及防覆寫狀態不能由報告自行宣稱通過。')
    verification = ARTIFACTS / 'verification.json'
    audit_text = json.dumps(json.loads(verification.read_text()), ensure_ascii=False, indent=2) if verification.exists() else '獨立驗證產物尚未提供。'
    chart = scientific_chart(result)
    chart_path = ROOT / 'docs/reports/assets/enclosure_control_v2_holdout.svg'
    chart_path.parent.mkdir(parents=True, exist_ok=True)
    chart_path.write_text(chart)
    prefix = '../../openspec/changes/validate-enclosure-four-controllers-20261005/'
    html = f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{TITLE}｜2026-10-05</title><style>
:root{{font-family:system-ui,-apple-system,"Noto Sans TC",sans-serif;color:#17233a;background:#eff3f7;line-height:1.75}}
*{{box-sizing:border-box}}body{{margin:0}}main{{max-width:1120px;margin:auto;padding:28px 20px 60px}}
header,section{{background:white;border:1px solid #d9e1eb;border-radius:15px;padding:24px;margin-bottom:20px}}
h1{{font-size:clamp(1.65rem,4vw,2.4rem);line-height:1.35}}h2{{font-size:1.4rem}}h3{{font-size:1.1rem}}
.eyebrow{{color:#37619d;font-weight:700}}.lead{{font-size:1.12rem}}nav{{display:flex;flex-wrap:wrap;gap:10px 20px}}
a{{color:#2457a5;text-underline-offset:3px}}.scroll{{max-width:100%;overflow-x:auto}}table{{border-collapse:collapse;width:100%;font-size:.9rem}}
th,td{{padding:10px;border-bottom:1px solid #dfe6ef;text-align:left;vertical-align:top}}th{{background:#edf2f9;white-space:nowrap}}
pre{{white-space:pre-wrap;overflow-wrap:anywhere;background:#f3f6fa;padding:16px;font-size:.82rem}}
code{{overflow-wrap:anywhere}}figure{{margin:20px 0}}figure svg{{display:block;width:100%;height:auto}}figcaption,.note{{color:#526176;font-size:.92rem}}
.callout{{border-left:4px solid #37619d;background:#eff5fd;padding:14px 18px}}summary{{cursor:pointer;font-weight:700;padding:10px 0}}
@media(max-width:600px){{main{{padding:14px 10px}}header,section{{padding:18px 14px}}td,th{{padding:8px}}}}
@media print{{body{{background:white}}main{{max-width:none;padding:0}}header,section{{border:0;padding:8px 0}}nav{{display:none}}.scroll{{overflow:visible}}table{{font-size:7pt}}h2{{break-after:avoid}}}}
</style></head><body><main><header><p class="eyebrow">探索性假設模型研究 · 第二階段</p>
<h1>我把 LQR 納入機箱風扇控制的四方法比較</h1>
<p class="lead">我想確認有限的調參預算下，較複雜的控制器能帶來哪些追蹤改善，又付出多少風扇能耗、動作變化與計算代價。</p>
<p>報告整理日期：2026-10-05；結果產生時間：{escape(str(result.get('evaluated_at', '結果檔未記錄')))}。本頁不代表已向教授口頭報告。</p>
<nav><a href="#question">問題與方法</a><a href="#results">實際結果</a><a href="#limits">限制與下一步</a><a href="#script">口頭講稿</a><a href="#sources">來源</a></nav></header>
<section id="question"><h2>我遇到什麼問題，如何修正比較</h2>
<p>第一階段的 MPC 在假設模型下改善追蹤，但候選數不同、PID 沒有負載前饋，而且過載時數值求解常回退。我因此把第二階段固定為四方法、每方法三候選乘三個 calibration seeds，先選參再凍結。這讓候選評估回合相同，仍不代表 CPU 計算時間相同。</p>
<p>我採用固定風扇、PID 加平衡點前饋、經限制的 LQR 與受限制 MPC。CPU 和 GPU 共用一個風扇，兩個 60°C 目標通常無法同時成為平衡点。我先分配可達平衡點，再以離散 Riccati 方程求 LQR 增益；限制 PWM 和每步變化後，不宣稱仍有原始 LQR 的全域最優或穩定保證。</p>
<p>我查到 OSQP 的 MPC 範例與 SciPy 的離散 Riccati 方程文件，將 MPC 改成明確的二次規劃，並檢查殘差與回退。求解器是否正常與風扇是否足夠散熱，是分開的研究問題。方法方程是自行數學化整理，沒有借用文獻公式編號。</p>
<div class="scroll"><table><thead><tr><th>方法</th><th>僅依 calibration 選出的參數</th></tr></thead><tbody>{selected_rows}</tbody></table></div>
<p class="note">舊 v1 holdout 已開啟，只保留歷史比較；本輪使用新的合成 seeds。假設模型變體只作指定條件壓力測試。</p></section>
<section id="results"><h2>我實際得到的結果</h2><p>{escape(data['text'])}</p>
<figure>{chart}<figcaption>柱為三 seed 等權平均，黑點為每個 seed。追蹤 MAE 與能耗 proxy 必須分開解讀；圖中沒有實體量測或推論統計信賴區間。</figcaption></figure>
<div class="scroll"><table><thead><tr><th>切分</th><th>方法</th><th>MAE °C</th><th>RMSE °C</th><th>取樣超溫 s</th><th>風扇 proxy Wh</th><th>PWM TV</th><th>回退步／回合</th></tr></thead><tbody>{aggregate_rows}</tbody></table></div>
<h3>預先固定的研究判準</h3><p>H-CTRL-01 檢查四方法數值健康與命令限制，包含過載；H-CTRL-02／03 分別檢查 MPC 相對 PID＋前饋／LQR 的 holdout MAE 是否至少降低 5%，且逐 seed 取樣超溫不增加。不通過也保留結論。</p>
<div class="scroll"><table><tbody>{decision_rows}</tbody></table></div>
<details><summary>全部 {data['run_count']} 回合：溫度、數值健康與控制時間</summary><div class="scroll"><table><thead><tr><th>回合</th><th>tracking MAE °C</th><th>prediction MAE °C</th><th>peak CPU/GPU °C</th><th>超溫 s</th><th>proxy Wh</th><th>回退步</th><th>安全覆寫步</th><th>控制 p95 s</th><th>首次60s誤差帶 s</th></tr></thead><tbody>{per_run_rows}</tbody></table></div><p>此欄是首次連續 60 秒雙節點都落在目標 ±2°C 的時刻；未達不當成零。預測誤差與控制追蹤誤差是不同量。</p></details></section>
<section id="limits"><h2>我目前能支持的範圍</h2><p>{escape(data['boundary'])}</p><p>{escape(data['overload'])}</p>
<p>我接下來需要獨立辨識資料、感測與負載量測誤差評估，以及具備硬體和介面後的實體介入 protocol。改求解器或增加基準方法都不能把既有結果重新包裝成未見確認。</p></section>
<section id="script"><h2>我準備向教授說明的重點</h2><p>我先把機箱問題縮成 CPU、GPU 和風扇延遲的假設模型。這次我把 LQR 加入，並讓 PID 也使用相同模型的平衡點前饋。四方法的選參只看 calibration，之後才開新的合成測試。</p><p>{escape(data['text'])}</p>
<p>我的判讀會同時看溫度、超溫、風扇能耗 proxy 和求解回退。即使演算法每一步都正常求解，過載仍可能超過風扇能力。我現在能交代的是假設模型內的比較；實體機箱和感測器驗證還需要另外執行。</p>
<h3>我想請教授討論</h3><p>下一階段是否優先補獨立熱模型辨識和量測誤差，再決定這些模型式控制器是否值得進行實體測試？</p></section>
<section id="sources"><h2>研究來源與完整證據</h2><p><a href="https://osqp.org/docs/examples/mpc.html">OSQP MPC 範例</a> · <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.solve_discrete_are.html">SciPy 離散 Riccati 方程</a> · <a href="enclosure_mpc_2026-10-05_zh.html">第一階段歷史報告</a></p>
<p><a href="{prefix}protocol.md">v2 protocol</a> · <a href="{prefix}config.json">固定設定</a> · <a href="{prefix}artifacts/freeze.json">freeze</a> · <a href="{prefix}artifacts/result.json">完整結果</a> · <a href="{prefix}artifacts/verification.json">獨立核對</a></p>
<details><summary>來源凍結、執行防覆寫與核對紀錄</summary><h3>Attempt markers</h3><pre>{escape(marker_text)}</pre><h3>獨立核對</h3><pre>{escape(audit_text)}</pre></details>
<p class="note">本頁生成不等於文件排版已審查。Office 輸出的逐頁視覺 QA 應以同步驗證紀錄為準，不能由生成器自行標記完成。</p></section></main></body></html>'''
    OUTPUT.write_text(html)
    return OUTPUT


if __name__ == '__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    print(build())
