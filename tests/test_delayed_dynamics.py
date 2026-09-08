import unittest
from digital_twin.control.delayed_dynamics import DelayedPortablePI,fit_arx,rollout_rmse,identify_bank

class DelayedDynamicsTests(unittest.TestCase):
    def rows(self):
        rows=[];history=[0.0,0.0];us=[]
        for i in range(180):
            u=((i*17)%37)/36;us.append(u)
            lag=us[i-3] if i>=3 else .5
            next_y=1.3*history[-1]-.4*history[-2]+.2*(lag-.5)
            rows.append(dict(T=22+history[-1],next_T=22+next_y,u=u,outdoor=22,time_s=i*60))
            history.append(next_y)
        return rows
    def test_recovers_known_stable_second_order_delay(self):
        model=fit_arx(self.rows(),list(range(11,160)),2,3,22)
        self.assertEqual(model['status'],'FITTED')
        self.assertAlmostEqual(model['a'][0],1.3,places=6)
        self.assertAlmostEqual(model['a'][1],-.4,places=6)
        self.assertAlmostEqual(model['b'],.2,places=6)
        self.assertLess(rollout_rmse(model,self.rows(),[160,170],22),1e-6)
    def test_rejects_growing_pole_without_clipping(self):
        rows=[];t=.01
        for i in range(80):
            u=(i%7)/6;nxt=1.08*t+.1*(u-.5)
            rows.append(dict(T=22+t,next_T=22+nxt,u=u,outdoor=22,time_s=i*60));t=nxt
        m=fit_arx(rows,list(range(11,80)),1,0,22)
        self.assertEqual(m['status'],'REJECTED_POLE_OR_GAIN');self.assertGreater(m['radius'],1)
    def test_delay_queue_is_actual_past_input(self):
        c=DelayedPortablePI(22,60,.1,600,.2,2,True);c.prime(22,.5);c.step(22,.5,0)
        c.step(22,.8,1);self.assertAlmostEqual(c.disturbance,0)
        c.step(22,.9,2);self.assertAlmostEqual(c.disturbance,0)
        c.step(22,.1,3);self.assertAlmostEqual(c.disturbance,-.012)
    def test_shared_bank_has_ten_candidates_and_common_history(self):
        b=identify_bank(self.rows(),22,60)
        self.assertEqual(len(b['candidates']),10)
        self.assertEqual(len(set(m['n'] for m in b['candidates'])),1)
        self.assertEqual(b['status'],'FITTED')
    def test_rollout_does_not_use_intermediate_measured_temperatures(self):
        rows=self.rows();m=fit_arx(rows,list(range(11,150)),2,3,22)
        score=rollout_rmse(m,rows,[160],22)
        changed=[dict(r) for r in rows]
        for i in range(161,170):changed[i]['T']+=999
        self.assertEqual(score,rollout_rmse(m,changed,[160],22))

if __name__=='__main__':unittest.main()
