"""Retrospective steady-capacity diagnostic from archived assumed-model inputs."""
import csv
import json

from sparse_enclosure_corrections import ORIGINAL, ARTIFACTS, equilibrium


def analyze():
    result = json.loads((ORIGINAL / 'result.json').read_text())
    config = json.loads((ORIGINAL / 'config.json').read_text())
    settings = config['settings']
    episodes = []
    for run in result['runs']:
        if run['split'] != 'holdout' or run['task'] != 'closed_loop':
            continue
        p = config['rigs'][run['rig']]
        with (ORIGINAL / run['csv']).open() as stream:
            rows = [{k:float(v) for k,v in row.items()} for row in csv.DictReader(stream)]
        low, high = [], []
        for row in rows:
            heat = row['declared_power'] + config['extra_unobserved_heat_W']
            low.append(float(equilibrium(p, heat, row['inlet'], settings['pwm_max'])[0]))
            high.append(float(equilibrium(p, heat, row['inlet'], settings['pwm_min'])[0]))
        episodes.append({'rig':run['rig'], 'seed':run['seed'], 'method':run['method'], 'n':len(rows),
                         'held_input_full_fan_equilibrium_above_limit_steps':sum(t > settings['limit'] for t in low),
                         'held_input_target_outside_steady_fan_range_steps':sum(not a <= settings['target'] <= b for a,b in zip(low,high)),
                         'max_full_fan_equilibrium_C':max(low),
                         'actual_sampled_overtemp_steps':sum(row['source_truth_next'] > settings['limit'] for row in rows)})
    p = config['rigs']['contact_poor']
    selected = [e for e in episodes if e['rig'] == 'contact_poor' and e['method'] == 'rank_h6']
    return {'evidence_class':'retrospective_assumed_network_capacity_diagnostic',
            'example':{'rig':'contact_poor', 'inlet_C':22., 'total_heat_W':3.35, 'fan':1.,
                       'source_equilibrium_C':float(equilibrium(p, 3.35, 22., 1.)[0])},
            'contact_poor_rank_h6':{'n':sum(e['n'] for e in selected),
                 'held_input_full_fan_equilibrium_above_limit_steps':sum(e['held_input_full_fan_equilibrium_above_limit_steps'] for e in selected),
                 'actual_sampled_overtemp_steps':sum(e['actual_sampled_overtemp_steps'] for e in selected)},
            'episodes':episodes,
            'boundary':'Held-input steady equilibria are not actual overtemperature counts or finite-horizon infeasibility. No hypothesis criterion or existing result is changed.'}


if __name__ == '__main__':
    report = analyze()
    (ARTIFACTS / 'capacity_diagnostic.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k:v for k,v in report.items() if k != 'episodes'}, ensure_ascii=False, indent=2))
