import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from digital_twin.control.startup_pi import StartupPI
from digital_twin.control.portable_pi import PortablePI
from digital_twin.control.delayed_dynamics import tuning
from select_boptest_startup import windows,gate,select
MODEL=dict(tau_s=600,delay_steps=0,steady_gain_C_per_u=10,b=.1)


class StartupTests(unittest.TestCase):
    def test_disabled_matches_original(self):
        g=tuning(MODEL,60,.5); a=StartupPI(22,60,MODEL); b=PortablePI(22,60,g['kp'],g['ti'],g['b'])
        a.prime(21,.4);b.prime(21,.4)
        for i,t in enumerate([21,21.2,23,20,22]*20):
            self.assertEqual(a.step(t,.4,i),b.step(t,.4,i))

    def test_dwell_transfer_and_no_rearm(self):
        a=StartupPI(22,60,MODEL,.1);a.prime(21,.4)
        for i,t in enumerate([21,21,21.95,21.95,21.95,21.95,21.95]):a.step(t,.4,i)
        self.assertEqual(a.exit_code,2);self.assertFalse(a.active)
        self.assertLess(a.diagnostics['handover_mismatch'],1e-12)
        g=tuning(MODEL,60,.5);b=PortablePI(22,60,g['kp'],g['ti'],g['b']);b.prime(21.95,.4);b.integral=a.integral
        for i,t in enumerate([20,21,23,22],start=7):
            self.assertEqual(a.step(t,.4,i),b.step(t,.4,i));self.assertFalse(a.active)

    def test_crossing_both_directions(self):
        for t,nxt in [(21,22.01),(23,21.99)]:
            a=StartupPI(22,60,MODEL,.05);a.prime(t,.5)
            a.step(t,.5,0);a.step(t,.5,1);a.step(nxt,.5,2)
            self.assertEqual(a.exit_code,3);self.assertLess(a.diagnostics['handover_mismatch'],1e-12)

    def test_deadline_and_bounds(self):
        a=StartupPI(22,60,MODEL,.05);a.prime(20,.5);last=0
        for i in range(100):
            u=a.step(20,.5,i);self.assertTrue(0<=u<=1)
            self.assertLessEqual(abs(a.correction),.1)
            if a.active:self.assertLessEqual(abs(a.correction-last),.02000000001)
            last=a.correction
        self.assertEqual(a.exit_code,4);self.assertEqual(a.exit_min,60)

    def test_initial_inside_stays_disabled(self):
        a=StartupPI(22,60,MODEL,.2);a.prime(21.9,.5)
        for i in range(10):a.step(20,.5,i)
        self.assertFalse(a.active);self.assertEqual(a.correction,0)

    def test_hold_is_censored_or_confirmed(self):
        c=dict(target_C=22,step_s=60,power_outputs={})
        rows=[dict(next_T=21,u=.5) for _ in range(180)]
        self.assertIsNone(windows(rows,c)['acquisition_onset_min'])
        for r in rows[10:25]:r['next_T']=22
        w=windows(rows,c);self.assertEqual(w['acquisition_onset_min'],11);self.assertEqual(w['acquisition_confirmation_min'],25)
        rows[24]['next_T']=21
        self.assertIsNone(windows(rows,c)['acquisition_onset_min'])

    def test_late_damage_rejected(self):
        from copy import deepcopy
        b=dict(early=dict(mae_C=1,max_abs_error_C=2),late=dict(mae_C=.1,max_abs_error_C=.2,requested_TV_u=.1),acquisition_onset_min=40)
        c=deepcopy(b);c['early']['mae_C']=.5;c['late']['mae_C']=.2
        self.assertFalse(gate(b,c)['passed'])
        records=[dict(band_C=None,windows=b),dict(band_C=.05,windows=c)]
        self.assertIsNone(select(records)['band_C'])
