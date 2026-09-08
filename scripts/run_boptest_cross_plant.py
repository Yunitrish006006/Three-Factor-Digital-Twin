"""Frozen shared small-data adaptation across configured BOPTEST plants."""
import argparse,csv,hashlib,json,math,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from digital_twin.control.portable_pi import PortablePI,fit_dynamics,gains,clamp
ART=ROOT/'openspec/changes/evaluate-boptest-cross-plant/artifacts'
CONFIG=ROOT/'scripts/boptest_cross_plant_devices.json'
VENDOR=ROOT/'outputs/vendor/boptest-v0.9.0'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def fmu_path(c):return VENDOR/'testcases'/c['case']/'models/wrapped.fmu'
def encode(c,u):return c['supply_min_C']+clamp(u)*(c['supply_max_C']-c['supply_min_C'])
def decode(c,supply):return clamp((supply-c['supply_min_C'])/(c['supply_max_C']-c['supply_min_C']))

def metrics(rows,c):
    e=[r['next_T']-c['target_C'] for r in rows];n=len(e);dt=c['step_s']
    return {'n':n,'mae_C':sum(map(abs,e))/n,'rmse_C':math.sqrt(sum(x*x for x in e)/n),
        'max_abs_error_C':max(map(abs,e)),'within_0_5_pct':100*sum(abs(x)<=.5 for x in e)/n,
        'requested_TV_u':sum(abs(a['u']-b['u']) for a,b in zip(rows,rows[1:])),
        'saturation_pct':100*sum(r['u']<=0 or r['u']>=1 for r in rows)/n,
        'outside_20_30_n':sum(not 20<=r['next_T']<=30 for r in rows),
        **{k.replace('_W','_kWh'):sum(r['next_'+k] for r in rows)*dt/3.6e6 for k in c['power_outputs']}}


