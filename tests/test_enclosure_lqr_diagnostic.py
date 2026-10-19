import copy
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from run_enclosure_lqr_diagnostic import episode,all_metrics,HeatNetwork,ARMS
from verify_enclosure_lqr_diagnostic import audit
from dataclasses import asdict


class DiagnosticContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=HeatNetwork();cls.rows=episode(cls.p,cls.p,619999,'estimated_fitted')
        cls.run_record={'panel':'fixture','seed':619999,'arm':'estimated_fitted','metrics':all_metrics(cls.rows)}
        cls.config={'panels':{'fixture':asdict(cls.p)},'arms':ARMS}
        cls.cal={'fixture':{'parameters':asdict(cls.p)}}

    def test_valid_input_only_replay(self):
        self.assertLess(audit(self.rows,self.run_record,self.config,self.cal),1e-5)

    def test_reject_corrupted_oracle_access(self):
        rows=copy.deepcopy(self.rows);rows[0]['source_control']=rows[0]['source_truth_current_C']
        with self.assertRaisesRegex(ValueError,'oracle access'):audit(rows,self.run_record,self.config,self.cal)

    def test_reject_mutated_command(self):
        rows=copy.deepcopy(self.rows);rows[4]['pwm']+=.02
        with self.assertRaisesRegex(ValueError,'controller replay'):audit(rows,self.run_record,self.config,self.cal)

    def test_reject_false_truth_and_schedule(self):
        for key in ('source_truth_next_C','power_W'):
            rows=copy.deepcopy(self.rows);rows[3][key]+=.1
            with self.assertRaises(ValueError):audit(rows,self.run_record,self.config,self.cal)

    def test_oracle_model_does_not_replace_observer(self):
        rows=episode(self.p,self.p,619999,'truth_exact')
        self.assertTrue(all(r['source_control']==r['source_truth_current_C'] for r in rows))
        self.assertNotEqual(rows[0]['source_estimate_C'],rows[0]['source_control'])
        run={**self.run_record,'arm':'truth_exact','metrics':all_metrics(rows)}
        audit(rows,run,self.config,self.cal)


if __name__=='__main__':unittest.main()
