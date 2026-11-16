#!/usr/bin/env python3
"""Plot saved five-strategy trajectories; no controller execution or tuning."""
from pathlib import Path
import csv
import hashlib
import json
import platform

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STUDY = ROOT / 'openspec/changes/compare-enclosure-five-methods-20261026'
ART = STUDY / 'artifacts'
OUT = HERE / 'delivery/2026-11-16_temperature_curves'
OUT.mkdir(parents=True, exist_ok=True)
for path in Path('/System/Library/Fonts/Supplemental').glob('Times New Roman*.ttf'):
    font_manager.fontManager.addfont(str(path))
plt.rcParams.update({'font.family': 'Times New Roman', 'font.size': 11,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'svg.fonttype': 'path'})

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

result = json.loads((ART / 'result.json').read_text())
verification = json.loads((ART / 'verification.json').read_text())
assert verification['status'] == 'PASS'
assert sha(ART / 'result.json') == verification['result_sha256']
config = json.loads((STUDY / 'config.json').read_text())
dt = config['settings']['dt_s']
methods = ['fixed', 'pi', 'pid', 'lqr', 'mpc']
labels = dict(zip(methods, ['Fixed PWM', 'PI', 'PID', 'LQR', 'MPC']))
colors = dict(zip(methods, ['#6b7280', '#2878b5', '#309355', '#ce6e24', '#8865a9']))
styles = dict(zip(methods, ['-', '-', ':', '--', '-.']))
splits = {'validation': 'Validation', 'holdout': 'Holdout',
          'plant_holdout': 'Parameter mismatch', 'overload': 'Overload'}
runs = {}
manifest = {'result_sha256': sha(ART / 'result.json'), 'dt_s': dt,
            'source': str(ART.relative_to(ROOT)), 'traces': [],
            'selection': 'All 60 evaluation runs; main example is the smallest holdout seed.',
            'time_alignment': 'Initial state at 0 s, then next_* states at time_s + dt_s.',
            'python': platform.python_version(), 'matplotlib': matplotlib.__version__}
for run in result['runs']:
    source = ART / run['trace_path']
    assert sha(source) == run['trace_sha256']
    with source.open() as f:
        rows = list(csv.DictReader(f))
    data = {key: np.array([float(r[key]) for r in rows]) for key in
            ('time_s', 'cpu_C', 'gpu_C', 'next_cpu_C', 'next_gpu_C',
             'cpu_W', 'gpu_W', 'inlet_C', 'pwm', 'fan', 'next_fan')}
    assert len(rows) == config['steps']
    assert np.array_equal(np.diff(data['time_s']), np.full(len(rows)-1, dt))
    for component in ('cpu', 'gpu', 'fan'):
        key = component + '_C' if component != 'fan' else 'fan'
        assert np.array_equal(data['next_'+key][:-1], data[key][1:])
    data['t'] = np.r_[data['time_s'][0], data['time_s'] + dt]
    for component in ('cpu', 'gpu'):
        data[component] = np.r_[data[component+'_C'][0], data['next_'+component+'_C']]
    mae = np.mean(np.abs(np.c_[data['next_cpu_C'], data['next_gpu_C']] - 60))
    assert abs(mae - run['metrics']['tracking_mae_C']) < 1e-10
    runs[run['split'], run['seed'], run['method']] = data
    manifest['traces'].append({k: run[k] for k in ('split', 'seed', 'method', 'trace_path', 'trace_sha256')})

for split in splits:
    for seed in config['seeds'][split]:
        ref = runs[split, seed, 'fixed']
        for method in methods:
            data = runs[split, seed, method]
            for key in ('time_s', 'cpu_W', 'gpu_W', 'inlet_C'):
                assert np.array_equal(data[key], ref[key])
            assert data['cpu'][0] == ref['cpu'][0] and data['gpu'][0] == ref['gpu'][0]

def plot_temperature(ax, split, seed, component):
    for method in methods:
        d = runs[split, seed, method]
        ax.plot(d['t'], d[component], label=labels[method], color=colors[method],
                ls=styles[method], lw=2.0 if method == 'pi' else 1.5)
    ax.axhline(60, color='#222222', ls=(0, (6, 3)), lw=.9, label='Target 60°C')
    if split == 'overload':
        limit = config['settings']['limits_C'][0 if component == 'cpu' else 1]
        ax.axhline(limit, color='#b32626', ls=(0, (2, 3)), lw=1,
                   label=f'Evaluation limit {limit:g}°C')
    ax.set_xlim(0, 1200)
    ax.set_xticks(np.arange(0, 1201, 240))
    ax.set_ylabel(f'{component.upper()} temperature (°C)')
    ax.grid(alpha=.18)

def save(fig, name):
    for ext in ('png', 'svg'):
        fig.savefig(OUT / f'{name}.{ext}', dpi=300, facecolor='white',
                    bbox_inches='tight', pad_inches=.15)
    plt.close(fig)

main_seed = min(config['seeds']['holdout'])
assert all(50 < runs['holdout', main_seed, m][c].min()
           and runs['holdout', main_seed, m][c].max() < 68
           for m in methods for c in ('cpu', 'gpu'))
fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
for ax, component in zip(axes, ('cpu', 'gpu')):
    plot_temperature(ax, 'holdout', main_seed, component)
    ax.set_ylim(50, 68)
axes[-1].set_xlabel('Time (s)')
fig.suptitle(f'CPU / GPU temperature response — simulation\nHoldout test, seed {main_seed}', y=.98)
fig.legend(*axes[0].get_legend_handles_labels(), loc='upper center',
           bbox_to_anchor=(.5, .90), ncol=6, frameon=False, fontsize=10)
