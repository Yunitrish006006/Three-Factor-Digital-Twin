"""Assumed enclosure model and constrained MPC; no physical actuation.

Plant integration and controller prediction are deliberately different.
Temperature limits are soft constraints; bounds and slew are hard constraints.
"""
from dataclasses import dataclass, replace
import math
import time

import numpy as np
from scipy.optimize import minimize


@dataclass(frozen=True)
class ThermalParameters:
    capacities: tuple = (1200., 1800.)  # J/K, CPU/GPU
    conductances: tuple = (1.5, 2.)  # W/K
    fan_gains: tuple = (6., 8.)  # W/K per normalized effective fan
    fan_tau_s: float = 20.
    max_rpm: float = 6000.

    def __post_init__(self):
        if any(len(v) != 2 for v in (self.capacities, self.conductances, self.fan_gains)):
            raise ValueError('Two thermal nodes required')
        if not all(math.isfinite(v) and v > 0 for v in
                   (*self.capacities, *self.conductances, *self.fan_gains,
                    self.fan_tau_s, self.max_rpm)):
            raise ValueError('Physical parameters must be positive and finite')


@dataclass(frozen=True)
class ControlSettings:
    dt_s: float = 10.
    horizon: int = 12
    targets_C: tuple = (60., 60.)
    limits_C: tuple = (80., 85.)
    warnings_C: tuple = (75., 80.)
    pwm_min: float = .2
    pwm_max: float = 1.
    max_delta: float = .1
    margin_C: float = 2.
    input_weight: float = 1.
    delta_weight: float = 5.
    slack_weight: float = 1e4
    maxiter: int = 80

    def __post_init__(self):
        if (not isinstance(self.horizon, int) or self.horizon < 1
                or self.maxiter < 1 or self.dt_s <= 0
                or not 0 <= self.pwm_min < self.pwm_max <= 1
                or not 0 < self.max_delta <= 1
                or any(len(v) != 2 for v in (self.targets_C, self.limits_C, self.warnings_C))):
            raise ValueError('Invalid controller settings')
        values = (self.dt_s, self.pwm_min, self.pwm_max, self.max_delta,
                  self.margin_C, self.input_weight, self.delta_weight, self.slack_weight,
                  *self.targets_C, *self.limits_C, *self.warnings_C)
        if not all(math.isfinite(v) for v in values):
            raise ValueError('Nonfinite settings')
        if (self.margin_C < 0 or self.input_weight < 0 or self.delta_weight < 0
                or self.slack_weight <= 0
                or any(t >= w or w >= lim for t, w, lim in
                       zip(self.targets_C, self.warnings_C, self.limits_C))):
            raise ValueError('Invalid costs or temperature ordering')


def validate_observation(state, inlet_C, powers_W):
    x, p = np.asarray(state, float), np.asarray(powers_W, float)
    if (x.shape != (3,) or p.shape != (2,) or not np.isfinite(x).all()
            or not np.isfinite(p).all() or not math.isfinite(inlet_C)
            or (p < 0).any() or not 0 <= x[2] <= 1):
        raise ValueError('Invalid state, inlet or powers')
    return x, p


class EnclosurePlant:
    def __init__(self, parameters=None):
        self.parameters = parameters or ThermalParameters()
        self.reset()

    def reset(self, temperatures_C=(60., 60.), fan=.5):
        self.state = np.array([*temperatures_C, fan], float)
        validate_observation(self.state, 30., (0., 0.))
        return self.state.copy()

    def step(self, pwm, inlet_C, powers_W, dt_s=10.):
        x, p = validate_observation(self.state, inlet_C, powers_W)
        if not math.isfinite(pwm) or not 0 <= pwm <= 1 or not math.isfinite(dt_s) or dt_s <= 0:
            raise ValueError('Invalid actuator or time step')
        pars = self.parameters
        # At most one-second thermal integration; fan uses exact first-order update.
        substeps = int(math.ceil(dt_s))
        h = dt_s / substeps
        for _ in range(substeps):
            cooling = np.asarray(pars.conductances) + np.asarray(pars.fan_gains) * x[2]
            x[:2] += h * (p - cooling * (x[:2] - inlet_C)) / pars.capacities
            x[2] = pwm + (x[2] - pwm) * math.exp(-h / pars.fan_tau_s)
        self.state = x
        return x.copy()


