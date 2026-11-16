#!/usr/bin/env python3
"""Publication figures from the frozen unified study; does not run a controller."""
from pathlib import Path
import json, hashlib, runpy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
for fontfile in Path("/System/Library/Fonts/Supplemental").glob("Times New Roman*.ttf"):
 font_manager.fontManager.addfont(str(fontfile))
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
ROOT = Path(__file__).resolve().parents[3]
ART = ROOT/'openspec/changes/compare-enclosure-five-methods-20261026/artifacts'
OUT = Path(__file__).resolve().parent/'figures'
OUT.mkdir(parents=True,exist_ok=True)
result_bytes=(ART/'result.json').read_bytes()
verification=json.loads((ART/'verification.json').read_text())
assert verification['status']=='PASS' and hashlib.sha256(result_bytes).hexdigest()==verification['result_sha256']
result=json.loads(result_bytes)
plt.rcParams.update({'font.family':'Times New Roman','mathtext.fontset':'custom','mathtext.rm':'Times New Roman','mathtext.it':'Times New Roman:italic','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(3.05,2.10),dpi=400)
ax.axis('off');ax.set_xlim(0,3.05);ax.set_ylim(0,2.10)
def box(x,y,w,h,label,fc='#edf4f7',edge='#26556c'):
 p=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.035',facecolor=fc,edgecolor=edge,linewidth=1.1);ax.add_patch(p)
 ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontweight='normal',fontsize=10.28,linespacing=1.1)
def arrow(a,b):
 ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=10,linewidth=1.1,color='#2b6477'))
ax.text(.19,1.88,'PWM  u',ha='left',va='center',fontsize=10.28)
arrow((.72,1.86),(1.08,1.86))
box(1.11,1.65,.83,.40,'Fan state\nf',fc='#eef7e8',edge='#4b7e40')
box(.12,.63,1.20,.56,'CPU\nheat source\n$T_{\\mathrm{CPU}}, P_{\\mathrm{CPU}}$')
box(1.73,.63,1.20,.56,'GPU\nheat source\n$T_{\\mathrm{GPU}}, P_{\\mathrm{GPU}}$')
arrow((1.36,1.62),(.75,1.23));arrow((1.69,1.62),(2.29,1.23))
ax.text(1.525,.40,r'Shared inlet  $T_{\mathrm{in}}$',ha='center',fontsize=10.28)
ax.text(1.525,.15,r'Cooling  $(G_i+k_i f)(T_i-T_{\mathrm{in}})$',ha='center',fontsize=10.28)
fig.subplots_adjust(left=.025,right=.975,top=.96,bottom=.04)
fig.savefig(OUT/'model_diagram.jpg',dpi=400,pil_kwargs={'quality':95},facecolor='white');plt.close(fig)
colors={'fixed':'#7c8793','pi':'#2878b5','pid':'#55a868','lqr':'#dd8452','mpc':'#8865a9'}
fig,ax=plt.subplots(figsize=(7.54/2.54,2.95),dpi=220)
for method,label,off in [('fixed','Fixed PWM',(5,5)),('pi','PI',(-15,7)),('pid','PID',(5,-11)),('lqr','LQR',(-31,-14)),('mpc','MPC',(4,17))]:
 d=result['aggregates']['holdout'][method];x=d['fan_energy_proxy_Wh'];y=d['tracking_mae_C']
 ax.scatter([x],[y],s=85,color=colors[method],zorder=3);ax.annotate(label,(x,y),xytext=off,textcoords='offset points',fontsize=10)
ax.set_xlabel('Fan energy proxy\n(Wh / episode)');ax.set_ylabel('Tracking MAE (°C)')
ax.set_xlim(.64,1.2);ax.set_ylim(1.2,2.55);ax.grid(alpha=.18,zorder=0)
# Three paired holdout seeds are stated in the manuscript figure caption.
fig.tight_layout(pad=.4);fig.savefig(OUT/'holdout_tradeoff.jpg',dpi=240,pil_kwargs={'quality':95});plt.close(fig)
runpy.run_path(str(Path(__file__).with_name('build_control_equations.py')))
print('Created two figures from',verification['result_sha256'],'and numbered equations from the manuscript')
