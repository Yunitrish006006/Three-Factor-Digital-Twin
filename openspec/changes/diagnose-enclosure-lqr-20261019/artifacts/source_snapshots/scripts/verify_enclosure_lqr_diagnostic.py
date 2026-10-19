"""Stored-observation audit; never refits or reruns a closed-loop study."""
import csv
import json
from pathlib import Path
from statistics import mean
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from digital_twin.enclosure.session import HeatNetwork,SparseObserver,SessionController,Observation,steady_state,command
from verify_enclosure_session_study import sha,require,recompute_metrics,independently_integrate,compare_nested
from run_enclosure_lqr_diagnostic import ARTIFACTS,STATE_NAMES,lqr_probe


def audit(rows,run,config,calibration):
    require(len(rows)==120,'row count')
    method,oracle,exact=config['arms'][run['arm']]
    fitted=HeatNetwork(**calibration[run['panel']]['parameters']);true=HeatNetwork(**config['panels'][run['panel']])
    model=true if exact else fitted
    rng=np.random.default_rng(run['seed']);powers=np.repeat(rng.uniform(.8,3.2,6),20)
    inlets=22+.3*np.sin(2*np.pi*np.arange(120)/120+rng.uniform(0,2*np.pi))
    noise=rng.normal(size=(120,3))*[.1,.1,.005]
    state=np.r_[inlets[0]+np.array([1.5,.5,.2]),.4];previous=.4
    observer=SparseObserver(fitted,float(inlets[0]));controller=SessionController(method,model)
    largest=0.
    for k,r in enumerate(rows):
        obs=Observation.from_row(r)
        require(abs(obs.time_s-5*k)<1e-9 and int(r['step'])==k,'time')
        require(abs(obs.power_W-powers[k])<1e-10 and abs(obs.inlet_C-inlets[k])<1e-10,'schedule')
        current=np.array([float(r[n+'_truth_current'+('_C' if i<3 else '')]) for i,n in enumerate(STATE_NAMES)])
        require(np.allclose(current,state,atol=1e-9,rtol=0),'truth continuity')
        measured=current[[1,2,3]]+noise[k];measured[2]=np.clip(measured[2],0,1)
        require(np.allclose(measured,[obs.plate_C,obs.air_C,obs.fan_fraction],atol=1e-9,rtol=0),'noise provenance')
        estimated=observer.update(measured)
        require(np.allclose(estimated,[float(r[n+'_estimated']) for n in STATE_NAMES],atol=1e-8,rtol=0),'observer state')
        expected=current if oracle else estimated
        require(np.allclose(expected,[float(r[n+'_control']) for n in STATE_NAMES],atol=1e-8,rtol=0),'oracle access/state contract')
        duty,info=controller.step(expected,obs.inlet_C,obs.power_W,previous,observed_plate_air=measured[:2])
        require(abs(duty-float(r['pwm']))<1e-8 and abs(previous-float(r['previous_pwm']))<1e-9,'input-only controller replay')
        require(.2-1e-9<=duty<=1+1e-9 and abs(duty-previous)<=.1+1e-9,'command constraints')
        require(int(r['warning'])==int(info['warning']) and int(r['fallback'])==int(info['fallback']),'warning/fallback')
        if method=='lqr' and not info['fallback']:
            diagnostic=lqr_probe(expected,model,obs.inlet_C,obs.power_W,previous)
            for key,value in diagnostic.items():require(abs(float(r[key])-value)<1e-8,'raw diagnostic '+key)
        else:require(all(float(r[key])==0 for key in ('raw_valid','raw_lqr_pwm','amplitude_clipped','slew_limited')),'non-LQR diagnostics')
        prediction=observer.predict(duty,obs.inlet_C,obs.power_W)
        require(abs(float(r['source_estimate_C'])-estimated[0])<1e-8 and abs(float(r['source_prediction_next_C'])-prediction[0])<1e-8,'estimate/prediction')
        warm=steady_state(true,obs.inlet_C,obs.power_W,.2)[0];cool=steady_state(true,obs.inlet_C,obs.power_W,1.)[0]
        require(int(r['steady_target_outside_range'])==int(not cool<=28<=warm),'steady range diagnostic')
        following=np.array([float(r[n+'_truth_next'+('_C' if i<3 else '')]) for i,n in enumerate(STATE_NAMES)])
        independent=independently_integrate(current,duty,obs.inlet_C,obs.power_W,config['panels'][run['panel']],0.)
        err=float(np.abs(following-independent).max());largest=max(largest,err)
        require(err<1e-5,'independent dynamics')
        require(np.isfinite(float(r['compute_ms'])) and float(r['compute_ms'])>=0,'timing')
        previous,state=duty,following
    m=recompute_metrics(rows,'closed_loop')
    for key in ('amplitude_clipped','slew_limited','steady_target_outside_range'):m[key+'_fraction']=mean(float(r[key]) for r in rows)
    m['control_source_mae_C']=mean(abs(float(r['source_control'])-float(r['source_truth_current_C'])) for r in rows)
    m['raw_valid_steps']=sum(int(r['raw_valid']) for r in rows)
    compare_nested(run['metrics'],m,'metrics')
    return largest


