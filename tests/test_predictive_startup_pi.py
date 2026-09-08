import unittest
from digital_twin.control.predictive_startup_pi import PredictiveStartupPI
from digital_twin.control.portable_pi import PortablePI
from digital_twin.control.delayed_dynamics import tuning
M=dict(tau_s=600,delay_steps=0,steady_gain_C_per_u=10,b=.1)

class PredictiveTests(unittest.TestCase):
    def test_core_matches_original_and_no_integral_injection(self):
        g=tuning(M,60,.5)
        for horizon in (None,3,10,30):
            a=PredictiveStartupPI(22,60,M,horizon);b=PortablePI(22,60,g['kp'],g['ti'],g['b'])
            a.prime(21,.4);b.prime(21,.4)
            last=0;exited=False
            for i,t in enumerate([21,21.02,21.06,21.15,21.3,21.6,21.95,22.1]+[20]*80):
                u=a.step(t,.4,i);v=b.step(t,.4,i)
                self.assertEqual(a.integral,b.integral);self.assertEqual(a.diagnostics['pi_core_u'],v)
                self.assertLessEqual(abs(a.correction-last),.02000000001);last=a.correction
                if exited:self.assertFalse(a.active)
                if not a.active:exited=True
                if i>=60:self.assertEqual(u,v);self.assertEqual(a.correction,0)
                if horizon is None:self.assertEqual(u,v)

    def test_deadline_with_slow_integrator(self):
        m=dict(M,tau_s=1e9);a=PredictiveStartupPI(22,60,m,3);a.prime(20,.5)
        for i in range(61):a.step(20,.5,i)
        self.assertEqual(a.exit_code,4);self.assertEqual(a.exit_min,55);self.assertLessEqual(a.zero_min,60)

    def test_predictive_exit_before_crossing(self):
        a=PredictiveStartupPI(22,60,M,30);a.prime(21,.5);a.step(21,.5,0);a.step(21.3,.5,1)
        self.assertEqual(a.exit_code,2);self.assertGreater(22-21.3,.1)

    def test_both_directions_and_bounds(self):
        for start,end in [(21,22.1),(23,21.9)]:
            a=PredictiveStartupPI(22,60,M,3);a.prime(start,.5)
            for i,t in enumerate([start,start,end]+[end]*10):
                u=a.step(t,.5,i);self.assertTrue(0<=u<=1);self.assertLessEqual(abs(a.correction),.1)
            self.assertEqual(a.exit_code,3);self.assertEqual(a.correction,0)