def linearize(state, inlet_C, powers_W, parameters, settings):
    """Affine Euler x_next=A x+B u+c about the observed operating point."""
    x, p = validate_observation(state, inlet_C, powers_W)
    c = np.asarray(parameters.capacities)
    gain = np.asarray(parameters.fan_gains)
    cooling = np.asarray(parameters.conductances) + gain * x[2]
    jac = np.zeros((3, 3))
    jac[0, 0], jac[1, 1] = -cooling / c
    jac[:2, 2] = -gain * (x[:2] - inlet_C) / c
    jac[2, 2] = -1 / parameters.fan_tau_s
    b = np.array([0., 0., 1 / parameters.fan_tau_s])
    drift = np.r_[(p - cooling * (x[:2] - inlet_C)) / c,
                  -x[2] / parameters.fan_tau_s]
    return np.eye(3) + settings.dt_s * jac, settings.dt_s * b, settings.dt_s * (drift - jac @ x)


def prediction_map(state, inlet_C, powers_W, parameters, settings):
    A, B, c = linearize(state, inlet_C, powers_W, parameters, settings)
    base, mapping = [], []
    x = np.asarray(state, float).copy()
    m = np.zeros((3, settings.horizon))
    for k in range(settings.horizon):
        x = A @ x + c
        m = A @ m
        m[:, k] += B
        base.extend(x[:2])
        mapping.extend(m[:2].copy())
    return np.asarray(base), np.asarray(mapping)


def bounded_command(request, previous, settings):
    if not math.isfinite(request) or not math.isfinite(previous):
        raise ValueError('Nonfinite PWM')
    if not settings.pwm_min - 1e-8 <= previous <= settings.pwm_max + 1e-8:
        raise ValueError('Previous PWM outside actuator limits')
    low = max(settings.pwm_min, previous - settings.max_delta)
    high = min(settings.pwm_max, previous + settings.max_delta)
    return float(np.clip(request, low, high))


