"""Audited, result-derived diagnostics for the current research artifacts."""
from pathlib import Path
import hashlib
import json
from html import escape
from statistics import mean

ROOT=Path(__file__).resolve().parents[1]
ARTIFACTS=ROOT/'openspec/changes/diagnose-enclosure-lqr-20261019/artifacts'
TITLE='LQR 狀態與模型資訊診斷 2026-10-19'
LABELS={'estimated_fitted':'估測狀態／辨識模型','truth_fitted':'真實狀態／辨識模型',
        'estimated_exact':'估測狀態／正確模型','truth_exact':'真實狀態／正確模型','pi':'PI：估測／辨識'}


def data():
    r=json.loads((ARTIFACTS/'result.json').read_text());v=json.loads((ARTIFACTS/'verification.json').read_text())
    assert v['status']=='PASS' and v['result_sha256']==hashlib.sha256((ARTIFACTS/'result.json').read_bytes()).hexdigest()
    return r


def paragraphs():
    r=data();a=r['aggregates'];model=r['decisions']['H-ENC-91'];state=r['decisions']['H-ENC-92'];base=a['estimated_fitted']
    return [
      '我以四個新同族熱模型平台，各兩個新擾動種子，完成 40 回合、4,800 筆診斷。每個平台先用 180 筆可見觀測做相同的四參數辨識，共 720 筆校正資料。四個 LQR 組別分別替換控制器使用的狀態與參數，觀測器始終保留原辨識模型，另保留 PI 基準。真實狀態與正確參數只供模擬診斷，不能視為實機稀疏量測可用資訊。',
      f"依序為估測／辨識、真值／辨識、估測／正確、真值／正確、PI，平均追蹤 MAE 為 "+'／'.join(f"{a[x]['tracking_mae_C']:.4f}" for x in LABELS)+'°C。'+
      f"在真實狀態下換成正確控制器模型，誤差降低 {100*model['reduction_fraction']:.2f}%，雖有 {model['wins_of_8']}/8 組改善，仍未達 5% 門檻。固定辨識模型而提供真實狀態，誤差反增 {-100*state['reduction_fraction']:.2f}%，僅 {state['wins_of_8']}/8 組改善。H-ENC-91 與 H-ENC-92 均不支持。",
      f"估測／辨識 LQR 的原始命令有 {100*base['amplitude_clipped_fraction']:.2f}% 超出 PWM 範圍，{100*base['slew_limited_fraction']:.2f}% 另受到變化率限制。這是警告覆寫前的命令診斷，比例可以重疊，不能直接解讀成限幅造成多少追蹤損失。{100*base['steady_target_outside_range_fraction']:.2f}% 的當前擾動，其 28°C 目標落在真實模型兩端風扇穩態溫度範圍外；此為靜態提示，不能宣稱有限時間不可行。全部組別沒有取樣超溫或控制器回退。",
      f"本批估測／辨識 LQR 相對 PI 的追蹤誤差降低 {100*(1-base['tracking_mae_C']/a['pi']['tracking_mae_C']):.2f}%，風扇耗能 proxy 卻增加 {100*(base['fan_energy_proxy_Wh']/a['pi']['fan_energy_proxy_Wh']-1):.2f}%。新舊排名不同，提醒我結論依賴平台、擾動及評分目標。這次移除了先前的隱藏功率偏差與額外熱路徑，只能支持新條件下的資訊介入結果；不能倒推 10/12 排名的唯一原因，也沒有證明估測誤差有益、固定權重最佳或實機有效。下一步應隔離權重與限制的作用，尚未執行。"]


def thesis_blocks():
    if not (ARTIFACTS/'verification.json').exists():return []
    return [{'type':'heading','text':TITLE,'level':1}]+[{'type':'paragraph','text':p} for p in paragraphs()]


def outline_text():return '\n\n## '+TITLE+'\n\n'+'\n\n'.join(paragraphs())+'\n'


def ieee_text():
    r=data();a=r['aggregates'];base=a['estimated_fitted']
    return (r'\subsection{State and Controller-Model Diagnostics}'+'\n'
      'A separate preregistered exploratory factorial diagnostic uses four fresh same-family plants, two disturbance seeds, 40 episodes and 4,800 samples, plus 720 measured commissioning observations. '
      'Only the controller state and parameters are replaced independently; every sparse observer retains its fitted model. True states and exact plant parameters are simulation-only diagnostic information. '
      'Tracking MAE for estimated/fitted, true/fitted, estimated/exact, true/exact LQR and measured-input PI is '
      +r'/\allowbreak{}'.join(f"{a[x]['tracking_mae_C']:.4f}" for x in LABELS)+r'~$^\circ$C. '
      'With true state, exact controller parameters improve MAE by 0.69\\% (6/8 wins), below the fixed 5\\% gate. With the fitted model, true state increases MAE by 1.08\\% (4/8 wins). Both H-ENC-91 and H-ENC-92 are not supported. '
      'The practical LQR raw request exceeds the amplitude range in 80.52\\% of samples; 20.10\\% also require slew limiting before warning overrides. These counts do not identify the causal loss due to saturation. '
      'All arms have zero sampled overtemperature and no controller fallback. LQR lowers tracking error by 5.94\\% relative to PI but increases the fan-energy proxy by 70.44\\%. '
      'This panel removes hidden heat bias and unmodeled paths; it neither identifies the sole cause of the earlier ranking nor supports physical efficacy.'+'\n\n')


