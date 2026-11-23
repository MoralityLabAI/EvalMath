from fractions import Fraction as F
from importlib.util import find_spec
import unittest
from chronology_data import make_data,key,target,exact_actions,summarize
from nonstationary import literal_values


class ChronologyDataTests(unittest.TestCase):
    def test_custody_and_frozen_evaluation(self):
        train,dev,m=make_data(1200,500)
        a={key(h) for _,h in train}
        b={key(h) for rows in dev.values() for _,h in rows}
        self.assertFalse(a&b)
        self.assertEqual(m["cross_split_bags"],0)
        self.assertTrue(all(k in (0,1) for k,_ in train))
        self.assertEqual(set(dev),{f"{part}_k{k}" for part in ("paired","ordinary") for k in (0,1,2)})
        for k in (0,1,2):
            rows=dev[f"paired_k{k}"]
            a=exact_actions(rows,"pair_orderless")
            s=summarize(rows,a,True)
            self.assertAlmostEqual(s["mean_regret"],s["orderless_floor"],places=13)
            self.assertEqual(s["different_action_fraction"],0)
            self.assertEqual(summarize(rows,exact_actions(rows,"full"),True)["mean_regret"],0)
        self.assertGreater(summarize(dev["paired_k1"],exact_actions(dev["paired_k1"],"pair_orderless"),True)["orderless_floor"],0)

    def test_teacher_against_independent_path_oracle(self):
        for r in ((1,(0,23,1)),(1,(23,0,1)),(2,(0,12,16)),(0,(0,23,1))):
            self.assertEqual(target(r),literal_values(r[1],r[0]))

    @unittest.skipUnless(find_spec("torch"),"dedicated CPU workflow installs torch")
    def test_matched_models_and_orderless_invariance(self):
        import torch
        from chronology_router import ARMS,model,count,encode,fit,actions
        rows=[(1,(0,23,1)),(1,(23,0,1))]
        x,k,y=encode(rows,True)
        counts=[]
        for arm in ARMS:
            m=model(arm)
            counts.append(count(m))
            self.assertEqual(tuple(m(x,k).shape),(2,8))
            if arm in ("hist_last","reset"):
                self.assertTrue(torch.equal(m(x,k)[0],m(x,k)[1]))
            m,trace=fit(arm,101,(x,k,y),1)
            self.assertEqual(len(trace),1)
        self.assertEqual(counts,[2696,2792,2696,2696,2762])
        self.assertLess(max(counts)/min(counts),1.05)


if __name__=="__main__":
    unittest.main()
