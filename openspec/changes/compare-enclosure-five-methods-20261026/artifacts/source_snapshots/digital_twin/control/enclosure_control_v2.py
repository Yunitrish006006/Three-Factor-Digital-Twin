"""Versioned four-controller simulation implementation; no physical actuation.

The v1 plant and settings remain frozen. All methods share command limiting and
warning/failure handling. Temperature constraints are soft, not safety proofs.
"""
from dataclasses import replace
import math
import time

import numpy as np
import osqp
from scipy import sparse
from scipy.linalg import expm, solve_discrete_are
from scipy.optimize import minimize_scalar

from .enclosure_mpc import (
    ControlSettings, ThermalParameters, EnclosurePlant, bounded_command,
    validate_observation,
)


OSQP_OPTIONS = dict(eps_abs=1e-7, eps_rel=1e-7, max_iter=100000, rho=1., eps_prim_inf=1e-10, eps_dual_inf=1e-10,
                    adaptive_rho_interval=25, polishing=True, verbose=False)
RESIDUAL_TOL = 1e-5
OBJECTIVE_SCALE = 1.0
DARE_RESIDUAL_TOL = 1e-5


def linearize_zoh(state, inlet_C, powers_W, parameters, settings):
    """Exact ZOH discretization of the local continuous affine approximation."""
    x, p = validate_observation(state, inlet_C, powers_W)
    capacities = np.asarray(parameters.capacities)
    gains = np.asarray(parameters.fan_gains)
    cooling = np.asarray(parameters.conductances) + gains * x[2]
    jac = np.zeros((3, 3))
    jac[0, 0], jac[1, 1] = -cooling / capacities
    jac[:2, 2] = -gains * (x[:2] - inlet_C) / capacities
    jac[2, 2] = -1. / parameters.fan_tau_s
    b = np.array([0., 0., 1. / parameters.fan_tau_s])
    drift = np.r_[(p - cooling * (x[:2] - inlet_C)) / capacities,
                  -x[2] / parameters.fan_tau_s]
    augmented = np.zeros((5, 5))
    augmented[:3, :3] = jac
    augmented[:3, 3] = b
    augmented[:3, 4] = drift - jac @ x
    discrete = expm(settings.dt_s * augmented)
    if not np.isfinite(discrete).all():
        raise FloatingPointError('Nonfinite affine ZOH model')
    return discrete[:3, :3], discrete[:3, 3], discrete[:3, 4]


def prediction_map_v2(state, inlet_C, powers_W, parameters, settings):
    """Condensed thermal prediction for a fixed local model over the horizon."""
    A, B, c = linearize_zoh(state, inlet_C, powers_W, parameters, settings)
    return _prediction_map(state, A, B, c, settings.horizon)


def _prediction_map(state, A, B, c, horizon):
    x = np.asarray(state, dtype=float).copy()
    mapping = np.zeros((3, horizon))
    base, blocks = [], []
    for index in range(horizon):
        x = A @ x + c
        mapping = A @ mapping
        mapping[:, index] += B
        base.extend(x[:2])
        blocks.extend(mapping[:2].copy())
    return np.asarray(base), np.asarray(blocks)


def equilibrium_allocation(inlet_C, powers_W, parameters, settings):
    """Shared bounded scalar target allocation with fixed tracking/input cost.

    Both endpoints are checked; this is the registered bounded search procedure,
    not a claim that a general nonlinear allocation has a global certificate.
    """
    _, powers = validate_observation([*settings.targets_C, .5], inlet_C, powers_W)
    conductances = np.asarray(parameters.conductances)
    gains = np.asarray(parameters.fan_gains)

    def equilibrium(u):
        return inlet_C + powers / (conductances + gains * u)

    def objective(u):
        error = (equilibrium(u) - settings.targets_C) / 5.
        return float(error @ error + u * u)

    result = minimize_scalar(objective, method='bounded',
                             bounds=(settings.pwm_min, settings.pwm_max),
                             options={'xatol': 1e-10, 'maxiter': 100})
    if not result.success or not math.isfinite(result.x) or not math.isfinite(result.fun):
        raise RuntimeError('Equilibrium allocation failed')
    choices = (settings.pwm_min, float(result.x), settings.pwm_max)
    u = min(choices, key=objective)
    return u, np.r_[equilibrium(u), u]


