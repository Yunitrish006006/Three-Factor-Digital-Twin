import unittest
from unittest.mock import patch
from digital_twin.control.enclosure_unified import UnifiedController

class UnifiedTests(unittest.TestCase):
 def test_pi_requires_no_derivative(self):
  with self.assertRaises(ValueError):UnifiedController('pi',dict(kp=.03,ki=.0001,kd=.01))
 def test_plain_feedback_no_power_feedforward(self):
  a=UnifiedController('pi',dict(kp=.03,ki=.0001,kd=0));b=UnifiedController('pi',dict(kp=.03,ki=.0001,kd=0))
  ua,ia=a.step([60,60,.5],30,(90,130),.5);ub,ib=b.step([60,60,.5],30,(200,280),.5)
  self.assertEqual(ua,ub);self.assertEqual(ia['raw_pwm'],.6);self.assertEqual(ib['raw_pwm'],.6)
 def test_common_slew_and_warning(self):
  for method,params in [('fixed',dict(pwm=.4)),('pi',dict(kp=.03,ki=.0001,kd=0)),('pid',dict(kp=.03,ki=.0001,kd=.03)),('lqr',dict(input_weight=1)),('mpc',dict(input_weight=1))]:
   u,info=UnifiedController(method,params).step([76,81,.5],30,(110,150),.5)
   self.assertTrue(info['warning']);self.assertAlmostEqual(u,.6)
 def test_pid_derivative_effect(self):
  a=UnifiedController('pi',dict(kp=.001,ki=0,kd=0));b=UnifiedController('pid',dict(kp=.001,ki=0,kd=.05))
  for ctl in (a,b):ctl.step([60,60,.5],30,(100,150),.6)
  _,ia=a.step([61,61,.5],30,(100,150),.6);_,ib=b.step([61,61,.5],30,(100,150),.6)
  self.assertGreater(ib['raw_pwm'],ia['raw_pwm'])
 def test_exception_fallback(self):
  ctl=UnifiedController('lqr',dict(input_weight=1))
  with patch.object(ctl.delegate,'_lqr',side_effect=RuntimeError('fixture')):u,info=ctl.step([60,60,.5],30,(100,150),.5)
  self.assertTrue(info['fallback']);self.assertAlmostEqual(u,.6)
