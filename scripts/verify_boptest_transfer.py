"""Independent CSV, split, noise parity and selection audit."""
import csv
import json
import random
from run_boptest_transfer import ART, ROOT, PRIOR, source_hashes, select, sha, metrics


def main():
    dev = json.loads((ART/'development.json').read_text())
    transfer = json.loads((ART/'transfer.json').read_text())
    selection = json.loads((ART/'selection.json').read_text())
    assert dev['status'] == transfer['status'] == 'COMPLETED'
    assert dev['sources'] == transfer['sources'] == selection['sources'] == source_hashes()
    assert selection['development_sha256'] == sha(ART/'development.json')
    assert transfer['selection_sha256'] == sha(ART/'selection.json')
    assert selection['selected'] == select(dev['records'])
    assert len(dev['records']) == 8 and len(transfer['records']) == 18
    initial, noises = {}, {}
    for r in dev['records'] + transfer['records']:
        path = ROOT/r['trace']
        assert sha(path) == r['sha256']
        with path.open() as f:
            rows = [{k:float(v) for k,v in row.items()} for row in csv.DictReader(f)]
        assert len(rows) == 1440
        assert rows[0]['time_s'] == r['day']*86400
        for a,b in zip(rows,rows[1:]):
            assert b['time_s'] - a['time_s'] == 60
            assert abs(a['next_T']-b['T']) < 1e-9
        for k,v in metrics(rows).items():
            assert abs(v-r['metrics'][k]) < 1e-9
        assert abs(metrics(rows[:30])['mae_C']-r['initial_30min_mae_C']) < 1e-9
        assert abs(metrics(rows[30:])['mae_C']-r['after_30min_mae_C']) < 1e-9
        key=(r['day'],r['noise_sd_C'])
        assert abs(initial.setdefault(key,rows[0]['T'])-rows[0]['T']) < 1e-9
        seq=[row['noise_C'] for row in rows]
        assert noises.setdefault(key,seq)==seq
        rng=random.Random(42000+r['day'])
        expected=[rng.gauss(0,r['noise_sd_C']) if r['noise_sd_C'] else 0 for row in rows]
        assert seq == expected
        for row in rows:
            assert abs(row['measurement_T']-row['T']-row['noise_C']) < 1e-12
            assert 12<=row['command']<=40
            assert abs(row['fan']-.5) < 1e-9
    prior=json.loads((PRIOR/'result_v2.json').read_text())
    for r in dev['records']:
        if r['controller']=='v2':
            expected=next(p['metrics'] for p in prior['evaluations'] if p['day']==r['day'])
            assert r['metrics']==expected, 'Legacy controller reproduction changed'
    chosen=selection['selected']
    comparisons=[]
    for day, noise in transfer['cases']:
        same={r['controller']:r for r in transfer['records'] if r['day']==day and r['noise_sd_C']==noise}
        a,b,g=[same[n]['metrics'] for n in (chosen,'v2','grid_handover')]
        comparisons.append({'day':day,'noise_sd_C':noise,'mae_gain_vs_v2_C':b['mae_C']-a['mae_C'],
            'mae_gap_vs_grid_C':a['mae_C']-g['mae_C'],
            'nonregression_vs_v2':a['mae_C']<=b['mae_C']+.01 and a['max_abs_error_C']<=b['max_abs_error_C']+.1,
            'within_exploratory_grid_margin':a['mae_C']<=g['mae_C']+.05 and a['max_abs_error_C']<=g['max_abs_error_C']+.5})
    gain=sum(c['mae_gain_vs_v2_C'] for c in comparisons)/len(comparisons)
    decision={'status':'PASS','traces':26,'selection':chosen,'comparisons':comparisons,
        'macro_mae_gain_vs_v2_C':gain,'protocol_improvement_gate':gain>0 and all(c['nonregression_vs_v2'] for c in comparisons),
        'within_exploratory_grid_margin_all':all(c['within_exploratory_grid_margin'] for c in comparisons),
        'transfer_sha256':sha(ART/'transfer.json'),'verifier_sha256':sha(__file__)}
    (ART/'verification.json').write_text(json.dumps(decision,indent=2)+'\n')
    print(json.dumps(decision,indent=2))


if __name__=='__main__':
    main()
