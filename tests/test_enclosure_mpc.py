import unittest
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np

from digital_twin.control.enclosure_mpc import (
    ControlSettings, ThermalParameters, EnclosurePlant, EnclosureMPC,
    EnclosureBaseline, bounded_command, linearize, prediction_map,
)


class EnclosureControlTests(unittest.TestCase):
    def test_energy_balance_equilibrium(self):
        plant=EnclosurePlant()
        state=plant.reset((60.,60.),.5)
        np.testing.assert_allclose(plant.step(.5,30.,(135.,180.),30.),state,atol=1e-10)

    def test_more_fan_cools_and_rpm_lags(self):
        slow,fast=EnclosurePlant(),EnclosurePlant()
        a=slow.step(.2,30.,(180.,240.),60.)
        b=fast.step(1.,30.,(180.,240.),60.)
        self.assertTrue(np.all(b[:2]<a[:2]))
        self.assertGreater(b[2],.5);self.assertLess(b[2],1.)

    def test_reset_repeats_exactly(self):
        p=EnclosurePlant();a=p.step(.8,30.,(180.,240.))
        p.reset();np.testing.assert_array_equal(a,p.step(.8,30.,(180.,240.)))

    def test_affine_model_matches_energy_balance_at_operating_point(self):
        x=np.array([62.,66.,.5]);p=ThermalParameters();s=ControlSettings()
        A,B,c=linearize(x,30.,(180.,240.),p,s)
        expected=x.copy()
        expected[:2]+=10*(np.array([180.,240.])-(np.array(p.conductances)+np.array(p.fan_gains)*.5)*(x[:2]-30))/p.capacities
        expected[2]+=10*(.8-.5)/20
        np.testing.assert_allclose(A@x+B*.8+c,expected)

    def test_condensed_map_matches_repeated_affine_steps(self):
        x=np.array([62.,66.,.5]);p=ThermalParameters();s=ControlSettings(horizon=4)
        base,M=prediction_map(x,30.,(180.,240.),p,s)
        A,B,c=linearize(x,30.,(180.,240.),p,s)
        u=np.array([.6,.7,.7,.8]);states=[]
        for command in u:
            x=A@x+B*command+c;states.extend(x[:2])
        np.testing.assert_allclose(base+M@u,states)

    def test_horizon_one_has_analytic_bounded_optimum(self):
        # First Euler thermal step is independent of new PWM because fan has lag.
        s=ControlSettings(horizon=1,input_weight=10.)
        u,info=EnclosureMPC(settings=s).step([60.,60.,.5],30.,(135.,180.),.5)
        self.assertFalse(info['fallback'])
        self.assertAlmostEqual(u,.4,places=5)

    def test_mpc_reacts_to_current_load(self):
        low,hi=EnclosureMPC(),EnclosureMPC()
        u0,i0=low.step([60.,60.,.5],30.,(60.,90.),.5)
        u1,i1=hi.step([60.,60.,.5],30.,(200.,280.),.5)
        self.assertFalse(i0['fallback']);self.assertFalse(i1['fallback'])
        self.assertGreater(u1,u0)

    def test_solver_failure_ramps_to_max(self):
        failed=SimpleNamespace(success=False,x=np.zeros(36),message='injected failure')
        with patch('digital_twin.control.enclosure_mpc.minimize',return_value=failed):
            u,info=EnclosureMPC().step([60.,60.,.5],30.,(180.,240.),.5)
        self.assertAlmostEqual(u,.6);self.assertTrue(info['fallback'])
        self.assertEqual(info['reason'],'solver_or_residual_failure')

    def test_false_success_with_bad_constraints_is_rejected(self):
        bad=SimpleNamespace(success=True,x=np.r_[np.ones(12),np.zeros(24)],message='false success')
        with patch('digital_twin.control.enclosure_mpc.minimize',return_value=bad):
            _,info=EnclosureMPC().step([60.,60.,.5],30.,(180.,240.),.5)
        self.assertTrue(info['fallback'])

    def test_warning_override_is_common_and_rate_limited(self):
        for ctl in (EnclosureMPC(),EnclosureBaseline('fixed',pwm=.4),
                    EnclosureBaseline('pid',kp=.01,ki=0.,kd=0.)):
            u,info=ctl.step([76.,60.,.5],30.,(180.,240.),.5)
            self.assertAlmostEqual(u,.6);self.assertTrue(info['safety_override'])

    def test_slew_and_bounds_at_edges(self):
        s=ControlSettings()
        self.assertAlmostEqual(bounded_command(1.,.95,s),1.)
        self.assertAlmostEqual(bounded_command(0.,.25,s),.2)
        with self.assertRaises(ValueError):bounded_command(float('nan'),.5,s)

    def test_invalid_model_or_observation_rejected(self):
        with self.assertRaises(ValueError):ThermalParameters(fan_tau_s=0.)
        with self.assertRaises(ValueError):ControlSettings(max_delta=0.)
        with self.assertRaises(ValueError):ControlSettings(dt_s=float('nan'))
        with self.assertRaises(ValueError):EnclosureMPC().step([float('nan'),60.,.5],30.,(100.,100.),.5)
        with self.assertRaises(ValueError):EnclosurePlant().step(.5,30.,(-1.,100.))


if __name__=='__main__':unittest.main()
