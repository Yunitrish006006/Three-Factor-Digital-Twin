import unittest
from dataclasses import replace

import numpy as np

from digital_twin.control.sparse_enclosure import (
    HeatNetwork, TransferSettings, thermal_rhs, advance, command,
    SparseObserver, TransferController, fit_sparse_network,
)


class SparseEnclosureTests(unittest.TestCase):
    def test_energy_balance_internal_paths_cancel(self):
        p = HeatNetwork()
        t = np.array([30., 25., 23.])
        rate = thermal_rhs(t, .5, 22., 2., p)
        external = 2. - p.bypass * (30. - 22.) - (p.air_base + p.air_fan * .5) * (23. - 22.)
        self.assertAlmostEqual(float(rate @ p.capacities), external, places=12)

    def test_equilibrium_and_integration_accuracy(self):
        p = HeatNetwork()
        x = np.array([22., 22., 22., .4])
        np.testing.assert_allclose(advance(x, .4, 22., 0., p), x)
        rough = advance([30., 26., 23., .4], .9, 22., 2., p)
        fine = advance([30., 26., 23., .4], .9, 22., 2., p, substeps=100)
        self.assertLess(float(np.max(np.abs(rough - fine))), .005)

    def test_observer_only_accepts_declared_channels(self):
        obs = SparseObserver(HeatNetwork(), 22.)
        with self.assertRaises(ValueError):
            obs.update([42., 23., 22., .4])
        with self.assertRaises(ValueError):
            obs.update([float('nan'), 22., .4])
        x = obs.update([23., 22., .4])
        self.assertEqual(x.shape, (4,))
        obs.predict(.5, 22., 2.)
        self.assertGreaterEqual(np.linalg.eigvalsh(obs.covariance).min(), -1e-12)

    def test_hidden_truth_has_no_effect_on_estimates_or_commands(self):
        def replay(truth):
            observer = SparseObserver(HeatNetwork(), 22.)
            controller = TransferController('rank_h6', HeatNetwork())
            previous, outputs, scores = .4, [], []
            for source_truth in truth:
                x = observer.update([23., 22.3, .5])
                u, _ = controller.step(x, 22., 2., previous)
                outputs.append([*x, u])
                scores.append(abs(x[0] - source_truth))
                observer.predict(u, 22., 2.)
                previous = u
            return outputs, scores
        a, score_a = replay([25.] * 10)
        b, score_b = replay([100.] * 10)
        np.testing.assert_array_equal(a, b)
        self.assertNotEqual(score_a, score_b)

    def test_limits_all_methods_and_horizon_one_equivalence(self):
        s, p = TransferSettings(), HeatNetwork()
        for method in ('fixed', 'pi', 'pid', 'rank_h1', 'rank_h6', 'rank_h6_no_correction'):
            c = TransferController(method, p)
            previous = .4
            for source in (22., 29.6, 40., 24., 26.):
                u, _ = c.step([source, 23., 22., .4], 22., 2., previous)
                self.assertLessEqual(abs(u - previous), s.slew + 1e-12)
                self.assertTrue(s.pwm_min <= u <= s.pwm_max)
                previous = u
        with self.assertRaises(ValueError):
            command(float('nan'), .4)

    def test_sparse_identification_without_truth(self):
        true = replace(HeatNetwork(), contact=1.1, plate_fan=1.3)
        x, records = np.array([22., 22., 22., .4]), []
        for k in range(120):
            u, power = (.25 if (k // 15) % 2 == 0 else .75), (.8 if (k // 20) % 2 == 0 else 2.8)
            records.append({'inlet': 22., 'power': power, 'pwm': u, 'plate': x[1], 'air': x[2]})
            x = advance(x, u, 22., power, true)
        p, info = fit_sparse_network(records)
        self.assertTrue(info['success'])
        self.assertAlmostEqual(p.contact, true.contact, places=5)
        self.assertAlmostEqual(p.plate_fan, true.plate_fan, places=5)

    def test_nonpositive_network_rejected(self):
        with self.assertRaises(ValueError):
            HeatNetwork(contact=-1.)


if __name__ == '__main__':
    unittest.main()
