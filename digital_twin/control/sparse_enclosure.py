"""Temperature-only transfer candidate. No hardware API or held-out truth input.

This adapts the physics -> sparse correction -> action-ranking workflow, rather
than replacing the room estimator or calling finite candidate ranking full MPC.
"""
from dataclasses import dataclass, replace, asdict
import math

import numpy as np
from scipy.optimize import least_squares


@dataclass(frozen=True)
class HeatNetwork:
    capacities: tuple = (20., 80., 30.)
    contact: float = .7
    plate_base: float = .15
    plate_fan: float = .8
    air_base: float = 1.
    air_fan: float = 1.5
    bypass: float = .05
    fan_tau: float = 15.

    def __post_init__(self):
        numbers = [*self.capacities, self.contact, self.plate_base, self.plate_fan,
                   self.air_base, self.air_fan, self.bypass, self.fan_tau]
        if len(self.capacities) != 3 or any(not math.isfinite(v) or v <= 0 for v in numbers):
            raise ValueError('Finite positive network parameters required')


@dataclass(frozen=True)
class TransferSettings:
    dt: float = 5.
    target: float = 28.
    warning: float = 29.5
    limit: float = 30.
    pwm_min: float = .2
    pwm_max: float = 1.
    slew: float = .1
    kp: float = .12
    ki: float = .002
    kd: float = .05
    derivative_alpha: float = .25
    backcalc: float = .2
    input_cost: float = .15
    slew_cost: float = .5
    thermal_cost: float = 100.


def command(request, previous, s=TransferSettings()):
    if not math.isfinite(request) or not math.isfinite(previous):
        raise ValueError('Nonfinite command')
    if not s.pwm_min - 1e-10 <= previous <= s.pwm_max + 1e-10:
        raise ValueError('Previous command outside bounds')
    return float(np.clip(request, max(s.pwm_min, previous - s.slew),
                         min(s.pwm_max, previous + s.slew)))


def thermal_rhs(temps, fan, inlet, power, p):
    """Equal-and-opposite internal exchanges, supporting batched temperatures."""
    t = np.asarray(temps, dtype=float)
    source_plate = p.contact * (t[..., 0] - t[..., 1])
    plate_air = (p.plate_base + p.plate_fan * fan) * (t[..., 1] - t[..., 2])
    air_out = (p.air_base + p.air_fan * fan) * (t[..., 2] - inlet)
    bypass = p.bypass * (t[..., 0] - inlet)
    return np.stack([power - source_plate - bypass,
                     source_plate - plate_air, plate_air - air_out], axis=-1) / p.capacities


def advance(state, request, inlet, power, p, dt=5., substeps=2):
    """RK4 heat integration with analytic mid-substep fan and exact fan endpoint."""
    x = np.asarray(state, dtype=float).copy()
    u = np.asarray(request, dtype=float)
    if (x.shape[-1] != 4 or not np.isfinite(x).all() or not np.isfinite(u).all()
            or not math.isfinite(inlet) or not math.isfinite(power)
            or not math.isfinite(dt) or dt <= 0 or substeps < 1
            or np.any((u < 0) | (u > 1))):
        raise ValueError('Invalid thermal-network input')
    h = dt / substeps
    for _ in range(substeps):
        t, fan = x[..., :3], x[..., 3]
        mid = u + (fan - u) * np.exp(-h / (2 * p.fan_tau))
        k1 = thermal_rhs(t, mid, inlet, power, p)
        k2 = thermal_rhs(t + h * k1 / 2, mid, inlet, power, p)
        k3 = thermal_rhs(t + h * k2 / 2, mid, inlet, power, p)
        k4 = thermal_rhs(t + h * k3, mid, inlet, power, p)
        x[..., :3] = t + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        x[..., 3] = u + (fan - u) * np.exp(-h / p.fan_tau)
    if not np.isfinite(x).all():
        raise FloatingPointError('Nonfinite network evolution')
    return x


def transition_jacobian(fan, p, dt):
    ch, cp, ca = p.capacities
    g, v, w = p.contact, p.plate_base + p.plate_fan * fan, p.air_base + p.air_fan * fan
    m = np.array([[-(g + p.bypass) / ch, g / ch, 0.],
                  [g / cp, -(g + v) / cp, v / cp],
                  [0., v / ca, -(v + w) / ca]]) * dt
    return np.eye(3) + m + m @ m / 2 + m @ m @ m / 6 + m @ m @ m @ m / 24


