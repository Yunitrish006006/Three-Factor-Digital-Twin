"""Offline, temperature-only enclosure workflow; no hardware actuation or truth input.

The existing room estimator retains its own humidity/light/spatial contracts.
This module integrates calibrated thermal prediction, sparse correction and
control through a separate measured-input interface in the canonical package.
"""
from dataclasses import dataclass, asdict, replace
import math
import time

import numpy as np
from scipy.linalg import solve_discrete_are
from scipy.optimize import brentq, least_squares, minimize

from digital_twin.control.sparse_enclosure import (
    HeatNetwork, TransferSettings, SparseObserver, advance, command,
)
from digital_twin.control.sparse_enclosure_v2 import TransferController

METHODS = ('fixed', 'pi', 'pid', 'lqr', 'linear_mpc', 'rank_h1', 'rank_h6',
           'rank_h6_no_correction')


@dataclass(frozen=True)
class Observation:
    time_s: float
    plate_C: float
    air_C: float
    fan_fraction: float
    inlet_C: float
    power_W: float

    def __post_init__(self):
        if (any(not math.isfinite(v) for v in asdict(self).values())
                or self.time_s < 0 or self.power_W < 0
                or not 0 <= self.fan_fraction <= 1):
            raise ValueError('Finite time/temperatures, nonnegative power and fan in [0,1] required')

    @classmethod
    def from_row(cls, row):
        # Explicit selection: reference/scorer columns never become inputs.
        return cls(**{key: float(row[key]) for key in cls.__dataclass_fields__})


def steady_state(parameters, inlet, power, pwm):
    p = parameters
    g, v, w = p.contact, p.plate_base + p.plate_fan * pwm, p.air_base + p.air_fan * pwm
    conductance = np.array([[g + p.bypass, -g, 0.], [-g, g + v, -v], [0., -v, v + w]])
    temperatures = np.linalg.solve(conductance, [power + p.bypass * inlet, 0., w * inlet])
    return np.r_[temperatures, pwm]


def equilibrium(parameters, inlet, power, settings):
    low, high = settings.pwm_min, settings.pwm_max
    warm = steady_state(parameters, inlet, power, low)[0]
    cool = steady_state(parameters, inlet, power, high)[0]
    if warm <= settings.target:
        duty = low
    elif cool >= settings.target:
        duty = high
    else:
        duty = brentq(lambda u: steady_state(parameters, inlet, power, u)[0] - settings.target,
                      low, high)
    return steady_state(parameters, inlet, power, duty), duty


def linearize(state, pwm, inlet, power, parameters, dt):
    x = np.asarray(state, dtype=float)
    eps = 1e-5
    base = advance(x, pwm, inlet, power, parameters, dt)
    a = np.column_stack([(advance(x + eps * e, pwm, inlet, power, parameters, dt)
                          - advance(x - eps * e, pwm, inlet, power, parameters, dt)) / (2 * eps)
                         for e in np.eye(4)])
    # At duty=1 a central stencil would exceed the primitive's physical bounds.
    left, right = max(0., pwm - eps), min(1., pwm + eps)
    b = ((advance(x, right, inlet, power, parameters, dt)
          - advance(x, left, inlet, power, parameters, dt)) / (right - left)).reshape(4, 1)
    return a, b, base - a @ x - b[:, 0] * pwm


