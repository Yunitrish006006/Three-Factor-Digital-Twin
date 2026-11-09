"""Five control laws sharing one enclosure observation/constraint contract."""
import math
import time
import numpy as np
from .enclosure_mpc import ThermalParameters, ControlSettings, bounded_command, validate_observation
from .enclosure_control_v2 import EnclosureControllerV2, prediction_map_v2


class UnifiedController:
    def __init__(self, method, values, parameters=None, settings=None, feedback=None):
        if method not in ('fixed','pi','pid','lqr','mpc'):
            raise ValueError('Unknown unified controller')
        self.method=method;self.values=dict(values)
        self.p=parameters or ThermalParameters();self.s=settings or ControlSettings()
        self.feedback=feedback or {'bias':.6,'derivative_alpha':.25,'backcalc':.2}
        self.integral=0.;self.derivative=0.;self.previous_error=None
        self.delegate=EnclosureControllerV2('pid' if method=='pi' else method,values,self.p,self.s)
        if method=='pi' and values['kd']!=0:raise ValueError('PI derivative must be zero')

    def step(self,state,inlet,powers,previous):
        x,_=validate_observation(state,inlet,powers)
        bounded_command(previous,previous,self.s)
        info={'fallback':False,'reason':'','solver_status':self.method,'primal_residual':None,'dual_residual':None}
        try:
            if self.method=='fixed':raw=self.values['pwm']
            elif self.method in ('pi','pid'):
                error=float(np.max(x[:2]-self.s.targets_C))
                rate=0. if self.previous_error is None else (error-self.previous_error)/self.s.dt_s
                self.derivative+=self.feedback['derivative_alpha']*(rate-self.derivative)
                self.integral+=self.values['ki']*error*self.s.dt_s
                self.previous_error=error
                raw=self.feedback['bias']+self.values['kp']*error+self.integral+self.values['kd']*self.derivative
            elif self.method=='lqr':raw=self.delegate._lqr(x,inlet,powers)
            else:
                base,mapping=prediction_map_v2(x,inlet,powers,self.p,self.delegate.settings)
                raw,extra=self.delegate._mpc(base,mapping,previous);info.update(extra)
            if not math.isfinite(raw):raise FloatingPointError('Nonfinite command')
        except (ValueError,RuntimeError,FloatingPointError,np.linalg.LinAlgError) as exc:
            raw=self.s.pwm_max;info.update(reason='controller_exception',solver_status=type(exc).__name__)
        # OSQP exceptions are handled by the caller as explicit numeric fallback.
        info['fallback']=bool(info['reason'])
        warning=bool(np.any(x[:2]>=self.s.warnings_C))
        requested=self.s.pwm_max if warning or info['fallback'] else raw
        applied=bounded_command(requested,previous,self.s)
        if self.method in ('pi','pid'):
            if info['fallback']:self.integral=0.;self.previous_error=None;self.derivative=0.
            else:self.integral+=self.feedback['backcalc']*(applied-raw)
        info.update(raw_pwm=float(raw),warning=warning)
        return applied,info
