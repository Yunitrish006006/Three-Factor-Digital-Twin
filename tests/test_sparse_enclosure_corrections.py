import copy
import csv
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from digital_twin.control.sparse_enclosure import HeatNetwork, SparseObserver, thermal_rhs
from digital_twin.control.sparse_enclosure_v2 import TransferController
from artifact_visual_qa import visual_qa_status
from sparse_enclosure_corrections import ORIGINAL, sha, equilibrium
from verify_sparse_enclosure_integrity import check_integrity, check_trace, load_rows
from verify_sparse_enclosure import check_artifacts

METHODS = ('fixed', 'pi', 'pid', 'rank_h1', 'rank_h6', 'rank_h6_no_correction')


class CorrectedWarningTests(unittest.TestCase):
    def test_raw_threshold_crossing_overrides_every_method_before_slew(self):
        for channel in (0, 1):
            for method in METHODS:
                with self.subTest(method=method, channel=channel):
                    p = HeatNetwork()
                    observer = SparseObserver(p, 22.)
                    observer.predict(.4, 22., 0.)
                    raw = [22., 22.]
                    raw[channel] = 29.51
                    x = observer.update([*raw, .4])
                    self.assertLess(x[channel + 1], 29.5)
                    u, info = TransferController(method, p).step(x, 22., 0., .4, observed_plate_air=raw)
                    self.assertTrue(info['warning'])
                    self.assertAlmostEqual(u, .5)

    def test_estimated_source_also_triggers_warning(self):
        for method in METHODS:
            _, info = TransferController(method, HeatNetwork()).step([29.5, 22., 22., .4], 22., 0., .4, observed_plate_air=[22., 22.])
            self.assertTrue(info['warning'])

    def test_posterior_plate_alone_does_not_replace_raw_warning_channel(self):
        for method in METHODS:
            _, info = TransferController(method, HeatNetwork()).step([24., 31., 31., .4], 22., 0., .4, observed_plate_air=[22., 22.])
            self.assertFalse(info['warning'])

    def test_raw_channel_is_required_and_malformed_observations_reject(self):
        c = TransferController('pi', HeatNetwork())
        with self.assertRaises(TypeError):
            c.step([24., 23., 22., .4], 22., 0., .4)
        for raw in ([22.], [22., 22., 40.], [float('nan'), 22.]):
            with self.assertRaises(ValueError):
                c.step([24., 23., 22., .4], 22., 0., .4, observed_plate_air=raw)
        self.assertEqual(c.integral, 0.)


class ScorerIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads((ORIGINAL / 'result.json').read_text())
        cls.config = json.loads((ORIGINAL / 'config.json').read_text())
        cls.episode = cls.result['runs'][0]
        cls.rows = load_rows(ORIGINAL / cls.episode['csv'])

    def test_original_evidence_passes_independent_reference(self):
        report = check_integrity()
        self.assertTrue(report['passed'], report['errors'][:3])
        self.assertEqual(report['verified_steps'], 19440)
        self.assertLess(report['maximum_reference_difference']['source_C'], .01)

    def test_wrong_time_is_rejected(self):
        rows = copy.deepcopy(self.rows)
        for row in rows:
            row['time_s'] = 123456.
        errors, _ = check_trace(rows, self.episode, self.config)
        self.assertIn('timestamp/step alignment', errors)

    def test_reordered_truth_rejects_after_recomputed_legacy_scores(self):
        # Preserve the review's exact failure: legacy metrics can be made coherent
        # while source truth is paired with the wrong time.
        with tempfile.TemporaryDirectory() as temporary:
            dest = Path(temporary) / 'artifacts'
            shutil.copytree(ORIGINAL, dest)
            rows = copy.deepcopy(self.rows)
            for row, value in zip(rows, [r['source_truth_next'] for r in rows][::-1]):
                row['source_truth_next'] = value
            path = dest / self.episode['csv']
            with path.open('w', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                writer.writeheader(); writer.writerows(rows)
            result = copy.deepcopy(self.result)
            truth = [r['source_truth_next'] for r in rows]
            pred = [r['source_prediction_next']-r['source_truth_next'] for r in rows]
            result['runs'][0]['metrics'].update(prediction_mae_C=float(np.mean(np.abs(pred))),
                tracking_mae_C=float(np.mean(np.abs(np.array(truth)-28.))), max_source_C=max(truth),
                overtemp_s=sum(t>30 for t in truth)*5., out_of_domain_steps=sum(t<20 or t>30 for t in truth))
            group = [r['metrics'] for r in result['runs'] if r['task']==self.episode['task']
                     and r['split']==self.episode['split'] and r['method']==self.episode['method']]
            result['aggregates'][self.episode['task']][self.episode['split']][self.episode['method']] = {
                key:float(np.mean([m[key] for m in group])) for key in group[0]}
            (dest / 'result.json').write_text(json.dumps(result))
            self.assertTrue(check_artifacts(dest)['passed'])
            errors, _ = check_trace(rows, self.episode, self.config)
            self.assertIn('source truth continuity', errors)

    def test_coordinated_truth_shift_cannot_evade_dynamics_check(self):
        rows = copy.deepcopy(self.rows)
        for k, row in enumerate(rows):
            if k:
                row['source_truth_current'] += 1.
            row['source_truth_next'] += 1.
        errors, _ = check_trace(rows, self.episode, self.config)
        self.assertNotIn('source truth continuity', errors)
        self.assertTrue(any('source dynamics' in error for error in errors))

    def test_exogenous_noise_and_fan_corruptions_reject(self):
        for key, error_label in (('declared_power', 'power provenance'), ('inlet','inlet provenance'),
                                 ('plate_observed','noise provenance'), ('fan_observed','fan observation provenance'),
                                 ('fan_truth_next','fan endpoint dynamics')):
            rows = copy.deepcopy(self.rows)
            rows[10][key] += 1.
            errors, _ = check_trace(rows, self.episode, self.config)
            self.assertTrue(any(error_label in error for error in errors), key)

    def test_missing_csv_is_rejected_instead_of_success(self):
        with tempfile.TemporaryDirectory() as temporary:
            self.assertFalse(check_integrity(temporary)['passed'])


class VisualProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.artifact = 'report.html'
        (self.root / self.artifact).write_text('<html>observed content</html>')
        (self.root / 'evidence.json').write_text('{"observed":"test fixture"}')
        self.store = self.root / 'observations.json'
        self.record = {'artifact':self.artifact, 'artifact_sha256':sha(self.root/self.artifact),
            'observed_utc':'2026-10-06T00:00:00+00:00', 'observer':'unit-test fixture',
            'method':'fixture only, not a real Browser observation', 'scope':'fixture', 'status':'PASS',
            'checks':{'anchors':'PASS'}, 'evidence':[{'path':'evidence.json','sha256':sha(self.root/'evidence.json')}]}

    def write_store(self):
        self.store.write_text(json.dumps({'schema_version':1, 'observations':[self.record]}))

    def status(self):
        return visual_qa_status(self.root, self.store, self.artifact, ('anchors',))

    def test_same_content_record_passes_without_refreshing_observation(self):
        self.write_store(); before = self.store.read_bytes()
        self.assertEqual(self.status()['status'],'PASS')
        self.assertEqual(self.store.read_bytes(),before)

    def test_broken_html_is_stale_and_original_date_is_preserved(self):
        self.write_store()
        (self.root/self.artifact).write_text('<a href="#missing">broken</a><script>throw Error("bad")</script>')
        result = self.status()
        self.assertEqual(result['status'],'STALE')
        self.assertEqual(result['observation']['observed_utc'],self.record['observed_utc'])

    def test_browser_utc_timestamp_is_supported(self):
        self.record['observed_utc']='2026-10-06T00:00:00.000Z'; self.write_store()
        self.assertEqual(self.status()['status'],'PASS')
        self.record['observed_utc']=123; self.write_store()
        self.assertEqual(self.status()['status'],'INVALID')

    def test_missing_record_is_not_evaluated(self):
        self.assertEqual(self.status()['status'],'NOT_EVALUATED')

    def test_malformed_or_incomplete_record_is_invalid(self):
        self.store.write_text('{')
        self.assertEqual(self.status()['status'],'INVALID')
        del self.record['observed_utc']; self.write_store()
        self.assertEqual(self.status()['status'],'INVALID')

    def test_changed_evidence_is_stale(self):
        self.write_store(); (self.root/'evidence.json').write_text('changed')
        self.assertEqual(self.status()['status'],'STALE')

    def test_missing_required_check_is_not_accepted(self):
        self.record['checks']={};self.write_store()
        self.assertEqual(self.status()['status'],'NOT_ACCEPTED')


class CapacityTests(unittest.TestCase):
    def test_steady_solution_matches_heat_balance_and_counterexample(self):
        from dataclasses import asdict, replace
        p=replace(HeatNetwork(),contact=.45)
        steady=equilibrium(asdict(p),3.35,22.,1.)
        np.testing.assert_allclose(thermal_rhs(steady,1.,22.,3.35,p),0.,atol=1e-14)
        self.assertAlmostEqual(steady[0],32.39986167374765)
        self.assertGreater(steady[0],30.)


if __name__ == '__main__':
    unittest.main()
