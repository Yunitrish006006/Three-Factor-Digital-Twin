from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from run_boptest_jitter import SmoothObserver
from run_boptest_transfer import ObserverPI

class JitterTests(unittest.TestCase):
    def test_reject_invalid_smoothing(self):
        for alpha in [0,1.1,-1]:
            with self.assertRaises(ValueError):SmoothObserver(3,250,.1,alpha)
    def test_first_command_preserves_handover(self):
        c=SmoothObserver(3,250,.1,.35);s=dict(T=22,supply=40,fan=.2);c.prime(s)
        self.assertAlmostEqual(c(s,0),29.2)
    def test_identity_matches_observer_without_delay(self):
        a=SmoothObserver(3,250,.1,1);b=ObserverPI(3,250,.1);s=dict(T=22,supply=30,fan=.5)
        a.prime(s);b.prime(s)
        for i in range(10):
            u=a(s,i);self.assertAlmostEqual(u,b(s,i))
            s=dict(T=22+.01*i,supply=u,fan=.5)
    def test_observer_uses_actual_applied_action(self):
        c=SmoothObserver(3,250,.1,1);s=dict(T=22,supply=30,fan=.5);c.prime(s);c(s,0)
        c(dict(s,supply=25),1)
        self.assertAlmostEqual(c.disturbance,.8*(-.8)+.2*(-.3))
    def test_smoothed_command_between_previous_and_raw(self):
        s=dict(T=22,supply=30,fan=.5);a=SmoothObserver(3,250,.1,.35);b=SmoothObserver(3,250,.1,1)
        a.prime(s);b.prime(s);a(s,0);b(s,0)
        perturbed=dict(s,T=23)
        raw=b(perturbed,1)
        self.assertAlmostEqual(a(perturbed,1),30+.35*(raw-30))

if __name__=='__main__':unittest.main()
