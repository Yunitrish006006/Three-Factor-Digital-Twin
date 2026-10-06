"""Numerical and failure-mode checks; these do not run registered episodes."""
import math
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np
from scipy.integrate import solve_ivp

from digital_twin.control.enclosure_control_v2 import (
    ControlSettings, ThermalParameters, EnclosurePlant, equilibrium_allocation,
    linearize_zoh, prediction_map_v2, make_controller,
)


class EnclosureControlV2Tests(unittest.TestCase):
    def setUp(self):
        self.p, self.s = ThermalParameters(), ControlSettings()

    def controllers(self):
        return [make_controller('fixed', {'pwm': .4}),
                make_controller('pid', {'kp': .03, 'ki': .0001, 'kd': 0.}),
                make_controller('lqr', {'input_weight': 1.}),
                make_controller('mpc', {'input_weight': 1.})]

    def test_zoh_matches_independent_continuous_affine_integration(self):
        x, inlet, powers, u = np.array([62., 66., .5]), 30., np.array([180., 240.]), .8
        capacities, gains = np.asarray(self.p.capacities), np.asarray(self.p.fan_gains)
        cooling = np.asarray(self.p.conductances) + gains * x[2]
        def dynamics(_, y):
            thermal = ((powers - cooling * (x[:2] - inlet))
                       - cooling * (y[:2] - x[:2])
                       - gains * (x[:2] - inlet) * (y[2] - x[2])) / capacities
            return np.r_[thermal, (u - y[2]) / self.p.fan_tau_s]
        truth = solve_ivp(dynamics, (0., self.s.dt_s), x, rtol=1e-11, atol=1e-12).y[:, -1]
        A, B, c = linearize_zoh(x, inlet, powers, self.p, self.s)
        np.testing.assert_allclose(A @ x + B * u + c, truth, atol=1e-9)
        self.assertTrue(np.all(B[:2] < 0.))

    def test_zoh_preserves_physical_equilibrium(self):
        x = np.array([60., 60., .5])
        A, B, c = linearize_zoh(x, 30., (135., 180.), self.p, self.s)
        np.testing.assert_allclose(A @ x + B * .5 + c, x, atol=1e-11)

    def test_condensed_prediction_matches_rollout(self):
        x, u = np.array([62., 66., .5]), np.linspace(.4, .9, self.s.horizon)
        base, mapping = prediction_map_v2(x, 30., (180., 240.), self.p, self.s)
        A, B, c = linearize_zoh(x, 30., (180., 240.), self.p, self.s)
        temperatures = []
        for command in u:
            x = A @ x + B * command + c
            temperatures.extend(x[:2])
        np.testing.assert_allclose(base + mapping @ u, temperatures, atol=1e-10)

    def test_allocation_is_feasible_and_satisfies_thermal_balance(self):
        for powers in ((0., 0.), (200., 280.), (450., 600.)):
            u, x = equilibrium_allocation(30., powers, self.p, self.s)
            self.assertGreaterEqual(u, .2); self.assertLessEqual(u, 1.)
            np.testing.assert_allclose((np.asarray(self.p.conductances) + np.asarray(self.p.fan_gains) * u)
                                       * (x[:2] - 30.), powers, atol=1e-10)
            plant = EnclosurePlant(); plant.reset(x[:2], x[2])
            np.testing.assert_allclose(plant.step(u, 30., powers), x, atol=1e-10)

    def test_lqr_holds_allocated_equilibrium(self):
        u, x = equilibrium_allocation(30., (200., 280.), self.p, self.s)
        for weight in (.1, 1., 10.):
            applied, info = make_controller('lqr', {'input_weight': weight}).step(x, 30., (200., 280.), u)
            self.assertFalse(info['fallback'])
            self.assertAlmostEqual(applied, u, places=9)
            self.assertIsNone(info['accepted_slack_max_C'])

    def test_common_warning_override_and_slew(self):
        for controller in self.controllers():
            applied, info = controller.step([76., 60., .5], 30., (180., 240.), .5)
            self.assertAlmostEqual(applied, .6)
            self.assertTrue(info['safety_override'])

    def test_mpc_accepts_nominal_and_overload_qps(self):
        for state, powers, previous in (([60., 60., .5], (200., 280.), .5),
                                        ([60., 61., .5], (450., 600.), .5),
                                        ([91., 91., 1.], (450., 600.), 1.)):
            applied, info = make_controller('mpc', {'input_weight': 1.}).step(state, 30., powers, previous)
            self.assertFalse(info['fallback'], info)
            self.assertEqual(info['solver_status'], 'solved')
            self.assertLessEqual(info['primal_residual'], 1e-5)
            self.assertLessEqual(info['dual_residual'], 1e-5)
            self.assertIsNotNone(info['accepted_slack_max_C'])
            self.assertLessEqual(abs(applied - previous), .1 + 1e-10)

    def test_failed_or_false_success_qp_uses_fallback(self):
        cases = [(2, np.zeros(36), 0., 0.), (1, np.zeros(36), 0., 0.),
                 (1, np.ones(36), 1., 0.)]
        for status, z, primal, dual in cases:
            result = SimpleNamespace(x=z, info=SimpleNamespace(status_val=status, status='injected',
                                                               prim_res=primal, dual_res=dual))
            with patch('digital_twin.control.enclosure_control_v2.osqp.OSQP') as cls:
                cls.return_value.solve.return_value = result
                applied, info = make_controller('mpc', {'input_weight': 1.}).step([60., 60., .5], 30., (200., 280.), .5)
            self.assertAlmostEqual(applied, .6)
            self.assertTrue(info['fallback'])
            self.assertIsNone(info['accepted_slack_max_C'])

    def test_lqr_solver_failure_uses_common_fallback(self):
        with patch('digital_twin.control.enclosure_control_v2.solve_discrete_are', side_effect=np.linalg.LinAlgError('injected')):
            applied, info = make_controller('lqr', {'input_weight': 1.}).step([60., 60., .5], 30., (200., 280.), .5)
        self.assertAlmostEqual(applied, .6)
        self.assertTrue(info['fallback'])

    def test_lqr_rejects_false_dare_solution(self):
        with patch('digital_twin.control.enclosure_control_v2.solve_discrete_are', return_value=np.zeros((3, 3))):
            _, info = make_controller('lqr', {'input_weight': 1.}).step([60., 60., .5], 30., (200., 280.), .5)
        self.assertTrue(info['fallback'])

    def test_prediction_and_cap_diagnostic_use_applied_command(self):
        state = np.array([76., 60., .5])
        for controller in self.controllers():
            applied, info = controller.step(state, 30., (450., 600.), .5)
            A, B, c = linearize_zoh(state, 30., (450., 600.), self.p, self.s)
            np.testing.assert_allclose(info['predicted'], (A @ state + B * applied + c)[:2])
            base, mapping = prediction_map_v2(state, 30., (450., 600.), self.p, self.s)
            expected = max(0., float(np.max(base + mapping @ np.full(12, applied) - np.tile([78., 83.], 12))))
            self.assertAlmostEqual(info['applied_violation_C'], expected)
            self.assertTrue(math.isfinite(info['solver_s']))
            self.assertGreater(info['solver_s'], 0.)

    def test_invalid_input_is_rejected_before_optimization(self):
        with self.assertRaises(ValueError): make_controller('lqr', {'input_weight': 0.})
        with self.assertRaises(ValueError): make_controller('fixed', {'pwm': 2.})
        with self.assertRaises(ValueError): make_controller('pid', {'kp': .1})
        with self.assertRaises(ValueError):
            self.controllers()[0].step([float('nan'), 60., .5], 30., (100., 100.), .5)


if __name__ == '__main__':
    unittest.main()
