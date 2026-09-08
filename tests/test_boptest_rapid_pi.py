import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('boptest_pilot', Path(__file__).resolve().parents[1] / 'scripts/run_boptest_rapid_pi.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class BoptestPilotTests(unittest.TestCase):
    def test_antiwindup_and_recovery(self):
        pi = m.PI()
        for i in range(1000):
            self.assertEqual(pi({'T': -30}, i), 40)
        self.assertEqual(pi.integral, 0)
        self.assertLess(pi({'T': 23}, 1001), 22)

    def test_nonfinite_actuation_rejected(self):
        with self.assertRaises(ValueError):
            m.clip(float('nan'))

    def test_identifies_known_physical_transition(self):
        rows = []
        for i in range(120):
            t = 21 + (i % 5) * .2
            outdoor = 4 + (i % 9)
            command = 18 + (i % 7) * 3
            solar = (i % 11) * 50
            delta = .01 * (outdoor - t) + .08 * (command - t) + .03 * solar / 1000 + .1
            rows.append(dict(T=t, outdoor=outdoor, command=command, solar=solar,
                             next_T=t + delta, time_s=i * 60))
        fit = m.fit_rc(rows)
        self.assertEqual(fit['status'], 'FITTED')
        for actual, expected in zip(fit['coefficients'], [.01, .08, .03, .1]):
            self.assertAlmostEqual(actual, expected, places=6)
        self.assertEqual(fit['fit_end_s'], 7200)

    def test_nonphysical_model_falls_back(self):
        rows = [dict(T=22, outdoor=i % 9, command=i % 7 + 12, solar=(i % 11)*100,
                     next_T=22 - .1 * (i % 7 + 12 - 22), time_s=60*i) for i in range(100)]
        self.assertEqual(m.fit_rc(rows)['status'], 'REJECTED_NONPHYSICAL')

    def test_independent_controller_integrals(self):
        first, second = m.PI(), m.PI()
        first({'T': 21}, 0)
        self.assertEqual(second.integral, 0)


if __name__ == '__main__':
    unittest.main()
