"""Noise-aware command smoothing and measured applied-action observer."""
import argparse, csv, json, math, random, tempfile, time
from pathlib import Path
from run_boptest_rapid_pi import DT,TARGET,CHANNELS,FMU,ROOT,sha,clip,metrics
from run_boptest_transfer import ObserverPI, HandoverPI
CHANGE=ROOT/'openspec/changes/reduce-boptest-command-jitter'
ART=CHANGE/'artifacts'
PRIOR=ROOT/'openspec/changes/pilot-boptest-rapid-pi/artifacts'
OUT=ROOT/'outputs/boptest_jitter'

class SmoothObserver(ObserverPI):
    def __init__(self,kp,ti,b,alpha):
        super().__init__(kp,ti,b)
        if not 0<alpha<=1: raise ValueError('invalid alpha')
        self.alpha=alpha
    def prime(self,state):
        super().prime(state)
        self.filtered_u=self.first
    def __call__(self,state,index):
        if index>0: self.previous_u=state['supply']
        raw=super().__call__(state,index)
        if index==0: return raw
        self.filtered_u=clip(self.filtered_u+self.alpha*(raw-self.filtered_u))
        self.integral+=.1*(self.filtered_u-raw)
        return self.filtered_u

def episode(name, start, hours, controller, noise_sd=0.0, delay=0):
    rng = random.Random(52000 + int(start / 86400))
    from fmpy import extract, read_model_description
    from fmpy.fmi2 import FMU2Slave
    began = time.perf_counter()
    md = read_model_description(str(FMU), validate=False)
    vr = {v.name: v.valueReference for v in md.modelVariables}
    rows = []
    with tempfile.TemporaryDirectory(prefix='boptest-') as temp:
        extract(str(FMU), unzipdir=temp)
        fmu = FMU2Slave(guid=md.guid, unzipDirectory=temp,
                        modelIdentifier=md.coSimulation.modelIdentifier,
                        instanceName='pilot')
        fmu.instantiate()
        try:
            fmu.setupExperiment(startTime=start - 86400)
            fmu.enterInitializationMode()
            fmu.setBoolean([vr['con_oveTSetHea_activate'], vr['con_oveTSetCoo_activate']], [True, True])
            fmu.setReal([vr['con_oveTSetHea_u'], vr['con_oveTSetCoo_u']], [TARGET + 273.15] * 2)
            fmu.exitInitializationMode()

            def observe():
                values = dict(zip(CHANNELS, fmu.getReal([vr[v] for v in CHANNELS.values()])))
                for k in ('T', 'outdoor', 'supply'):
                    values[k] -= 273.15
                if not all(math.isfinite(v) for v in values.values()):
                    raise ValueError('nonfinite FMU measurement')
                return values

            t = start - 86400
            for _ in range(int(86400 / DT)):
                fmu.doStep(currentCommunicationPoint=t, communicationStepSize=DT)
                t += DT
            outgoing = observe()
            first_noise = rng.gauss(0, noise_sd) if noise_sd else 0.0
            measured_outgoing = dict(outgoing, T=outgoing['T'] + first_noise)
            if hasattr(controller, 'prime'):
                controller.prime(measured_outgoing)
            if controller is not None:
                fmu.setReal([vr['fcu_oveTSup_u']], [clip(outgoing['supply']) + 273.15])
                fmu.setBoolean([vr['fcu_oveFan_activate'], vr['fcu_oveTSup_activate']], [True, True])
                fmu.setReal([vr['fcu_oveFan_u']], [0.5])
            initial_applied = clip(measured_outgoing['T'] + measured_outgoing['fan']/.5*(measured_outgoing['supply']-measured_outgoing['T']))
            queue = [initial_applied] * delay
            for i in range(int(hours * 3600 / DT)):
                state = observe()
                noise = first_noise if i == 0 else (rng.gauss(0, noise_sd) if noise_sd else 0.0)
                measured = dict(state, T=state['T'] + noise)
                command = state['supply'] if controller is None else clip(controller(measured, i))
                queue.append(command)
                applied = queue.pop(0)
                if controller is not None:
                    fmu.setReal([vr['fcu_oveTSup_u']], [applied + 273.15])
                fmu.doStep(currentCommunicationPoint=t, communicationStepSize=DT)
                nxt = observe()
                row = dict(time_s=t, **state, measurement_T=measured['T'], noise_C=noise, command=command, applied_command=applied, next_T=nxt['T'])
                for k in ('heat_W', 'cool_W', 'fan_W'):
                    row['next_' + k] = nxt[k]
                rows.append(row)
                t += DT
            fmu.terminate()
        finally:
            fmu.freeInstance()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / (name + '.csv')
    with path.open('w') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return rows, {'trace': str(path.relative_to(ROOT)), 'sha256': sha(path),
                  'wall_seconds_including_warmup': time.perf_counter() - began,
                  'common_warmup_hours': 24, 'scored_hours': hours, 'outgoing': outgoing,
                  'delay_steps': delay, 'initial_applied': initial_applied,
                  'applied_total_variation_C': sum(abs(a['applied_command']-b['applied_command']) for a,b in zip(rows,rows[1:])),
                  'initial_30min_mae_C': metrics(rows[:30])['mae_C'],
                  'after_30min_mae_C': metrics(rows[30:])['mae_C'], 'metrics': metrics(rows)}

