"""Replay all commands, frozen inputs, selection and held-out-date gates."""
import csv
import json
import math
from run_boptest_startup import source_hashes, CONFIG
from run_boptest_cross_plant import ROOT,sha,metrics
from select_boptest_startup import ART,windows,select,gate
from digital_twin.control.startup_pi import StartupPI


def close(a,b):
    if isinstance(a,dict):
        assert a.keys()==b.keys()
        for k in a:close(a[k],b[k])
    elif isinstance(a,(int,float)) and not isinstance(a,bool):assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-12),(a,b)
    else:assert a==b,(a,b)


def main():
    freeze=ART/'freeze.json';assert json.loads(freeze.read_text())['sources']==source_hashes()
    selection=json.loads((ART/'selection.json').read_text())
    result=dict(status='PASS',plants={},unique_episodes=0,scored_hours=0,warmup_hours=0,wall_seconds=0,source_hashes=source_hashes())
    seen=set()
    for name,c in json.loads(CONFIG.read_text()).items():
        devpath=ART/(name+'_development.json');dev=json.loads(devpath.read_text())
        assert sha(devpath)==selection['development_sources'][str(devpath.relative_to(ROOT))]
        assert select(dev['evaluations'])==selection['selections'][name]
        conf=json.loads((ART/(name+'_confirmation.json')).read_text())
        assert len(dev['evaluations'])==4 and len(conf['evaluations'])==4
        assert [r['band_C'] for r in dev['evaluations']]==[None,.05,.1,.2]
        for data in (dev,conf):
            assert data['status']=='COMPLETED' and data['freeze_sha256']==sha(freeze)
            if data is conf:assert data['selection_sha256']==sha(ART/'selection.json')
            for rec in data['evaluations']:
                p=ROOT/rec['trace'];assert sha(p)==rec['sha256']
                if rec['reused']:
                    assert selection['selections'][name]['band_C'] is None and rec['trace'] in seen
                    base=next(r for r in data['evaluations'] if r['day']==rec['day'] and r['method']=='auto_pi')
                    close(rec['windows'],base['windows']);assert rec['sha256']==base['sha256'];continue
                assert rec['trace'] not in seen;seen.add(rec['trace'])
                with p.open() as f:rows=[{k:float(v) for k,v in row.items()} for row in csv.DictReader(f)]
                assert len(rows)==rec['scored_hours']*3600/c['step_s']
                ctrl=StartupPI(c['target_C'],c['step_s'],data['model'],rec['band_C'])
                ctrl.prime(rec['initial_state']['T'],rec['initial_u'])
                for i,row in enumerate(rows):
                    close(ctrl.step(row['T'],row['previous_u'],i,outdoor=row['outdoor']),row['u'])
                    for k,v in ctrl.diagnostics.items():close(v,row[k])
                    assert 0<=row['u']<=1 and abs(row['correction'])<=.10000000001
                    assert row['handover_mismatch']<1e-10
                    if i>=60:assert row['active']==0 and row['correction']==0
                    if i:close(rows[i-1]['next_T'],row['T'])
                close(windows(rows,c),rec['windows']);close(metrics(rows,c),rec['metrics'])
                assert rec['exit_code']==ctrl.exit_code and rec['exit_min']==ctrl.exit_min
                result['unique_episodes']+=1
                for k in ('scored_hours','warmup_hours','wall_seconds'):result[k]+=rec[k]
        decisions=[]
        for day in (35,70):
            b,a=[r for r in conf['evaluations'] if r['day']==day]
            assert a['band_C']==selection['selections'][name]['band_C']
            close(b['initial_state'],a['initial_state'])
            decisions.append(dict(day=day,reused=a['reused'],**gate(b['windows'],a['windows']),
                                  early_gain_C=b['windows']['early']['mae_C']-a['windows']['early']['mae_C'],
                                  late_gain_C=b['windows']['late']['mae_C']-a['windows']['late']['mae_C']))
        candidate_paths=[ROOT/x['trace'] for x in dev['evaluations'][1:]]
        trajectories=[]
        for trace in candidate_paths:
            with trace.open() as f:trajectories.append([(float(x['u']),float(x['next_T'])) for x in csv.DictReader(f)])
        equal=all(t==trajectories[0] for t in trajectories[1:])
        result['plants'][name]=dict(development_bands_identical_trajectories=equal,
                                   boundary_identified=not equal and selection['selections'][name]['band_C'] is not None and all(x['passed'] for x in decisions),
                                   boundary_note='All bands produce identical physical trajectories; tie-break is not identification.' if equal else 'Different trajectories, but no boundary meets the full development gate.',
                                   selection=selection['selections'][name],confirmation=decisions,
                                   supported_both_dates=all(x['passed'] for x in decisions))
    result['aggregate_simulated_hours']=result['scored_hours']+result['warmup_hours']
    (ART/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='source_hashes'},indent=2))
if __name__=='__main__':main()
