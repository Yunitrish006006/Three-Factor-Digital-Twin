"""Versioned source-blind thermal structure selection; earlier study stays frozen."""
from dataclasses import asdict, dataclass, replace
import math
import time

import numpy as np
from scipy.optimize import least_squares
from digital_twin.control.sparse_enclosure import HeatNetwork, SparseObserver, TransferSettings, command
from digital_twin.control.sparse_enclosure_v2 import TransferController
from digital_twin.enclosure.session import Observation


@dataclass(frozen=True)
class ThermalPathParameters(HeatNetwork):
    source_air: float = 0.

    def __post_init__(self):
        super().__post_init__()
        if not math.isfinite(self.source_air) or self.source_air < 0:
            raise ValueError('Source-air thermal conductance must be finite and nonnegative')


def thermal_rates(temperatures, fan, inlet, power, p):
    t = np.asarray(temperatures, dtype=float)
    hp = p.contact * (t[..., 0] - t[..., 1])
    pa = (p.plate_base + p.plate_fan * fan) * (t[..., 1] - t[..., 2])
    ha = p.source_air * (t[..., 0] - t[..., 2])
    out = (p.air_base + p.air_fan * fan) * (t[..., 2] - inlet)
    bypass = p.bypass * (t[..., 0] - inlet)
    return np.stack([power - hp - ha - bypass, hp - pa, pa + ha - out], axis=-1) / p.capacities


def advance(state, duty, inlet, power, p, dt=5., substeps=2):
    x, u = np.asarray(state, dtype=float).copy(), np.asarray(duty, dtype=float)
    if (x.shape[-1] != 4 or not np.isfinite(x).all() or not np.isfinite(u).all()
            or np.any((u < 0) | (u > 1)) or not math.isfinite(inlet)
            or not math.isfinite(power) or power < 0 or not math.isfinite(dt)
            or dt <= 0 or not isinstance(substeps, int) or substeps < 1):
        raise ValueError('Invalid thermal-network input')
    h = dt / substeps
    for _ in range(substeps):
        t, fan = x[..., :3], x[..., 3]
        middle = u + (fan - u) * np.exp(-h / (2 * p.fan_tau))
        k1 = thermal_rates(t, middle, inlet, power, p)
        k2 = thermal_rates(t + h*k1/2, middle, inlet, power, p)
        k3 = thermal_rates(t + h*k2/2, middle, inlet, power, p)
        k4 = thermal_rates(t + h*k3, middle, inlet, power, p)
        x[..., :3] = t + h*(k1 + 2*k2 + 2*k3 + k4)/6
        x[..., 3] = u + (fan-u)*np.exp(-h/p.fan_tau)
    if not np.isfinite(x).all():
        raise FloatingPointError('Nonfinite thermal state')
    return x


def transition(fan, p, dt):
    ch, cp, ca = p.capacities
    g, h = p.contact, p.source_air
    v, w = p.plate_base+p.plate_fan*fan, p.air_base+p.air_fan*fan
    matrix = np.array([[-(g+h+p.bypass)/ch, g/ch, h/ch],
                       [g/cp, -(g+v)/cp, v/cp],
                       [h/ca, v/ca, -(h+v+w)/ca]])*dt
    return np.eye(3)+matrix+matrix@matrix/2+matrix@matrix@matrix/6+matrix@matrix@matrix@matrix/24


class StructureObserver(SparseObserver):
    def predict(self, duty, inlet, power):
        a = transition(self.state[3], self.parameters, self.settings.dt)
        self.state = advance(self.state, duty, inlet, power, self.parameters, self.settings.dt)
        self.covariance = a@self.covariance@a.T + np.diag([.02, .01, .01])
        return self.state.copy()


class StructureController(TransferController):
    def ranked_candidates(self, estimate, inlet, power, previous, horizon):
        s = self.settings
        requests = np.linspace(s.pwm_min, s.pwm_max, 9)
        states = np.tile(estimate, (len(requests), 1))
        last, costs, first = np.full(len(requests), previous), np.zeros(len(requests)), None
        for _ in range(horizon):
            duties = np.clip(requests, np.maximum(s.pwm_min, last-s.slew), np.minimum(s.pwm_max, last+s.slew))
            if first is None:
                first = duties.copy()
            states = advance(states, duties, inlet, power, self.parameters, s.dt)
            costs += ((states[:, 0]-s.target)**2+s.input_cost*duties**2+s.slew_cost*(duties-last)**2
                      +s.thermal_cost*np.maximum(states[:, 0]-s.limit, 0)**2)
            last = duties
        chosen = int(np.argmin(costs/horizon))
        return float(first[chosen]), {'cost': float(costs[chosen]/horizon), 'requested_pwm': float(requests[chosen])}


