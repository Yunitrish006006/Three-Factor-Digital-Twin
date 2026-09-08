import unittest
from digital_twin.control.consistent_pi import ConsistentPI,responses
from digital_twin.control.delayed_dynamics import tuning
from digital_twin.control.portable_pi import PortablePI

class ConsistentPITests(unittest.TestCase):
    def model(self,b=.2,delay=2):
        return dict(a=[1.3,-.4],b=b,c=.01,intercept=.002,delay_steps=delay,tau_s=600,steady_gain_C_per_u=b/.1,validation_rollout_rmse_C=.02)
    def test_full_arx_innovation_is_zero_for_exact_plant_with_environment(self):
        m=self.model();c=ConsistentPI(22,60,m);c.prime(22,.5)
        ts=[22.,22.];us=[]
        for k in range(60):
            outdoor=15+k*.03;u=(k%9)/8
            c.step(ts[-1],us[-1] if us else .5,k,outdoor)
            if c.diagnostics['observer_ready']:self.assertAlmostEqual(c.diagnostics['innovation_C'],0,places=10)
            us.append(u);lag=us[k-2] if k>=2 else .5
            ts.append(22+1.3*(ts[-1]-22)-.4*(ts[-2]-22)+m['b']*(lag-.5)+.01*(outdoor-22)+.002)
    def test_disabled_observer_matches_original_pi(self):
        m=self.model();g=tuning(m,60,.5);base=PortablePI(22,60,g['kp'],g['ti'],g['b'],False);c=ConsistentPI(22,60,m,False)
        for ctrl in (base,c):ctrl.prime(22.4,.7)
        last=.7
        for k in range(100):
            t=22+(k%17-8)*.15
            expected=base.step(t,last,k);got=c.step(t,last,k,15)
            self.assertEqual(expected,got);last=got
    def test_delay_outside_horizon_falls_back_exactly(self):
        m=self.model(delay=10);self.assertEqual(responses(m)[1],0)
        a=ConsistentPI(22,60,m,False);b=ConsistentPI(22,60,m,True)
        a.prime(22,.5);b.prime(22,.5)
        for k in range(60):self.assertEqual(a.step(23,.5,k,10),b.step(23,.5,k,10))
    def test_small_gain_is_not_inverted_without_regularization(self):
        c=ConsistentPI(22,60,self.model(b=1e-8,delay=0));c.prime(22,.5)
        for k in range(60):c.step(23,.5,k,15)
        self.assertEqual(c.correction,0)
    def test_correction_magnitude_and_slew_are_bounded(self):
        c=ConsistentPI(22,60,self.model(b=2,delay=0));c.prime(22,.5);previous=0
        for k in range(100):
            c.step(22+k*.03,.5,k,22)
            self.assertLessEqual(abs(c.correction),.1+1e-12)
            self.assertLessEqual(abs(c.correction-previous),.01+1e-12);previous=c.correction
    def test_current_outdoor_cannot_change_previous_interval_innovation(self):
        cs=[ConsistentPI(22,60,self.model(delay=0)) for _ in range(2)]
        for c in cs:c.prime(22,.5);c.step(22,.5,0,15);c.step(22,.5,1,15)
        cs[0].step(22,.5,2,-100);cs[1].step(22,.5,2,100)
        self.assertEqual(cs[0].diagnostics['innovation_C'],cs[1].diagnostics['innovation_C'])
