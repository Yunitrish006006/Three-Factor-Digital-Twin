"""Declarative native-unit adapter; controller never sees device identity."""
import csv
import math
import tempfile
import time
from run_boptest_cross_plant import ROOT, fmu_path, sha, metrics
from digital_twin.control.portable_pi import clamp


def encode(c, u):
    return c['actuator_min'] + clamp(u) * (c['actuator_max'] - c['actuator_min'])


def decode(c, value):
    return clamp((value - c['actuator_min']) / (c['actuator_max'] - c['actuator_min']))


def validate_config(c, variables):
    lookup = {v.name: v for v in variables}
    assert c['actuator_max'] > c['actuator_min']
    for signal, causality in [(c['actuator_input'], 'input'), (c['actuator_activate'], 'input'),
                              (c['actuator_output'], 'output'), (c['temperature'], 'output'), (c['outdoor'], 'output')]:
        assert lookup[signal].causality == causality, signal
    for signal in [c['temperature'], c['outdoor']]:
        assert lookup[signal].unit == 'K', signal
    v = lookup[c['actuator_input']]
    assert v.unit == c['actuator_unit']
    if v.min is not None: assert c['actuator_min'] >= float(v.min)
    if v.max is not None: assert c['actuator_max'] <= float(v.max)
    assert lookup[c['actuator_activate']].type == 'Boolean'
    for o in c['overrides']:
        v = lookup[o['input']]
        assert v.causality == 'input' and lookup[o['activate']].type == 'Boolean'
        assert v.unit == o['unit']
        if v.min is not None: assert o['value'] >= float(v.min)
        if v.max is not None: assert o['value'] <= float(v.max)
    for signal in c['power_outputs'].values():
        assert lookup[signal].causality == 'output' and lookup[signal].unit == 'W'


def episode(c, name, start, hours, controller):
    from fmpy import extract, read_model_description
    from fmpy.fmi2 import FMU2Slave
    path = ROOT / 'outputs/boptest_consistent' / c['case'] / (name + '.csv')
    if path.exists() or path.with_suffix('.partial.csv').exists():
        raise RuntimeError('Trace already exists')
    began = time.perf_counter(); dt = c['step_s']; rows = []
    md = read_model_description(str(fmu_path(c)), validate=False)
    validate_config(c, md.modelVariables)
    vr = {v.name: v.valueReference for v in md.modelVariables}
    channels = {'T': c['temperature'], 'outdoor': c['outdoor'], 'actuator_native': c['actuator_output'], **c['power_outputs']}
    def write(destination):
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open('x') as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    try:
        with tempfile.TemporaryDirectory(prefix='boptest-native-') as temp:
            extract(str(fmu_path(c)), unzipdir=temp)
            fmu = FMU2Slave(guid=md.guid, unzipDirectory=temp, modelIdentifier=md.coSimulation.modelIdentifier, instanceName='native')
            fmu.instantiate()
            try:
                fmu.setupExperiment(startTime=start-86400); fmu.enterInitializationMode()
                for o in c['overrides']:
                    fmu.setBoolean([vr[o['activate']]], [True]); fmu.setReal([vr[o['input']]], [o['value']])
                fmu.exitInitializationMode()
                def observe():
                    state = dict(zip(channels, fmu.getReal([vr[v] for v in channels.values()])))
                    for k in ['T','outdoor']: state[k] -= 273.15
                    if not all(math.isfinite(v) for v in state.values()): raise ValueError('Nonfinite FMU output')
                    return state
                t = start-86400
                for _ in range(int(86400/dt)):
                    fmu.doStep(currentCommunicationPoint=t, communicationStepSize=dt); t += dt
                initial = observe(); initial_u = decode(c, initial['actuator_native'])
                if controller is not None: controller.prime(initial['T'], initial_u)
                fmu.setReal([vr[c['actuator_input']]], [encode(c,initial_u)])
                fmu.setBoolean([vr[c['actuator_activate']]], [True])
                for i in range(int(hours*3600/dt)):
                    state = observe(); previous_u = decode(c,state['actuator_native'])
                    u = clamp(initial_u+[-.15,.15,0,.25,-.25,.10][(i//15)%6]) if controller is None else controller.step(state['T'],previous_u,i,outdoor=state['outdoor'])
                    fmu.setReal([vr[c['actuator_input']]], [encode(c,u)])
                    fmu.doStep(currentCommunicationPoint=t, communicationStepSize=dt); nxt=observe()
                    row = dict(time_s=t, **state, previous_u=previous_u,u=u,next_T=nxt['T'])
                    if controller is not None: row.update(controller.diagnostics)
                    for k in c['power_outputs']: row['next_'+k] = nxt[k]
                    rows.append(row); t += dt
                fmu.terminate()
            finally:
                fmu.freeInstance()
    except Exception:
        if rows: write(path.with_suffix('.partial.csv'))
        raise
    write(path)
    return rows, {'trace':str(path.relative_to(ROOT)), 'sha256':sha(path), 'scored_hours':hours, 'warmup_hours':24,
                  'wall_seconds':time.perf_counter()-began, 'initial_state':initial,'initial_u':initial_u,'metrics':metrics(rows,c),
                  'first_30min_mae_C':metrics(rows[:30],c)['mae_C'],'after_30min_mae_C':metrics(rows[30:],c)['mae_C']}