class CalibratedEnclosureSession:
    def __init__(self, parameters, inlet_C, method='rank_h6', correction=True, settings=TransferSettings()):
        if not isinstance(parameters, ThermalPathParameters) or not math.isfinite(inlet_C):
            raise ValueError('A valid thermal path model and inlet are required')
        if method not in ('pi', 'rank_h6'):
            raise ValueError('This version isolates PI and six-step ranking')
        self.parameters, self.settings = parameters, settings
        self.observer = StructureObserver(parameters, inlet_C, correction=correction, settings=settings)
        self.controller = StructureController(method, parameters, settings)
        self.previous, self.last_time = .4, None

    def process(self, observation):
        if not isinstance(observation, Observation):
            raise TypeError('Declared sparse observation required')
        if self.last_time is not None and not math.isclose(
                observation.time_s-self.last_time, self.settings.dt, abs_tol=1e-6, rel_tol=0):
            raise ValueError('Invalid sample cadence; state unchanged')
        started = time.perf_counter()
        estimate = self.observer.update([observation.plate_C, observation.air_C, observation.fan_fraction])
        previous = self.previous
        duty, info = self.controller.step(estimate, observation.inlet_C, observation.power_W, previous,
                                          observed_plate_air=[observation.plate_C, observation.air_C])
        predicted = self.observer.predict(duty, observation.inlet_C, observation.power_W)
        self.previous, self.last_time = duty, observation.time_s
        return {'time_s': observation.time_s, 'source_estimate_C': float(estimate[0]),
                'source_prediction_next_C': float(predicted[0]), 'pwm': duty, 'previous_pwm': previous,
                'warning': int(info['warning']), 'fallback': 0,
                'compute_ms': 1000*(time.perf_counter()-started)}


STARTS = {'S': [.7, .8, 1., 15.], 'F': [.7, .8, 1., 1., 1., 15., .05]}
BOUNDS = {'S': ([.25, .3, .6, 5.], [1.5, 2., 1.6, 40.]),
          'F': ([.25, .3, .6, .6, .6, 5., 0.], [1.5, 2., 1.6, 1.6, 1.6, 40., .3])}


def parameters_for(structure, values):
    if structure not in STARTS:
        raise ValueError('Unknown model structure')
    scales = [values[2]]*3 if structure == 'S' else values[2:5]
    return ThermalPathParameters(contact=float(values[0]), plate_fan=float(values[1]),
                                 capacities=tuple(c*float(v) for c, v in zip((20., 80., 30.), scales)),
                                 fan_tau=float(values[3] if structure == 'S' else values[5]),
                                 source_air=0. if structure == 'S' else float(values[6]))


def visible_errors(parameters, observations, duties):
    state = np.array([observations[0].inlet_C]*3+[.4])
    errors = []
    for obs, duty in zip(observations, duties):
        errors.append((state[1:4]-[obs.plate_C, obs.air_C, obs.fan_fraction])/[.1, .1, .005])
        state = advance(state, duty, obs.inlet_C, obs.power_W, parameters)
    return np.asarray(errors)


def choose_structure(candidates):
    base, flexible = candidates['S'], candidates['F']
    return 'F' if (flexible['success'] and math.isfinite(flexible['selection_score'])
                   and flexible['selection_score'] <= .95*base['selection_score']) else 'S'


def fit_structures(records):
    """Two bounded fits on first120, chronological selection on last60; no refit."""
    if len(records) != 180:
        raise ValueError('Exactly180 commissioning samples required by this versioned protocol')
    observations = [Observation.from_row(row) for row in records]
    if any(not math.isclose(b.time_s-a.time_s, 5., rel_tol=0, abs_tol=1e-6)
           for a, b in zip(observations, observations[1:])):
        raise ValueError('Commissioning cadence must be5s')
    duties = np.array([float(row['pwm']) for row in records])
    if not np.isfinite(duties).all() or np.any((duties < 0) | (duties > 1)):
        raise ValueError('Invalid commissioning duty')
    candidates = {}
    for structure in ('S', 'F'):
        calls, started = 0, time.perf_counter()
        def residual(values):
            nonlocal calls
            calls += 1
            return visible_errors(parameters_for(structure, values), observations[:120], duties[:120]).ravel()
        fit = least_squares(residual, STARTS[structure], bounds=BOUNDS[structure], max_nfev=40)
        good = bool(fit.success and np.isfinite(fit.x).all())
        model = parameters_for(structure, fit.x) if good else ThermalPathParameters()
        scores = visible_errors(model, observations, duties)
        singular = np.linalg.svd(fit.jac, compute_uv=False)
        lower, upper = np.asarray(BOUNDS[structure][0]), np.asarray(BOUNDS[structure][1])
        hits = np.flatnonzero((fit.x-lower <= 1e-5*(upper-lower)) | (upper-fit.x <= 1e-5*(upper-lower)))
        candidates[structure] = {'success': good, 'fallback': not good, 'nfev': int(fit.nfev),
                                 'residual_calls': calls, 'wall_time_s': time.perf_counter()-started,
                                 'training_score': float(np.mean(scores[:120]**2)),
                                 'selection_score': float(np.mean(scores[120:]**2)),
                                 'parameters': asdict(model), 'fitted_values': [float(v) for v in fit.x],
                                 'parameter_bound_indices': [int(v) for v in hits],
                                 'jacobian_condition': float(singular[0]/singular[-1]) if singular[-1]>1e-12 else None}
    selected = choose_structure(candidates)
    return ThermalPathParameters(**candidates[selected]['parameters']), {
        'selected_structure': selected, 'candidates': candidates, 'training_rows': 120,
        'selection_rows': 60, 'trial_count': 2, 'refit_after_selection': False,
        'selection_channels': ['plate_C', 'air_C', 'fan_fraction'],
        'known_initial_state': 'all temperatures=inlet and fan=.4', 'source_reference_input': False}
