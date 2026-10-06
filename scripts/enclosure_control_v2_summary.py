"""Evidence-derived text for the four-controller study; historical v1 is separate."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGE = ROOT / 'openspec/changes/validate-enclosure-four-controllers-20261005'
ARTIFACTS = CHANGE / 'artifacts'
TITLE = '機箱四方法探索性模擬（v2）'
METHODS = ('fixed', 'pid', 'lqr', 'mpc')
LABELS = {'fixed': '固定風扇', 'pid': 'PID＋平衡點前饋',
          'lqr': '經限制的 LQR', 'mpc': '受限制 MPC'}
SPLITS = ('validation', 'holdout', 'plant_holdout', 'overload')
BOUNDARY = (
    '四方法使用相同候選評估回合預算，CPU 計算時間並不相等。PID＋前饋、LQR 與 MPC '
    '知道名義假設參數，且完整狀態可見；數值積分方式不同不等於獨立物理驗證。'
    'plant_holdout 是三組預先指定的假設參數變體，不能支持跨實體設備泛化。'
    '新合成 seeds 也不是實體設備樣本。超溫秒數按每 10 秒末端取樣估計；'
    '風扇能耗採 10u³ W 假設，不能代替整機功耗。溫度限制為軟限制，'
    '求解成功不代表熱能力足夠或硬體安全。實體機箱、NTC、throttling、整機功耗與 E8 '
    '仍為 NOT_EVALUATED。舊 v1 報告中的 LQR TODO 是第一階段的歷史狀態。'
)


def summary(artifacts=ARTIFACTS):
    path = Path(artifacts) / 'result.json'
    if not path.exists():
        return None
    result = json.loads(path.read_text())
    runs = result['runs']
    if not runs or any(m not in result['aggregates']['holdout'] for m in METHODS):
        raise ValueError('Four-method result is incomplete')
    hold = result['aggregates']['holdout']
    counts = (len(runs), sum(r['n'] for r in runs))
    maes = '、'.join(f"{LABELS[m]} {hold[m]['tracking_mae_C']:.4f}°C" for m in METHODS)
    energy = '／'.join(f"{hold[m]['fan_energy_proxy_Wh']:.4f}" for m in METHODS)
    decisions = result['decisions']
    gates = '；'.join(f'{k}={v}' for k, v in decisions.items() if k.startswith('H-'))
    if not gates:
        raise ValueError('Result has no research decisions')
    overload = result['aggregates']['overload']
    overload_text = '；'.join(
        f"{LABELS[m]}：取樣超溫 {overload[m]['overtemp_s']:.1f} s、"
        f"數值回退 {overload[m]['fallback_n']:.2f} 步／回合" for m in METHODS)
    text = (f'2026-10-05 第二階段完成四方法假設模型探索性比較，共 {counts[0]} 回合、'
            f'{counts[1]:,} 控制步。每方法依相同三個 calibration seeds 評估三個候選，'
            f'選參後凍結，再開啟新的 validation、holdout、假設模型變體與過載。'
            f'holdout 三 seed 等權 tracking MAE：{maes}。'
            f'相同方法順序的風扇能耗 proxy 為 {energy} Wh。研究判準：{gates}。')
    return {'result': result, 'text': text, 'boundary': BOUNDARY,
            'overload': overload_text, 'decisions_text': gates, 'run_count': counts[0],
            'step_count': counts[1]}


def thesis_blocks():
    data = summary()
    if data is None:
        return []
    return [{'type': 'heading', 'text': TITLE, 'level': 1},
            *({'type': 'paragraph', 'text': data[k]} for k in ('text', 'overload', 'boundary'))]


def outline_text():
    data = summary()
    if data is None:
        return ''
    return '\n\n## ' + TITLE + '\n\n' + '\n\n'.join(data[k] for k in ('text', 'overload', 'boundary')) + '\n'


def ieee_text():
    data = summary()
    if data is None:
        raise FileNotFoundError('A completed v2 result is required before manuscript synchronization')
    r = data['result']; hold = r['aggregates']['holdout']
    maes = '/'.join(f"{hold[m]['tracking_mae_C']:.4f}" for m in METHODS)
    energies = '/'.join(f"{hold[m]['fan_energy_proxy_Wh']:.4f}" for m in METHODS)
    return (
        r'\subsection{Exploratory Enclosure Control Simulation}' + '\n\n'
        r'The historical three-method SLSQP study is retained as v1~\cite{scipyslsqp}; its opened holdout is not reused as unseen evidence. '
        r'Version 2 compares fixed fan, equilibrium-feedforward PID, bounded gain-scheduled LQR~\cite{scipydare}, '
        r'and OSQP MPC~\cite{osqpmpc}. Shared assumed parameters, current observations, PWM/slew limits and safety overrides '
        r'are fixed; each method receives three candidates on three calibration seeds, without equalizing CPU time. '
        f'After freezing, {data["run_count"]} episodes ({data["step_count"]:,} steps) cover validation, new synthetic holdout, '
        r'three assumed plant variants and overload. Holdout macro tracking MAE is '
        + maes + r'~$^\circ$C, with fan-energy proxy ' + energies + r' Wh, respectively. '
        r'MAE, sampled overtemperature, command variation and numerical fallback are reported separately. '
        r'Full-state access and known nominal parameters limit interpretation; designated plant variants do not establish '
        r'cross-device generality. Thermal slack and successful numerical solves do not establish sufficient cooling or hardware safety. '
        r'Physical identification, NTC measurements, throttling and whole-system energy remain unevaluated; E8 is unchanged.' + '\n\n')
