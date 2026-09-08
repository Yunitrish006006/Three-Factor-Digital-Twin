"""Development pilot on the pinned BOPTEST FMU; not the official KPI service.

Run from school with outputs/boptest-venv/bin/python scripts/run_boptest_rapid_pi.py.
Only calibration transitions enter fit_rc(). Evaluation is never a fit input.
"""
from __future__ import annotations

import csv
import hashlib
import html
import importlib.metadata
import json
import math
from pathlib import Path
import platform
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
CHANGE = ROOT / 'openspec/changes/pilot-boptest-rapid-pi'
VENDOR = ROOT / 'outputs/vendor/boptest-v0.9.0'
FMU = VENDOR / 'testcases/bestest_air/models/wrapped.fmu'
OUT = ROOT / 'outputs/boptest_rapid_pi/v1'
DT = 60.0
TARGET = 22.0
CHANNELS = {
    'T': 'zon_reaTRooAir_y',
    'outdoor': 'zon_weaSta_reaWeaTDryBul_y',
    'solar': 'zon_weaSta_reaWeaHGloHor_y',
    'supply': 'fcu_oveTSup_y', 'fan': 'fcu_oveFan_y',
    'heat_W': 'fcu_reaPHea_y', 'cool_W': 'fcu_reaPCoo_y',
    'fan_W': 'fcu_reaPFan_y',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def clip(x, lo=12.0, hi=40.0):
    if not math.isfinite(x):
        raise ValueError('nonfinite actuator command')
    return max(lo, min(hi, x))


class PI:
    def __init__(self, kp=2.0, ti=1200.0, model=None):
        if kp <= 0 or ti <= 0:
            raise ValueError('PI gains must be positive')
        self.kp, self.ti, self.model = kp, ti, model
        self.integral = 0.0

    def __call__(self, state, index):
        error = TARGET - state['T']
        bias = TARGET
        if self.model is not None:
            a, b, c, d = self.model
            bias -= (a * (state['outdoor'] - TARGET)
                     + c * state['solar'] / 1000.0 + d) / b
        delta = self.kp / self.ti * error * DT
        tentative = bias + self.kp * error + self.integral + delta
        # Permit integration only when unsaturated or moving back from a limit.
        if 12 <= tentative <= 40 or (tentative > 40 and delta < 0) or (tentative < 12 and delta > 0):
            self.integral += delta
        return clip(bias + self.kp * error + self.integral)


def fit_rc(rows):
    import numpy as np
    x = np.array([[r['outdoor'] - r['T'], r['command'] - r['T'],
                   r['solar'] / 1000, 1] for r in rows])
    y = np.array([r['next_T'] - r['T'] for r in rows])
    coef = np.linalg.solve(x.T @ x + 1e-8 * np.eye(4), x.T @ y)
    a, b, c, d = map(float, coef)
    condition = float(np.linalg.cond(x))
    record = {'coefficients': [a, b, c, d], 'n': len(rows),
              'fit_rmse_C': float(np.sqrt(np.mean((x @ coef - y) ** 2))),
              'condition_number': condition if math.isfinite(condition) else None,
              'rank': int(np.linalg.matrix_rank(x)),
              'solar_identifiable': bool(np.ptp(x[:, 2]) > 0),
              'fit_start_s': rows[0]['time_s'], 'fit_end_s': rows[-1]['time_s'] + DT}
    if not (a > 0 and b > 0 and a + b < 1):
        record.update(status='REJECTED_NONPHYSICAL', kp=2.0, ti=1200.0)
    else:
        tau = -DT / math.log(1 - a - b)
        gain = b / (a + b)
        record.update(status='FITTED', kp=tau / (gain * 600), ti=tau)
    return record


def episode(name, start, hours, controller):
    from fmpy import extract, read_model_description
    from fmpy.fmi2 import FMU2Slave
    began = time.perf_counter()
    md = read_model_description(str(FMU), validate=False)
    vr = {v.name: v.valueReference for v in md.modelVariables}
    rows = []
    with tempfile.TemporaryDirectory(prefix='boptest-') as temp:
        extract(str(FMU), unzipdir=temp)
        fmu = FMU2Slave(guid=md.guid, unzipDirectory=temp,
                        modelIdentifier=md.coSimulation.modelIdentifier,
                        instanceName='pilot')
        fmu.instantiate()
        try:
            fmu.setupExperiment(startTime=start - 86400)
            fmu.enterInitializationMode()
            fmu.setBoolean([vr['con_oveTSetHea_activate'], vr['con_oveTSetCoo_activate']], [True, True])
            fmu.setReal([vr['con_oveTSetHea_u'], vr['con_oveTSetCoo_u']], [TARGET + 273.15] * 2)
            fmu.exitInitializationMode()

            def observe():
                values = dict(zip(CHANNELS, fmu.getReal([vr[v] for v in CHANNELS.values()])))
                for k in ('T', 'outdoor', 'supply'):
                    values[k] -= 273.15
                if not all(math.isfinite(v) for v in values.values()):
                    raise ValueError('nonfinite FMU measurement')
                return values

            t = start - 86400
            for _ in range(int(86400 / DT)):
                fmu.doStep(currentCommunicationPoint=t, communicationStepSize=DT)
                t += DT
            if controller is not None:
                fmu.setBoolean([vr['fcu_oveFan_activate'], vr['fcu_oveTSup_activate']], [True, True])
                fmu.setReal([vr['fcu_oveFan_u']], [0.5])
            for i in range(int(hours * 3600 / DT)):
                state = observe()
                command = state['supply'] if controller is None else clip(controller(state, i))
                if controller is not None:
                    fmu.setReal([vr['fcu_oveTSup_u']], [command + 273.15])
                fmu.doStep(currentCommunicationPoint=t, communicationStepSize=DT)
                nxt = observe()
                row = dict(time_s=t, **state, command=command, next_T=nxt['T'])
                for k in ('heat_W', 'cool_W', 'fan_W'):
                    row['next_' + k] = nxt[k]
                rows.append(row)
                t += DT
            fmu.terminate()
        finally:
            fmu.freeInstance()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / (name + '.csv')
    with path.open('w') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return rows, {'trace': str(path.relative_to(ROOT)), 'sha256': sha(path),
                  'wall_seconds_including_warmup': time.perf_counter() - began,
                  'common_warmup_hours': 24, 'scored_hours': hours, 'metrics': metrics(rows)}


def metrics(rows):
    errors = [r['next_T'] - TARGET for r in rows]
    n = len(errors)
    return {
        'n': n, 'mae_C': sum(map(abs, errors)) / n,
        'rmse_C': math.sqrt(sum(e * e for e in errors) / n),
        'max_abs_error_C': max(map(abs, errors)),
        'within_0_5_C_pct': 100 * sum(abs(e) <= .5 for e in errors) / n,
        'iae_C_h': sum(map(abs, errors)) * DT / 3600,
        'outside_20_30_C_n': sum(not 20 <= r['next_T'] <= 30 for r in rows),
        'saturation_pct': 100 * sum(r['command'] <= 12 or r['command'] >= 40 for r in rows) / n,
        'command_total_variation_C': sum(abs(a['command'] - b['command']) for a, b in zip(rows, rows[1:])),
        **{k.replace('_W', '_kWh'): sum(r['next_' + k] for r in rows) * DT / 3.6e6
           for k in ('heat_W', 'cool_W', 'fan_W')},
    }


def save(result):
    path = CHANGE / 'artifacts/result.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')