def main():
    load=lambda n:json.loads((ARTIFACTS/n).read_text())
    result,config,calibration,freeze=map(load,('result.json','config.json','calibration.json','freeze.json'))
    require(sha(ARTIFACTS/'config.json')==freeze['config_sha256'],'config freeze')
    require(sha(ARTIFACTS/'calibration.json')==result['calibration_sha256'],'calibration freeze')
    require(sha(ARTIFACTS/'historical_hashes.json')==freeze['historical_manifest_sha256'],'historical manifest')
    for n,h in freeze['source_hashes'].items():require(sha(ROOT/n)==h and sha(ARTIFACTS/'source_snapshots'/n)==h,'source '+n)
    old=load('historical_hashes.json')
    for n,h in old.items():require(sha(ROOT/n)==h,'historical artifact '+n)
    calibration_rows=0
    for panel,c in calibration.items():
        path=ARTIFACTS/f'calibration_{panel}.csv';require(sha(path)==c['csv_sha256'],'calibration csv')
        rows=list(csv.DictReader(path.open()));require(len(rows)==180,'calibration length')
        rng=np.random.default_rng(config['calibration_seeds'][panel]);state=np.array([22.,22.,22.,.4])
        for k,row in enumerate(rows):
            obs=state[[1,2,3]]+rng.normal(size=3)*[.1,.1,.005];obs[2]=np.clip(obs[2],0,1)
            require(np.allclose(obs,[float(row[n]) for n in ('plate_C','air_C','fan_fraction')],atol=2e-6,rtol=0),'calibration observations')
            power=.8 if (k//20)%2==0 else 2.8;duty=.25 if (k//15)%2==0 else .75
            require(float(row['time_s'])==k*5 and float(row['power_W'])==power and float(row['pwm'])==duty and float(row['inlet_C'])==22,'calibration schedule')
            state=independently_integrate(state,duty,22.,power,config['panels'][panel],0.)
        calibration_rows+=len(rows)
    largest=0.;seen=set()
    for run in result['runs']:
        key=(run['panel'],run['seed'],run['arm']);require(key not in seen,'duplicate run');seen.add(key)
        path=ARTIFACTS/run['csv'];require(sha(path)==run['sha256'],'trace hash')
        rows=list(csv.DictReader(path.open()));largest=max(largest,audit(rows,run,config,calibration))
    expected={(p,s,a) for p in config['panels'] for s in config['seeds'] for a in config['arms']}
    require(seen==expected and len(seen)==40 and result['step_count']==4800,'complete factorial')
    aggregate={a:{k:mean(r['metrics'][k] for r in result['runs'] if r['arm']==a) for k in result['runs'][0]['metrics']} for a in config['arms']}
    compare_nested(result['aggregates'],aggregate,'aggregate')
    require(len(result['pairs'])==8 and {(p['panel'],p['seed']) for p in result['pairs']}=={(p,s) for p in config['panels'] for s in config['seeds']},'paired coverage')
    for pair in result['pairs']:
        t={r['arm']:r['metrics']['tracking_mae_C'] for r in result['runs'] if (r['panel'],r['seed'])==(pair['panel'],pair['seed'])}
        compare_nested(pair['tracking_mae_C'],t,'pair')
        values={'model_effect_with_true_state_C':t['truth_fitted']-t['truth_exact'],'model_effect_with_estimated_state_C':t['estimated_fitted']-t['estimated_exact'],
          'state_effect_with_fitted_model_C':t['estimated_fitted']-t['truth_fitted'],'state_effect_with_exact_model_C':t['estimated_exact']-t['truth_exact'],
          'interaction_C':t['estimated_fitted']-t['truth_fitted']-t['estimated_exact']+t['truth_exact']}
        for k,v in values.items():require(abs(pair[k]-v)<1e-9,'contrast '+k)
    for hid,base,var in [('H-ENC-91','truth_fitted','truth_exact'),('H-ENC-92','estimated_fitted','truth_fitted')]:
        d=result['decisions'][hid];b,v=aggregate[base],aggregate[var]
        reduction=1-v['tracking_mae_C']/b['tracking_mae_C'];wins=sum(p['tracking_mae_C'][var]<p['tracking_mae_C'][base] for p in result['pairs'])
        ok=reduction>=.05 and wins>=6 and v['overtemp_s']<=b['overtemp_s'] and v['fallbacks']==b['fallbacks']==0
        compare_nested(d,{'status':'supported' if ok else 'not_supported','reduction_fraction':reduction,'wins_of_8':wins,'baseline':base,'variant':var},hid)
    receipt={'status':'PASS','episodes':40,'rows':4800,'calibration_rows':calibration_rows,'historical_files_unchanged':len(old),
      'max_independent_state_difference':largest,'source_hashes_verified':True,'oracle_access_and_input_replay':'PASS','result_sha256':sha(ARTIFACTS/'result.json')}
    (ARTIFACTS/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
