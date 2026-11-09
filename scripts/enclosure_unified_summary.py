"""Result-derived summary for the 2026-10-26 common-environment study."""
from pathlib import Path
from html import escape
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
CHANGE=ROOT/'openspec/changes/compare-enclosure-five-methods-20261026'
ART=CHANGE/'artifacts';TITLE='同環境五種機箱控制方法比較 2026-10-26'
LABELS={'fixed':'固定 PWM','pi':'PI','pid':'PID','lqr':'LQR','mpc':'MPC'}
def data():
 r=json.loads((ART/'result.json').read_text());v=json.loads((ART/'verification.json').read_text())
 if v['status']!='PASS' or v['result_sha256']!=hashlib.sha256((ART/'result.json').read_bytes()).hexdigest():raise ValueError('Unaudited unified results')
 return r

def paragraphs():
 r=data();a=r['aggregates'];h=a['holdout'];c=json.loads((ART/'freeze.json').read_text())['config']
 return [
 '我在同一個假設 CPU/GPU 雙熱節點模型內，直接比較固定 PWM、PI、PID、LQR 與 MPC。每方法同為三組候選、三個校準種子，共 45 校準回合；選定後凍結，再完成四分組共 60 正式回合。共保留 12,600 步。每個分組／seed 的五種方法共用初始條件、完整當下狀態、入口溫度、功率與風扇限制；不提供未來負載。PI/PID 採固定偏置 .6、最大節點溫度誤差回授與 anti-windup，未加模型前饋；LQR/MPC 使用名義模型。相同資訊權限及候選回合預算並不代表方法結構、搜尋品質或 CPU 計算量相同。',
 '名義熱容量為 CPU/GPU 1200/1800 J/K、導熱係數1.5/2 W/K、風扇增益6/8 W/K、時間常數20秒。目標60/60°C、警告75/80°C、上限80/85°C；每10秒控制一次，每回合120步（1200秒），PWM .2–1且每步最大變化.1。真實熱狀態每1秒Euler、風扇精確一階更新；這是完全狀態可見的控制律比較，不是稀疏感測或實體機箱驗證。',
 '保留測試組依固定 PWM、PI、PID、LQR、MPC 的追蹤 MAE 為 '+ '／'.join(f"{h[m]['tracking_mae_C']:.4f}" for m in LABELS)+'°C；每回合風扇能耗代理值為 '+'／'.join(f"{h[m]['fan_energy_proxy_Wh']:.4f}" for m in LABELS)+' Wh。'+f"LQR 的本組 MAE 最低，比 PID 低 {100*(1-h['lqr']['tracking_mae_C']/h['pid']['tracking_mae_C']):.2f}%，能耗代理值則高 {100*(h['lqr']['fan_energy_proxy_Wh']/h['pid']['fan_energy_proxy_Wh']-1):.2f}%。PI 與 PID 的差距僅 {h['pi']['tracking_mae_C']-h['pid']['tracking_mae_C']:.4f}°C。",
 'validation、holdout、指定參數失配組與過載組的最低平均 MAE 方法依序為 LQR、LQR、MPC、MPC。前三組所有方法沒有取樣超溫；過載組 CPU/GPU 為440/580W，各方法均超溫，平均超溫時間為 '+'／'.join(f"{a['overload'][m]['overtemp_s']:.1f}" for m in LABELS)+'秒／回合。過載 MPC 有一次殘差 gate 拒絕回退，其他正式回合無回退；全部命令限幅與限速違例為零。過載下單看 MAE 排名不能稱任何方法安全。',
 '以上排名限於本批假設參數、完整狀態資訊及有限候選校準，並非演算法的普遍最優性或硬體證據。代理能耗公式為10×PWM³ W，非量測功率。獨立核對覆蓋105回合、12,600列及1,995個回合指標，逐步標量積分與儲存狀態最大差異為零，並拒絕兩種資料篡改。數據檢查不等於獨立重新最佳化 LQR/MPC，也不包含硬體安全驗證。']

