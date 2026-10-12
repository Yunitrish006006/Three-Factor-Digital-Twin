import csv
from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np
from digital_twin.enclosure.session import (
    Observation, EnclosureSession, SessionController, HeatNetwork, METHODS,
    TransferSettings, steady_state, equilibrium, linearize, advance, fit_observations,
)


class EnclosureSessionTests(unittest.TestCase):
    def test_reference_columns_cannot_change_estimate_or_command(self):
        row = dict(time_s=0, plate_C=24, air_C=23, fan_fraction=.4, inlet_C=22, power_W=2)
        outputs = []
        for reference in (-500, 999999):
            session = EnclosureSession(HeatNetwork(), 22)
            outputs.append(session.process(Observation.from_row({**row, 'source_reference_C': reference})))
        for key in ('pwm', 'source_estimate_C', 'source_prediction_next_C'):
            self.assertEqual(outputs[0][key], outputs[1][key])

    def test_missing_and_nonfinite_sensor_rejected(self):
        row = dict(time_s=0, plate_C=24, air_C=23, fan_fraction=.4, inlet_C=22, power_W=2)
        for key in row:
            with self.subTest(key=key):
                with self.assertRaises(ValueError):
                    Observation.from_row({**row, key: float('nan')})
                with self.assertRaises(KeyError):
                    Observation.from_row({k: v for k, v in row.items() if k != key})
        for fan in (-.01, 1.01):
            with self.assertRaises(ValueError):
                Observation.from_row({**row, 'fan_fraction': fan})

    def test_cadence_failure_is_atomic(self):
        session = EnclosureSession(HeatNetwork(), 22, 'pi')
        session.process(Observation(0, 23, 22.2, .4, 22, 2))
        state, covariance = session.observer.state.copy(), session.observer.covariance.copy()
        integral, previous = session.controller.integral, session.previous_pwm
        for timestamp in (0, 4, 10):
            with self.assertRaises(ValueError):
                session.process(Observation(timestamp, 25, 24, .5, 22, 2))
            np.testing.assert_array_equal(session.observer.state, state)
            np.testing.assert_array_equal(session.observer.covariance, covariance)
            self.assertEqual(session.controller.integral, integral)
            self.assertEqual(session.previous_pwm, previous)

    def test_raw_warning_for_all_methods_and_both_channels(self):
        for method in METHODS:
            for raw in ([29.5, 22], [22, 29.5]):
                control = SessionController(method, HeatNetwork())
                duty, info = control.step([22, 22, 22, .4], 22, 2, .4, observed_plate_air=raw)
                self.assertTrue(info['warning'], method)
                self.assertAlmostEqual(duty, .5)

    def test_commands_obey_bounds_and_slew_under_extreme_load(self):
        for method in METHODS:
            session = EnclosureSession(HeatNetwork(), 22, method)
            for k in range(5):
                result = session.process(Observation(5*k, 35, 32, .4, 22, 20))
                self.assertTrue(.2 <= result['pwm'] <= 1)
                self.assertLessEqual(abs(result['pwm'] - result['previous_pwm']), .10000001)

    def test_equilibrium_balances_energy_and_bounds(self):
        p, s = HeatNetwork(), TransferSettings()
        for power in (0, 2, 20):
            center, duty = equilibrium(p, 22, power, s)
            np.testing.assert_allclose(advance(center, duty, 22, power, p), center, atol=1e-9)
            self.assertTrue(.2 <= duty <= 1)

    def test_linearization_matches_small_perturbation(self):
        x, u = steady_state(HeatNetwork(), 22, 2, .5), .5
        a, b, offset = linearize(x, u, 22, 2, HeatNetwork(), 5)
        delta = np.array([1e-4, -1e-4, 2e-4, 1e-5])
        exact = advance(x+delta, u+1e-5, 22, 2, HeatNetwork())
        approx = a@(x+delta) + b[:, 0]*(u+1e-5) + offset
        np.testing.assert_allclose(exact, approx, atol=1e-8)

    def test_failed_mpc_or_riccati_uses_feasible_shared_fallback(self):
        failed = SimpleNamespace(success=False, x=np.array([np.nan]*6))
        for method, mocked in [('linear_mpc', 'minimize'), ('lqr', 'solve_discrete_are')]:
            kwargs = {'return_value': failed} if method == 'linear_mpc' else {'side_effect': np.linalg.LinAlgError()}
            with patch('digital_twin.enclosure.session.'+mocked, **kwargs):
                duty, info = SessionController(method, HeatNetwork()).step(
                    [28, 25, 23, .4], 22, 2, .4, observed_plate_air=[25, 23])
            self.assertTrue(info['fallback'])
            self.assertLessEqual(abs(duty-.4), .10000001)

    def test_calibration_rejects_time_or_command_corruption(self):
        good = dict(time_s=0, plate_C=22, air_C=22, fan_fraction=.4, inlet_C=22, power_W=1, pwm=.4)
        for rows in ([], [good, {**good, 'time_s': 10}], [{**good, 'pwm': 2}]):
            with self.assertRaises(ValueError):
                fit_observations(rows)

    def test_constant_state_lqr_returns_equilibrium_command(self):
        control = SessionController('lqr', HeatNetwork())
        center, duty = equilibrium(HeatNetwork(), 22, 2, TransferSettings())
        actual, info = control.step(center, 22, 2, duty, observed_plate_air=center[1:3])
        self.assertFalse(info['fallback'])
        self.assertAlmostEqual(actual, duty, places=8)


if __name__ == '__main__':
    unittest.main()
