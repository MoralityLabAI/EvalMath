from fractions import Fraction as F
from itertools import product
import unittest
from partial import (MODELS,RATES,SCHEDULES,MODES,ARMS,PULSE,PASSIVE,SCALE,
                     enumerate_channel,channel,prior,masses,posterior,score,receipt)


class PartialTests(unittest.TestCase):
    def test_likelihood_against_literal_hidden_path_enumeration(self):
        for a,mode in product(SCHEDULES,MODES):
            table=channel(a,mode)
            for i,(r,t) in enumerate(MODELS):
                p={o:F(l[i],SCALE) for o,l in table if l[i]}
                self.assertEqual(p,enumerate_channel(a,r,t,mode))
                self.assertEqual(sum(p.values()),1)

    def test_history_compression_exact_sufficiency(self):
        for a,(r,t) in product(SCHEDULES,MODELS):
            p=enumerate_channel(a,r,t,"difference")
            full=enumerate_channel(a,r,t,"full")
            for y in product(range(2),repeat=3):
                d=(y[0]^y[1],y[1]^y[2])
                self.assertEqual(full.get(y,0),p.get(d,0)/2)

    def test_memoryless_alias_and_iid_no_go(self):
        for a,(r,t) in product(SCHEDULES,MODELS):
            self.assertEqual(enumerate_channel(a,r,t,"last"),{(0,):F(1,2),(1,):F(1,2)})
            self.assertEqual(enumerate_channel(a,2,t,"full"),
                             {y:F(1,8) for y in product(range(2),repeat=3)})
        for n,arm in product(range(4),ARMS):
            self.assertEqual(score(2,n,arm),F(1,4))
            self.assertEqual(score(2,n,arm,"certified"),0)

    def test_persistent_driver_and_pulse(self):
        for t in range(4):
            self.assertEqual(enumerate_channel(PULSE,0,t,"difference"),
                             {(t&1,(t&1)^((t>>1)&1)):F(1)})
        self.assertEqual(score(0,1,"pulse_history"),1)
        self.assertEqual(score(0,1,"pulse_history","certified"),1)
        self.assertEqual(score(0,3,"pulse_one_difference"),F(1,2))
        self.assertEqual(score(0,3,"pulse_last"),F(1,4))

    def test_noisy_repeat_and_unknown_rate(self):
        self.assertEqual(score(1,1,"pulse_history"),F(9,16))
        self.assertEqual(score(1,2,"pulse_history"),F(9,16))
        self.assertEqual(score(1,3,"pulse_history"),F(729,1024))
        self.assertEqual(score(None,1,"pulse_history"),F(29,48))
        self.assertEqual(score(None,3,"pulse_history"),F(2009,3072))
        for r,n,arm in product((1,2,None),range(4),ARMS):
            self.assertEqual(score(r,n,arm,"certified"),0)

    def test_independent_fixed_policy_bayes_census(self):
        # Enumerate literal transcripts, using independent transition oracle
        # instead of integer likelihood matrices or the recursive evaluator.
        for regime in (0,1,2,None):
            models=[m for m in MODELS if regime is None or m[0]==regime]
            for n in (1,2,3):
                total=F(0)
                for transcript in product(tuple(product(range(2),repeat=2)),repeat=n):
                    target=[F(0)]*4
                    for r,t in models:
                        p=F(1,len(models))
                        obs=enumerate_channel(PULSE,r,t,"difference")
                        for o in transcript:
                            p*=obs.get(o,0)
                        target[t]+=p
                    total+=max(target)
                self.assertEqual(total,score(regime,n,"pulse_history"))

    def test_policy_value_dominance_and_equal_cost(self):
        for r,n in product((0,1,2,None),range(4)):
            for arm in ARMS:
                self.assertLessEqual(score(r,n,arm),score(r,n,"optimal_history"))
            self.assertEqual(score(r,n,"passive_history"),F(1,4))
            self.assertEqual(score(r,n,"pulse_last"),F(1,4))
            if n:
                self.assertLessEqual(score(r,n-1,"optimal_history"),score(r,n,"optimal_history"))

    def test_receipt_determinism(self):
        self.assertEqual(receipt(),receipt())


if __name__=="__main__":
    unittest.main()