class SessionController(TransferController):
    """Sparse-state comparators; common raw warning and final command limiting."""
    def __init__(self, method, parameters, settings=TransferSettings()):
        if method not in METHODS:
            raise ValueError('Unknown enclosure session method')
        super().__init__('rank_h6' if method in ('lqr', 'linear_mpc') else method,
                         parameters, settings)
        self.method = method

    def linear_mpc(self, estimate, inlet, power, previous):
        s, horizon = self.settings, 6
        a, b, offset = linearize(estimate, previous, inlet, power, self.parameters, s.dt)
        state = np.asarray(estimate).copy()
        influence = np.zeros((4, horizon))
        base, gain = [], []
        for k in range(horizon):
            state = a @ state + offset
            influence = a @ influence
            influence[:, k] += b[:, 0]
            base.append(state[0])
            gain.append(influence[0].copy())
        base, gain = np.asarray(base), np.asarray(gain)
        difference = np.eye(horizon) - np.eye(horizon, k=-1)
        first = np.r_[previous, np.zeros(horizon - 1)]

        def objective(u):
            predicted = base + gain @ u
            delta = difference @ u - first
            error = predicted - s.target
            excess = np.maximum(predicted - s.limit, 0.)
            value = (error @ error + s.input_cost * (u @ u)
                     + s.slew_cost * (delta @ delta) + s.thermal_cost * (excess @ excess)) / horizon
            gradient = (2 * gain.T @ (error + s.thermal_cost * excess)
                        + 2 * s.input_cost * u + 2 * s.slew_cost * difference.T @ delta) / horizon
            return float(value), gradient

        constraints = {'type': 'ineq',
                       'fun': lambda u: np.r_[s.slew - (difference @ u - first),
                                              s.slew + (difference @ u - first)],
                       'jac': lambda u: np.vstack([-difference, difference])}
        fit = minimize(objective, np.full(horizon, previous), jac=True, method='SLSQP',
                       bounds=[(s.pwm_min, s.pwm_max)] * horizon,
                       constraints=constraints, options={'ftol': 1e-7, 'maxiter': 40})
        good = (fit.success and np.isfinite(fit.x).all()
                and np.all(fit.x >= s.pwm_min - 1e-7)
                and np.all(fit.x <= s.pwm_max + 1e-7)
                and np.all(np.abs(difference @ fit.x - first) <= s.slew + 1e-7))
        if not good:
            raise ArithmeticError('Linear MPC solution failed sequence feasibility checks')
        return float(fit.x[0]), {'optimizer_iterations': int(fit.nit), 'cost': float(fit.fun)}

    def step(self, estimate, inlet, power, previous, *, observed_plate_air):
        if self.method not in ('lqr', 'linear_mpc'):
            u, info = super().step(estimate, inlet, power, previous,
                                   observed_plate_air=observed_plate_air)
            return u, {**info, 'fallback': False}
        x, raw_observed = np.asarray(estimate, dtype=float), np.asarray(observed_plate_air, dtype=float)
        if (x.shape != (4,) or raw_observed.shape != (2,)
                or not np.isfinite(x).all() or not np.isfinite(raw_observed).all()
                or not math.isfinite(inlet) or not math.isfinite(power) or power < 0):
            raise ValueError('Invalid sparse controller input')
        s, info = self.settings, {'warning': False, 'fallback': False}
        try:
            if self.method == 'lqr':
                center, feedforward = equilibrium(self.parameters, inlet, power, s)
                a, b, _ = linearize(center, feedforward, inlet, power, self.parameters, s.dt)
                q, r = np.diag([1., .25, .1, .02]), np.array([[.15]])
                p = solve_discrete_are(a, b, q, r)
                gain = np.linalg.solve(r + b.T @ p @ b, b.T @ p @ a)
                raw = float(feedforward - (gain @ (x - center))[0])
            else:
                raw, details = self.linear_mpc(x, inlet, power, previous)
                info.update(details)
            if not math.isfinite(raw):
                raise ArithmeticError('Nonfinite optimizer command')
        except (ArithmeticError, np.linalg.LinAlgError, ValueError):
            raw, details = self.ranked_candidates(x, inlet, power, previous, 6)
            info.update(details)
            info['fallback'] = True
        if max(float(x[0]), float(np.max(raw_observed))) >= s.warning:
            raw, info['warning'] = s.pwm_max, True
        return command(raw, previous, s), info


