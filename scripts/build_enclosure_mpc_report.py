#!/usr/bin/env python3
"""Offline report and standalone scientific plot from actual frozen results."""
import base64
import csv
from html import escape
import json
from pathlib import Path

from enclosure_mpc_summary import ARTIFACTS, ROOT, summary


def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    data=summary();r=data['result'];hold=r['aggregates']['holdout']
    figure,axes=plt.subplots(3,1,figsize=(10,8),sharex=True,layout='constrained')
    for method in ('fixed','pid','mpc'):
        record=next(x for x in r['runs'] if x['split']=='holdout' and x['seed']==31 and x['method']==method)
        with (ARTIFACTS/record['trace_path']).open() as f:
            rows=list(csv.DictReader(f))
        t=[(float(x['time_s'])+10)/60 for x in rows]
        for ax,key in zip(axes,['next_cpu_C','next_gpu_C','pwm']):
            ax.plot(t,[float(x[key]) for x in rows],label=method.upper(),linewidth=1.7)
    for ax,label in zip(axes,['CPU temperature (C)','GPU temperature (C)','PWM fraction']):
        ax.set_ylabel(label);ax.grid(alpha=.2);ax.legend(ncol=3,loc='upper right')
    axes[0].axhline(60,color='gray',linestyle='--',alpha=.7)
    axes[1].axhline(60,color='gray',linestyle='--',alpha=.7)
    axes[2].set_xlabel('Time (min)');figure.suptitle('Assumed enclosure model | Holdout seed 31')
    plot=ROOT/'docs/reports/assets/enclosure_mpc_2026-10-05.png';plot.parent.mkdir(exist_ok=True)
    figure.savefig(plot,dpi=160);plt.close(figure)
    image=base64.b64encode(plot.read_bytes()).decode()
    table=''
    for split in ('validation','holdout','mismatch','overload'):
        for method,m in r['aggregates'][split].items():
            table+=f"<tr><td>{split}</td><td>{method.upper()}</td><td>{m['tracking_mae_C']:.4f}</td><td>{m['tracking_rmse_C']:.4f}</td><td>{m['overtemp_s']:.1f}</td><td>{m['fan_energy_proxy_Wh']:.4f}</td><td>{m['pwm_total_variation']:.3f}</td><td>{m['fallback_n']:.2f}</td></tr>"
    full=''
    for run in r['runs']:
        m=run['metrics'];settle=m['settling_time_s']
        full+=f"<tr><td>{escape(run['id'])}</td><td>{m['tracking_mae_C']:.4f}</td><td>{m['prediction_mae_C']:.4f}</td><td>{m['max_cpu_C']:.2f}/{m['max_gpu_C']:.2f}</td><td>{m['overtemp_s']:.0f}</td><td>{m['fallback_n']}</td><td>{m['slack_max_C']:.3f}</td><td>{m['solve_p95_s']*1000:.2f}</td><td>{settle if settle is not None else '未達'}</td></tr>"
    html=f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>機箱 MPC 執行計劃與模擬結果</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#f4f6f8;color:#203047;font:17px/1.8 system-ui,sans-serif}}main{{max-width:1120px;margin:auto;padding:36px 24px}}header,section{{background:white;padding:28px;margin:22px 0;border-radius:12px}}h1{{font-size:clamp(27px,4vw,40px);line-height:1.3}}h2{{font-size:25px}}nav{{display:flex;gap:16px;flex-wrap:wrap}}a{{color:#076579;overflow-wrap:anywhere}}.lead{{font-size:21px}}.notice{{border-left:4px solid #ad6330;padding:14px 18px;background:#fff5e9}}.scroll{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{padding:10px;text-align:left;border-bottom:1px solid #d9e0e8;white-space:nowrap}}th{{background:#edf3f6}}img{{width:100%;height:auto}}pre{{overflow:auto;background:#f2f5f7;padding:16px;font-size:14px}}summary{{cursor:pointer;font-weight:600;padding:12px 0}}.meta{{color:#536679}}@media(max-width:600px){{main{{padding:10px}}header,section{{padding:18px}}.lead{{font-size:19px}}}}@media print{{body{{background:white}}header,section{{break-inside:avoid}}.scroll{{overflow:visible}}table{{font-size:9px}}th,td{{padding:5px;white-space:normal}}}}
