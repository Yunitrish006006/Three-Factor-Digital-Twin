"""Shared ARX model bank and delay-aware normalized PI; no plant identity."""
import math
import time
from .portable_pi import PortablePI


def fit_arx(rows,indices,order,delay,target):
    import numpy as np
    x=np.array([[rows[k-j]['T']-target for j in range(order)]+[rows[k-delay]['u']-.5,rows[k]['outdoor']-target,1.] for k in indices])
    y=np.array([rows[k]['next_T']-target for k in indices])
    beta=np.linalg.solve(x.T@x+1e-8*np.eye(order+3),x.T@y)
    a=list(map(float,beta[:order]));b,c,d=map(float,beta[order:])
    poles=np.roots([1.]+[-v for v in a]);radius=float(max(abs(poles)))
    denominator=1-sum(a);gain=b/denominator if denominator!=0 else None
    valid=(math.isfinite(radius) and 0<radius<.999999 and b>0 and gain is not None and math.isfinite(gain) and gain>0)
    return {'order':order,'delay_steps':delay,'a':a,'b':b,'c':c,'intercept':d,'poles':[[float(z.real),float(z.imag)] for z in poles],
            'radius':radius,'steady_gain_C_per_u':gain,'status':'FITTED' if valid else 'REJECTED_POLE_OR_GAIN',
            'n':len(indices),'rank':int(np.linalg.matrix_rank(x)),'fit_one_step_rmse_C':float(np.sqrt(np.mean((x@beta-y)**2)))}


def rollout_rmse(model,rows,starts,target,horizon=10):
    errors=[];order=model['order'];delay=model['delay_steps']
    for start in starts:
        history={k:rows[k]['T']-target for k in range(start-order+1,start+1)}
        outdoor=rows[start]['outdoor']-target
        for k in range(start,start+horizon):
            prediction=sum(a*history[k-j] for j,a in enumerate(model['a']))+model['b']*(rows[k-delay]['u']-.5)+model['c']*outdoor+model['intercept']
            history[k+1]=prediction
            errors.append(prediction+target-rows[k]['next_T'])
    return math.sqrt(sum(e*e for e in errors)/len(errors))


def identify_bank(rows,target,dt):
    began=time.perf_counter();indices=list(range(11,len(rows)))
    if len(indices)<30:raise ValueError('Insufficient common history/validation endpoints')
    cut=11+int(.7*len(indices));train=list(range(11,cut));starts=list(range(cut,len(rows)-9,10))
    result={'status':'NO_ADMISSIBLE_MODEL','input_rows':len(rows),'start_s':rows[0]['time_s'],'end_s':rows[-1]['time_s']+dt,
            'training_end_index_exclusive':cut,'validation_starts':starts,'validation_points':10*len(starts),'candidates':[],'refits':[]}
    for order in [1,2]:
        for delay in [0,1,3,5,10]:
            candidate=fit_arx(rows,train,order,delay,target)
            candidate['validation_rollout_rmse_C']=rollout_rmse(candidate,rows,starts,target) if candidate['status']=='FITTED' else None
            result['candidates'].append(candidate)
    valid=sorted([c for c in result['candidates'] if c['status']=='FITTED'],key=lambda c:(c['validation_rollout_rmse_C'],c['order'],c['delay_steps']))
    for c in valid:
        refit=fit_arx(rows,indices,c['order'],c['delay_steps'],target);result['refits'].append(refit)
        if refit['status']=='FITTED':
            refit['tau_s']=-dt/math.log(refit['radius']);refit['validation_rollout_rmse_C']=c['validation_rollout_rmse_C']
            result.update(status='FITTED',selected=refit);break
    result['offline_fit_count']=len(result['candidates'])+len(result['refits']);result['fit_wall_seconds']=time.perf_counter()-began
    return result


def tuning(model,dt,q):
    tau=model['tau_s'];dead=model['delay_steps']*dt;response=max(3*dt,q*tau,dead)
    return {'kp':tau/(model['steady_gain_C_per_u']*(response+dead)),'ti':tau,'b':model['b'],'response_s':response,'delay_steps':model['delay_steps']}


class DelayedPortablePI(PortablePI):
    def __init__(self,target,dt,kp,ti,b,delay_steps,hybrid=False):
        super().__init__(target,dt,kp,ti,b,hybrid)
        if not isinstance(delay_steps,int) or delay_steps<0:raise ValueError('Invalid discrete delay')
        self.delay_steps=delay_steps
    def prime(self,temperature,applied_u):
        super().prime(temperature,applied_u)
        self.input_history=[self.first]*self.delay_steps
    def step(self,temperature,previous_applied_u,index):
        if index==0:return super().step(temperature,previous_applied_u,index)
        self.input_history.append(previous_applied_u);delayed_u=self.input_history.pop(0)
        return super().step(temperature,delayed_u,index)
