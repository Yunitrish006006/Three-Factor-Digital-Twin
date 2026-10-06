"""One evidence-backed supplement shared by the project document builders."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ARTIFACTS=ROOT/'openspec/changes/implement-enclosure-mpc-20261005/artifacts'
TITLE='機箱受限制 MPC 探索性模擬'


def summary():
    path=ARTIFACTS/'result.json'
    if not path.exists():
        return None
    r=json.loads(path.read_text())
    hold=r['aggregates']['holdout']
    m,p,f=(hold[k] for k in ('mpc','pid','fixed'))
    return {
        'result':r,
        'text':(
            f"2026-10-05 完成 CPU/GPU 雙熱節點與風扇延遲的受限制 MPC 探索性模擬。"
            f"calibration 後鎖定控制器，另跑 36 回合、4,320 個控制步，涵蓋 validation、"
            f"holdout、模型失配與過載。holdout 的三 seed macro tracking MAE 為固定風扇 "
            f"{f['tracking_mae_C']:.4f}°C、PID {p['tracking_mae_C']:.4f}°C、"
            f"MPC {m['tracking_mae_C']:.4f}°C，MPC 相對 PID 降低 "
            f"{r['decisions']['holdout_relative_mae_gain_vs_pid']*100:.2f}%。"
            f"nominal 六個 MPC 回合均無 PWM／slew 違例、超溫或求解回退。"
        ),
        'boundary':(
            f"代價是 holdout 風扇能耗 proxy 由 PID {p['fan_energy_proxy_Wh']:.4f} Wh "
            f"增至 MPC {m['fan_energy_proxy_Wh']:.4f} Wh，PWM total variation 亦增加。"
            f"過載仍超溫，MPC 平均每回合 {r['aggregates']['overload']['mpc']['fallback_n']:.2f} "
            f"步求解回退；溫度為軟限制，不能視為安全保證。"
            "參數、負載與功耗曲線均為假設，plant 與 predictor 雖採不同數值積分，仍共享"
            "名義熱參數。本結果只支持假設模型內的探索性可行性與追蹤改善，不代表機箱辨識、"
            "NTC、實體控制、throttling、整機功耗或跨設備確認。E8 保持 NOT_EVALUATED，LQR 保持 TODO。"
        ),
    }


def thesis_blocks():
    data=summary()
    if data is None:
        return []
    return [{'type':'heading','text':TITLE,'level':1},
            {'type':'paragraph','text':data['text']},
            {'type':'paragraph','text':data['boundary']}]


def outline_text():
    data=summary()
    if data is None:
        return ''
    return '\n\n## '+TITLE+'\n\n'+data['text']+'\n\n'+data['boundary']+'\n'
