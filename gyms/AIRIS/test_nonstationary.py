from fractions import Fraction as F
import unittest
from itertools import product
from nonstationary import (HAZARDS,EVENTS,PRIOR,advance,posterior,values,literal_posterior,
                           literal_values,optimal,orderless_floor,pair_values,census)
from curriculum import make_bundle,audit


class DriftTests(unittest.TestCase):
    def test_filter_against_literal_hidden_path_oracle(self):
        for k,h in product(HAZARDS,((0,23,1),(23,0,1),(0,None,1),(),(17,6))):
            w=posterior(h,k)
            self.assertEqual(tuple(F(x,sum(w)) for x in w),literal_posterior(h,k))
            self.assertEqual(values(w,k),literal_values(h,k))

    def test_revocation_preserves_physical_time(self):
        self.assertNotEqual(posterior((0,None,1),1),posterior((0,1),1))
        self.assertEqual(posterior((0,None,1),0),posterior((0,1),0))

    def test_strict_order_alias_and_stationary_control(self):
        # Probe IDs from the preregistered enumeration order.
        key=(0,23,1)
        q,r=pair_values(key,1)
        self.assertFalse(set(optimal(q))&set(optimal(r)))
        self.assertGreater(orderless_floor(q,r),F(1,100))
        s,t=pair_values(key,0)
        self.assertEqual(s,t)
        self.assertEqual(orderless_floor(s,t),0)

    def test_full_census_and_custody(self):
        train,dev,summaries=make_bundle()
        self.assertEqual([summaries[str(k)]["strict_pairs"] for k in HAZARDS],[0,272,32,0])
        self.assertTrue(all(x["pairs"]==15872 for x in summaries.values()))
        self.assertTrue(all("teacher" in r for r in train))
        self.assertTrue(all("teacher" not in r for r in dev))
        self.assertTrue(any(r["input"]["drift_resample_probability"]=="2/4" for r in dev))
        self.assertFalse(any(r["input"]["drift_resample_probability"]=="2/4" for r in train))
        counts=audit(train,dev)
        self.assertGreater(counts["train_groups"],0)
        self.assertEqual(len(train)%4,0)
        with self.assertRaises(ValueError):
            audit(train,[{**dev[0],"teacher":{}}])


if __name__=="__main__":
    unittest.main()