fig.subplots_adjust(top=.81, bottom=.10, left=.11, right=.98, hspace=.17)
save(fig, 'holdout_102621_temperature')

# Single-column manuscript variant: preserve 10 pt labels at 7.54 cm width.
with plt.rc_context({'font.size': 10}):
    fig, axes = plt.subplots(2, 1, figsize=(7.54 / 2.54, 4.1), sharex=True)
    for ax, component in zip(axes, ('cpu', 'gpu')):
        plot_temperature(ax, 'holdout', main_seed, component)
        ax.set_ylabel(f'{component.upper()} (°C)', labelpad=1)
        ax.set_xticks([0, 400, 800, 1200])
        ax.set_yticks([50, 55, 60, 65])
        ax.set_ylim(50, 68)
        ax.tick_params(labelsize=10, pad=2)
    axes[-1].set_xlabel('Time (s)', labelpad=2)
    handles, names = axes[0].get_legend_handles_labels()
    names[-1] = 'Target 60°C'
    fig.legend(handles, names, loc='upper center', bbox_to_anchor=(.54, 1.0),
               ncol=2, frameon=False, fontsize=10, handlelength=1.7,
               columnspacing=1.0, labelspacing=.3)
    fig.subplots_adjust(top=.80, bottom=.12, left=.20, right=.94, hspace=.18)
    for extension in ('png', 'svg'):
        fig.savefig(HERE / 'figures' / f'temperature_response.{extension}',
                    dpi=400, facecolor='white')
    plt.close(fig)

# Context for the main example: interval inputs are zero-order held.
fig, axes = plt.subplots(3, 1, figsize=(8, 6), sharex=True)
ref = runs['holdout', main_seed, 'fixed']
for component, color in [('cpu', '#a04432'), ('gpu', '#2878b5')]:
    axes[0].stairs(ref[component+'_W'], ref['t'], baseline=None,
                   label=component.upper(), color=color, lw=1.2)
axes[0].set_ylabel('Heat input (W)'); axes[0].legend(frameon=False, ncol=2)
axes[1].stairs(ref['inlet_C'], ref['t'], baseline=None, color='#444444', lw=1.1)
axes[1].set_ylabel('Inlet temperature (°C)')
axes[1].set_ylim(ref['inlet_C'].min() - .4, ref['inlet_C'].max() + .4)
for method in methods:
    d = runs['holdout', main_seed, method]
    axes[2].stairs(d['pwm'], d['t'], baseline=None, color=colors[method],
                   ls=styles[method], label=labels[method], lw=1.5)
axes[2].set_ylabel('PWM duty ratio'); axes[2].set_ylim(.15, 1.05)
fig.legend(*axes[2].get_legend_handles_labels(), loc='upper center',
           bbox_to_anchor=(.5, .89), frameon=False, ncol=5, fontsize=10)
axes[2].set_xlabel('Time (s)')
for ax in axes:
    ax.set_xlim(0, 1200); ax.set_xticks(np.arange(0, 1201, 240)); ax.grid(alpha=.18)
fig.suptitle(f'Common inputs and controller output — simulation\nHoldout test, seed {main_seed}', y=.98)
fig.subplots_adjust(top=.80, bottom=.10, left=.12, right=.98, hspace=.18)
save(fig, 'holdout_102621_inputs_pwm')

for split, label in splits.items():
    seeds = config['seeds'][split]
    fig, axes = plt.subplots(2, 3, figsize=(12, 6.3), sharex=True, sharey=True)
    values = np.concatenate([runs[split, seed, method][c]
                             for seed in seeds for method in methods for c in ('cpu', 'gpu')])
    lo, hi = min(60, values.min()) - 2, max(60, values.max()) + 2
    for col, seed in enumerate(seeds):
        for row, component in enumerate(('cpu', 'gpu')):
            ax = axes[row, col]
            plot_temperature(ax, split, seed, component)
            ax.set_ylim(lo, hi)
            if col: ax.set_ylabel('')
            if row: ax.set_xlabel('Time (s)')
        axes[0, col].set_title(f'Seed {seed}', fontsize=11)
    fig.suptitle(f'{label}: CPU / GPU temperature response — simulation', y=.98)
    handles, legend_labels = axes[0, 0].get_legend_handles_labels()
    if split == 'overload':
        h, l = axes[1, 0].get_legend_handles_labels()
        handles.append(h[-1]); legend_labels.append(l[-1])
    fig.legend(handles, legend_labels, loc='upper center', bbox_to_anchor=(.5, .93),
               ncol=4 if split == 'overload' else 6, frameon=False, fontsize=10)
    fig.subplots_adjust(top=.78, bottom=.10, left=.07, right=.99, hspace=.17, wspace=.10)
    save(fig, f'{split}_all_seeds')

with (OUT / 'temperature_curves.csv').open('w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['split', 'seed', 'method', 'time_s', 'cpu_C', 'gpu_C'])
    for (split, seed, method), d in runs.items():
        writer.writerows(zip([split]*len(d['t']), [seed]*len(d['t']),
                             [method]*len(d['t']), d['t'], d['cpu'], d['gpu']))
manifest['script_sha256'] = sha(Path(__file__))
manifest['checks'] = {'trace_hashes': 60, 'paired_exogenous_inputs': 'PASS',
                       'state_continuity': 'PASS', 'recomputed_mae': 'PASS',
                       'temperature_points_per_run': 121, 'csv_rows': 7260}
(OUT / 'provenance.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(f'Created 6 PNG / SVG figure pairs and 7,260 temperature rows in {OUT}')