class EnclosureMPC:
    def __init__(self, parameters=None, settings=None):
        self.parameters = parameters or ThermalParameters()
        self.settings = settings or ControlSettings()
        if self.settings.dt_s > self.parameters.fan_tau_s:
            raise ValueError('Euler predictor requires dt <= fan time constant')
        self.warm = None

    def step(self, state, inlet_C, powers_W, previous):
        started = time.perf_counter()
        x, _ = validate_observation(state, inlet_C, powers_W)
        s, n = self.settings, self.settings.horizon
        bounded_command(previous, previous, s)
        base, M = prediction_map(x, inlet_C, powers_W, self.parameters, s)
        reference = np.tile(s.targets_C, n)
        caps = np.tile(np.asarray(s.limits_C) - s.margin_C, n)
        D = np.eye(n) - np.eye(n, k=-1)
        previous_vector = np.r_[previous, np.zeros(n - 1)]

        def objective(z):
            u, slack = z[:n], z[n:]
            error = (base + M @ u - reference) / 5.
            delta = D @ u - previous_vector
            return (error @ error + s.input_weight * (u @ u)
                    + s.delta_weight * (delta @ delta) + s.slack_weight * (slack @ slack))

        def gradient(z):
            u, slack = z[:n], z[n:]
            g = (2 * M.T @ (base + M @ u - reference) / 25.
                 + 2 * s.input_weight * u
                 + 2 * s.delta_weight * D.T @ (D @ u - previous_vector))
            return np.r_[g, 2 * s.slack_weight * slack]

        # All constraints are affine, including thermal slack.
        K = np.vstack([np.c_[D, np.zeros((n, 2*n))],
                       np.c_[-D, np.zeros((n, 2*n))],
                       np.c_[M, -np.eye(2*n)]])
        upper = np.r_[s.max_delta + previous_vector,
                      s.max_delta - previous_vector, caps - base]
        guess = self.warm if self.warm is not None else np.full(n, previous)
        u0, last = [], previous
        for item in guess:
            last = bounded_command(float(item), last, s)
            u0.append(last)
        u0 = np.asarray(u0)
        z0 = np.r_[u0, np.maximum(0., base + M @ u0 - caps) + 1e-6]
        reason, raw_status, z = '', 'not_run', None
        try:
            result = minimize(objective, z0, jac=gradient, method='SLSQP',
                              bounds=[(s.pwm_min, s.pwm_max)] * n + [(0., None)] * (2*n),
                              constraints={'type': 'ineq', 'fun': lambda z: upper - K @ z,
                                           'jac': lambda z: -K},
                              options={'maxiter': s.maxiter, 'ftol': 1e-7})
            z, raw_status = result.x, str(result.message)
            valid = (result.success and np.isfinite(z).all()
                     and np.min(upper - K @ z) >= -1e-5
                     and np.min(z[:n]) >= s.pwm_min - 1e-5
                     and np.max(z[:n]) <= s.pwm_max + 1e-5
                     and np.min(z[n:]) >= -1e-5)
            if not valid:
                reason = 'solver_or_residual_failure'
        except (ValueError, FloatingPointError, RuntimeError) as exc:
            reason, raw_status = 'solver_exception', type(exc).__name__
        if reason:
            applied = bounded_command(s.pwm_max, previous, s)
            self.warm = None
        else:
            applied = bounded_command(float(z[0]), previous, s)
            self.warm = np.r_[z[1:n], z[n-1]]
        safety = bool(np.any(x[:2] >= s.warnings_C))
        if safety:
            applied = bounded_command(s.pwm_max, previous, s)
        A, B, c = linearize(x, inlet_C, powers_W, self.parameters, s)
        predicted = A @ x + B * applied + c
        return applied, {'predicted': predicted, 'fallback': bool(reason),
                         'reason': reason, 'solver_status': raw_status,
                         'slack_max_C': float(np.max(z[n:])) if z is not None and np.isfinite(z).all() else None,
                         'safety_override': safety, 'solve_s': time.perf_counter() - started}


class EnclosureBaseline:
    def __init__(self, method, parameters=None, settings=None, **kwargs):
        if method not in ('fixed', 'pid'):
            raise ValueError('Unknown baseline')
        self.method, self.values = method, kwargs
        self.parameters, self.settings = parameters or ThermalParameters(), settings or ControlSettings()
        self.integral, self.previous_error = 0., None

    def step(self, state, inlet_C, powers_W, previous):
        x, _ = validate_observation(state, inlet_C, powers_W)
        s = self.settings
        if self.method == 'fixed':
            raw = self.values['pwm']
        else:
            error = float(np.max(x[:2] - s.targets_C))
            derivative = 0. if self.previous_error is None else (error - self.previous_error) / s.dt_s
            self.integral += self.values['ki'] * error * s.dt_s
            raw = .5 + self.values['kp'] * error + self.integral + self.values['kd'] * derivative
            self.previous_error = error
        safety = bool(np.any(x[:2] >= s.warnings_C))
        applied = bounded_command(s.pwm_max if safety else raw, previous, s)
        if self.method == 'pid':
            self.integral += .2 * (applied - raw)
        A, B, c = linearize(x, inlet_C, powers_W, self.parameters, s)
        return applied, {'predicted': A @ x + B * applied + c, 'fallback': False,
                         'reason': '', 'solver_status': 'baseline', 'slack_max_C': None,
                         'safety_override': safety, 'solve_s': 0.}
