import unittest
from digital_twin.control.handover_pi import HandoverPI,POLICIES
from digital_twin.control.portable_pi import PortablePI
from digital_twin.control.delayed_dynamics import tuning
M=dict(tau_s=600,delay_steps=0,steady_gain_C_per_u=10,b=.1)

class HandoverTests(unittest.TestCase):
    def test_disabled_exact_original(self):
        a=HandoverPI(22,60,M);g=tuning(M,60,.5);b=PortablePI(22,60,g['kp'],g['ti'],g['b'])
        a.prime(21,.4);b.prime(21,.4)
        for i,t in enumerate([21,25,19,22]*20):self.assertEqual(a.step(t,.4,i),b.step(t,.4,i))

    def test_same_factor_prefix_and_handover(self):
        for duration in (15,55):
            a,b=[HandoverPI(22,60,M,f'{duration}_{mode}') for mode in ('taper','retain')]
            a.prime(21,.4);b.prime(21,.4)
            for i in range(duration):self.assertEqual(a.step(21,.4,i),b.step(21,.4,i));self.assertEqual(a.integral,b.integral)
            a.step(21,.4,duration);b.step(21,.4,duration)
            self.assertEqual(a.exit_min,duration);self.assertEqual(b.exit_min,duration)
            self.assertAlmostEqual(b.integral-a.integral,.1)
            self.assertLess(b.diagnostics['handover_mismatch'],1e-12)

    def test_zero_deadline_no_rearm_and_post_pi(self):
        for policy in POLICIES:
            a=HandoverPI(22,60,M,policy);a.prime(21,.5);last=0
            for i in range(70):
                u=a.step(21,.5,i);self.assertTrue(0<=u<=1)
                if a.mode=='taper' or a.active:self.assertLessEqual(abs(a.correction-last),.02000000001)
                last=a.correction
            self.assertLessEqual(a.zero_min,60);self.assertFalse(a.active)
            g=tuning(M,60,.5);b=PortablePI(22,60,g['kp'],g['ti'],g['b']);b.prime(21,.5);b.integral=a.integral
            for i,t in enumerate([19,23,22,20],start=70):self.assertEqual(a.step(t,.5,i),b.step(t,.5,i));self.assertFalse(a.active)

    def test_crossing_both_signs(self):
        for start,end in ((21,22.1),(23,21.9)):
            for mode in ('taper','retain'):
                a=HandoverPI(22,60,M,'55_'+mode);a.prime(start,.5)
                for i,t in enumerate([start,start,end]+[end]*6):a.step(t,.5,i)
                self.assertEqual(a.exit_code,3);self.assertEqual(a.exit_min,2);self.assertEqual(a.correction,0)
