#!/usr/bin/env python3
"""Versioned four-controller experiment. Existing attempts are never overwritten."""
import argparse
import csv
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import random
import subprocess
import sys
import time

import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from digital_twin.control.enclosure_mpc import ThermalParameters, ControlSettings, EnclosurePlant, bounded_command
from digital_twin.control.enclosure_control_v2 import make_controller, prediction_map_v2
CHANGE=ROOT/'openspec/changes/validate-enclosure-four-controllers-20261005'
SOURCES=['digital_twin/control/enclosure_mpc.py','digital_twin/control/enclosure_control_v2.py',
         'scripts/run_enclosure_control_v2.py','scripts/verify_enclosure_control_v2.py',
         'scripts/enclosure_control_v2_requirements.txt']+[str((CHANGE/n).relative_to(ROOT)) for n in ('config.json','protocol.md','research.md')]


def now(): return datetime.now(timezone.utc).isoformat()
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def json_write(path,value,exclusive=False):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x' if exclusive else 'w') as f: json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
def source_hashes(): return {p:sha(ROOT/p) for p in SOURCES}
def load_config(): return json.loads((CHANGE/'config.json').read_text())


def scenario(config,split,seed):
    rng=random.Random(seed)
    cpu,gpu=config['schedules'][split];steps=config['steps']
    for i in range(steps):
        segment=min(len(cpu)-1,i*len(cpu)//steps)
        inlet=29.+(seed%3-1)+1.5*(i>=40)+.5*(i>=80)+rng.uniform(-.2,.2)
        yield {'inlet_C':inlet,'cpu_W':max(0.,cpu[segment]+rng.uniform(-5,5)),
               'gpu_W':max(0.,gpu[segment]+rng.uniform(-8,8))}


def plant_parameters(config,split,seed):
    nominal=ThermalParameters(**config['parameters'])
    if split!='plant_holdout': return nominal
    variant=config['variants'][config['seeds'][split].index(seed)]
    return replace(nominal,capacities=tuple(a*b for a,b in zip(nominal.capacities,variant['capacity_factors'])),
                   conductances=tuple(a*b for a,b in zip(nominal.conductances,variant['conductance_factors'])),
                   fan_gains=tuple(a*b for a,b in zip(nominal.fan_gains,variant['fan_gain_factors'])),
                   fan_tau_s=variant['fan_tau_s'])


def episode(config,method,values,split,seed):
    settings=ControlSettings(**config['settings']);nominal=ThermalParameters(**config['parameters'])
    pars=plant_parameters(config,split,seed)
    plant=EnclosurePlant(pars);plant.reset((58.+seed%3,59.+seed%3),.5)
    ctl=make_controller(method,values,nominal,settings)
    previous=.5;rows=[]
    for index,disturbance in enumerate(scenario(config,split,seed)):
        state=plant.state.copy();powers=(disturbance['cpu_W'],disturbance['gpu_W'])
        started=time.perf_counter()
        u,info=ctl.step(state,disturbance['inlet_C'],powers,previous)
        control_s=time.perf_counter()-started;deadline=int(control_s>=settings.dt_s)
        if deadline:
            u=bounded_command(settings.pwm_max,previous,settings)
            base,mapping=prediction_map_v2(state,disturbance['inlet_C'],powers,nominal,settings)
            pred=base+mapping@np.full(settings.horizon,u)
            info.update(predicted=pred[:2],fallback=True,reason='deadline',accepted_slack_max_C=None,
                        applied_violation_C=float(np.maximum(pred-np.tile(np.array(settings.limits_C)-settings.margin_C,settings.horizon),0.).max()))
        future=plant.step(u,disturbance['inlet_C'],powers,settings.dt_s)
        rows.append({'step':index,'time_s':index*settings.dt_s,'cpu_C':float(state[0]),'gpu_C':float(state[1]),'fan':float(state[2]),
                     **disturbance,'previous_pwm':previous,'pwm':u,'rpm':float(future[2]*pars.max_rpm),
                     'next_fan':float(future[2]),'next_cpu_C':float(future[0]),'next_gpu_C':float(future[1]),
                     'pred_cpu_C':float(info['predicted'][0]),'pred_gpu_C':float(info['predicted'][1]),
                     'fallback':int(info['fallback']),'reason':info['reason'],'solver_status':info['solver_status'],
                     'accepted_slack_max_C':info['accepted_slack_max_C'],'applied_violation_C':info['applied_violation_C'],
                     'safety_override':int(info['safety_override']),'solver_s':info['solver_s'],
                     'primal_residual':info['primal_residual'],'dual_residual':info['dual_residual'],
                     'control_s':control_s,'deadline':deadline})
        previous=u
    return rows


def metrics(rows,config):
    s=config['settings'];dt=s['dt_s']
    temp=np.array([[r['next_cpu_C'],r['next_gpu_C']] for r in rows]);pred=np.array([[r['pred_cpu_C'],r['pred_gpu_C']] for r in rows])
    error=temp-s['targets_C'];violation=np.maximum(temp-s['limits_C'],0.)
    u=np.array([r['pwm'] for r in rows]);delta=u-np.array([r['previous_pwm'] for r in rows])
    timings=np.array([r['control_s'] for r in rows]);within=np.all(np.abs(error)<=2.,axis=1)
    window=int(np.ceil(60./dt));band=None
    for i in range(len(rows)-window+1):
        if within[i:i+window].all(): band=(i+1)*dt;break
    accepted=[r['accepted_slack_max_C'] for r in rows if r['accepted_slack_max_C'] is not None]
    m={'tracking_mae_C':float(np.abs(error).mean()),'tracking_rmse_C':float(np.sqrt((error**2).mean())),
       'prediction_mae_C':float(np.abs(pred-temp).mean()),'prediction_rmse_C':float(np.sqrt(((pred-temp)**2).mean())),
       'overtemp_s':float(np.any(violation>0,axis=1).sum()*dt),'pwm_total_variation':float(np.abs(delta).sum()),
       'bounds_violations':int(((u<s['pwm_min']-1e-8)|(u>s['pwm_max']+1e-8)).sum()),
       'slew_violations':int((np.abs(delta)>s['max_delta']+1e-8).sum()),
       'fan_energy_proxy_Wh':float((10*u**3).sum()*dt/3600.),
       'fallback_n':sum(r['fallback'] for r in rows),'safety_override_n':sum(r['safety_override'] for r in rows),
       'deadline_n':sum(r['deadline'] for r in rows),'accepted_slack_max_C':max(accepted) if accepted else None,
       'applied_violation_max_C':max(r['applied_violation_C'] for r in rows),
       'control_p50_s':float(np.quantile(timings,.5)),'control_p95_s':float(np.quantile(timings,.95)),
       'control_max_s':float(timings.max()),'solver_p95_s':float(np.quantile([r['solver_s'] for r in rows],.95)),
       'band_entry_60s_s':band,'selection_score':float((error**2/25).mean()+.01*(u**3).mean()+1e4*(violation**2).mean()),
       'whole_system_power_W':None,'throttling_time_s':None}
    for i,node in enumerate(('cpu','gpu')):
        m.update({node+'_mae_C':float(np.abs(error[:,i]).mean()),node+'_rmse_C':float(np.sqrt((error[:,i]**2).mean())),
                  'max_'+node+'_C':float(temp[:,i].max()),node+'_overtemp_s':float((violation[:,i]>0).sum()*dt)})
    return m


def numerical_hash(rows):
    ignored={'control_s','solver_s'}
    return hashlib.sha256(json.dumps([{k:v for k,v in row.items() if k not in ignored} for row in rows],sort_keys=True,allow_nan=False).encode()).hexdigest()


def save_episode(out,config,method,values,split,seed,candidate_index=None):
    started=time.perf_counter();rows=episode(config,method,values,split,seed)
    name=f'{split}_{seed}_{method}'+(f'_candidate_{candidate_index}' if candidate_index is not None else '')
    path=out/'traces'/f'{name}.csv';path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    return {'id':name,'method':method,'split':split,'seed':seed,'candidate_index':candidate_index,'parameters':values,
            'n':len(rows),'trace_path':str(path.relative_to(out)),'trace_sha256':sha(path),
            'numerical_sha256':numerical_hash(rows),'metrics':metrics(rows,config),'episode_wall_s':time.perf_counter()-started}


def aggregate(runs,config):
    groups={}
    for split in ('validation','holdout','plant_holdout','overload'):
        groups[split]={}
        for method in config['candidates']:
            subset=[r['metrics'] for r in runs if r['split']==split and r['method']==method]
            group={k:sum(m[k] for m in subset)/len(subset) if all(m[k] is not None for m in subset) else None for k in subset[0]}
            group.update(episodes_n=len(subset),band_entry_60s_achieved_n=sum(m['band_entry_60s_s'] is not None for m in subset))
            groups[split][method]=group
    return groups


def decisions(runs,agg,config):
    healthy=all(r['metrics']['bounds_violations']==0 and r['metrics']['slew_violations']==0
                and r['metrics']['control_p95_s']<config['settings']['dt_s'] and r['metrics']['fallback_n']/r['n']<=.05 for r in runs)
    d={'H-CTRL-01':'SUPPORTED_SIMULATION_ONLY' if healthy else 'NOT_SUPPORTED'}
    for comparator,hypothesis in (('pid','H-CTRL-02'),('lqr','H-CTRL-03')):
        h=agg['holdout'];gain=(h[comparator]['tracking_mae_C']-h['mpc']['tracking_mae_C'])/h[comparator]['tracking_mae_C']
        safe=all(next(r['metrics']['overtemp_s'] for r in runs if r['split']=='holdout' and r['seed']==seed and r['method']=='mpc')<=
                 next(r['metrics']['overtemp_s'] for r in runs if r['split']=='holdout' and r['seed']==seed and r['method']==comparator) for seed in config['seeds']['holdout'])
        d[hypothesis]='SUPPORTED_SIMULATION_ONLY' if gain>=.05 and safe else 'NOT_SUPPORTED'
        d['holdout_relative_mae_gain_vs_'+comparator]=gain
    d.update(physical_enclosure='NOT_EVALUATED',E8='NOT_EVALUATED',NTC='NOT_EVALUATED',boundary=config['boundary'])
    return d


def calibrate(out):
    config=load_config();records={};selected={}
    for method,choices in config['candidates'].items():
        records[method]=[]
        for index,values in enumerate(choices):
            runs=[save_episode(out,config,method,values,'calibration',seed,index) for seed in config['seeds']['calibration']]
            score=sum(r['metrics']['selection_score'] for r in runs)/len(runs)
            records[method].append({'parameters':values,'score':score,'runs':runs})
        best=min(enumerate(records[method]),key=lambda pair:(pair[1]['score'],pair[0]))
        selected[method]=best[1]['parameters'];print('selected',method,selected[method],best[1]['score'],flush=True)
    json_write(out/'calibration.json',{'candidates':records,'selected':selected},True)
    sources=source_hashes()
    for path in sources:
        dest=out/'source_snapshots'/path;dest.parent.mkdir(parents=True,exist_ok=True)
        with dest.open('xb') as f:f.write((ROOT/path).read_bytes())
    freeze={'status':'FROZEN_BEFORE_EVALUATION','registered_at':now(),'config':config,'selected':selected,'sources':sources,
            'calibration_sha256':sha(out/'calibration.json'),'environment':{'python':platform.python_version(),**{p:importlib.metadata.version(p) for p in ('numpy','scipy','osqp')}},
            'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'git_dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()),'boundary':config['boundary']}
    json_write(out/'freeze.json',freeze,True)


