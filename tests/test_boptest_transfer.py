import importlib.util
from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from run_boptest_transfer import HandoverPI, ObserverPI, select


class BoptestTransferTests(unittest.TestCase):
    def test_heat_equivalent_handover(self):
        p = HandoverPI(3, 250)
        state = dict(T=22, supply=40, fan=.2)
        p.prime(state)
        self.assertAlmostEqual(p(state, 0), 29.2)
        self.assertAlmostEqual(.5*(p(state, 0)-22), .2*(40-22))

    def test_handover_limits(self):
        p = HandoverPI(3, 250)
        state = dict(T=22, supply=40, fan=1)
        p.prime(state)
        self.assertEqual(p(state, 0), 40)

    def test_observer_constant_balance(self):
        p = ObserverPI(3, 250, .1)
        state = dict(T=22, supply=30, fan=.5)
        p.prime(state)
        for i in range(100):
            self.assertAlmostEqual(p(state, i), 30)

    def test_observer_rejects_bad_gain(self):
        with self.assertRaises(ValueError):
            ObserverPI(3, 250, 0)

    def test_selection_rejects_one_bad_date(self):
        records = []
        for day in (3, 180):
            for name in ('v2', 'v3_handover', 'v4_observer'):
                error = .01 if name == 'v4_observer' else .05
                maximum = 2 if name == 'v4_observer' and day == 180 else .2
                records.append(dict(day=day, controller=name, metrics=dict(mae_C=error, max_abs_error_C=maximum)))
        self.assertEqual(select(records), 'v3_handover')


if __name__ == '__main__':
    unittest.main()
