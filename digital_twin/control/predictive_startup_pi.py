"""Causal trend withdrawal with independent ordinary PI integral catch-up."""
from .portable_pi import PortablePI, clamp
from .delayed_dynamics import tuning


class PredictiveStartupPI(PortablePI):
    def __init__(self,target,dt,model,horizon=None):
        g=tuning(model,dt,.5)
        super().__init__(target,dt,g['kp'],g['ti'],g['b'])
        if horizon not in (None,3,10,30):raise ValueError('Undeclared horizon')
        self.horizon=horizon

    def prime(self,temperature,applied_u):
        super().prime(temperature,applied_u)
        self.i0=self.integral;self.sign=1 if self.target-temperature>=0 else -1
        self.active=self.horizon is not None and abs(self.target-temperature)>.1
        self.correction=0.;self.slope=0.;self.last_T=temperature
        self.exit_code=0 if self.active else 1;self.exit_min=-1.;self.zero_min=-1.
        self.diagnostics={}

    def step(self,temperature,previous_applied_u,index,outdoor=None):
        base=super().step(temperature,previous_applied_u,index)
        error=self.target-temperature
        if index:
            self.slope=(2*self.slope+(temperature-self.last_T)/self.dt)/3
        catchup=max(0.,self.sign*(self.integral-self.i0))
        desired=self.sign*max(0.,min(.1,self.kp*abs(error))-catchup)
        projected=self.sign*error-max(0.,self.sign*self.slope)*(self.horizon or 0)*60
        if index and self.active:
            code=3 if self.sign*error<=0 else 2 if projected<=.1 else 5 if desired==0 and index*self.dt>=300 else 4 if index*self.dt>=3300 else 0
            if code:
                self.active=False;self.exit_code=code;self.exit_min=index*self.dt/60
        if index:
            goal=desired if self.active else 0.
            self.correction+=max(-.02*self.dt/60,min(.02*self.dt/60,goal-self.correction))
            if abs(self.correction)<1e-14:self.correction=0.
            if not self.active and self.correction==0 and self.zero_min<0:self.zero_min=index*self.dt/60
        self.last_T=temperature
        self.diagnostics=dict(active=float(self.active),correction=self.correction,integral=self.integral,
                              pi_core_u=base,trend_C_per_s=self.slope,integral_catchup=catchup,projected_signed_error=projected,
                              exit_code=self.exit_code,exit_min=self.exit_min,zero_min=self.zero_min,horizon_min=self.horizon or 0)
        return clamp(base+self.correction)
