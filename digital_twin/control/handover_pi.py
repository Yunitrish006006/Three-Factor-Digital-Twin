"""Two-factor startup study: shared boost, distinct duration and handover."""
import math
from .portable_pi import PortablePI,clamp
from .delayed_dynamics import tuning
POLICIES=('15_taper','15_retain','55_taper','55_retain')

class HandoverPI(PortablePI):
    def __init__(self,target,dt,model,policy=None):
        g=tuning(model,dt,.5)
        super().__init__(target,dt,g['kp'],g['ti'],g['b'])
        if policy not in (None,)+POLICIES:raise ValueError('Undeclared policy')
        self.policy=policy
        self.duration=int(policy.split('_')[0]) if policy else 0
        self.mode=policy.split('_')[1] if policy else 'none'

    def prime(self,temperature,applied_u):
        super().prime(temperature,applied_u)
        self.initial_error=self.target-temperature
        self.active=self.policy is not None and abs(self.initial_error)>.1
        self.correction=0.;self.exit_code=0 if self.active else 1;self.exit_min=-1.;self.zero_min=-1.
        self.diagnostics={}

    def step(self,temperature,previous_applied_u,index,outdoor=None):
        if not getattr(self,'initialized',False):raise RuntimeError('Prime first')
        if not math.isfinite(temperature):raise ValueError('Nonfinite temperature')
        error=self.target-temperature;mismatch=0.
        if index and self.active:
            code=3 if error*self.initial_error<=0 else 4 if index*self.dt>=self.duration*60 else 0
            if code:
                self.active=False;self.exit_code=code;self.exit_min=index*self.dt/60
                if self.mode=='retain':
                    before=.5+self.kp*error+self.integral+self.correction
                    self.integral+=self.correction;self.correction=0.
                    mismatch=abs(before-(.5+self.kp*error+self.integral))
        if index:
            desired=max(-.1,min(.1,self.kp*error)) if self.active else 0.
            self.correction+=max(-.02*self.dt/60,min(.02*self.dt/60,desired-self.correction))
            if abs(self.correction)<1e-14:self.correction=0.
            if not self.active and self.correction==0 and self.zero_min<0:self.zero_min=index*self.dt/60
        base=super().step(temperature,previous_applied_u,index)
        raw=.5+self.kp*error+self.integral
        out=self.first if index==0 else clamp(raw+self.correction)
        self.diagnostics=dict(active=float(self.active),correction=self.correction,integral=self.integral,
            pi_core_u=base,exit_code=self.exit_code,exit_min=self.exit_min,zero_min=self.zero_min,
            duration_min=self.duration,retain_mode=float(self.mode=='retain'),handover_mismatch=mismatch)
        return out