def episode(c,name,start,hours,controller):
    from fmpy import extract,read_model_description
    from fmpy.fmi2 import FMU2Slave
    began=time.perf_counter();dt=c['step_s'];rows=[]
    md=read_model_description(str(fmu_path(c)),validate=False);vr={v.name:v.valueReference for v in md.modelVariables}
    channels={'T':c['temperature'],'outdoor':c['outdoor'],'supply_C':c['supply'],'aux':c['aux_output'],**c['power_outputs']}
    with tempfile.TemporaryDirectory(prefix='boptest-cross-') as temp:
        extract(str(fmu_path(c)),unzipdir=temp)
        fmu=FMU2Slave(guid=md.guid,unzipDirectory=temp,modelIdentifier=md.coSimulation.modelIdentifier,instanceName='cross')
        fmu.instantiate()
        try:
            fmu.setupExperiment(startTime=start-86400);fmu.enterInitializationMode()
            fmu.setBoolean([vr[v] for v in c['target_activates']]+[vr[c['aux_activate']]],[True]*3)
            fmu.setReal([vr[v] for v in c['target_inputs']]+[vr[c['aux_input']]],[c['target_C']+273.15]*2+[c['aux_value']])
            fmu.exitInitializationMode()
            def observe():
                state=dict(zip(channels,fmu.getReal([vr[v] for v in channels.values()])))
                for k in ['T','outdoor','supply_C']:state[k]-=273.15
                if not all(math.isfinite(v) for v in state.values()):raise ValueError('Nonfinite FMU output')
                return state
            t=start-86400
            for _ in range(int(86400/dt)):
                fmu.doStep(currentCommunicationPoint=t,communicationStepSize=dt);t+=dt
            initial=observe();initial_u=decode(c,initial['supply_C'])
            if controller is not None:controller.prime(initial['T'],initial_u)
            fmu.setReal([vr[c['supply_input']]],[encode(c,initial_u)+273.15]);fmu.setBoolean([vr[c['supply_activate']]],[True])
            for i in range(int(hours*3600/dt)):
                state=observe();previous_u=decode(c,state['supply_C'])
                u=clamp(initial_u+[-.15,.15,0,.25,-.25,.10][(i//15)%6]) if controller is None else controller.step(state['T'],previous_u,i)
                fmu.setReal([vr[c['supply_input']]],[encode(c,u)+273.15])
                fmu.doStep(currentCommunicationPoint=t,communicationStepSize=dt);nxt=observe()
                row=dict(time_s=t,**state,previous_u=previous_u,u=u,next_T=nxt['T'])
                for k in c['power_outputs']:row['next_'+k]=nxt[k]
                rows.append(row);t+=dt
            fmu.terminate()
        finally:fmu.freeInstance()
    path=ROOT/'outputs/boptest_cross_plant'/c['case']/(name+'.csv');path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    return rows,{'trace':str(path.relative_to(ROOT)),'sha256':sha(path),'scored_hours':hours,'warmup_hours':24,
        'wall_seconds':time.perf_counter()-began,'initial_state':initial,'initial_u':initial_u,'metrics':metrics(rows,c),
        'first_30min_mae_C':metrics(rows[:30],c)['mae_C'],'after_30min_mae_C':metrics(rows[30:],c)['mae_C']}


def source_hashes(configs):
    paths=[Path(__file__),CONFIG,ROOT/'digital_twin/control/portable_pi.py',ART.parent/'protocol.md']+[fmu_path(c) for c in configs.values()]
    return {str(p.relative_to(ROOT)):sha(p) for p in paths}

def make(c,fit,q,method):
    g=gains(fit,c['step_s'],q)
    return PortablePI(c['target_C'],c['step_s'],g['kp'],g['ti'],g['b'],hybrid=method=='proposed')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--plant',choices=['air','hydronic'],required=True);name=parser.parse_args().plant
    configs=json.loads(CONFIG.read_text());c=configs[name];ART.mkdir(parents=True,exist_ok=True)
    dest=ART/(name+'.json');freeze=ART/'freeze.json';sources=source_hashes(configs)
    if dest.exists():raise SystemExit('Plant evidence already exists; no overwrite')
    if freeze.exists():
        if json.loads(freeze.read_text())['sources']!=sources:raise SystemExit('Frozen sources changed')
    else:freeze.write_text(json.dumps({'sources':sources,'before_any_generalized_simulation':True},indent=2)+'\n')
    result={'status':'RUNNING','plant':name,'config':c,'freeze_sha256':sha(freeze),'sources':sources,'fits':{},'trials':[],'evaluations':[],'skips':[],'failures':[]}
    def save():
        tmp=dest.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');tmp.replace(dest)
    save()
    try:
        rows,rec=episode(c,'identification',86400,6,None);result['identification']=rec
        for h in [2,6]:
            fit=fit_dynamics(rows[:int(h*3600/c['step_s'])],c['target_C'],c['step_s']);result['fits'][str(h)]=fit
            if fit['status']!='FITTED':result['skips'].append({'budget_h':h,'reason':fit['status']});continue
            for method in ['auto_pi','proposed']:
                for q in [.5,1.]:
                    _,rec=episode(c,f'trial_{h}_{method}_{q}',2*86400,2,make(c,fit,q,method))
                    result['trials'].append(dict(budget_h=h,method=method,q=q,parameters=gains(fit,c['step_s'],q),**rec));save()
                    print(name,'trial',h,method,q,rec['metrics']['mae_C'],flush=True)
        selected=[]
        for h in [2,6]:
            for method in ['auto_pi','proposed']:
                candidates=[r for r in result['trials'] if r['budget_h']==h and r['method']==method]
                if candidates:
                    best=min(candidates,key=lambda r:r['metrics']['mae_C']);selected.append({'budget_h':h,'method':method,'q':best['q'],'trial_trace_sha256':best['sha256']})
        save();selection_path=ART/(name+'_selection.json')
        if selection_path.exists():raise RuntimeError('Selection exists')
        selection_path.write_text(json.dumps({'selected':selected,'sources':sources,'pre_evaluation_result_sha256':sha(dest)},indent=2)+'\n')
        # Preserve the actual pre-evaluation snapshot, since final result will grow.
        (ART/(name+'_adaptation.json')).write_bytes(dest.read_bytes())
        result['selection_sha256']=sha(selection_path);save()
        for day in [10,40]:
            for choice in selected:
                h,method,q=choice['budget_h'],choice['method'],choice['q']
                _,rec=episode(c,f'eval_{day}_{h}_{method}',day*86400,24,make(c,result['fits'][str(h)],q,method))
                result['evaluations'].append(dict(day=day,budget_h=h,adaptation_exposure_h=h+4,method=method,q=q,**rec));save()
                print(name,'eval',day,h,method,rec['metrics']['mae_C'],flush=True)
        result['status']='COMPLETED';save()
    except Exception as exc:
        result['status']='FAILED';result['failures'].append({'type':type(exc).__name__,'message':str(exc)});save();raise

if __name__=='__main__':main()