def thesis_blocks():
 if not (ART/'verification.json').exists():return []
 h=data()['aggregates']['holdout']
 return [{'type':'heading','level':1,'text':TITLE}]+[{'type':'paragraph','text':p} for p in paragraphs()]+[{'type':'table','headers':['方法','MAE °C','能耗代理 Wh','超溫秒'], 'rows':[[LABELS[m]]+[f"{h[m][k]:.4f}" for k in ['tracking_mae_C','fan_energy_proxy_Wh','overtemp_s']] for m in LABELS]}]

def md_section():
 return '\n\n## '+TITLE+'\n\n'+'\n\n'.join(paragraphs())+'\n'

def ieee_text():
 a=data()['aggregates'];h=a['holdout']
 return (r'\subsection{Five Controllers in One Assumed Enclosure Environment}'+'\n'
 'A separate exploratory comparison fixes one two-node CPU/GPU plant, present full-state observations, inlet/load schedules and actuator constraints for fixed PWM, plain PI, plain PID, gain-scheduled LQR and MPC. Each method receives three candidates and three calibration seeds (45 episodes); selected parameters are frozen before 60 evaluation episodes across four splits, totaling 12,600 calibration/evaluation steps. PI/PID use a fixed 0.6 bias without model feedforward, whereas LQR/MPC use the nominal plant model; equal input availability and trial counts do not imply equal model use or search quality. '
 'Targets are 60/60 C, control interval 10 s, episode duration 1200 s, PWM range [0.2,1] and slew 0.1 per step. Holdout tracking MAE for fixed PWM, PI, PID, LQR and MPC is '+r'/\allowbreak{}'.join(f"{h[m]['tracking_mae_C']:.4f}" for m in LABELS)+r'~$^\circ$C; corresponding fan-energy proxies are '+r'/\allowbreak{}'.join(f"{h[m]['fan_energy_proxy_Wh']:.4f}" for m in LABELS)+r'~Wh. '
 'LQR has the lowest nominal holdout MAE, while MPC has the lowest mean MAE under the specified parameter mismatch. Every method overheats under the 440/580 W overload; one MPC step is rejected by the residual gate and falls back. All command bounds and slew checks pass. Energy is the assumed 10 PWM cubed power proxy, not measured fan or system energy. Independent stored-data/scalar-dynamics verification covers 105 episodes and preserves adverse outcomes; it does not independently re-optimize LQR/MPC. No hardware efficacy or universal ranking is established.\n\n')

def sync_text():
 start='<!-- BEGIN UNIFIED ENCLOSURE 20261026 -->';end='<!-- END UNIFIED ENCLOSURE 20261026 -->';block=start+md_section()+end+'\n'
 for rel in ['docs/thesis/presentation_outline_zh.md','docs/thesis/presentation_outline_zh_30min.md','docs/thesis/presentation_speaker_notes_zh_30min.md','docs/research/current_enclosure_control_scope_2026-10-19_zh.md']:
  p=ROOT/rel;s=p.read_text();s=re.sub(re.escape(start)+'.*?'+re.escape(end)+r'\n*','',s,flags=re.S);p.write_text(s.rstrip()+'\n\n'+block)
 p=ROOT/'docs/papers/ieee/paper.tex';s=p.read_text();a='% BEGIN UNIFIED ENCLOSURE 20261026';b='% END UNIFIED ENCLOSURE 20261026';nb=a+'\n'+ieee_text()+b+'\n\n'
 if a in s:s=re.sub(re.escape(a)+'.*?'+re.escape(b)+r'\n*',lambda _:nb,s,flags=re.S)
 else:s=s.replace(r'\section{Discussion and Conclusion}',nb+r'\section{Discussion and Conclusion}',1)
 p.write_text(s)
 p=ROOT/'docs/papers/conference_review_2026-10-19/manuscript_zh.md';s=p.read_text();s=re.sub(re.escape(start)+'.*?'+re.escape(end)+r'\n*','',s,flags=re.S);s=s.replace('## 參考文獻',block+'\n## 參考文獻',1);p.write_text(s)
if __name__=='__main__':sync_text()
