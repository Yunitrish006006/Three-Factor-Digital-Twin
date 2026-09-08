"""Trace-level audit of jitter/delay study and predeclared decision."""
import csv,json,random
from run_boptest_jitter import ART,ROOT,sha,source_hashes,select,metrics

def main():
    dev=json.loads((ART/'development.json').read_text());t=json.loads((ART/'transfer.json').read_text());sel=json.loads((ART/'selection.json').read_text())
    assert dev['status']==t['status']=='COMPLETED'
    assert dev['sources']==t['sources']==sel['sources']==source_hashes()
    assert sel['development_sha256']==sha(ART/'development.json')
    assert t['selection_sha256']==sha(ART/'selection.json')
    assert sel['selected']==select(dev['records'])
    assert len(dev['records'])==16 and len(t['records'])==6*len(t['controllers'])
    states={};sequences={}
    for record in dev['records']+t['records']:
        path=ROOT/record['trace'];assert sha(path)==record['sha256']
        with path.open() as f:rows=[{k:float(v) for k,v in r.items()} for r in csv.DictReader(f)]
        assert len(rows)==1440 and rows[0]['time_s']==record['day']*86400
        key=(record['day'],record['noise_sd_C'],record['delay_steps'])
        assert abs(states.setdefault(key,rows[0]['T'])-rows[0]['T'])<1e-9
        noise=[r['noise_C'] for r in rows];assert sequences.setdefault(key,noise)==noise
        rng=random.Random(52000+record['day'])
        assert noise==[rng.gauss(0,record['noise_sd_C']) if record['noise_sd_C'] else 0 for _ in rows]
        for a,b in zip(rows,rows[1:]):
            assert b['time_s']-a['time_s']==60 and abs(a['next_T']-b['T'])<1e-9
            assert abs(b['supply']-a['applied_command'])<1e-9
        queue=[record['initial_applied']]*record['delay_steps']
        for r in rows:
            queue.append(r['command']);assert r['applied_command']==queue.pop(0)
            assert 12<=r['command']<=40 and 12<=r['applied_command']<=40
            assert abs(r['fan']-.5)<1e-9
            assert abs(r['measurement_T']-r['T']-r['noise_C'])<1e-12
        for k,v in metrics(rows).items():assert abs(v-record['metrics'][k])<1e-9
        variation=sum(abs(a['applied_command']-b['applied_command']) for a,b in zip(rows,rows[1:]))
        assert abs(variation-record['applied_total_variation_C'])<1e-9
        assert abs(metrics(rows[:30])['mae_C']-record['initial_30min_mae_C'])<1e-9
        assert abs(metrics(rows[30:])['mae_C']-record['after_30min_mae_C'])<1e-9
    comparisons=[]
    for day,noise,delay in t['cases']:
        records={r['controller']:r for r in t['records'] if (r['day'],r['noise_sd_C'],r['delay_steps'])==(day,noise,delay)}
        a=records[sel['selected']]['metrics'];b=records['v4']['metrics']
        comparisons.append({'day':day,'noise_sd_C':noise,'delay_steps':delay,'mae_delta_C':a['mae_C']-b['mae_C'],
            'max_error_delta_C':a['max_abs_error_C']-b['max_abs_error_C'],'requested_variation_ratio':a['command_total_variation_C']/b['command_total_variation_C'],
            'nonregression':a['mae_C']<=b['mae_C']+.02 and a['max_abs_error_C']<=b['max_abs_error_C']+.2})
    noisy=[r for r in t['records'] if r['noise_sd_C']>0]
    ratio=sum(r['metrics']['command_total_variation_C'] for r in noisy if r['controller']==sel['selected'])/sum(r['metrics']['command_total_variation_C'] for r in noisy if r['controller']=='v4')
    result={'status':'PASS','traces':len(dev['records'])+len(t['records']),'selected':sel['selected'],'comparisons':comparisons,
        'noisy_requested_variation_ratio':ratio,'improvement_gate':all(c['nonregression'] for c in comparisons) and ratio<=.8,
        'transfer_sha256':sha(ART/'transfer.json'),'verifier_sha256':sha(__file__)}
    (ART/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
