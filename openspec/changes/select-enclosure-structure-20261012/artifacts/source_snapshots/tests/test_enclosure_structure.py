from dataclasses import replace
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import numpy as np

from digital_twin.control.sparse_enclosure import advance as old_advance,HeatNetwork
from digital_twin.enclosure.session import Observation
from digital_twin.enclosure.calibrated_session import (
    ThermalPathParameters,thermal_rates,advance,transition,StructureController,
    CalibratedEnclosureSession,fit_structures,parameters_for,choose_structure,
)


class StructureTests(unittest.TestCase):
    def test_extra_exchange_preserves_total_energy(self):
        p=ThermalPathParameters(source_air=.2)
        rates=thermal_rates([30,26,24],.4,22,3,p)
        expected=3-p.bypass*(30-22)-(p.air_base+p.air_fan*.4)*(24-22)
        self.assertAlmostEqual(float(np.dot(rates,p.capacities)),expected)

    def test_no_extra_path_matches_frozen_primitive(self):
        state=[28,25,23,.4]
        np.testing.assert_allclose(advance(state,.8,22,2,ThermalPathParameters()),
                                   old_advance(state,.8,22,2,HeatNetwork()),atol=1e-12)

    def test_zero_power_equilibrium_and_fan_solution(self):
        p=ThermalPathParameters(source_air=.2)
        x=advance([22,22,22,.4],.8,22,0,p,dt=10)
        np.testing.assert_allclose(x[:3],22)
        self.assertAlmostEqual(x[3],.8+(.4-.8)*np.exp(-10/p.fan_tau))

    def test_independent_capacity_mapping(self):
        p=parameters_for('F',[.7,.8,1.4,.8,1.2,20,.1])
        self.assertEqual(p.capacities,(28.,64.,36.))
        self.assertEqual(p.source_air,.1)

    def test_invalid_path_and_input_rejected(self):
        for extra in (-.1,float('nan')):
            with self.assertRaises(ValueError):ThermalPathParameters(source_air=extra)
        with self.assertRaises(ValueError):advance([22]*4,.5,22,-1,ThermalPathParameters())

    def test_selection_threshold_failure_and_nan(self):
        for score,success,expected in ((.95,True,'F'),(.951,True,'S'),(.1,False,'S'),(float('nan'),True,'S')):
            self.assertEqual(choose_structure({'S':{'selection_score':1},'F':{'success':success,'selection_score':score}}),expected)

    def test_training_is_only_first120_and_truth_columns_not_used(self):
        rows=[dict(time_s=5*k,plate_C=22,air_C=22,fan_fraction=.4,inlet_C=22,power_W=0,pwm=.4,
                   source_reference_C=99999) for k in range(180)]
        calls=[]
        def fit(fun,start,bounds,max_nfev):
            errors=fun(np.array(start))
            calls.append(errors.size)
            return SimpleNamespace(success=True,x=np.array(start),jac=np.eye(len(start)),nfev=1)
        with patch('digital_twin.enclosure.calibrated_session.least_squares',side_effect=fit):
            _,report=fit_structures(rows)
        self.assertEqual(calls,[360,360])
        self.assertFalse(report['source_reference_input'])
        self.assertEqual(report['training_rows'],120)
        self.assertEqual(report['selection_rows'],60)
        self.assertFalse(report['refit_after_selection'])
        self.assertEqual(report['candidates']['S']['residual_calls'],1)

    def test_raw_warning_source_truth_invariance_and_cadence(self):
        for method in ('pi','rank_h6'):
            for key in ('plate_C','air_C'):
                inputs=dict(time_s=0,plate_C=22,air_C=22,fan_fraction=.4,inlet_C=22,power_W=2)
                inputs[key]=29.5
                session=CalibratedEnclosureSession(ThermalPathParameters(source_air=.1),22,method)
                result=session.process(Observation.from_row({**inputs,'source_reference_C':-999}))
                self.assertEqual(result['warning'],1)
                self.assertAlmostEqual(result['pwm'],.5)
                old=session.observer.state.copy()
                with self.assertRaises(ValueError):session.process(Observation.from_row(inputs))
                np.testing.assert_array_equal(session.observer.state,old)

    def test_covariance_transition_has_positive_transfer(self):
        a=transition(.4,ThermalPathParameters(source_air=.2),.001)
        self.assertGreater(a[0,2],0)
        self.assertGreater(a[2,0],0)


if __name__=='__main__':unittest.main()
