"""Frozen-source BOPTEST handover and causal disturbance-observer comparison."""
import argparse
import csv
import json
import math
from pathlib import Path
import random
import tempfile
import time
from run_boptest_rapid_pi import PI, DT, TARGET, CHANNELS, FMU, ROOT, sha, clip, metrics

CHANGE = ROOT / 'openspec/changes/improve-boptest-transfer'
ART = CHANGE / 'artifacts'
PRIOR = ROOT / 'openspec/changes/pilot-boptest-rapid-pi/artifacts'
OUT = ROOT / 'outputs/boptest_transfer'


class HandoverPI(PI):
    def prime(self, state):
        self.first = clip(state['T'] + state['fan'] / .5 * (state['supply'] - state['T']))
        self.integral = self.first - TARGET - self.kp * (TARGET - state['T'])

    def __call__(self, state, index):
        if index == 0:
            return self.first
        return super().__call__(state, index)


class ObserverPI(HandoverPI):
    def __init__(self, kp, ti, b):
        super().__init__(kp, ti)
        if not math.isfinite(b) or b <= 0:
            raise ValueError('invalid actuator gain')
        self.b = b

    def prime(self, state):
        super().prime(state)
        self.disturbance = -self.b * (self.first - state['T'])
        self.integral = 0.0
        self.previous_T = state['T']
        self.previous_u = self.first

    def __call__(self, state, index):
        if index == 0:
            return self.first
        observed = state['T'] - self.previous_T - self.b * (self.previous_u - self.previous_T)
        self.disturbance = .8 * self.disturbance + .2 * observed
        bias = TARGET - self.disturbance / self.b
        error = TARGET - state['T']
        delta = self.kp / self.ti * error * DT
        tentative = bias + self.kp * error + self.integral + delta
        if 12 <= tentative <= 40 or (tentative > 40 and delta < 0) or (tentative < 12 and delta > 0):
            self.integral += delta
        command = clip(bias + self.kp * error + self.integral)
        self.previous_T, self.previous_u = state['T'], command
        return command


def episode(name, start, hours, controller, noise_sd=0.0):
    rng = random.Random(42000 + int(start / 86400))
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
            outgoing = observe()
            first_noise = rng.gauss(0, noise_sd) if noise_sd else 0.0
            measured_outgoing = dict(outgoing, T=outgoing['T'] + first_noise)
            if hasattr(controller, 'prime'):
                controller.prime(measured_outgoing)
            if controller is not None:
                fmu.setReal([vr['fcu_oveTSup_u']], [clip(outgoing['supply']) + 273.15])
                fmu.setBoolean([vr['fcu_oveFan_activate'], vr['fcu_oveTSup_activate']], [True, True])
                fmu.setReal([vr['fcu_oveFan_u']], [0.5])
            for i in range(int(hours * 3600 / DT)):
                state = observe()
                noise = first_noise if i == 0 else (rng.gauss(0, noise_sd) if noise_sd else 0.0)
                measured = dict(state, T=state['T'] + noise)
                command = state['supply'] if controller is None else clip(controller(measured, i))
                if controller is not None:
                    fmu.setReal([vr['fcu_oveTSup_u']], [command + 273.15])
                fmu.doStep(currentCommunicationPoint=t, communicationStepSize=DT)
                nxt = observe()
                row = dict(time_s=t, **state, measurement_T=measured['T'], noise_C=noise, command=command, next_T=nxt['T'])
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
                  'common_warmup_hours': 24, 'scored_hours': hours, 'outgoing': outgoing,
                  'initial_30min_mae_C': metrics(rows[:30])['mae_C'],
                  'after_30min_mae_C': metrics(rows[30:])['mae_C'], 'metrics': metrics(rows)}


def source_hashes():
    return {str(p.relative_to(ROOT)): sha(p) for p in (
        Path(__file__), ROOT / 'scripts/run_boptest_rapid_pi.py',
        CHANGE / 'protocol.md', PRIOR / 'result.json', PRIOR / 'result_v2.json', FMU)}