class EnclosureSession:
    """One advancing stream. Reference temperatures are intentionally absent."""
    def __init__(self, parameters, inlet_C, method='rank_h6', correction=True,
                 settings=TransferSettings(), previous_pwm=.4):
        if (not math.isfinite(inlet_C) or settings.dt <= 0
                or not settings.pwm_min <= previous_pwm <= settings.pwm_max):
            raise ValueError('Invalid session initialization')
        self.settings, self.parameters = settings, parameters
        self.observer = SparseObserver(parameters, inlet_C,
                                       correction=correction and method != 'rank_h6_no_correction',
                                       settings=settings)
        self.controller = SessionController(method, parameters, settings)
        self.previous_pwm, self.last_time = previous_pwm, None

    def process(self, observation):
        if not isinstance(observation, Observation):
            raise TypeError('An Observation with declared input channels is required')
        if self.last_time is not None and not math.isclose(
                observation.time_s - self.last_time, self.settings.dt, rel_tol=0., abs_tol=1e-6):
            raise ValueError('Missing, duplicate or out-of-order sample; session unchanged')
        started = time.perf_counter()
        estimated = self.observer.update([observation.plate_C, observation.air_C,
                                          observation.fan_fraction])
        previous = self.previous_pwm
        duty, info = self.controller.step(estimated, observation.inlet_C, observation.power_W,
                                          previous, observed_plate_air=[observation.plate_C, observation.air_C])
        predicted = self.observer.predict(duty, observation.inlet_C, observation.power_W)
        self.previous_pwm, self.last_time = duty, observation.time_s
        return {'time_s': observation.time_s, 'source_estimate_C': float(estimated[0]),
                'source_prediction_next_C': float(predicted[0]), 'pwm': duty,
                'previous_pwm': previous, 'warning': bool(info['warning']),
                'fallback': bool(info['fallback']), 'compute_ms': 1000 * (time.perf_counter() - started)}


def fit_observations(records, settings=TransferSettings()):
    """Bounded commissioning; known initial equilibrium and capacity ratios.

    No reference channel is selected. Actual residual calls include numerical
    differentiation; nfev alone is not the total computation budget.
    """
    if not records:
        raise ValueError('Empty commissioning data')
    observations = [Observation.from_row(row) for row in records]
    for current, following in zip(observations, observations[1:]):
        if not math.isclose(following.time_s - current.time_s, settings.dt, rel_tol=0., abs_tol=1e-6):
            raise ValueError('Calibration cadence must be fixed')
    commands = np.array([float(row['pwm']) for row in records])
    if not np.isfinite(commands).all() or np.any((commands < 0) | (commands > 1)):
        raise ValueError('Calibration commands must be in [0,1]')
    nominal, calls = HeatNetwork(), 0
    def parameters(values):
        return replace(nominal, contact=float(values[0]), plate_fan=float(values[1]),
                       capacities=tuple(c * float(values[2]) for c in nominal.capacities),
                       fan_tau=float(values[3]))
    def residual(values):
        nonlocal calls
        calls += 1
        p = parameters(values)
        initial_inlet = observations[0].inlet_C
        state = np.array([initial_inlet] * 3 + [.4])
        errors = []
        for obs, duty in zip(observations, commands):
            errors.extend((state[1:4] - [obs.plate_C, obs.air_C, obs.fan_fraction]) / [.1, .1, .005])
            state = advance(state, duty, obs.inlet_C, obs.power_W, p, settings.dt)
        return np.asarray(errors)
    started = time.perf_counter()
    fit = least_squares(residual, [.7, .8, 1., 15.],
                        bounds=([.25, .3, .6, 5.], [1.5, 2., 1.6, 40.]), max_nfev=40)
    singular = np.linalg.svd(fit.jac, compute_uv=False)
    good = bool(fit.success and np.isfinite(fit.x).all())
    fitted = parameters(fit.x) if good else nominal
    return fitted, {'success': good, 'fallback': not good, 'nfev': int(fit.nfev),
                    'residual_calls': calls, 'wall_time_s': time.perf_counter() - started,
                    'cost': float(fit.cost), 'jacobian_condition': float(singular[0] / singular[-1])
                    if singular[-1] > 1e-12 else None, 'parameters': asdict(fitted),
                    'input_channels': list(Observation.__dataclass_fields__),
                    'known_initial_state': 'all temperatures equal measured inlet; fan .4',
                    'fitted_parameters': ['contact', 'plate_fan', 'common_capacity_scale', 'fan_tau']}