def report(result):
    table = ''.join('<tr>' + ''.join(f'<td>{html.escape(str(v))}</td>' for v in
                    (r['day'], r['controller'], f"{r['metrics']['mae_C']:.3f}",
                     f"{r['metrics']['max_abs_error_C']:.3f}",
                     f"{r['metrics']['within_0_5_C_pct']:.1f}%", r['calibration_hours'])) + '</tr>'
                    for r in result['evaluations'])
    text = '''<!doctype html><html lang="zh-Hant"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>BOPTEST 自動調參初測</title>
<style>body{font:18px/1.7 system-ui;background:#eef2f7;color:#182738;margin:0}main{max-width:1100px;margin:auto;padding:35px}section{background:white;padding:30px;margin:25px 0;border-radius:15px}h1{font-size:38px}table{border-collapse:collapse;width:100%;font-size:15px}td,th{padding:9px;text-align:left;border-bottom:1px solid #ccd}code{overflow-wrap:anywhere}@media print{section{break-inside:avoid}body{background:white}}</style>
<main><h1>用更少調參時間，達到相同或更好的控溫？</h1>
<p>2026-09-08 · BOPTEST 官方模型本機開發初測 · 尚非獨立確認實驗</p>
<section><h2>目前補上的能力</h2><p>原有空間估測是當下溫度推估；本次另建「控制動作 → 下一步溫度」的動態辨識、PI 自動整定、環境前饋與積分防飽和。未移植原有神經網路權重，也尚未證明神經網路有額外效益。</p>
<p>官方 bestest_air FMU，FMPy 0.3.22；目標 22°C，每分鐘控制一次。外接控制器都固定風量 0.5、供氣 12–40°C。embedded 為內建控制器參考，風量策略不同，不作同等能源效率排名。</p></section>
<section><h2>開發結果：每個日期完整列出</h2><table><tr><th>年內日序（從 0 起）</th><th>控制器</th><th>MAE °C</th><th>最大誤差 °C</th><th>±0.5°C 內</th><th>主動校正時數</th></tr>''' + table + '''</table>
<p>所有案例另有相同 24 小時暖機。2／6 小時是模擬系統接受辨識激勵的時間；grid 為 9 組 × 6 小時。不是研究者工作時數。fixed 的 0 小時代表預先指定參數，沒有計算專家既有知識成本。</p></section>
<section><h2>判斷界線</h2><p>這是建築空調模型的閉迴路開發證據，不是 EUV、半導體設備或濕度控制驗證。兩個確定性日期不足以推論跨地區可靠性；也沒有感測雜訊、多機種、人工調參工時比較。不能据此宣稱新穎性或論文主張已完成。</p>
<p>降低調整成本仍需：相同資料預算的強基準、多個環境／設備，以及不再調參的独立確認。原有 20–30°C 空間估測範圍沒有被此試驗擴張。</p>
<p>完整係數、失敗、能源分項、越界與軌跡雜湊見 <a href="../../openspec/changes/pilot-boptest-rapid-pi/artifacts/result.json">機器可讀證據</a>（由 docs/reports 以外路徑開啟時請用專案檔案）。</p></section>
<section><h2>資料來源與重現</h2><p><a href="https://github.com/ibpsa/project1-boptest/tree/v0.9.0">BOPTEST v0.9.0</a> · <a href="https://github.com/CATIA-Systems/FMPy/tree/v0.3.22">FMPy 0.3.22</a></p><p>直接執行官方 FMU，不宣稱與官方 REST／KPI 完全等價。完整逐分鐘 CSV 保存在 outputs/boptest_rapid_pi/v1。</p><code>outputs/boptest-venv/bin/python scripts/run_boptest_rapid_pi.py</code></section></main></html>'''
    # reports is two levels below project root
    (ROOT / 'docs/reports/boptest_rapid_pi_2026-09-08_zh.html').write_text(text)


