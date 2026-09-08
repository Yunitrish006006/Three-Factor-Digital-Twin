"""Native unit mapping must not mix Kelvin and normalized compressor commands."""
import importlib.util
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from boptest_native_adapter import encode, decode, validate_config

class NativeAdapterTests(unittest.TestCase):
    def test_native_units_round_trip_and_limits(self):
        for bounds in [(0,1),(273.15,318.15),(-10000,10000)]:
            c=dict(actuator_min=bounds[0],actuator_max=bounds[1])
            for u in [0,.2,.5,1]:self.assertAlmostEqual(decode(c,encode(c,u)),u)
            self.assertEqual(encode(c,-1),bounds[0]);self.assertEqual(encode(c,2),bounds[1])

    def fixture(self):
        c=dict(actuator_min=0,actuator_max=1,actuator_input='u',actuator_output='y',actuator_activate='active',actuator_unit='1',temperature='T',outdoor='out',overrides=[],power_outputs={})
        variables=[SimpleNamespace(name=n,causality=ca,unit=unit,min=low,max=high,type=kind) for n,ca,unit,low,high,kind in [('u','input','1',0,1,'Real'),('y','output','1',None,None,'Real'),('active','input',None,None,None,'Boolean'),('T','output','K',None,None,'Real'),('out','output','K',None,None,'Real')]]
        return c,variables

    def test_rejects_wrong_temperature_unit(self):
        c,v=self.fixture();validate_config(c,v);v[-1].unit='degC'
        with self.assertRaises(AssertionError):validate_config(c,v)

    def test_rejects_out_of_bounds_installation_override(self):
        c,v=self.fixture();c['overrides']=[dict(input='u',activate='active',value=2,unit='1')]
        with self.assertRaises(AssertionError):validate_config(c,v)