def make_controller(name):
    prior = json.loads((PRIOR / 'result_v2.json').read_text())
    kp, ti = prior['kp'], prior['ti']
    if name == 'v2':
        return PI(kp, ti)
    if name == 'v3_handover':
        return HandoverPI(kp, ti)
    if name == 'v4_observer':
        b = json.loads((PRIOR / 'result.json').read_text())['fits']['2']['coefficients'][1]
        return ObserverPI(kp, ti, b)
    if name == 'grid_handover':
        return HandoverPI(6, 300)
    raise ValueError(name)


def select(records):
    qualified = []
    for name in ('v3_handover', 'v4_observer'):
        own = [r for r in records if r['controller'] == name]
        ok = True
        for r in own:
            base = next(b for b in records if b['day'] == r['day'] and b['controller'] == 'v2')['metrics']
            ok &= r['metrics']['mae_C'] <= base['mae_C'] + .01
            ok &= r['metrics']['max_abs_error_C'] <= base['max_abs_error_C'] + .1
        if len(own) == 2 and ok:
            qualified.append((sum(r['metrics']['mae_C'] for r in own)/2, name))
    return min(qualified)[1] if qualified else 'v2'


def main():
    global OUT
    parser = argparse.ArgumentParser()
    parser.add_argument('--phase', choices=['development', 'transfer'], required=True)
    phase = parser.parse_args().phase
    ART.mkdir(parents=True, exist_ok=True)
    dest = ART / (phase + '.json')
    if dest.exists():
        raise SystemExit('Evidence exists; never overwrite an inspected phase.')
    selection_path = ART / 'selection.json'
    sources = source_hashes()
    if phase == 'development':
        names = ['v2', 'v3_handover', 'v4_observer', 'grid_handover']
        cases = [(3, 0), (180, 0)]
    else:
        selection = json.loads(selection_path.read_text())
        if selection['sources'] != sources or selection['development_sha256'] != sha(ART / 'development.json'):
            raise SystemExit('Source/development changed since selection; transfer blocked.')
        names = list(dict.fromkeys(['v2', selection['selected'], 'grid_handover']))
        cases = [(d, 0) for d in (35, 95, 245, 305)] + [(95, .05), (245, .05)]
    OUT = ROOT / 'outputs/boptest_transfer' / phase
    result = {'status': 'RUNNING', 'phase': phase, 'sources': sources,
              'cases': cases, 'controllers': names, 'records': [], 'failures': [],
              'selection_sha256': sha(selection_path) if phase == 'transfer' else None,
              'scope': 'SAME_FMU_NEW_DATES_AND_NOISE' if phase == 'transfer' else 'REUSED_DEVELOPMENT_DATES'}

    def save():
        temp = dest.with_suffix('.tmp')
        temp.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
        temp.replace(dest)

    save()
    try:
        for day, noise in cases:
            for name in names:
                _, rec = episode(f'day{day}_noise{noise}_{name}', day * 86400, 24, make_controller(name), noise)
                result['records'].append(dict(day=day, noise_sd_C=noise, controller=name,
                                              calibration_hours=54 if name == 'grid_handover' else 2, **rec))
                save()
                print(phase, day, noise, name, rec['metrics']['mae_C'], rec['metrics']['max_abs_error_C'], flush=True)
        result['status'] = 'COMPLETED'
        save()
        if phase == 'development':
            if selection_path.exists():
                raise RuntimeError('Selection already exists')
            selection = {'selected': select(result['records']), 'sources': sources,
                         'development_sha256': sha(dest), 'created_before_transfer': True}
            selection_path.write_text(json.dumps(selection, indent=2) + '\n')
            print('FROZEN SELECTION:', selection['selected'], flush=True)
    except Exception as exc:
        result['status'] = 'FAILED'
        result['failures'].append({'type': type(exc).__name__, 'message': str(exc)})
        save()
        raise


if __name__ == '__main__':
    main()