def evaluate(out):
    freeze=json.loads((out/'freeze.json').read_text())
    if freeze['sources']!=source_hashes() or freeze['config']!=load_config() or freeze['calibration_sha256']!=sha(out/'calibration.json'):
        raise ValueError('Sources/config/calibration changed after freeze')
    config=freeze['config'];runs=[]
    for split in ('validation','holdout','plant_holdout','overload'):
        for seed in config['seeds'][split]:
            for method,values in freeze['selected'].items():runs.append(save_episode(out,config,method,values,split,seed))
        print('completed',split,flush=True)
    agg=aggregate(runs,config)
    json_write(out/'result.json',{'status':'COMPLETED_EXPLORATORY_ASSUMED_MODEL_SIMULATION','evaluated_at':now(),
                                'freeze_sha256':sha(out/'freeze.json'),'runs':runs,'aggregates':agg,'decisions':decisions(runs,agg,config),'boundary':config['boundary']},True)
    print(json.dumps(agg['holdout'],indent=2),flush=True)


def run_phase(out,phase):
    out.mkdir(parents=True,exist_ok=True)
    # Spell stable marker names explicitly; create before reading any episode.
    marker=out/('calibration_attempt.json' if phase=='calibrate' else 'evaluation_attempt.json')
    record={'status':'STARTED','started_at':now(),'command':sys.argv}
    json_write(marker,record,True)
    try:(calibrate if phase=='calibrate' else evaluate)(out)
    except BaseException as error:
        record.update(status='FAILED',finished_at=now(),error_type=type(error).__name__,error=str(error));json_write(marker,record);raise
    record.update(status='COMPLETED',finished_at=now());json_write(marker,record)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--phase',choices=['calibrate','evaluate'],required=True)
    parser.add_argument('--output-dir',type=Path,default=CHANGE/'artifacts');args=parser.parse_args();run_phase(args.output_dir,args.phase)
if __name__=='__main__':main()
