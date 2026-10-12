"""Read-only full audit; independent truth/metrics/selection, input-only replay."""
import copy
import csv
from datetime import datetime
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
from digital_twin.enclosure.calibrated_session import (
    ThermalPathParameters, StructureObserver, CalibratedEnclosureSession, visible_errors, BOUNDS,
)
from digital_twin.enclosure.session import Observation
from verify_enclosure_session_study import sha, require, independently_integrate, recompute_metrics, compare_nested

ARTIFACTS=ROOT/'openspec/changes/select-enclosure-structure-20261012/artifacts'
OPEN=('S_physics','S_corrected','selected_physics','selected_corrected')
CLOSED=('S_pi','selected_pi','S_rank_h6','selected_rank_h6')


def audit_calibration(records,fit,plant):
    require(len(records)==180,'Calibration count')
    require(fit['training_rows']==120 and fit['selection_rows']==60 and fit['trial_count']==2
            and not fit['refit_after_selection'] and not fit['source_reference_input'],'Selection/training contract')
    require(fit['selection_channels']==['plate_C','air_C','fan_fraction'],'Hidden truth in selection')
    rng,state=np.random.default_rng(612700),np.array([22.,22.,22.,.4])
    obs=[]; duties=[]
    for k,row in enumerate(records):
        require(set(row)==set(Observation.__dataclass_fields__)|{'pwm'},'Calibration column contract')
        item=Observation.from_row(row); duty=float(row['pwm'])
        power=.8 if (k//20)%2==0 else 2.8
        expected=state[[1,2,3]]+rng.normal(size=3)*[.1,.1,.005]
        expected[2]=np.clip(expected[2],0,1)
        require(item.time_s==5*k and item.inlet_C==22 and item.power_W==power
                and duty==(.25 if (k//15)%2==0 else .75),'Calibration schedule/cadence')
        require(np.allclose([item.plate_C,item.air_C,item.fan_fraction],expected,rtol=0,atol=1e-7),'Calibration provenance')
        state=independently_integrate(state,duty,22.,power,plant,plant['source_air'])
        obs.append(item); duties.append(duty)
    for structure,v in fit['candidates'].items():
        require(1<=v['nfev']<=40 and v['residual_calls']>=v['nfev'],'Fit budget')
        require(v['fallback']==(not v['success']) and v['wall_time_s']>=0,'Fit fallback/cost')
        values=np.array(v['fitted_values']); low,high=map(np.array,BOUNDS[structure])
        require(len(values)==len(low) and np.all(values>=low) and np.all(values<=high),'Fit bounds')
        model=ThermalPathParameters(**v['parameters'])
        errors=visible_errors(model,obs,duties)
        require(np.isclose(v['training_score'],np.mean(errors[:120]**2),rtol=1e-10)
                and np.isclose(v['selection_score'],np.mean(errors[120:]**2),rtol=1e-10),'Selection score corruption')
        if not v['success']:
            require(model==ThermalPathParameters(),'Failed fit must use nominal fallback')
    s,f=fit['candidates']['S'],fit['candidates']['F']
    expected='F' if f['success'] and np.isfinite(f['selection_score']) and f['selection_score']<=.95*s['selection_score'] else 'S'
    require(fit['selected_structure']==expected,'Selection rule corruption')


def audit_trace(rows,run,config,calibration):
    require(len(rows)==120,'Trace count')
    rig=config['rigs'][run['rig']]; plant=rig['parameters']
    require(run['split']==rig['split'] and run['seed'] in config['seeds'][rig['split']],'Split identity')
    rng=np.random.default_rng(run['seed']); powers=np.repeat(rng.uniform(.8,3.2,6),20)
    phase=rng.uniform(0,2*np.pi); inlets=22+.3*np.sin(2*np.pi*np.arange(120)/120+phase)
    noise=rng.normal(size=(120,3))*[.1,.1,.005]; state=np.r_[inlets[0]+[1.5,.5,.2],.4]
    fit=calibration[run['rig']]; key='S' if run['method'].startswith('S_') else fit['selected_structure']
    model=ThermalPathParameters(**fit['candidates'][key]['parameters'])
    session=CalibratedEnclosureSession(model,float(inlets[0]),'pi' if run['method'].endswith('_pi') else 'rank_h6') if run['task']=='closed_loop' else None
    observer=StructureObserver(model,float(inlets[0]),correction=run['method'].endswith('_corrected')) if session is None else None
    previous,maximum=.4,0.
    for k,row in enumerate(rows):
        obs=Observation.from_row(row)
        require(int(row['step'])==k and obs.time_s==5*k,'Timestamp corruption')
        require(abs(obs.power_W-powers[k])<1e-10 and abs(obs.inlet_C-inlets[k])<1e-10,'Workload provenance')
        current=np.array([float(row[n]) for n in ('source_truth_current_C','plate_truth_current_C','air_truth_current_C','fan_truth_current')])
        require(np.allclose(current,state,atol=1e-8,rtol=0),'Truth continuity corruption')
        measured=current[[1,2,3]]+noise[k]; measured[2]=np.clip(measured[2],0,1)
        require(np.allclose([obs.plate_C,obs.air_C,obs.fan_fraction],measured,atol=1e-10,rtol=0),'Noise/observation provenance')
        duty=float(row['pwm'])
        require(abs(float(row['previous_pwm'])-previous)<1e-9,'Previous command continuity')
        if session:
            output=session.process(obs)
            require(.2-1e-9<=duty<=1+1e-9 and abs(duty-previous)<=.1+1e-9,'Command violation')
            require(int(row['warning'])==int(max(float(row['source_estimate_C']),obs.plate_C,obs.air_C)>=29.5),'Raw warning masked')
        else:
            estimate=observer.update([obs.plate_C,obs.air_C,obs.fan_fraction])
            require(duty==(.4 if (k//25)%2==0 else .8),'Open-loop command')
            prediction=observer.predict(duty,obs.inlet_C,obs.power_W)
            output={'source_estimate_C':estimate[0],'source_prediction_next_C':prediction[0],'pwm':duty,'warning':0,'fallback':0}
        for key in ('source_estimate_C','source_prediction_next_C','pwm','warning','fallback'):
            require(abs(float(row[key])-float(output[key]))<1e-7,'Input-only replay: '+key)
        require(np.isfinite(float(row['compute_ms'])) and float(row['compute_ms'])>=0,'Compute time')
        following=np.array([float(row[n]) for n in ('source_truth_next_C','plate_truth_next_C','air_truth_next_C','fan_truth_next')])
        independent=independently_integrate(current,duty,obs.inlet_C,obs.power_W+.15,plant,plant['source_air'])
        difference=float(np.max(np.abs(following-independent)))
        require(difference<1e-5,'Independent dynamics corruption')
        maximum=max(maximum,difference); previous,state=duty,following
    return maximum


def verify(artifacts=ARTIFACTS):
    artifacts=Path(artifacts)
    config,calibration,result,freeze=[json.loads((artifacts/n).read_text()) for n in ('config.json','calibration.json','result.json','freeze.json')]
    require(datetime.fromisoformat(freeze['utc'])<datetime.fromisoformat(result['completed_utc']),'Freeze order')
    require(result['run_count']==96 and result['step_count']==11520 and len(result['runs'])==96,'Design count')
    require(tuple(config['open_methods'])==OPEN and tuple(config['closed_methods'])==CLOSED,'Comparators')
    require(config['seeds']=={'validation':[612711,612712],'holdout':[612721,612722]},'Preregistered seeds')
    for relative,value in freeze['source_hashes'].items():
        require(sha(ROOT/relative)==value and sha(artifacts/'source_snapshots'/relative)==value,'Frozen source drift: '+relative)
    for relative,value in freeze['input_hashes'].items():
        require(sha(artifacts/relative)==value,'Frozen input drift: '+relative)
    history=json.loads((artifacts/'historical_manifest.json').read_text())
    for relative,value in history.items():
        require(sha(ROOT/relative)==value,'Historical artifact drift: '+relative)
    for rig,fit in calibration.items():
        with (artifacts/f'calibration_{rig}.csv').open(newline='') as stream:
            audit_calibration(list(csv.DictReader(stream)),fit,config['rigs'][rig]['parameters'])
    seen,maximum=set(),0.
    for run in result['runs']:
        identity=(run['task'],run['rig'],run['seed'],run['method'])
        require(identity not in seen,'Duplicate episode'); seen.add(identity)
        path=artifacts/run['csv']; require(sha(path)==run['sha256'],'Trace hash')
        with path.open(newline='') as stream:
            rows=list(csv.DictReader(stream))
        compare_nested(recompute_metrics(rows,run['task']),run['metrics'],'Independent metrics')
        maximum=max(maximum,audit_trace(rows,run,config,calibration))
    expected={(task,rig,seed,method) for rig,v in config['rigs'].items() for seed in config['seeds'][v['split']]
              for task,methods in [('open_loop',OPEN),('closed_loop',CLOSED)] for method in methods}
    require(seen==expected,'Complete design')
    for task,methods in [('open_loop',OPEN),('closed_loop',CLOSED)]:
        for split in config['seeds']:
            for method in methods:
                items=[r['metrics'] for r in result['runs'] if (r['task'],r['split'],r['method'])==(task,split,method)]
                macro={k:float(np.mean([v[k] for v in items])) for k in items[0]}
                compare_nested(macro,result['aggregates'][task][split][method],'Macro metrics')
    h=result['aggregates']['open_loop']['holdout']; c=result['aggregates']['closed_loop']['holdout']
    gain=1-h['selected_corrected']['source_mae_C']/h['S_corrected']['source_mae_C']; wins=0
    for rig,v in config['rigs'].items():
        if v['split']!='holdout':
            continue
        for seed in config['seeds']['holdout']:
            values={r['method']:r['metrics']['source_mae_C'] for r in result['runs'] if (r['task'],r['rig'],r['seed'])==('open_loop',rig,seed)}
            wins+=values['selected_corrected']<values['S_corrected']
    tracking=1-c['selected_rank_h6']['tracking_mae_C']/c['S_rank_h6']['tracking_mae_C']
    expected_decisions={'H-ENC-71':'supported' if gain>=.1 and wins>=4 else 'not_supported',
        'H-ENC-72':'supported' if tracking>=.05 and c['selected_rank_h6']['overtemp_s']<=c['S_rank_h6']['overtemp_s']
        and c['selected_rank_h6']['fan_energy_proxy_Wh']<=1.2*c['S_rank_h6']['fan_energy_proxy_Wh'] else 'not_supported',
        'source_mae_reduction_fraction':gain,'source_wins_of_6':int(wins),'tracking_reduction_fraction':tracking}
    compare_nested(expected_decisions,result['decisions'],'Decisions')
    require(all(result[k]=='NOT_EVALUATED' for k in ('physical_identification','physical_actuation','humidity_light_transfer')),'Evidence scope')
    sample=next(r for r in result['runs'] if r['task']=='closed_loop' and r['method']=='selected_rank_h6')
    with (artifacts/sample['csv']).open(newline='') as stream:
        original=list(csv.DictReader(stream))
    rejected=[]
    for mutation in ('timestamp','coordinated_truth','fan_endpoint','raw_observation'):
        rows=copy.deepcopy(original)
        if mutation=='timestamp': rows[1]['time_s']='6'
        elif mutation=='coordinated_truth':
            for row in rows:
                for key in ('source_truth_current_C','source_truth_next_C'): row[key]=str(float(row[key])+1)
        elif mutation=='fan_endpoint': rows[0]['fan_truth_next']='.99'
        else: rows[0]['plate_C']='45'
        try: audit_trace(rows,sample,config,calibration)
        except ValueError: rejected.append(mutation)
        else: raise ValueError('Accepted corruption: '+mutation)
    wrong=copy.deepcopy(sample['metrics']); wrong['source_mae_C']+=1
    try: compare_nested(recompute_metrics(original,sample['task']),wrong,'Corrupt metrics')
    except ValueError: rejected.append('metrics')
    bad=copy.deepcopy(calibration[sample['rig']]); bad['selected_structure']='F' if bad['selected_structure']=='S' else 'S'
    with (artifacts/f'calibration_{sample["rig"]}.csv').open(newline='') as stream:
        records=list(csv.DictReader(stream))
    try: audit_calibration(records,bad,config['rigs'][sample['rig']]['parameters'])
    except ValueError: rejected.append('selection')
    require(len(rejected)==6,'Mutation probes')
    return {'status':'PASS','episodes':96,'rows':11520,'calibration_rows':1080,
            'historical_files_unchanged':len(history),'max_independent_state_difference':maximum,
            'mutation_rejections':rejected,'scope':'Full metric/selection/commissioning/dynamics audit and input-only replay. No refitting or study rerun.'}


if __name__=='__main__':
    report=verify()
    (ARTIFACTS/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