def main():
    # Refuse accidental overwriting of inspected development evidence.
    if (CHANGE / 'artifacts/result.json').exists():
        raise SystemExit('Evidence already exists; use a new version/path for another study.')
    result = {'status': 'RUNNING', 'scope': 'EXPLORATORY_OFFICIAL_FMU_CUSTOM_RUNNER',
              'source_commit': '9b1610bf7a108826bb3d22c72bffd2d71d7bb0a9',
              'fmu_sha256': sha(FMU), 'protocol_sha256': sha(CHANGE / 'protocol.md'),
              'runner_sha256': sha(__file__), 'python': platform.python_version(),
              'packages': {d.metadata['Name']: d.version for d in importlib.metadata.distributions()},
              'dt_s': DT, 'target_C': TARGET, 'failures': [], 'grid': [], 'fits': {}, 'evaluations': [],
              'service_probe_failures': ['HTTPS api.boptest.net SSL_ERROR_SYSCALL', 'HTTP /testcases 404'],
              'license': 'Upstream revised 3-clause BSD plus added paragraph; retain upstream and dependency notices.',
              'license_sha256': sha(VENDOR / 'license.md')}
    save(result)
    try:
        rows, record = episode('identification', 86400, 6,
                               lambda s, i: 22 + [-4, 8, 0, 12, -8, 4][(i // 15) % 6])
        result['identification'] = record
        for hours in (2, 6):
            result['fits'][str(hours)] = fit_rc(rows[:hours * 60])
        save(result)
        for kp in (.5, 2, 6):
            for ti in (300, 1200, 3600):
                _, rec = episode(f'grid_{kp}_{ti}', 86400, 6, PI(kp, ti))
                result['grid'].append(dict(kp=kp, ti=ti, **rec))
                save(result)
                print('grid', kp, ti, rec['metrics']['mae_C'], flush=True)
        best = min(result['grid'], key=lambda r: r['metrics']['mae_C'])
        result['selected_grid'] = {'kp': best['kp'], 'ti': best['ti']}
        for day in (3, 180):
            choices = [('embedded', 0, None), ('fixed_pi', 0, PI()),
                       ('grid_pi', 54, PI(best['kp'], best['ti']))]
            for hours in (2, 6):
                fit = result['fits'][str(hours)]
                for ff in (False, True):
                    model = fit['coefficients'] if ff and fit['status'] == 'FITTED' else None
                    choices.append((f'auto_{hours}h' + ('_ff' if ff else ''), hours,
                                    PI(fit['kp'], fit['ti'], model)))
            for name, budget, controller in choices:
                _, rec = episode(f'day{day}_{name}', day * 86400, 24, controller)
                result['evaluations'].append(dict(day=day, controller=name, calibration_hours=budget, **rec))
                save(result)
                print('evaluation', day, name, rec['metrics']['mae_C'], flush=True)
        result['feasibility_gate_vs_fixed'] = {}
        for name in ('auto_2h', 'auto_2h_ff', 'auto_6h', 'auto_6h_ff'):
            passes = []
            for day in (3, 180):
                lookup = {r['controller']: r['metrics'] for r in result['evaluations'] if r['day'] == day}
                m, b = lookup[name], lookup['fixed_pi']
                passes.append(m['mae_C'] <= b['mae_C'] and m['max_abs_error_C'] <= b['max_abs_error_C'] + .5)
            result['feasibility_gate_vs_fixed'][name] = all(passes)
        result['status'] = 'COMPLETED_DEVELOPMENT_ONLY'
        save(result)
        report(result)
    except Exception as exc:
        result['status'] = 'FAILED'
        result['failures'].append({'type': type(exc).__name__, 'message': str(exc)})
        save(result)
        raise


if __name__ == '__main__':
    main()
