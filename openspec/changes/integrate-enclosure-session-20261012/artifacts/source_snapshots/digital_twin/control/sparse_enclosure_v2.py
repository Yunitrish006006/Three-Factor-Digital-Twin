"""Corrective API; the frozen v1 module remains a historical reproducibility source.

Only the warning information contract changes. All methods require original
plate/air observations, including the no-correction ablation.
"""
import numpy as np

from .sparse_enclosure import TransferController as FrozenController, command


class TransferController(FrozenController):
    version = 'raw-warning-v2'

    def step(self, estimate, inlet, power, previous, *, observed_plate_air):
        x = np.asarray(estimate, dtype=float)
        observed = np.asarray(observed_plate_air, dtype=float)
        if x.shape != (4,) or not np.isfinite(x).all():
            raise ValueError('Expected source-blind state estimate')
        if observed.shape != (2,) or not np.isfinite(observed).all():
            raise ValueError('Expected original finite plate/air observations')
        # Preserve frozen control mathematics; do not replace ranker state with
        # noisy measurements merely to implement the separate warning contract.
        s = self.settings
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
        if max(float(x[0]), float(np.max(observed))) >= s.warning:
            raw, info['warning'] = s.pwm_max, True
        u = command(raw, previous, s)
        if self.method in ('pi', 'pid'):
            self.integral += s.backcalc * (u - raw)
        return u, info
