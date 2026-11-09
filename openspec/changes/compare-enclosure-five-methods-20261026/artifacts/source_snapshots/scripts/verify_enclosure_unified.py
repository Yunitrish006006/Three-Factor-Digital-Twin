#!/usr/bin/env python3
"""Independent stored-data, scenario, scalar-dynamics and metric audit. No reruns."""
import argparse,csv,hashlib,json,math,random,shutil,tempfile
from pathlib import Path
from statistics import mean
ROOT=Path(__file__).resolve().parents[1]
DEFAULT=ROOT/'openspec/changes/compare-enclosure-five-methods-20261026/artifacts'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(ok,msg):
 if not ok:raise ValueError(msg)
def close(a,b,msg):require(math.isclose(float(a),float(b),abs_tol=1e-8,rel_tol=1e-7),msg)
def percentile(v,q):
 v=sorted(v);k=(len(v)-1)*q;i=int(k);j=min(i+1,len(v)-1);return v[i]+(v[j]-v[i])*(k-i)
def compute(rows,c):
 s=c['settings'];n=len(rows);targets=s['targets_C'];limits=s['limits_C'];dt=s['dt_s']
 temps=[[r['next_cpu_C'],r['next_gpu_C']] for r in rows];errors=[[t[i]-targets[i] for i in range(2)] for t in temps];flat=[x for e in errors for x in e]
 ret={'tracking_mae_C':sum(abs(x) for x in flat)/(2*n),'tracking_rmse_C':math.sqrt(sum(x*x for x in flat)/(2*n)),
 'overtemp_s':dt*sum(any(t[i]>limits[i] for i in range(2)) for t in temps),'fan_energy_proxy_Wh':dt*sum(10*r['pwm']**3 for r in rows)/3600,
 'pwm_total_variation':sum(abs(r['pwm']-r['previous_pwm']) for r in rows),'fallback_n':sum(r['fallback'] for r in rows),'warning_n':sum(r['warning'] for r in rows),'deadline_n':sum(r['deadline'] for r in rows),
 'bounds_violations':sum(r['pwm']<s['pwm_min']-1e-8 or r['pwm']>s['pwm_max']+1e-8 for r in rows),'slew_violations':sum(abs(r['pwm']-r['previous_pwm'])>s['max_delta']+1e-8 for r in rows),'control_p95_s':percentile([r['control_s'] for r in rows],.95),'control_max_s':max(r['control_s'] for r in rows)}
 ret['selection_score']=sum(x*x/25 for x in flat)/(2*n)+.01*sum(r['pwm']**3 for r in rows)/n+1e4*sum(max(t[i]-limits[i],0)**2 for t in temps for i in range(2))/(2*n)
 for i,name in enumerate(['cpu','gpu']):
  ret[name+'_mae_C']=sum(abs(e[i]) for e in errors)/n;ret[name+'_rmse_C']=math.sqrt(sum(e[i]**2 for e in errors)/n);ret['max_'+name+'_C']=max(t[i] for t in temps)
 return ret

