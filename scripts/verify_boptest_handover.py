"""Replay predictive study and independently preserve reused baseline provenance."""
import csv,json
from run_boptest_handover import source_hashes,CONFIG
from run_boptest_cross_plant import ROOT,sha,metrics
from select_boptest_handover import ART,windows,select,gate
from verify_boptest_startup import close
from digital_twin.control.handover_pi import HandoverPI
from digital_twin.control.startup_pi import StartupPI

def main():
    freeze=ART/'freeze.json';assert json.loads(freeze.read_text())['sources']==source_hashes()
    selection=json.loads((ART/'selection.json').read_text())
    result=dict(status='PASS',plants={},unique_episodes=0,reused_records=0,scored_hours=0,warmup_hours=0,wall_seconds=0,sources=source_hashes())
    seen=set()
    for name,c in json.loads(CONFIG.read_text()).items():
        devpath=ART/(name+'_development.json');dev=json.loads(devpath.read_text())
        assert sha(devpath)==selection['development_sources'][str(devpath.relative_to(ROOT))]
        assert select(dev['evaluations'])==selection['selections'][name]
        conf=json.loads((ART/(name+'_confirmation.json')).read_text())
        assert [r['policy'] for r in dev['evaluations']]==[None,'15_taper','15_retain','55_taper','55_retain']
        assert [r['day'] for r in conf['evaluations']]==[48,48,83,83]
        trajectories={};snapshots=[]
        for data in (dev,conf):
            assert data['status']=='COMPLETED' and data['freeze_sha256']==sha(freeze)
            if data is conf:assert data['selection_sha256']==sha(ART/'selection.json')
            for rec in data['evaluations']:
                p=ROOT/rec['trace'];assert sha(p)==rec['sha256']
                if rec['reused']:
                    result['reused_records']+=1
                    if data is conf:
                        assert selection['selections'][name]['policy'] is None and rec['trace'] in seen
                        base=next(r for r in data['evaluations'] if r['day']==rec['day'] and r['method']=='auto_pi')
                        close(rec['windows'],base['windows']);assert rec['sha256']==base['sha256'];continue
                    old=json.loads((ROOT/rec['reference_source']).read_text())['evaluations'][0]
                    for k,v in old.items():
                        if k!='reused':close(rec[k],v)
                else:
                    assert rec['trace'] not in seen;seen.add(rec['trace']);result['unique_episodes']+=1
                    for k in ('scored_hours','warmup_hours','wall_seconds'):result[k]+=rec[k]
                with p.open() as f:rows=[{k:float(v) for k,v in row.items()} for row in csv.DictReader(f)]
                assert len(rows)==rec['scored_hours']*60
                ctrl=StartupPI(c['target_C'],c['step_s'],data['model']) if rec['reused'] else HandoverPI(c['target_C'],c['step_s'],data['model'],rec['policy'])
                ctrl.prime(rec['initial_state']['T'],rec['initial_u']);last=0.;stopped=False
                for i,row in enumerate(rows):
                    close(ctrl.step(row['T'],row['previous_u'],i,outdoor=row['outdoor']),row['u'])
                    for k,v in ctrl.diagnostics.items():close(v,row[k])
                    assert 0<=row['u']<=1 and abs(row['correction'])<=.10000000001
                    if not rec['reused']:
                        if not row['retain_mode'] or row['active']:assert abs(row['correction']-last)<=.02000000001
                        last=row['correction'];assert row['handover_mismatch']<1e-10
                        if stopped:assert row['active']==0
                        if row['active']==0:stopped=True
                        if i>=60:assert row['active']==0 and row['correction']==0
                    if i:close(rows[i-1]['next_T'],row['T'])
                close(windows(rows,c),rec['windows']);close(metrics(rows,c),rec['metrics'])
                if data is conf:
                    for index in (55,60,120):
                        snapshots.append(dict(day=rec['day'],method=rec['method'],minute=index,trace=rec['trace'],csv_data_row=index+1,
                                              **{k:rows[index][k] for k in ('T','u','integral','correction')}))
                assert rec['exit_code']==ctrl.exit_code and rec['exit_min']==ctrl.exit_min
                if data is dev and not rec['reused']:trajectories[rec['policy']]=[(x['u'],x['next_T']) for x in rows]
        decisions=[]
        for day in (48,83):
            b,a=[r for r in conf['evaluations'] if r['day']==day]
            assert a['policy']==selection['selections'][name]['policy'];close(b['initial_state'],a['initial_state'])
            decisions.append(dict(day=day,reused=a['reused'],**gate(b['windows'],a['windows']),early_gain_C=b['windows']['early']['mae_C']-a['windows']['early']['mae_C'],late_gain_C=b['windows']['late']['mae_C']-a['windows']['late']['mae_C']))
        contrasts=[]
        for label,ai,bi in [('handover_at15',2,1),('handover_at55',4,3),('duration_taper',3,1),('duration_retain',4,2)]:
            aa,bb=dev['evaluations'][ai],dev['evaluations'][bi]
            times=[r['exit_min'] for r in (aa,bb) if r['exit_min']>=0]
            prefix=int(min(times)) if times else 180
            ta,tb=trajectories[aa['policy']],trajectories[bb['policy']]
            for x,y in zip(ta[:prefix],tb[:prefix]):
                for xx,yy in zip(x,y):close(xx,yy)
            effects={w:{m:aa['windows'][w][m]-bb['windows'][w][m] for m in ('mae_C','rmse_C','max_abs_error_C','requested_TV_u')} for w in ('early','late')}
            contrasts.append(dict(label=label,a_index=ai,b_index=bi,a_policy=aa['policy'],b_policy=bb['policy'],a_minus_b=effects,
                                  identical_pretrigger_minutes=prefix,identical_entire_trajectory=ta==tb,
                                  a_acquisition_min=aa['windows']['acquisition_onset_min'],b_acquisition_min=bb['windows']['acquisition_onset_min']))
        result['plants'][name]=dict(selection=selection['selections'][name],confirmation=decisions,supported_both_dates=all(x['passed'] for x in decisions),
                                   factorial_contrasts=contrasts,withdrawal_snapshots=snapshots)
    result['aggregate_simulated_hours']=result['scored_hours']+result['warmup_hours']
    (ART/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='sources'},indent=2))
if __name__=='__main__':main()
