"""Offline professor report from immutable synthetic evidence and LQR reading notes."""
from html import escape
import io
import json
import os
import tempfile

os.environ.setdefault('MPLCONFIGDIR', tempfile.mkdtemp(prefix='sparse-enclosure-mpl-'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
matplotlib.rcParams['svg.hashsalt'] = 'sparse-enclosure-report-20261006'

from sparse_enclosure_summary import ROOT, ARTIFACTS, summary

METHODS=('fixed','pi','pid','rank_h1','rank_h6','rank_h6_no_correction')
LABELS=('Fixed','PI','PID','H=1','H=6','H=6, no correction')


def chart(data):
    c=data['result']['aggregates']['closed_loop']['holdout']
    fig,ax=plt.subplots(figsize=(8,3.8),layout='constrained')
    values=[c[m]['tracking_mae_C'] for m in METHODS]
    bars=ax.bar(LABELS,values,color=['#8495a5','#57a897','#57a897','#d6a85a','#446cab','#8d78a5'])
    ax.bar_label(bars,fmt='%.3f',padding=3)
    ax.set_ylim(0,max(values)*1.28)
    ax.set_ylabel('Tracking MAE (degrees C)')
    ax.set_title('Synthetic holdout: 3 assumed rigs x 2 seeds; equal episode weighting')
    ax.tick_params(axis='x',labelsize=9)
    ax.spines[['right','top']].set_visible(False)
    out=io.StringIO(); fig.savefig(out,format='svg',metadata={'Date':None}); plt.close(fig)
    svg=out.getvalue(); svg=svg[svg.index('<svg'):]
    return svg.replace('<svg ','<svg role="img" aria-label="六種方法的合成holdout追蹤MAE比較" ',1)


def build():
    data=summary(); r=data['result']; hold=r['aggregates']['closed_loop']['holdout']
    audit=json.loads((ARTIFACTS/'input_replay_audit.json').read_text())
    if not audit['passed']:
        raise ValueError('A passing input replay audit is required')
    rows=''.join('<tr><th>'+escape(label)+'</th>'+''.join(f'<td>{hold[m][k]:.4f}</td>' for k in
                 ('tracking_mae_C','source_mae_C','fan_energy_proxy_Wh','overtemp_s','command_variation'))+'</tr>'
                 for m,label in zip(METHODS,('固定風扇','PI','PID','單步排序','六步排序','六步無校正')))
    cal=json.loads((ARTIFACTS/'calibration.json').read_text())
    calrows=''.join(f'<tr><th>{escape(k)}</th><td>{v["estimated_parameters"]["contact"]:.4f}</td>'
                    f'<td>{v["estimated_parameters"]["plate_fan"]:.4f}</td><td>{v["nfev"]}</td>'
                    f'<td>{v["jacobian_condition"]:.2f}</td></tr>' for k,v in cal.items())
    maxsource=max(run['metrics']['max_source_C'] for run in r['runs'])
    document=f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>機箱模型研究與下週 LQR 論文介紹｜2026-10-06</title>
<style>
:root{{color-scheme:light;--ink:#253646;--muted:#586b7a;--accent:#315f87;--line:#d8e2e9}}
*{{box-sizing:border-box}}body{{margin:0;background:#f3f6f8;color:var(--ink);font:17px/1.8 system-ui,"PingFang TC",sans-serif;overflow-wrap:anywhere;overflow-x:clip}}
main{{max-width:1040px;margin:auto;padding:40px 24px 80px}}header,section{{background:white;border:1px solid var(--line);border-radius:15px;padding:28px;margin:20px 0}}
h1{{font-size:clamp(26px,4vw,40px);line-height:1.35}}h2{{font-size:25px}}h3{{font-size:19px}}p{{margin:14px 0}}a{{color:var(--accent)}}
.meta,.caption{{color:var(--muted);font-size:14px}}nav{{display:flex;flex-wrap:wrap;gap:10px;margin:20px 0}}nav a{{padding:5px 12px;background:#e9f0f5;border-radius:8px;text-decoration:none}}
.notice{{border-left:4px solid #bb8943;padding:12px 18px;background:#fff7e9}}.flow{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}}
.flow div{{background:#edf3f8;border:1px solid var(--line);border-radius:10px;padding:16px}}.flow strong{{display:block}}
.table-wrap{{overflow-x:auto;width:100%;max-width:100%;margin:18px 0}}table{{border-collapse:collapse;width:100%;font-size:14px}}td,th{{padding:11px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}
figure{{margin:24px 0}}figure svg{{width:100%;height:auto;display:block}}details{{border-top:1px solid var(--line);padding:12px 0}}summary{{cursor:pointer;font-weight:600}}
pre{{white-space:pre-wrap;overflow-wrap:anywhere;font:14px/1.8 ui-monospace,monospace;background:#f2f5f7;padding:16px;border-radius:8px}}
.controls{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}label{{display:block}}input{{max-width:100%;width:100%}}output{{display:block;background:#edf3f8;padding:16px;border-radius:8px;margin-top:15px}}
section{{scroll-margin-top:20px}}:focus-visible{{outline:3px solid #c9933b;outline-offset:3px}}
@media(max-width:650px){{main{{padding:14px 12px 50px}}header,section{{padding:20px 16px}}.flow,.controls{{grid-template-columns:1fr}}td,th{{padding:9px}}}}
@media print{{body{{background:white;font-size:11pt}}main{{max-width:none;padding:0}}header,section{{border:0;border-radius:0;padding:12px 0}}nav,.controls{{display:none}}details{{break-inside:avoid}}figure{{break-inside:avoid}}a{{color:inherit}}}}
</style></head><body><main>
<header><p class="meta">研究與備稿日期：2026-10-06｜本週教授交辦｜尚未實際口頭報告</p>
<h1>我如何把稀疏感測模型<br>逐步改到能研究機箱傳熱</h1>
<p>我完成了金屬傳熱與風管場景查證，並建立溫度候選原型。稀疏校正改善了熱源估測；多步排序比單步改善，但仍沒有比 PI 更準，也還存在超溫。</p>
<p class="notice">這份報告呈現假設熱網路的探索性模擬。真實機箱、硬體導熱改善、三因子完整遷移與實體控制尚未驗證。</p>
<nav aria-label="報告目錄"><a href="#assignment">交辦</a><a href="#devices">裝置場景</a><a href="#model">自己的模型</a><a href="#results">結果</a><a href="#limits">限制</a><a href="#lqr">LQR 論文</a><a href="#next">下一步</a></nav></header>
<section id="assignment"><h2>教授交代我的三件事</h2><ol><li>找到金屬片、導熱風管等裝置的場景，研究如何加強傳熱。</li><li>利用 MPC、LQR、PID、PI 的優點，開始改進自己的模型，使其能在機箱使用。</li><li>下週介紹 LQR 是什麼，報告一篇代表性論文。</li></ol>
<p>會議原轉述「LQZ」已確認為 LQR。我把模型改進與控制方法比較分開，先處理傳熱路徑和稀疏觀測，再看動作選擇。</p></section>
<section id="devices"><h2>我查到的裝置場景</h2>
<div class="table-wrap"><table><thead><tr><th>場景</th><th>實際機制</th><th>我如何用在候選設計</th></tr></thead><tbody>
<tr><th>金屬散熱片與接觸介面</th><td>固體導熱、接觸熱阻、向空氣散熱。</td><td>熱源與金屬片分開建模，辨識接觸熱導。<a href="https://www.ti.com/lit/an/sprabi3b/sprabi3b.pdf">TI 熱設計指南，PDF 第 6–7 頁</a></td></tr>
<tr><th>小型機箱進氣風管</th><td>引導新鮮空氣、減少熱空氣回流；NA-FD1 是 EVA foam 風管。</td><td>處理入口邊界和對流交換，不把廠商特定降溫幅度當成我的結果。<a href="https://www.noctua.at/en/products/na-fd1">Noctua 官方案例</a></td></tr>
<tr><th>PCB／金屬底板</th><td>可能提供平行傳熱路徑。</td><td>暫列後續擴充；需要底板溫度與幾何資料。<a href="https://www.ti.com/lit/an/sprabi3b/sprabi3b.pdf">TI Fig. 4，PDF 第 10 頁</a></td></tr>
</tbody></table></div>
<p>我選擇先用「可控熱源＋金屬片＋風扇／風管」整理需求。這是候選平台，沒有購買或製作；三組模擬係數是設計假設，不能解讀為金屬或風管已經量測到的效益。</p></section>
<section id="model"><h2>我開始改進的是自己的方法流程</h2>
<div class="flow" aria-label="候選原型流程"><div><strong>① 物理主模型</strong>熱源 → 金屬片 → 空氣 → 入口環境</div><div><strong>② 稀疏校正</strong>讀金屬片、空氣與風扇；熱源溫度只拿來驗證</div><div><strong>③ 候選預測</strong>預測不同 PWM 的下一步與六步結果</div><div><strong>④ 動作排序</strong>兼顧溫度、命令與變化代價，執行第一步後重算</div></div>
<p>我沿用物理為主、感測校正、候選動作排序的研究思路。這次新增的是獨立溫度原型；原室內八角點、濕度、照度與空間殘差網路尚未搬入。</p>
<details><summary>模型方程與辨識條件</summary><pre>C_h dT_h/dt = P − G_hp(T_h−T_p) − G_b(T_h−T_in)
C_p dT_p/dt = G_hp(T_h−T_p) − (G_p+k_p f)(T_p−T_a)
C_a dT_a/dt = (G_p+k_p f)(T_p−T_a) − (G_a+k_a f)(T_a−T_in)
τ_f df/dt = u−f</pre><p>以上是我自行數學化整理，不是文獻逐字公式。容量與部分係數已知，僅辨識接觸熱導與風扇對流增益，每平台相同 600 秒激發、單一起點、最多 30 次函數評估。以下局部 Jacobian condition 不等於全參數可辨識證明。</p>
<div class="table-wrap"><table><thead><tr><th>假設平台</th><th>辨識 G_hp W/K</th><th>辨識 k_p W/K</th><th>nfev</th><th>Jacobian condition</th></tr></thead><tbody>{calrows}</tbody></table></div><p>max_nfev 限制的是 SciPy 回報的函數評估數；數值 Jacobian 還有額外評估，並不表示每方法運算成本相等。</p></details></section>
<section id="results"><h2>我得到的改善與代價</h2><p>{escape(data['text'])}</p>
<figure>{chart(data)}<figcaption class="caption">三組指定假設平台 × 兩個新合成 seed 的等權平均；各方法使用相同可取得資訊與命令限制。不同閉迴路方法會造成不同的溫度與感測軌跡。</figcaption></figure>
<div class="table-wrap"><table><thead><tr><th>方法</th><th>追蹤 MAE °C</th><th>估測 MAE °C</th><th>風扇 proxy Wh</th><th>平均超溫秒／回合</th><th>Σ|ΔPWM|</th></tr></thead><tbody>{rows}</tbody></table></div>
<p>六步排序的風扇 proxy 比 PI 低，但追蹤較差；這是誤差與操作成本的權衡，不能只看其中一欄就宣稱全面較好。所有閉迴路命令都符合預先固定的 PWM 與每步變化限制。</p>
<details><summary>如何避免把估測改善當成控制改善</summary><p>估測比較使用同一份開迴路命令，分別對照名義物理、辨識物理和稀疏校正；控制比較另看 PI、PID、H=1、H=6 與移除校正。改善約 49.06% 指的是熱源估測，不是實體散熱效果。</p></details></section>
<section id="limits"><h2>我仍然遇到的限制</h2><p>{escape(data['boundary'])}</p>
<h3>先區分散熱能力與控制誤差</h3><p>{escape(data['corrections'])}</p>
<p>全部評估回合的最高熱源溫度是 {maxsource:.3f}°C。表中的超溫按每 5 秒末端取樣計算，不保證捕捉連續時間尖峰；感測噪聲或未建模熱量會讓估測警告晚於真實超溫。校正成功和命令合規都不能證明硬體安全。</p>
<p>這輪兩個事前探索判準都通過，但只支持這組指定熱網路內的可行性。已開啟的測試不再作為未來改進的未見確認資料，我沒有用結果回頭改設定。</p></section>
<section id="lqr"><h2>下週介紹：LQR 與 Kalman 1960</h2>
<p>LQR 是 Linear Quadratic Regulator，線性二次調節器。我先用線性狀態模型描述變化，再用 Q 指定狀態偏差代價、R 指定操作代價，求出狀態回授增益 K。它需要模型與狀態，不會自動完成熱參數辨識或稀疏感測。</p>
<p>我選的代表論文是 <strong>R. E. Kalman (1960), Contributions to the Theory of Optimal Control</strong>，刊於 Boletín de la Sociedad Matemática Mexicana，5，102–119 頁。它建立最優線性調節問題的理論，將可控性、可觀測性、Riccati 方程與存在／穩定條件連在一起。<a href="https://boletin.math.org.mx/pdf/2/5/BSMM%282%29.5.102-119.pdf">期刊原文</a></p>
<p>我重點查閱問題與定理敘述，尚未逐行重證全部證明。原文 p.104 假設控制部分的狀態精確已知；p.114 的穩定定理有明確條件。這提醒我先驗證稀疏估測，再討論控制，並另行處理風扇限幅與散熱能力。</p>
<details><summary>現代記號下的教學整理與原文定位</summary><pre>e = x−x_eq；v = u−u_eq
de/dt = Ae+Bv
J = ∫(eᵀQe+vᵀRv)dt
v = −Ke；K = R⁻¹BᵀP
AᵀP+PA−PBR⁻¹BᵀP+Q = 0</pre><p>以上為定常無限時域、無硬限制情況的自行整理，不是原文逐字轉錄。原文 (2.1–2.2) 在 p.103，二次成本 (A1) 在 p.111，Riccati (6.3) 在 p.112。原文掃描回授號誌另在閱讀筆記說明；我用目前的狀態方程與成本定義導出負號。</p></details>
<h3>調整 Q／R，看看回授的權衡</h3><p class="caption">純教學的一維示意：de/dt=−0.01e−0.01v，初始 e=3，u_eq=0.5。不是已辨識機箱、不是論文實驗或本輪控制結果。</p>
<div class="controls"><label for="q">狀態代價 Q：<span id="qvalue">1</span><input id="q" type="range" min="-1" max="1" step=".1" value="0" aria-label="Q 的十次方權重"></label>
<label for="r">操作代價 R：<span id="rvalue">1</span><input id="r" type="range" min="-1" max="1" step=".1" value="0" aria-label="R 的十次方權重"></label></div>
<output id="gain" aria-live="polite"></output><p class="caption">限幅後只能稱限制過的控制命令，不能沿用無限制 LQR 的最優保證。</p>
<p><a href="../research/lqr_kalman1960_reading_2026-10-06_zh.md">完整頁碼筆記</a> · <a href="lqr_oral_script_2026-10-06_zh.md">約五分鐘講稿</a>。備稿完成，尚未向教授報告。</p></section>
<section id="next"><h2>我接下來要驗證什麼</h2><ol><li>確認設備與平台能取得哪些量測：金屬片、空氣、入口、獨立熱源驗證、功率、PWM 與 RPM。</li><li>檢查熱容量、接觸熱阻與入口回流的不確定性，讓辨識不再依賴過多已知係數。</li><li>在新的事前固定資料上，比較有限排序、稀疏觀測 LQR 與 MPC；保留誤差、能耗和超溫的權衡。</li><li>下週先介紹 LQR 的問題、核心公式與限制，再說明我如何借用到機箱模型。</li></ol></section>
<details id="sources"><summary>研究來源與驗證紀錄</summary><p><a href="../research/enclosure_transfer_sources_2026-10-06_zh.md">場景／方法來源表</a> · <a href="../../openspec/changes/prototype-sparse-enclosure-transfer-20261006/protocol.md">事前驗證計畫</a> · <a href="../../openspec/changes/prototype-sparse-enclosure-transfer-20261006/artifacts/result.json">全部結果</a> · <a href="../../openspec/changes/prototype-sparse-enclosure-transfer-20261006/artifacts/input_replay_audit.json">只讀輸入的回放核對</a></p><p>所有 108 回合、19,440 步已由 CSV 重新計算指標，並僅用宣告的觀測回放估測與控制。這證明資料與實作紀錄的一致性，不把模擬變成物理驗證。</p><p><a href="professor_catchup_report_2026-10-05_zh.html">10/5 既有研究報告</a></p></details>
</main><script>
const q=document.getElementById('q'),r=document.getElementById('r');
function updateGain(){{const Q=10**Number(q.value),R=10**Number(r.value),a=.01,b=-.01;
const P=R/(b*b)*(Math.sqrt(a*a+b*b*Q/R)-a),K=b*P/R,raw=.5-K*3;
document.getElementById('qvalue').textContent=Q.toFixed(2);document.getElementById('rvalue').textContent=R.toFixed(2);
document.getElementById('gain').textContent='K = '+K.toFixed(3)+'；未限幅 PWM = '+raw.toFixed(3)+'；套用 0.2–1 示意限制後 = '+Math.max(.2,Math.min(1,raw)).toFixed(3);}}
q.addEventListener('input',updateGain);r.addEventListener('input',updateGain);updateGain();
</script></body></html>'''
    target=ROOT/'docs/reports/professor_research_2026-10-06_zh.html'
    target.write_text('\n'.join(line.rstrip() for line in document.splitlines())+'\n')
    return target


if __name__=='__main__':
    print(build())
