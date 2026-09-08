"""Frozen bank and controller on three additional FMUs."""
import argparse,csv,json
from pathlib import Path
import boptest_native_adapter as adapter
from run_boptest_cross_plant import ROOT,sha,fmu_path
CONFIG=ROOT/'scripts/boptest_more_devices.json'
from digital_twin.control.delayed_dynamics import identify_bank,tuning,DelayedPortablePI
ART=ROOT/'openspec/changes/evaluate-more-boptest-devices/artifacts'
OLD=ROOT/'openspec/changes/improve-portable-dynamics/artifacts'

def source_hashes():
    configs=json.loads(CONFIG.read_text())
    paths=[Path(__file__),CONFIG,ART.parent/'protocol.md',ROOT/'digital_twin/control/delayed_dynamics.py',ROOT/'digital_twin/control/portable_pi.py',ROOT/'scripts/run_boptest_cross_plant.py']
    paths += [ROOT/'scripts/boptest_native_adapter.py',OLD/'freeze.json',OLD/'air.json',OLD/'hydronic.json']
    for c in configs.values():
        paths += [fmu_path(c),fmu_path(c).parent.parent/'doc/index.html']
    return {str(p.relative_to(ROOT)):sha(p) for p in paths}

def make(c,model,q,method):
    g=tuning(model,c['step_s'],q)
    return DelayedPortablePI(c['target_C'],c['step_s'],g['kp'],g['ti'],g['b'],g['delay_steps'],hybrid=method=='proposed')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--plant',choices=['heat_pump','apartment','commercial'],required=True);name=parser.parse_args().plant
    c=json.loads(CONFIG.read_text())[name];ART.mkdir(parents=True,exist_ok=True);dest=ART/(name+'.json');fp=ART/'freeze.json';sources=source_hashes()
    if dest.exists():raise SystemExit('Evidence exists; no overwrite')
    if fp.exists():
        if json.loads(fp.read_text())['sources']!=sources:raise SystemExit('Frozen sources changed')
    else:fp.write_text(json.dumps({'sources':sources,'before_bank_scoring':True},indent=2)+'\n')
    result={'status':'RUNNING','plant':name,'config':c,'sources':sources,'freeze_sha256':sha(fp),'banks':{},'trials':[],'evaluations':[],'skips':[],'failures':[]}
    def save():
        tmp=dest.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');tmp.replace(dest)
    def episode(label,start,hours,controller):
        return adapter.episode(c,label,start,hours,controller)
    save()
    try:
        rows,rec=episode('identification',86400,6,None)
        result['identification']=rec;result['calibration_trace']=rec['trace'];save()
        for h in [2,6]:
            bank=identify_bank(rows[:h*60],c['target_C'],c['step_s']);result['banks'][str(h)]=bank;save()
            print(name,h,'BANK',bank.get('selected',bank['status']),flush=True)
            if bank['status']!='FITTED':result['skips'].append({'budget_h':h,'reason':bank['status']});continue
            for method in ['auto_pi','proposed']:
                for q in [.5,1.]:
                    _,rec=episode(f'trial_{h}_{method}_{q}',2*86400,2,make(c,bank['selected'],q,method))
                    result['trials'].append(dict(budget_h=h,method=method,q=q,**rec));save()
                    print(name,'trial',h,method,q,rec['metrics']['mae_C'],flush=True)
        selected=[]
        for h in [2,6]:
            for method in ['auto_pi','proposed']:
                candidates=[r for r in result['trials'] if r['budget_h']==h and r['method']==method]
                if candidates:
                    best=min(candidates,key=lambda r:r['metrics']['mae_C']);selected.append({'budget_h':h,'method':method,'q':best['q'],'trial_sha256':best['sha256']})
        save();sp=ART/(name+'_selection.json')
        if sp.exists():raise RuntimeError('Selection exists')
        sp.write_text(json.dumps({'selected':selected,'sources':sources,'adaptation_sha256':sha(dest)},indent=2)+'\n');(ART/(name+'_adaptation.json')).write_bytes(dest.read_bytes())
        result['selection_sha256']=sha(sp);save()
        for day in [20,50]:
            for ch in selected:
                h,m,q=ch['budget_h'],ch['method'],ch['q']
                _,rec=episode(f'eval_{day}_{h}_{m}',day*86400,24,make(c,result['banks'][str(h)]['selected'],q,m))
                result['evaluations'].append(dict(day=day,budget_h=h,method=m,q=q,active_adaptation_h=h+4,**rec));save()
                print(name,'eval',day,h,m,rec['metrics']['mae_C'],flush=True)
        result['status']='COMPLETED';save()
    except Exception as exc:
        result['status']='FAILED';result['failures'].append({'type':type(exc).__name__,'message':str(exc)});save();raise

if __name__=='__main__':main()
