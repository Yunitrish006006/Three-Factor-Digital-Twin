"""Scientific figures from stored diagnostic evidence; no simulation."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from enclosure_lqr_diagnostic_summary import data,ARTIFACTS,ROOT,LABELS

def main():
    r=data();out=ROOT/'docs/research/lqr_diagnostic_2026-10-19';out.mkdir(exist_ok=True)
    labels=['LQR E/F','LQR T/F','LQR E/X','LQR T/X','PI E/F']
    colors=['#236985','#96b6c3','#c2913a','#dcc79f','#596770']
    plt.rcParams.update({'font.size':11,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(10,4.7),layout='constrained')
    for ax,metric,title in zip(axes,['tracking_mae_C','fan_energy_proxy_Wh'],['Tracking MAE (deg C)','Fan energy proxy (Wh)']):
        values=[r['aggregates'][a][metric] for a in LABELS]
        bars=ax.bar(labels,values,color=colors);ax.set_ylabel(title);ax.set_ylim(0,max(values)*1.2)
        ax.tick_params(axis='x',labelrotation=30);ax.bar_label(bars,labels=[f'{v:.4f}' for v in values],padding=4,fontsize=9)
    fig.suptitle('Fresh diagnostic panel: 4 assumed plants x 2 seeds',fontsize=14)
    fig.savefig(out/'comparison.svg');plt.close(fig)
    worst=max((run for run in r['runs'] if run['arm']=='estimated_fitted'),key=lambda run:run['metrics']['tracking_mae_C'])
    rows=list(csv.DictReader((ARTIFACTS/worst['csv']).open()))
    x=np.array([float(row['time_s']) for row in rows]);col=lambda name:np.array([float(row[name]) for row in rows])
    fig,axes=plt.subplots(2,1,figsize=(10,6),sharex=True,layout='constrained')
    axes[0].plot(x,col('source_truth_current_C'),label='True source',color='#236985')
    axes[0].plot(x,col('source_estimate_C'),'--',label='Sparse estimate',color='#c2913a')
    axes[0].axhline(28,color='#596770',linestyle=':',label='Target 28 C');axes[0].set_ylabel('Temperature (deg C)');axes[0].legend(ncol=3,fontsize=9)
    axes[1].plot(x,col('raw_lqr_pwm'),label='Raw LQR request',color='#c2913a')
    axes[1].plot(x,col('pwm'),label='Applied PWM',color='#236985')
    axes[1].axhspan(.2,1,color='#236985',alpha=.12,label='Allowed amplitude')
    axes[1].set_ylabel('PWM request / applied');axes[1].set_xlabel('Time (s)');axes[1].legend(ncol=3,fontsize=9)
    fig.suptitle(f"Highest practical-LQR tracking MAE: {worst['panel']}, seed {worst['seed']}",fontsize=13)
    fig.savefig(out/'worst_case.svg');plt.close(fig)
    for svg in out.glob("*.svg"):
        svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines())+"\n")
    print(out)

if __name__=='__main__':main()