def comparison_table():
    a=data()['aggregates']
    return ('表 7　新資訊診斷（八回合平均）',['配置','追蹤 °C','proxy Wh','超溫 s'],
       [[LABELS[k]]+[f'{a[k][m]:.4f}' for m in ('tracking_mae_C','fan_energy_proxy_Wh','overtemp_s')] for k in LABELS])


def html_section(table):
    import base64
    def figure_uri(name):return 'data:image/svg+xml;base64,'+base64.b64encode((ROOT/'docs/research/lqr_diagnostic_2026-10-19'/name).read_bytes()).decode()
    r=data();ps=paragraphs();a=r['aggregates']
    rows=[[p['panel']+' / '+str(p['seed'])]+[f"{p[k]:+.4f}" for k in ('model_effect_with_true_state_C','model_effect_with_estimated_state_C','state_effect_with_fitted_model_C','state_effect_with_exact_model_C','interaction_C')] for p in r['pairs']]
    effects=('四種條件效果：正值代表替換減少追蹤誤差；交互作用為兩種狀態效果之差',['平台／種子','模型效果：真實狀態 °C','模型效果：估測狀態 °C','狀態效果：辨識模型 °C','狀態效果：正確模型 °C','交互作用 °C'],rows)
    content='<section id="diagnostic"><h2>新實驗：把 LQR 的估測與模型誤差分開</h2><p class="meta">本次新增 40 回合，2026-10-19 執行；先前 184 回合保留原結果。</p>'
    content+='<p>'+escape(ps[0])+'</p>'+table(comparison_table())+'<p>'+escape(ps[1])+'</p>'
    content+='<p>「正確模型」只替換控制器參數，觀測器不變。「真實狀態」只在標示的組別取代控制器輸入。這樣才能比較兩個因素，避免同時更換整條流程後無法解釋。</p>'
    content+='<figure><img src="../research/lqr_diagnostic_2026-10-19/comparison.svg" alt="五組控制的追蹤誤差與風扇耗能 proxy 比較" style="width:100%;height:auto"><figcaption>E：估測狀態，T：真實狀態，F：辨識模型，X：正確模型。兩張圖分別比較追蹤與耗能 proxy，不將兩者合成勝負。</figcaption></figure>'
    content+='<p>'+escape(ps[2])+'</p><details><summary>八組配對結果與反例</summary>'+table(effects)+'<p>模型效果為辨識模型 MAE 減去正確模型 MAE；狀態效果為估測狀態 MAE 減去真實狀態 MAE。交互作用為「辨識模型下的狀態改善」減去「正確模型下的狀態改善」，正負本身不代表整體優劣。四個平台各兩回合，沒有把 4,800 個時間點當成獨立樣本計算顯著性。</p></details>'
    content+='<p>'+escape(ps[3])+'</p><figure><img src="../research/lqr_diagnostic_2026-10-19/worst_case.svg" alt="估測與辨識 LQR 中追蹤誤差最高回合的溫度與命令" style="width:100%;height:auto"><figcaption>依估測／辨識 LQR 的最高回合追蹤 MAE 選取代表失敗案例。原始回授命令可以超出物理範圍，實際輸出仍經共同限幅與限速。</figcaption></figure>'
    content+='<p><a href="../../openspec/changes/diagnose-enclosure-lqr-20261019/artifacts/result.json">全部結果與配對</a> · <a href="../../openspec/changes/diagnose-enclosure-lqr-20261019/protocol.md">事前實驗規則</a></p></section>'
    for name in ('comparison.svg','worst_case.svg'):content=content.replace('../research/lqr_diagnostic_2026-10-19/'+name,figure_uri(name))
    content=content.replace('<figure><img','<figure><div class="figure-wrap" tabindex="0" role="region" aria-label="研究圖表，可左右捲動"><img').replace('<figcaption>','</div><figcaption>小螢幕可左右滑動圖表。')
    return content


def sync_text():
    import re
    target=ROOT/'docs/papers/ieee/paper.tex';s=target.read_text();begin='% BEGIN LQR DIAGNOSTIC 20261019';end='% END LQR DIAGNOSTIC 20261019'
    block=begin+'\n'+ieee_text()+end+'\n\n'
    if begin in s:s=re.sub(re.escape(begin)+'.*?'+re.escape(end)+r'\n*',lambda _:block,s,flags=re.S)
    else:s=s.replace(r'\section{Discussion and Conclusion}',block+r'\section{Discussion and Conclusion}',1)
    target.write_text(s)
    for n in ['presentation_outline_zh.md','presentation_outline_zh_30min.md','presentation_speaker_notes_zh_30min.md']:
        path=ROOT/'docs/thesis'/n;s=path.read_text()
        if TITLE in s:s=s[:s.index('\n\n## '+TITLE)]
        path.write_text(s+outline_text())


if __name__=='__main__':sync_text()
