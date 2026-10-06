"""One evidence-derived progress supplement for all coupled research artifacts."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGE = ROOT / 'openspec/changes/prototype-sparse-enclosure-transfer-20261006'
ARTIFACTS = CHANGE / 'artifacts'
TITLE = '稀疏機箱溫度候選原型（2026-10-06）'
BOUNDARY = ('本輪為溫度子問題與假設熱網路：已知熱容量和部分係數，單一方程家族、三組指定參數與合成噪聲。'
            '金屬片／風管增益是假設，未量測實際裝置；有限候選排序不是 LQR 或完整 MPC。'
            '20–30°C 外的樣本完整保留，但不擴張原室內模型適用域。'
            '濕度、光照、三維空間場、完整三因子遷移與實體辨識／介入均未評估。')


def summary():
    path = ARTIFACTS / 'result.json'
    if not path.exists():
        return None
    r = json.loads(path.read_text())
    h = r['aggregates']['open_loop']['holdout']
    c = r['aggregates']['closed_loop']['holdout']
    text = (f"2026-10-06 依教授交辦查證金屬傳熱與風管場景，建立熱源／金屬片／空氣熱網路候選原型，"
            f"以金屬片、空氣與風扇觀測估測未提供的熱源溫度。三組假設平台採相同有限辨識程序，"
            f"完成 {r['run_count']} 回合、{r['step_count']:,} 步。新的合成 holdout 上，"
            f"名義物理／辨識物理／稀疏校正熱源估測 MAE 為 "
            + '/'.join(f"{h[m]['source_mae_C']:.4f}" for m in ('nominal_physics','calibrated_physics','sparse_corrected'))
            + f"°C；稀疏校正相對辨識物理減少 {100*r['decisions']['source_mae_reduction_fraction']:.2f}%，6/6 組改善。"
            + '固定／PI／PID／單步排序／六步排序／六步無校正的 tracking MAE 為 '
            + '/'.join(f"{c[m]['tracking_mae_C']:.4f}" for m in ('fixed','pi','pid','rank_h1','rank_h6','rank_h6_no_correction'))
            + f"°C。六步相對單步減少 {100*r['decisions']['horizon_tracking_reduction_fraction']:.2f}%，仍未優於 PI；"
            f"六步排序平均取樣超溫 {c['rank_h6']['overtemp_s']:.2f} 秒／回合。"
            + 'H-ENC-31／H-ENC-32 只在此 exploratory simulation 的事前判準內 supported。')
    lqr = ('已為下週準備 LQR 與 Kalman (1960) Contributions to the Theory of Optimal Control 的介紹。'
           '重點查閱原文問題、狀態精確已知假設、可控／可觀測與 Riccati／穩定定理敘述；未重證全部證明，亦尚未口頭報告。')
    return {'result':r, 'text':text, 'boundary':BOUNDARY, 'lqr':lqr}


def thesis_blocks():
    s = summary()
    return [] if s is None else [{'type':'heading','text':TITLE,'level':1},
                                 *({'type':'paragraph','text':s[k]} for k in ('text','boundary','lqr'))]


def outline_text():
    s = summary()
    return '' if s is None else '\n\n## '+TITLE+'\n\n'+'\n\n'.join(s[k] for k in ('text','boundary','lqr'))+'\n'


def ieee_text():
    s=summary(); r=s['result']; c=r['aggregates']['closed_loop']['holdout']; h=r['aggregates']['open_loop']['holdout']
    return (r'\subsection{Sparse Thermal-Network Transfer Candidate}'+'\n'
            r'A separate temperature-only pilot follows the physics--sparse correction--action-ranking workflow. '
            r'Conductive contact and convective airflow are represented separately, motivated by thermal design guidance~\cite{tithermal2017,noctuaduct}. '
            r'A hidden heat-source temperature is inferred from plate/air temperatures and fan observations. '
            r'Three assumed rigs use identical bounded two-parameter calibration with known capacities and other coefficients. '
            f"Across {r['run_count']} episodes ({r['step_count']:,} steps), synthetic holdout source MAE for nominal/calibrated/corrected physics is "
            +'/'.join(f"{h[m]['source_mae_C']:.4f}" for m in ('nominal_physics','calibrated_physics','sparse_corrected'))
            +r'~$^\circ$C. Fixed/PI/PID/one-step/six-step/six-step-without-correction tracking MAE is '
            +'/'.join(f"{c[m]['tracking_mae_C']:.4f}" for m in ('fixed','pi','pid','rank_h1','rank_h6','rank_h6_no_correction'))
            +r'~$^\circ$C. Six-step ranking improves over one-step ranking but does not outperform PI in tracking; '
            f"sampled overtemperature averages {c['rank_h6']['overtemp_s']:.2f} s per holdout episode. "
            r'Finite candidate ranking borrows quadratic state/input costs and receding-horizon evaluation; it is not an LQR or full MPC solver. '
            r'Kalman\textquotesingle s foundational regulator study~\cite{kalman1960optimal} motivates separating state estimation from control. '
            r'All parameters and fan energy are assumed; out-of-domain samples do not extend the validated room domain. '
            r'Physical identification, hardware actuation and full three-factor transfer remain unevaluated.'+'\n\n')