def source_hashes():
    return {str(p.relative_to(ROOT)):sha(p) for p in (Path(__file__),ROOT/'scripts/run_boptest_transfer.py',ROOT/'scripts/run_boptest_rapid_pi.py',CHANGE/'protocol.md',PRIOR/'result.json',PRIOR/'result_v2.json',FMU)}

def make_controller(name):
    prior=json.loads((PRIOR/'result_v2.json').read_text());kp,ti=prior['kp'],prior['ti']
    b=json.loads((PRIOR/'result.json').read_text())['fits']['2']['coefficients'][1]
    if name=='v4':return ObserverPI(kp,ti,b)
    if name=='grid':return HandoverPI(6,300)
    return SmoothObserver(kp,ti,b,{'aware1':1,'smooth06':.6,'smooth035':.35}[name])

def select(records):
    base={(r['day'],r['delay_steps']):r for r in records if r['controller']=='v4'}
    baseline=sum(r['metrics']['command_total_variation_C'] for r in base.values())/len(base)
    qualified=[]
    for name in ('aware1','smooth06','smooth035'):
        own=[r for r in records if r['controller']==name]
        ok=len(own)==4
        for r in own:
            a,b=r['metrics'],base[r['day'],r['delay_steps']]['metrics']
            ok &= a['mae_C']<=b['mae_C']+.02 and a['max_abs_error_C']<=b['max_abs_error_C']+.2
        variation=sum(r['metrics']['command_total_variation_C'] for r in own)/len(own)
        if ok and variation<=baseline*.8:qualified.append((variation,name))
    return min(qualified)[1] if qualified else 'v4'

def main():
    global OUT
    parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=['development','transfer'],required=True);phase=parser.parse_args().phase
    ART.mkdir(parents=True,exist_ok=True);dest=ART/(phase+'.json');selpath=ART/'selection.json'
    if dest.exists():raise SystemExit('Existing evidence cannot be overwritten')
    sources=source_hashes()
    if phase=='development':
        names=['v4','aware1','smooth06','smooth035'];cases=[(d,.05,delay) for d in (95,245) for delay in (0,1)]
    else:
        selection=json.loads(selpath.read_text())
        if selection['sources']!=sources or selection['development_sha256']!=sha(ART/'development.json'):raise SystemExit('Frozen sources changed')
        names=list(dict.fromkeys(['v4',selection['selected'],'grid']));cases=[(d,n,l) for d in (65,155,275) for n,l in ((0,0),(.05,1))]
    OUT=ROOT/'outputs/boptest_jitter'/phase
    result={'status':'RUNNING','phase':phase,'sources':sources,'cases':cases,'controllers':names,'records':[],'failures':[],'selection_sha256':sha(selpath) if phase=='transfer' else None}
    def save():
        tmp=dest.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');tmp.replace(dest)
    save()
    try:
        for day,noise,delay in cases:
            for name in names:
                _,rec=episode(f'day{day}_noise{noise}_delay{delay}_{name}',day*86400,24,make_controller(name),noise,delay)
                result['records'].append(dict(day=day,noise_sd_C=noise,controller=name,**rec));save()
                print(phase,day,delay,name,rec['metrics']['mae_C'],rec['metrics']['command_total_variation_C'],flush=True)
        result['status']='COMPLETED';save()
        if phase=='development':
            if selpath.exists():raise RuntimeError('Selection exists')
            sel={'selected':select(result['records']),'sources':sources,'development_sha256':sha(dest)}
            selpath.write_text(json.dumps(sel,indent=2)+'\n');print('SELECTED',sel['selected'],flush=True)
    except Exception as exc:
        result['status']='FAILED';result['failures'].append(str(exc));save();raise

if __name__=='__main__':main()
