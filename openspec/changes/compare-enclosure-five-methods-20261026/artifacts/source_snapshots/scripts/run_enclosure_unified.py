#!/usr/bin/env python3
"""Preregister, calibrate and evaluate a new five-method study, without overwrites."""
import argparse,csv,hashlib,json,math,platform,random,shutil,subprocess,sys,time
from collections import defaultdict
from dataclasses import replace
from datetime import datetime,timezone
from pathlib import Path
from statistics import mean
import importlib.metadata
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
import osqp
from digital_twin.control.enclosure_mpc import ThermalParameters,ControlSettings,EnclosurePlant,bounded_command
from digital_twin.control.enclosure_unified import UnifiedController
CHANGE=ROOT/'openspec/changes/compare-enclosure-five-methods-20261026'
SOURCES=['digital_twin/control/enclosure_mpc.py','digital_twin/control/enclosure_control_v2.py','digital_twin/control/enclosure_unified.py',
'scripts/run_enclosure_unified.py','scripts/verify_enclosure_unified.py','tests/test_enclosure_unified.py']+[str((CHANGE/n).relative_to(ROOT)) for n in ['config.json','protocol.md','research.md','design.md','specs.md','reproducibility.md','proposal.md','.openspec.yaml','specs/enclosure-control/spec.md']]
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d,exclusive=False):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x' if exclusive else 'w') as f:json.dump(d,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
def sources():return {p:sha(ROOT/p) for p in SOURCES}
def scenario(config,split,seed):
 rng=random.Random(seed);cpu,gpu=config['schedules'][split]
 for i in range(config['steps']):
  seg=min(len(cpu)-1,i*len(cpu)//config['steps'])
  yield dict(inlet_C=29.+seed%3-1+1.5*(i>=40)+.5*(i>=80)+rng.uniform(-.2,.2),cpu_W=max(0.,cpu[seg]+rng.uniform(-5,5)),gpu_W=max(0.,gpu[seg]+rng.uniform(-8,8)))
def parameters(config,split,seed):
 p=ThermalParameters(**config['parameters'])
 if split=='plant_holdout':
  v=config['variants'][config['seeds'][split].index(seed)]
  p=replace(p,capacities=tuple(a*b for a,b in zip(p.capacities,v['capacity_factors'])),conductances=tuple(a*b for a,b in zip(p.conductances,v['conductance_factors'])),fan_gains=tuple(a*b for a,b in zip(p.fan_gains,v['fan_gain_factors'])),fan_tau_s=v['fan_tau_s'])
 return p
def quantile(x,q):return float(np.quantile(x,q))
def metrics(rows,c):
 s=c['settings'];n=len(rows);dt=s['dt_s'];es=[[r['next_cpu_C']-s['targets_C'][0],r['next_gpu_C']-s['targets_C'][1]] for r in rows];flat=[v for e in es for v in e]
 m=dict(tracking_mae_C=mean(map(abs,flat)),tracking_rmse_C=math.sqrt(mean(v*v for v in flat)),overtemp_s=sum(r['next_cpu_C']>s['limits_C'][0] or r['next_gpu_C']>s['limits_C'][1] for r in rows)*dt,
 fan_energy_proxy_Wh=sum(10*r['pwm']**3 for r in rows)*dt/3600,pwm_total_variation=sum(abs(r['pwm']-r['previous_pwm']) for r in rows),fallback_n=sum(r['fallback'] for r in rows),warning_n=sum(r['warning'] for r in rows),deadline_n=sum(r['deadline'] for r in rows),
 bounds_violations=sum(not s['pwm_min']-1e-8<=r['pwm']<=s['pwm_max']+1e-8 for r in rows),slew_violations=sum(abs(r['pwm']-r['previous_pwm'])>s['max_delta']+1e-8 for r in rows),control_p95_s=quantile([r['control_s'] for r in rows],.95),control_max_s=max(r['control_s'] for r in rows))
 viol=[max(r['next_cpu_C']-s['limits_C'][0],0)**2+max(r['next_gpu_C']-s['limits_C'][1],0)**2 for r in rows]
 m['selection_score']=mean(v*v/25 for v in flat)+.01*mean(r['pwm']**3 for r in rows)+1e4*sum(viol)/(2*n)
 for i,node in enumerate(['cpu','gpu']):
  vs=[r['next_'+node+'_C'] for r in rows];err=[e[i] for e in es]
  m[node+'_mae_C']=mean(map(abs,err));m[node+'_rmse_C']=math.sqrt(mean(v*v for v in err));m['max_'+node+'_C']=max(vs)
 return m

def episode(c,method,values,split,seed):
 nominal=ThermalParameters(**c['parameters']);s=ControlSettings(**c['settings']);p=parameters(c,split,seed)
 plant=EnclosurePlant(p);plant.reset((58.+seed%3,59.+seed%3),.5);ctl=UnifiedController(method,values,nominal,s,c['feedback']);previous=.5;rows=[]
 for index,dist in enumerate(scenario(c,split,seed)):
  x=plant.state.copy();started=time.perf_counter()
  try:u,info=ctl.step(x,dist['inlet_C'],(dist['cpu_W'],dist['gpu_W']),previous)
  except osqp.OSQPException as exc:
   u=bounded_command(s.pwm_max,previous,s);info=dict(fallback=True,reason='osqp_exception',solver_status=type(exc).__name__,primal_residual=None,dual_residual=None,raw_pwm=s.pwm_max,warning=bool(np.any(x[:2]>=s.warnings_C)))
  elapsed=time.perf_counter()-started;deadline=int(elapsed>=s.dt_s)
  if deadline:u=bounded_command(s.pwm_max,previous,s);info.update(fallback=True,reason='deadline')
  nxt=plant.step(u,dist['inlet_C'],(dist['cpu_W'],dist['gpu_W']),s.dt_s)
  rows.append(dict(step=index,time_s=index*s.dt_s,cpu_C=float(x[0]),gpu_C=float(x[1]),fan=float(x[2]),**dist,previous_pwm=previous,pwm=u,next_cpu_C=float(nxt[0]),next_gpu_C=float(nxt[1]),next_fan=float(nxt[2]),raw_pwm=info['raw_pwm'],fallback=int(info['fallback']),warning=int(info['warning']),reason=info['reason'],solver_status=info['solver_status'],primal_residual=info['primal_residual'],dual_residual=info['dual_residual'],control_s=elapsed,deadline=deadline))
  previous=u
 return rows

def save(c,out,method,values,split,seed,index=None):
 rows=episode(c,method,values,split,seed);name=f'{split}_{seed}_{method}'+(f'_candidate_{index}' if index is not None else '')
 p=out/'traces'/f'{name}.csv';p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 return dict(id=name,split=split,method=method,seed=seed,candidate_index=index,parameters=values,n=len(rows),trace_path=str(p.relative_to(out)),trace_sha256=sha(p),metrics=metrics(rows,c))

def aggregate(runs,c):
 agg={}
 for split in ['validation','holdout','plant_holdout','overload']:
  agg[split]={}
  for method in c['candidates']:
   ms=[r['metrics'] for r in runs if r['split']==split and r['method']==method]
   agg[split][method]={k:mean(m[k] for m in ms) for k in ms[0]}
 return agg

def phase(out,name):
 out.mkdir(parents=True,exist_ok=True);mark=out/(name+'_attempt.json');receipt=dict(started_at=now(),status='STARTED',command=sys.argv);write(mark,receipt,True)
 try:
  c=json.loads((CHANGE/'config.json').read_text())
  if name=='calibrate':
   src=sources();history={}
   for prior in ['validate-enclosure-four-controllers-20261005','prototype-sparse-enclosure-transfer-20261006','diagnose-enclosure-lqr-20261019']:
    for p in (ROOT/'openspec/changes'/prior).rglob('*'):
     if p.is_file():history[str(p.relative_to(ROOT))]=sha(p)
   write(out/'historical_hashes.json',history,True)
   write(out/'preregistration.json',dict(utc=now(),config=c,sources=src,historical_sha256=sha(out/'historical_hashes.json')),True)
   for rel in src:
    dest=out/'source_snapshots'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,dest)
   records={};selected={}
   for method,choices in c['candidates'].items():
    records[method]=[]
    for i,v in enumerate(choices):
     rs=[save(c,out,method,v,'calibration',seed,i) for seed in c['seeds']['calibration']]
     records[method].append(dict(parameters=v,score=mean(r['metrics']['selection_score'] for r in rs),runs=rs))
    best=min(enumerate(records[method]),key=lambda iv:(iv[1]['score'],iv[0]))[1];selected[method]=best['parameters'];print('selected',method,selected[method],flush=True)
   write(out/'calibration.json',dict(candidates=records,selected=selected),True)
   if sources()!=src:raise RuntimeError('Source changed during calibration')
   write(out/'freeze.json',dict(utc=now(),sources=src,config=c,selected=selected,calibration_sha256=sha(out/'calibration.json'),preregistration_sha256=sha(out/'preregistration.json'),environment=dict(python=platform.python_version(),**{p:importlib.metadata.version(p) for p in ['numpy','scipy','osqp']}),git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),git_dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip())),True)
  else:
   f=json.loads((out/'freeze.json').read_text())
   if f['sources']!=sources() or f['config']!=c or sha(out/'calibration.json')!=f['calibration_sha256']:raise RuntimeError('Frozen inputs changed')
   runs=[]
   for split in ['validation','holdout','plant_holdout','overload']:
    for seed in c['seeds'][split]:
     for method,values in f['selected'].items():runs.append(save(c,out,method,values,split,seed))
    print('completed',split,flush=True)
   agg=aggregate(runs,c);rankings={s:sorted(v,key=lambda m:(v[m]['tracking_mae_C'],m)) for s,v in agg.items()}
   pareto={}
   for s,v in agg.items():
    keys=['tracking_mae_C','fan_energy_proxy_Wh','overtemp_s'];pareto[s]=[m for m in v if not any(all(v[o][k]<=v[m][k] for k in keys) and any(v[o][k]<v[m][k] for k in keys) for o in v if o!=m)]
   write(out/'result.json',dict(status='COMPLETED_EXPLORATORY_SIMULATION',utc=now(),freeze_sha256=sha(out/'freeze.json'),runs=runs,aggregates=agg,mae_rankings=rankings,pareto=pareto,boundary=c['boundary'],physical='NOT_EVALUATED'),True)
 except BaseException as exc:
  receipt.update(status='FAILED',finished_at=now(),error_type=type(exc).__name__,error=str(exc));write(mark,receipt);raise
 receipt.update(status='COMPLETED',finished_at=now());write(mark,receipt)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--phase',choices=['calibrate','evaluate'],required=True);ap.add_argument('--output-dir',type=Path,default=CHANGE/'artifacts');args=ap.parse_args();phase(args.output_dir,args.phase)