def verify(out):
 load=lambda n:json.loads((out/n).read_text())
 f,cali,res,pre=map(load,['freeze.json','calibration.json','result.json','preregistration.json']);c=f['config'];metrics_checked=0;rows_total=0;max_error=0
 require(sha(out/'freeze.json')==res['freeze_sha256'],'freeze hash');require(sha(out/'calibration.json')==f['calibration_sha256'],'calibration hash');require(sha(out/'preregistration.json')==f['preregistration_sha256'],'preregistration hash')
 require(c==pre['config'] and f['sources']==pre['sources'],'preregistered source/config parity')
 for rel,h in f['sources'].items():require(sha(ROOT/rel)==h and sha(out/'source_snapshots'/rel)==h,'source hash '+rel)
 hist=load('historical_hashes.json');require(sha(out/'historical_hashes.json')==pre['historical_sha256'],'history manifest hash')
 for rel,h in hist.items():require(sha(ROOT/rel)==h,'historical evidence changed '+rel)
 ca,ev=load('calibrate_attempt.json'),load('evaluate_attempt.json')
 require(ca['status']==ev['status']=='COMPLETED','phase status');require(ca['started_at']<=pre['utc']<=ca['finished_at']<=ev['started_at'] and f['utc']<=ev['started_at'],'freeze/evaluation chronology')
 expected_cal=set((m,i,s) for m,vs in c['candidates'].items() for i in range(len(vs)) for s in c['seeds']['calibration']);seen_cal=set();seen_eval=set();all_metrics={};input_pairs={}
 calibration_runs=[]
 for method,candidates in cali['candidates'].items():
  require(len(candidates)==3,'three candidates')
  for i,candidate in enumerate(candidates):
   require(candidate['parameters']==c['candidates'][method][i],'candidate params')
   for r in candidate['runs']:
    key=(method,i,r['seed']);require(key not in seen_cal,'duplicate calibration');seen_cal.add(key);require(r['candidate_index']==i and r['parameters']==candidate['parameters'],'calibration parameter parity');calibration_runs.append(r)
   close(candidate['score'],mean(r['metrics']['selection_score'] for r in candidate['runs']),'calibration score')
  chosen=min(enumerate(candidates),key=lambda iv:(iv[1]['score'],iv[0]))[1]['parameters'];require(chosen==f['selected'][method]==cali['selected'][method],'selection')
 require(seen_cal==expected_cal,'calibration design completeness')
 expected_eval={(split,seed,m) for split in ['validation','holdout','plant_holdout','overload'] for seed in c['seeds'][split] for m in c['candidates']}
 for r in res['runs']:
  key=(r['split'],r['seed'],r['method']);require(key not in seen_eval,'duplicate eval');seen_eval.add(key);require(r['parameters']==f['selected'][r['method']],'frozen evaluated parameters')
 require(seen_eval==expected_eval,'evaluation design completeness')
 for run in calibration_runs+res['runs']:
  p=out/run['trace_path'];require(sha(p)==run['trace_sha256'],'trace hash '+run['id'])
  with p.open(newline='') as stream:raw=list(csv.DictReader(stream))
  require(len(raw)==run['n']==c['steps'],'trace rows')
  numeric=['step','time_s','cpu_C','gpu_C','fan','inlet_C','cpu_W','gpu_W','previous_pwm','pwm','next_cpu_C','next_gpu_C','next_fan','raw_pwm','fallback','warning','control_s','deadline']
  rows=[{**row,**{k:float(row[k]) for k in numeric}} for row in raw]
  par={k:list(v) if isinstance(v,list) else v for k,v in c['parameters'].items()}
  if run['split']=='plant_holdout':
   v=c['variants'][c['seeds']['plant_holdout'].index(run['seed'])]
   for k,factor in [('capacities','capacity_factors'),('conductances','conductance_factors'),('fan_gains','fan_gain_factors')]:par[k]=[a*b for a,b in zip(par[k],v[factor])]
   par['fan_tau_s']=v['fan_tau_s']
  state=[58.+run['seed']%3,59.+run['seed']%3,.5];prev=.5;rng=random.Random(run['seed']);cpu,gpu=c['schedules'][run['split']];feedback=c['feedback'];integral=0.;last_error=None;derivative=0.;exogenous=[]
  for i,row in enumerate(rows):
   for k in numeric:require(math.isfinite(row[k]),'finite data')
   require(row['control_s']>=0,'timing');close(row['step'],i,'step');close(row['time_s'],i*c['settings']['dt_s'],'time')
   seg=min(len(cpu)-1,i*len(cpu)//c['steps']);inlet=29.+run['seed']%3-1+1.5*(i>=40)+.5*(i>=80)+rng.uniform(-.2,.2);powers=[max(0.,cpu[seg]+rng.uniform(-5,5)),max(0.,gpu[seg]+rng.uniform(-8,8))]
   for k,v in [('inlet_C',inlet),('cpu_W',powers[0]),('gpu_W',powers[1]),('cpu_C',state[0]),('gpu_C',state[1]),('fan',state[2]),('previous_pwm',prev)]:close(row[k],v,'scenario/state '+k)
   exogenous.append([inlet,*powers]);warning=state[0]>=c['settings']['warnings_C'][0] or state[1]>=c['settings']['warnings_C'][1]
   require(row['warning']==int(warning),'warning rule');require(row['deadline']==int(row['control_s']>=c['settings']['dt_s']),'deadline')
   if run['method']=='fixed':close(row['raw_pwm'],run['parameters']['pwm'],'fixed control')
   if run['method'] in ('pi','pid'):
    e=max(state[0]-60,state[1]-60);rate=0. if last_error is None else (e-last_error)/c['settings']['dt_s'];derivative+=feedback['derivative_alpha']*(rate-derivative);integral+=run['parameters']['ki']*e*c['settings']['dt_s'];last_error=e
    raw_pwm=feedback['bias']+run['parameters']['kp']*e+integral+run['parameters']['kd']*derivative;close(row['raw_pwm'],raw_pwm,'feedback law');integral+=feedback['backcalc']*(row['pwm']-raw_pwm)
   require(bool(row['fallback'])==bool(row['reason']),'fallback reason')
   if run['method']=='mpc' and not row['fallback']:
    require(row['solver_status']=='solved','MPC solver acceptance');require(float(row['primal_residual'])<=1e-5 and float(row['dual_residual'])<=1e-5,'MPC residual acceptance')
   request=1. if warning or row['fallback'] else row['raw_pwm'];expected=min(max(request,max(.2,prev-.1)),min(1.,prev+.1));close(row['pwm'],expected,'common command limiting')
   require(.2-1e-8<=row['pwm']<=1.+1e-8 and abs(row['pwm']-prev)<=.1+1e-8,'input constraints')
   # Scalar plant reconstruction, independent of all production numerical code.
   steps=int(math.ceil(c['settings']['dt_s']));h=c['settings']['dt_s']/steps
   for _ in range(steps):
    oldfan=state[2]
    for node in range(2):state[node]+=h*(powers[node]-(par['conductances'][node]+par['fan_gains'][node]*oldfan)*(state[node]-inlet))/par['capacities'][node]
    state[2]=row['pwm']+(oldfan-row['pwm'])*math.exp(-h/par['fan_tau_s'])
   for k,v in [('next_cpu_C',state[0]),('next_gpu_C',state[1]),('next_fan',state[2])]:max_error=max(max_error,abs(row[k]-v));close(row[k],v,'independent dynamics '+k)
   prev=row['pwm']
  group=(run['split'],run['seed']);exohash=hashlib.sha256(json.dumps(exogenous).encode()).hexdigest();require(group not in input_pairs or input_pairs[group]==exohash,'shared exogenous input');input_pairs[group]=exohash
  m=compute(rows,c)
  require(set(m)==set(run['metrics']),'metric field completeness')
  for k,v in m.items():close(v,run['metrics'][k],'metric '+k);metrics_checked+=1
  all_metrics[run['id']]=m;rows_total+=len(rows)
 for split,methods in res['aggregates'].items():
  for method,a in methods.items():
   subset=[all_metrics[r['id']] for r in res['runs'] if r['split']==split and r['method']==method]
   for k,v in a.items():close(v,mean(x[k] for x in subset),'macro '+k)
  require(res['mae_rankings'][split]==sorted(methods,key=lambda m:(methods[m]['tracking_mae_C'],m)),'MAE ranking')
  keys=['tracking_mae_C','fan_energy_proxy_Wh','overtemp_s'];front=[m for m in methods if not any(all(methods[o][k]<=methods[m][k] for k in keys) and any(methods[o][k]<methods[m][k] for k in keys) for o in methods if o!=m)]
  require(res['pareto'][split]==front,'Pareto frontier')
 return dict(status='PASS',calibration_episodes=len(calibration_runs),evaluation_episodes=len(res['runs']),rows=rows_total,metric_checks=metrics_checked,max_independent_state_error=max_error,historical_files_unchanged=len(hist),paired_schedule_groups=len(input_pairs),result_sha256=sha(out/'result.json'),scope='stored-data metrics/scalar dynamics/feedback replay/solver-gate/source freeze; not independent re-optimization of LQR/MPC')

def self_test(out):
 for kind in ['result','trace']:
  with tempfile.TemporaryDirectory() as tmp:
   dest=Path(tmp)/'copy';shutil.copytree(out,dest)
   p=dest/'result.json';d=json.loads(p.read_text())
   if kind=='result':d['runs'][0]['metrics']['tracking_mae_C']+=1.;p.write_text(json.dumps(d))
   else:
    trace=dest/d['runs'][0]['trace_path'];trace.write_text(trace.read_text().replace('0.0,','99.0,',1))
   try:verify(dest)
   except ValueError:continue
   raise RuntimeError('Failed to reject '+kind+' corruption')
 return 'two corruption fixtures rejected'
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,default=DEFAULT);ap.add_argument('--self-test',action='store_true');args=ap.parse_args();v=verify(args.output_dir)
 if args.self_test:v['negative_checks']=self_test(args.output_dir)
 (args.output_dir/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2))