class SparseObserver:
    """Only plate/air/fan measurements; source temperature is inferred."""
    def __init__(self, parameters, inlet, correction=True, settings=TransferSettings()):
        self.parameters, self.settings, self.correction = parameters, settings, correction
        self.state = np.array([inlet, inlet, inlet, .4], dtype=float)
        self.covariance = np.diag([4., 1., 1.])
        self.measurement = np.array([[0., 1., 0.], [0., 0., 1.]])

    def update(self, plate_air_fan):
        obs = np.asarray(plate_air_fan, dtype=float)
        if obs.shape != (3,) or not np.isfinite(obs).all():
            raise ValueError('Expected finite plate, air and normalized RPM only')
        self.state[3] = np.clip(obs[2], 0., 1.)
        if self.correction:
            h, p = self.measurement, self.covariance
            r = np.diag([.01, .01])
            gain = np.linalg.solve(h @ p @ h.T + r, h @ p).T
            self.state[:3] += gain @ (obs[:2] - h @ self.state[:3])
            a = np.eye(3) - gain @ h
            self.covariance = a @ p @ a.T + gain @ r @ gain.T
        return self.state.copy()

    def predict(self, u, inlet, power):
        a = transition_jacobian(self.state[3], self.parameters, self.settings.dt)
        self.state = advance(self.state, u, inlet, power, self.parameters, self.settings.dt)
        self.covariance = a @ self.covariance @ a.T + np.diag([.02, .01, .01])
        return self.state.copy()


class TransferController:
    def __init__(self, method, parameters, settings=TransferSettings()):
        if method not in ('fixed', 'pi', 'pid', 'rank_h1', 'rank_h6', 'rank_h6_no_correction'):
            raise ValueError('Unknown transfer method')
        self.method, self.parameters, self.settings = method, parameters, settings
        self.integral, self.last_error, self.derivative = 0., None, 0.

    def ranked_candidates(self, estimate, inlet, power, previous, horizon):
        s = self.settings
        requests = np.linspace(s.pwm_min, s.pwm_max, 9)
        states = np.tile(estimate, (len(requests), 1))
        last = np.full(len(requests), previous)
        costs, first = np.zeros(len(requests)), None
        for _ in range(horizon):
            commands = np.clip(requests, np.maximum(s.pwm_min, last - s.slew),
                               np.minimum(s.pwm_max, last + s.slew))
            if first is None:
                first = commands.copy()
            states = advance(states, commands, inlet, power, self.parameters, s.dt)
            costs += ((states[:, 0] - s.target) ** 2 + s.input_cost * commands ** 2
                      + s.slew_cost * (commands - last) ** 2
                      + s.thermal_cost * np.maximum(states[:, 0] - s.limit, 0.) ** 2)
            last = commands
        index = int(np.argmin(costs / horizon))
        return float(first[index]), {'cost': float(costs[index] / horizon),
                                     'requested_pwm': float(requests[index])}

    def step(self, estimate, inlet, power, previous):
        x, s = np.asarray(estimate, dtype=float), self.settings
        if x.shape != (4,) or not np.isfinite(x).all():
            raise ValueError('Expected source-blind state estimate')
        info = {'warning': False}
        if self.method == 'fixed':
            raw = .6
        elif self.method in ('pi', 'pid'):
            error = float(x[0] - s.target)
            rate = 0. if self.last_error is None else (error - self.last_error) / s.dt
            self.derivative += s.derivative_alpha * (rate - self.derivative)
            self.integral += s.ki * error * s.dt
            self.last_error = error
            raw = .6 + s.kp * error + self.integral
            if self.method == 'pid':
                raw += s.kd * self.derivative
        else:
            horizon = 1 if self.method == 'rank_h1' else 6
            raw, extra = self.ranked_candidates(x, inlet, power, previous, horizon)
            info.update(extra)
        if np.max(x[:3]) >= s.warning:
            raw, info['warning'] = s.pwm_max, True
        u = command(raw, previous, s)
        if self.method in ('pi', 'pid'):
            self.integral += s.backcalc * (u - raw)
        return u, info


def fit_sparse_network(records, settings=TransferSettings()):
    """Single bounded fit using observed plate/air only, never source truth."""
    nominal = HeatNetwork()

    def residual(values):
        p = replace(nominal, contact=float(values[0]), plate_fan=float(values[1]))
        first = records[0]
        x = np.array([first['inlet']] * 3 + [.4])
        errors = []
        for row in records:
            errors.extend(x[1:3] - [row['plate'], row['air']])
            x = advance(x, row['pwm'], row['inlet'], row['power'], p, settings.dt)
        return np.asarray(errors)

    if not records:
        raise ValueError('Empty calibration data')
    fit = least_squares(residual, [.7, .8], bounds=([.25, .3], [1.5, 2.]), max_nfev=30)
    singular = np.linalg.svd(fit.jac, compute_uv=False)
    condition = float(singular[0] / singular[-1]) if singular[-1] > 1e-12 else None
    success = bool(fit.success and np.isfinite(fit.x).all())
    p = replace(nominal, contact=float(fit.x[0]), plate_fan=float(fit.x[1])) if success else nominal
    return p, {'success': success, 'fallback': not success, 'nfev': fit.nfev,
               'cost': float(fit.cost), 'jacobian_condition': condition,
               'estimated_parameters': asdict(p), 'input_temperature_channels': ['plate', 'air']}