class EnclosureControllerV2:
    """Common interface and safety wrapper for fixed, PID+FF, LQR and MPC."""

    def __init__(self, method, values, parameters=None, settings=None):
        required = {'fixed': {'pwm'}, 'pid': {'kp', 'ki', 'kd'},
                    'lqr': {'input_weight'}, 'mpc': {'input_weight'}}
        if method not in required or set(values) != required[method]:
            raise ValueError('Unknown method or unexpected controller parameters')
        if not all(math.isfinite(v) for v in values.values()):
            raise ValueError('Nonfinite controller parameter')
        if method == 'pid' and any(v < 0 for v in values.values()):
            raise ValueError('PID gains must be nonnegative')
        if method in ('lqr', 'mpc') and values['input_weight'] <= 0:
            raise ValueError('Positive input weight required')
        self.method, self.values = method, dict(values)
        self.parameters = parameters or ThermalParameters()
        self.settings = settings or ControlSettings()
        if method in ('lqr', 'mpc'):
            self.settings = replace(self.settings, input_weight=values['input_weight'])
        if method == 'fixed' and not self.settings.pwm_min <= values['pwm'] <= self.settings.pwm_max:
            raise ValueError('Fixed request outside PWM limits')
        self.integral, self.previous_error, self.warm = 0., None, None

    def _pid(self, state, inlet_C, powers_W):
        s = self.settings
        bias, _ = equilibrium_allocation(inlet_C, powers_W, self.parameters, s)
        error = float(np.max(state[:2] - s.targets_C))
        derivative = (0. if self.previous_error is None
                      else (error - self.previous_error) / s.dt_s)
        self.integral += self.values['ki'] * error * s.dt_s
        self.previous_error = error
        return bias + self.values['kp'] * error + self.integral + self.values['kd'] * derivative

    def _lqr(self, state, inlet_C, powers_W):
        s = self.settings
        u_eq, x_eq = equilibrium_allocation(inlet_C, powers_W, self.parameters, s)
        A, B_vector, _ = linearize_zoh(x_eq, inlet_C, powers_W, self.parameters, s)
        B = B_vector[:, None]
        Q, R = np.diag([.04, .04, 0.]), np.array([[s.input_weight]])
        P = solve_discrete_are(A, B, Q, R)
        K = np.linalg.solve(R + B.T @ P @ B, B.T @ P @ A)
        residual = A.T @ P @ A - P - A.T @ P @ B @ K + Q
        normalized = np.linalg.norm(residual, ord='fro') / max(1., np.linalg.norm(P, ord='fro'))
        radius = float(np.max(np.abs(np.linalg.eigvals(A - B @ K))))
        if (not np.isfinite(P).all() or not np.isfinite(K).all()
                or not math.isfinite(normalized) or normalized > DARE_RESIDUAL_TOL
                or not math.isfinite(radius) or radius >= 1.):
            raise RuntimeError('DARE residual or closed-loop stability check failed')
        return float(u_eq - (K @ (state - x_eq)).item())

    def _mpc(self, base, mapping, previous):
        s, n = self.settings, self.settings.horizon
        reference = np.tile(s.targets_C, n)
        caps = np.tile(np.asarray(s.limits_C) - s.margin_C, n)
        D = np.eye(n) - np.eye(n, k=-1)
        previous_vector = np.r_[previous, np.zeros(n - 1)]
        slack_scale = math.sqrt(s.slack_weight)
        hessian_u = 2. * (mapping.T @ mapping / 25. + s.input_weight * np.eye(n)
                           + s.delta_weight * D.T @ D)
        P = sparse.block_diag((hessian_u, 2. * np.eye(2 * n)), format='csc') * OBJECTIVE_SCALE
        q = np.r_[2. * (mapping.T @ (base - reference) / 25.
                         - s.delta_weight * D.T @ previous_vector), np.zeros(2 * n)] * OBJECTIVE_SCALE
        identity = np.eye(3 * n)
        matrix = sparse.csc_matrix(np.vstack([
            identity, np.c_[D, np.zeros((n, 2 * n))],
            np.c_[slack_scale * mapping, -np.eye(2 * n)]]))
        lower = np.r_[np.full(n, s.pwm_min), np.zeros(2 * n),
                      previous_vector - s.max_delta, np.full(2 * n, -np.inf)]
        upper = np.r_[np.full(n, s.pwm_max), np.full(2 * n, np.inf),
                      previous_vector + s.max_delta, slack_scale * (caps - base)]
        guess = np.full(n, previous) if self.warm is None else self.warm
        u0, last = [], previous
        for value in guess:
            last = bounded_command(float(value), last, s)
            u0.append(last)
        u0 = np.asarray(u0)
        initial = np.r_[u0, slack_scale * np.maximum(0., base + mapping @ u0 - caps)]
        solver = osqp.OSQP()
        solver.setup(P=sparse.triu(P, format='csc'), q=q, A=matrix, l=lower, u=upper,
                     **OSQP_OPTIONS)
        solver.warm_start(x=initial)
        result = solver.solve(raise_error=False)
        status = str(result.info.status)
        primal, dual = float(result.info.prim_res), float(result.info.dual_res)
        diagnostics = {'solver_status': status,
                       'primal_residual': primal if math.isfinite(primal) else None,
                       'dual_residual': dual if math.isfinite(dual) else None}
        z = result.x
        valid = (result.info.status_val == 1 and z is not None and z.shape == (3 * n,)
                 and np.isfinite(z).all() and math.isfinite(primal) and math.isfinite(dual)
                 and primal <= RESIDUAL_TOL and dual <= RESIDUAL_TOL)
        if valid:
            u, slack = z[:n], z[n:] / slack_scale
            delta = D @ u - previous_vector
            direct = max(0., float(np.max(s.pwm_min - u)), float(np.max(u - s.pwm_max)),
                         float(np.max(np.abs(delta) - s.max_delta)), float(np.max(-slack)),
                         float(np.max(base + mapping @ u - caps - slack)))
            valid = direct <= RESIDUAL_TOL
        if not valid:
            self.warm = None
            return s.pwm_max, {**diagnostics, 'reason': 'solver_or_residual_failure'}
        self.warm = np.r_[u[1:], u[-1]]
        return float(u[0]), {**diagnostics, 'accepted_slack_max_C': max(0., float(np.max(slack)))}

    def step(self, state, inlet_C, powers_W, previous):
        x, _ = validate_observation(state, inlet_C, powers_W)
        s = self.settings
        bounded_command(previous, previous, s)
        A, B, c = linearize_zoh(x, inlet_C, powers_W, self.parameters, s)
        base, mapping = _prediction_map(x, A, B, c, s.horizon)
        info = {'fallback': False, 'reason': '', 'solver_status': self.method,
                'accepted_slack_max_C': None, 'primal_residual': None, 'dual_residual': None}
        started = time.perf_counter()
        try:
            if self.method == 'fixed':
                raw = self.values['pwm']
            elif self.method == 'pid':
                raw = self._pid(x, inlet_C, powers_W)
            elif self.method == 'lqr':
                raw = self._lqr(x, inlet_C, powers_W)
            else:
                raw, diagnostics = self._mpc(base, mapping, previous)
                info.update(diagnostics)
            if not math.isfinite(raw):
                raise FloatingPointError('Nonfinite controller request')
        except (ValueError, RuntimeError, FloatingPointError, np.linalg.LinAlgError,
                osqp.OSQPException) as exc:
            raw = s.pwm_max
            info.update(reason='solver_exception', solver_status=type(exc).__name__)
        info['solver_s'] = time.perf_counter() - started
        info['fallback'] = bool(info['reason'])
        safety = bool(np.any(x[:2] >= s.warnings_C))
        applied = bounded_command(s.pwm_max if info['fallback'] or safety else raw, previous, s)
        if info['fallback']:
            self.warm = None
            info['accepted_slack_max_C'] = None
        if self.method == 'pid':
            if info['fallback']:
                self.integral, self.previous_error = 0., None
            else:
                self.integral += .2 * (applied - raw)
        caps = np.tile(np.asarray(s.limits_C) - s.margin_C, s.horizon)
        info.update(predicted=(A @ x + B * applied + c)[:2], safety_override=safety,
                    applied_violation_C=max(0., float(np.max(base + mapping @ np.full(s.horizon, applied) - caps))))
        return applied, info


def make_controller(method, values, parameters=None, settings=None):
    return EnclosureControllerV2(method, values, parameters, settings)