</style></head><body><main><header><p class="meta">2026-10-05 執行與整理 · 桌機機箱探索性模擬</p><h1>機箱 MPC 執行計劃與模擬結果</h1><p class="lead">我完成了受限制 MPC 的第一階段，並用鎖定的控制器比較固定風扇與 PID。</p><p>在三個保留 seed 中，MPC 的平均追蹤誤差為 {hold['mpc']['tracking_mae_C']:.3f}°C，PID 為 {hold['pid']['tracking_mae_C']:.3f}°C。MPC 使用更多風扇能耗 proxy，也產生更多 PWM 變化。</p><p class="notice">這些結果來自事前假設的熱模型與合成負載。實體機箱、NTC、整機功耗、throttling 與 E8 尚未評估；過載測試仍出現超溫與求解回退。</p><nav><a href="#plan">執行計劃</a><a href="#method">方法與限制</a><a href="#results">完整結果</a><a href="#limits">問題與下一步</a><a href="#sources">來源</a></nav></header>
<section id="plan"><h2>我的執行計劃</h2><div class="scroll"><table><thead><tr><th>順序</th><th>工作</th><th>狀態</th></tr></thead><tbody><tr><td>1</td><td>方法來源、模型假設與研究規格</td><td>完成</td></tr><tr><td>2</td><td>CPU/GPU 熱模型與可重設模擬</td><td>完成</td></tr><tr><td>3</td><td>受限制 MPC 與回退機制</td><td>完成</td></tr><tr><td>4</td><td>calibration 搜尋、鎖定與公平基準</td><td>完成</td></tr><tr><td>5</td><td>36 回合與原始軌跡核對</td><td>完成</td></tr><tr><td>6</td><td>報告與論文同步</td><td>見執行紀錄</td></tr><tr><td>下一階段</td><td>LQR 與四方法統一比較</td><td>TODO</td></tr></tbody></table></div><p><a href="../research/mpc_execution_plan_2026-10-05_zh.md">完整計劃表與完成條件</a></p></section>
<section id="method"><h2>我選擇的 MPC 方法</h2><p>我查到官方 MPC 範例採用有限 horizon、狀態與輸入限制，並只執行最佳序列的第一動作。我將此流程接到 CPU、GPU、風扇三個狀態的假設熱模型，用 SciPy SLSQP 求解。每個控制步長 10 秒，預測 12 步，共 120 秒。</p><p>CPU/GPU 目標為 60°C，溫度上限為 80/85°C。PWM 20–100%，每步最多改變 10 百分點。風扇有 20 秒延遲，RPM 與 PWM 分開記錄。控制器只能看當下功率與入口溫度，沒有未來負載真值。</p><p>我把溫度設成有 slack 的軟限制，將 PWM 与變化率設成硬限制。求解失敗時漸增到最大風扇；所有方法在警告溫度都有相同的安全覆寫。這個機制仍無法讓過載設備保持安全。</p><details><summary>模型與成本函數</summary><pre>C_i * dT_i/dt = P_i - (G_i + k_f_i*f)*(T_i-T_in)
tau_f * df/dt = u - f
J = sum(((T-target)/5)^2) + R_u*sum(u^2)
    + 5*sum(delta_u^2) + 10000*sum(slack^2)</pre><p>上述方程是我依流程自行數學化整理，模型參數沒有實機辨識。CPU/GPU 的高溫節點也與原室內估測域分開。</p></details><p>我只在 calibration 的 seeds 11/12/13 比較 4 個 fixed、18 個 PID、3 個 MPC 候選，選完才凍結。validation 用 seeds 21/22/23，holdout 用 31/32/33。stress 41/42/43 另測模型失配與過載，沒有回頭調參。</p></section>
<section id="results"><h2>我得到的結果</h2><p>{escape(data['text'])}</p><img src="data:image/png;base64,{image}" alt="保留 seed 31 的 CPU、GPU 溫度與 PWM 時序，三方法使用相同負載"><p class="meta">圖示單一 holdout seed；下表為每一 split 的三 seed macro mean。每回合 20 分鐘，不去除初始過渡。風扇 Wh 為假設的 10u³ W 模型。</p><div class="scroll"><table><thead><tr><th>split</th><th>方法</th><th>追蹤 MAE °C</th><th>RMSE °C</th><th>超溫 s</th><th>風扇 proxy Wh</th><th>PWM TV</th><th>回退步數</th></tr></thead><tbody>{table}</tbody></table></div><details><summary>全部 36 回合與失敗紀錄</summary><div class="scroll"><table><thead><tr><th>回合</th><th>追蹤 MAE °C</th><th>一步預測 MAE °C</th><th>CPU/GPU peak °C</th><th>超溫 s</th><th>回退步</th><th>slack °C</th><th>p95 ms</th><th>settling s</th></tr></thead><tbody>{full}</tbody></table></div><p>settling 是首次連續 60 秒兩节点均進入目標 ±2°C 的時間，沒有達成顯示未達。預測誤差與追蹤誤差是不同問題。</p></details></section>
<section id="limits"><h2>我遇到的問題與下一步</h2><p>{escape(data['boundary'])}</p><p>原本研究環境綁定的 Xcode Python 無法啟動，我建立另外的固定套件環境。舊調參的 OpenSpec 缺設計與 delta specs，我依既有產物補齊；沒有重新消耗 E15。</p><p>正常負載下，MPC 通過預定模擬可行性與相對 PID 追蹤改善判準。過載時的 SLSQP 不一定收斂，且最大風扇也無法消除超溫。後續需要獨立模型／實測校準、有限預算的 LQR 與前饋 PID 比較，再判斷是否有硬體試驗價值。</p></section>
<section id="sources"><h2>來源與可重現產物</h2><p><a href="https://osqp.org/docs/examples/mpc.html">OSQP 官方 MPC 範例</a> · <a href="https://docs.scipy.org/doc/scipy/reference/optimize.minimize-slsqp.html">SciPy SLSQP</a> · <a href="../research/enclosure_mpc_method_2026-10-05_zh.md">方法與參數說明</a></p><p><a href="../../openspec/changes/implement-enclosure-mpc-20261005/protocol.md">事前 protocol</a> · <a href="../../openspec/changes/implement-enclosure-mpc-20261005/artifacts/freeze.json">calibration freeze</a> · <a href="../../openspec/changes/implement-enclosure-mpc-20261005/artifacts/result.json">完整 JSON</a> · <a href="../../openspec/changes/implement-enclosure-mpc-20261005/artifacts/verification.json">軌跡核對</a> · <a href="../../openspec/changes/implement-enclosure-mpc-20261005/evidence.md">執行與限制紀錄</a></p></section></main></body></html>'''
    dest=ROOT/'docs/reports/enclosure_mpc_2026-10-05_zh.html';dest.write_text(html)
    print(dest)


if __name__=='__main__':main()
