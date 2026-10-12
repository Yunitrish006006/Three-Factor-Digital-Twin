import importlib.util
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/'scripts/score_enclosure_reference.py'
SPEC=importlib.util.spec_from_file_location('reference_score',PATH)
MODULE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ReferenceScoreTests(unittest.TestCase):
    def test_forecast_uses_next_time_and_preserves_missing_count(self):
        proposals={'commands':[{'time_s':0,'source_estimate_C':22,'source_prediction_next_C':25},
                               {'time_s':5,'source_estimate_C':23,'source_prediction_next_C':26}]}
        report=MODULE.score(proposals,[{'time_s':0,'source_reference_C':21},{'time_s':5,'source_reference_C':24}])
        self.assertEqual(report['current_estimate']['mae_C'],1)
        self.assertEqual(report['next_sample_forecast']['mae_C'],1)
        self.assertEqual(report['next_sample_forecast']['n'],1)
        self.assertEqual(report['missing_next_reference_count'],1)

    def test_missing_duplicate_and_nonfinite_references_are_rejected(self):
        proposals={'commands':[{'time_s':0,'source_estimate_C':22,'source_prediction_next_C':25}]}
        for reference in ([],[{'time_s':0,'source_reference_C':float('nan')}],
                          [{'time_s':0,'source_reference_C':22}]*2):
            with self.assertRaises(ValueError):
                MODULE.score(proposals,reference)
