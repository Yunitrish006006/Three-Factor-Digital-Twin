"""Plant-name-independent SISO temperature control in normalized actuator units.

Engineering-unit mapping belongs to the adapter. Constants are shared research
hyperparameters, not independently established universal settings.
"""
import math


def clamp(value):
    if not math.isfinite(value):
        raise ValueError('Nonfinite actuator request')
    return min(1.,max(0.,value))


class PortablePI:
    def __init__(self,target,dt,kp,ti,b,hybrid=False,alpha=.35):
        if not all(math.isfinite(x) and x>0 for x in (dt,kp,ti,b)):
            raise ValueError('Invalid positive controller parameter')
        if not 0<alpha<=1:raise ValueError('Invalid smoothing')
        self.target,self.dt,self.kp,self.ti,self.b=target,dt,kp,ti,b
        self.hybrid,self.alpha=hybrid,alpha

    def prime(self,temperature,applied_u):
        self.first=clamp(applied_u)
        self.filtered=self.first
        self.previous_T=temperature
        self.disturbance=-self.b*(self.first-.5)
        bias=self.first if self.hybrid else .5
        self.integral=self.first-bias-self.kp*(self.target-temperature)
        self.initialized=True

    def step(self,temperature,previous_applied_u,index):
        if not getattr(self,'initialized',False):raise RuntimeError('Prime controller first')
        if not math.isfinite(temperature):raise ValueError('Nonfinite temperature')
        if index==0:return self.first
        bias=.5
        if self.hybrid:
            residual=temperature-self.previous_T-self.b*(previous_applied_u-.5)
            self.disturbance=.8*self.disturbance+.2*residual
            bias=.5-self.disturbance/self.b
        error=self.target-temperature
        delta=self.kp/self.ti*error*self.dt
        tentative=bias+self.kp*error+self.integral+delta
        if 0<=tentative<=1 or (tentative>1 and delta<0) or (tentative<0 and delta>0):
            self.integral+=delta
        raw=clamp(bias+self.kp*error+self.integral)
        if self.hybrid:
            self.filtered=clamp(self.filtered+self.alpha*(raw-self.filtered))
            self.integral+=.1*(self.filtered-raw)
            output=self.filtered
        else:output=raw
        self.previous_T=temperature
        return output


def fit_dynamics(rows,target,dt):
    import numpy as np
    x=np.array([[-(r['T']-target),r['u']-.5,r['outdoor']-target,1] for r in rows])
    y=np.array([r['next_T']-r['T'] for r in rows])
    coef=np.linalg.solve(x.T@x+1e-8*np.eye(4),x.T@y)
    loss,b,c,d=map(float,coef)
    condition=float(np.linalg.cond(x))
    result={'n':len(rows),'coefficients':list(map(float,coef)),
            'condition_number':condition if math.isfinite(condition) else None,
            'rank':int(np.linalg.matrix_rank(x)),'fit_rmse_C':float(np.sqrt(np.mean((x@coef-y)**2))),
            'start_s':rows[0]['time_s'],'end_s':rows[-1]['time_s']+dt}
    if not (0<loss<1 and b>0 and all(math.isfinite(v) for v in coef)):
        result['status']='REJECTED_NONPHYSICAL'
    else:
        result.update(status='FITTED',tau_s=-dt/math.log(1-loss),steady_gain_C_per_u=b/loss,b_C_per_step_per_u=b)
    return result


def gains(fit,dt,q):
    tau=fit['tau_s'];response=max(3*dt,q*tau)
    return {'kp':tau/(fit['steady_gain_C_per_u']*response),'ti':tau,'b':fit['b_C_per_step_per_u'],'response_s':response}
