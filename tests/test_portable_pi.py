import unittest
from digital_twin.control.portable_pi import PortablePI,fit_dynamics,clamp,gains

class PortablePITests(unittest.TestCase):
    def test_constant_heat_balance_both_controllers(self):
        for hybrid in [False,True]:
            c=PortablePI(22,60,.2,600,.5,hybrid);c.prime(22,.7)
            for i in range(20):self.assertAlmostEqual(c.step(22,.7,i),.7)
    def test_initial_alignment_away_from_target(self):
        for hybrid in [False,True]:
            c=PortablePI(22,60,.2,600,.5,hybrid);c.prime(20,.8)
            self.assertEqual(c.step(20,.8,0),.8)
    def test_antiwindup_bounded_actuation(self):
        c=PortablePI(22,60,.2,600,.5);c.prime(22,.5)
        for i in range(1,100):self.assertEqual(c.step(-100,.5,i),1)
        self.assertAlmostEqual(c.integral,0)
    def test_identify_known_dynamics(self):
        rows=[]
        for i in range(120):
            t=21+(i%5)*.2;u=(i%7)/6;outdoor=i%11
            delta=.03*(-(t-22))+.5*(u-.5)+.01*(outdoor-22)+.02
            rows.append(dict(T=t,u=u,outdoor=outdoor,next_T=t+delta,time_s=i*60))
        fit=fit_dynamics(rows,22,60);self.assertEqual(fit['status'],'FITTED')
        for a,b in zip(fit['coefficients'],[.03,.5,.01,.02]):self.assertAlmostEqual(a,b,places=6)
        self.assertGreater(gains(fit,60,.5)['kp'],0)
    def test_nonphysical_fit_remains_rejected(self):
        rows=[dict(T=22+i%5,u=(i%7)/6,outdoor=i%11,next_T=22+i%5-.5*((i%7)/6-.5),time_s=i*60) for i in range(120)]
        self.assertEqual(fit_dynamics(rows,22,60)['status'],'REJECTED_NONPHYSICAL')
    def test_nonfinite_command(self):
        with self.assertRaises(ValueError):clamp(float('nan'))

if __name__=='__main__':unittest.main()
