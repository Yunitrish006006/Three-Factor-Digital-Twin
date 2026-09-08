"""One-shot startup assistance with integral-state transfer; no device identity."""
import math
from .portable_pi import PortablePI, clamp
from .delayed_dynamics import tuning


class StartupPI(PortablePI):
    def __init__(self, target, dt, model, band=None):
        g = tuning(model, dt, .5)
        super().__init__(target, dt, g['kp'], g['ti'], g['b'])
        if band is not None and band not in (.05, .1, .2):
            raise ValueError('Undeclared exit band')
        self.band = band

    def prime(self, temperature, applied_u):
        super().prime(temperature, applied_u)
        self.initial_error = self.target-temperature
        self.active = self.band is not None and abs(self.initial_error)>self.band
        self.correction = 0.
        self.dwell = 0
        self.exit_code = 0 if self.active else 1  # 1 disabled/inside,2 dwell,3 crossing,4 deadline
        self.exit_min = -1.
        self.diagnostics = {}

    def step(self, temperature, previous_applied_u, index, outdoor=None):
        if not getattr(self, 'initialized', False): raise RuntimeError('Prime first')
        if not math.isfinite(temperature): raise ValueError('Nonfinite temperature')
        error = self.target-temperature
        mismatch = 0.
        if index == 0:
            output = self.first
        else:
            if self.active:
                self.dwell = self.dwell+1 if abs(error)<=self.band else 0
                code = 2 if self.dwell>=5 else 3 if error*self.initial_error<=0 else 4 if index*self.dt>=3600 else 0
                if code:
                    before = .5+self.kp*error+self.integral+self.correction
                    self.integral += self.correction
                    self.correction = 0.
                    mismatch = abs(before-(.5+self.kp*error+self.integral))
                    self.active = False
                    self.exit_code, self.exit_min = code, index*self.dt/60
                else:
                    desired = max(-.1, min(.1, self.kp*error))
                    self.correction += max(-.02*self.dt/60, min(.02*self.dt/60, desired-self.correction))
            delta = self.kp/self.ti*error*self.dt
            tentative = .5+self.kp*error+self.integral+self.correction+delta
            if 0<=tentative<=1 or tentative>1 and delta<0 or tentative<0 and delta>0:
                self.integral += delta
            output = clamp(.5+self.kp*error+self.integral+self.correction)
        self.diagnostics = dict(active=float(self.active), correction=self.correction, dwell=self.dwell,
                                exit_code=self.exit_code, exit_min=self.exit_min, handover_mismatch=mismatch,
                                integral=self.integral, band_C=self.band or 0.)
        return output
