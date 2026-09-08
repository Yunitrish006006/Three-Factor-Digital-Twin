"""Full-ARX innovation with bounded regularized correction; shared across plants."""
import math
from .portable_pi import clamp
from .delayed_dynamics import tuning


def responses(model, horizon=10):
    """Ten-step disturbance and delayed-input step responses from zero perturbations."""
    a=model['a']; order=len(a); disturbance=[0.]*order; command=[0.]*order
    impulse=[]
    for k in range(horizon):
        disturbance.append(sum(v*disturbance[-1-j] for j,v in enumerate(a))+1.)
        command.append(sum(v*command[-1-j] for j,v in enumerate(a))+(model['b'] if k>=model['delay_steps'] else 0.))
        impulse.append(sum(v*impulse[k-1-j] for j,v in enumerate(a) if k-1-j>=0)+(1. if k==0 else 0.))
    return disturbance[-1],command[-1],math.sqrt(sum(v*v for v in impulse))


class ConsistentPI:
    def __init__(self, target, dt, model, enabled=True):
        self.target,self.dt,self.model,self.enabled=target,dt,model,enabled
        g=tuning(model,dt,.5);self.kp,self.ti=g['kp'],g['ti']
        self.L,self.G,self.noise_gain=responses(model)
        self.beta=1-math.exp(-dt/max(600.,model['tau_s']))
        self.floor=max(.02,model['validation_rollout_rmse_C'])
        self.cap=.1;self.slew=.01*dt/60

    def prime(self,temperature,applied_u):
        self.first=clamp(applied_u)
        self.integral=self.first-.5-self.kp*(self.target-temperature)
        self.temperatures=[];self.inputs=[];self.last_outdoor=None
        self.mean=0.;self.second=0.;self.correction=0.
        self.diagnostics={'prediction_C':temperature,'innovation_C':0.,'correction_u':0.,'confidence':0.,'sigma_C':self.floor,'observer_ready':0.}

    def step(self,temperature,previous_applied_u,index,outdoor=None):
        if not math.isfinite(temperature) or outdoor is None or not math.isfinite(outdoor):raise ValueError('Finite current observations required')
        if index!=len(self.temperatures):raise ValueError('Nonconsecutive observation index')
        if index==0:
            self.temperatures.append(temperature);self.last_outdoor=outdoor
            return self.first
        self.inputs.append(previous_applied_u)
        m=self.model;order=len(m['a']);delay=m['delay_steps']
        ready=len(self.temperatures)>=order and len(self.inputs)>delay
        prediction=temperature;innovation=0.;confidence=0.;sigma=self.floor;desired=0.
        if self.enabled and ready:
            prediction=self.target+sum(a*(self.temperatures[-1-j]-self.target) for j,a in enumerate(m['a']))+m['b']*(self.inputs[-1-delay]-.5)+m['c']*(self.last_outdoor-self.target)+m['intercept']
            innovation=temperature-prediction
            self.mean+=self.beta*(innovation-self.mean);self.second+=self.beta*(innovation*innovation-self.second)
            sigma=max(self.floor,math.sqrt(max(0.,self.second-self.mean*self.mean))*self.noise_gain)
            confidence=(self.cap*self.G)**2/((self.cap*self.G)**2+sigma*sigma)
            if self.G>0 and confidence>=.2:
                desired=max(-self.cap,min(self.cap,-self.G*self.L*self.mean/(self.G*self.G+(sigma/self.cap)**2)))
        self.correction+=max(-self.slew,min(self.slew,desired-self.correction))
        error=self.target-temperature;delta=self.kp/self.ti*error*self.dt
        tentative=.5+self.kp*error+self.integral+delta+self.correction
        if 0<=tentative<=1 or tentative>1 and delta<0 or tentative<0 and delta>0:self.integral+=delta
        output=clamp(.5+self.kp*error+self.integral+self.correction)
        self.temperatures.append(temperature);self.last_outdoor=outdoor
        self.diagnostics=dict(prediction_C=prediction,innovation_C=innovation,correction_u=self.correction,confidence=confidence,sigma_C=sigma,observer_ready=float(self.enabled and ready))
        return output
