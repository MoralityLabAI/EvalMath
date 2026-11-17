"""HG-07 exact Gaussian and information-fibre adversarial cases."""
import unittest
from fractions import Fraction as Q
from itertools import product
from spiral_ln.evaluation_hypergames_raw import (
    fit_raw_system,independent_fit_predict,identified_fraction_uniform_query,
    design_posterior_cardinality,sparse_collision_union_bound,parity_mask,
    observation_goal_floor
)
from spiral_ln.evaluation_hypergames_rank import rank


class ExactRawParityMath(unittest.TestCase):
    def test_full_rank_recovers_every_query(self):
        x=(1,2,4,7); y=tuple(parity_mask(q,5) for q in x)
        fit=fit_raw_system(x,y,3,1)
        self.assertEqual(fit.rank,3)
        self.assertEqual(tuple(fit.predict_if_identified(q) for q in range(8)),
                         tuple(parity_mask(q,5) for q in range(8)))

    def test_rank_deficient_abstains(self):
        fit=fit_raw_system((1,2),(1,0),3,1)
        self.assertEqual(fit.rank,2)
        self.assertEqual(fit.predict_if_identified(3),1)
        self.assertIsNone(fit.predict_if_identified(4))
        self.assertEqual(identified_fraction_uniform_query((1,2),3),Q(1,2))

    def test_multiple_outputs(self):
        x=(1,2,4,7)
        y=tuple(parity_mask(z,3) | (parity_mask(z,6)<<1) for z in x)
        fit=fit_raw_system(x,y,3,2)
        self.assertEqual(tuple(fit.predict_if_identified(q) for q in range(8)),
                         tuple(parity_mask(q,3)|(parity_mask(q,6)<<1) for q in range(8)))

    def test_inconsistent_rejected(self):
        with self.assertRaises(ValueError):fit_raw_system((1,1),(0,1),3,1)

    def test_bad_masks(self):
        for val in (-1,8,True):
            if val is True:
                with self.assertRaises(ValueError):fit_raw_system((val,),(1,),3,1)
            else:
                with self.assertRaises(ValueError):fit_raw_system((val,),(1,),3,1)

    def test_invalid_query(self):
        fit=fit_raw_system((1,),(0,),3,1)
        for q in (-1,8):
            with self.assertRaises(ValueError):fit.predict_if_identified(q)

    def test_posterior_size_exhaustive(self):
        for d in range(1,5):
            for x in range(1<<d):
                inputs=(x,)
                prior=design_posterior_cardinality(inputs,d)
                measured=sum(all(parity_mask(m,q)==0 for q in inputs) for m in range(1<<d))
                self.assertEqual(prior,measured)
                self.assertEqual(prior,1<<(d-rank(inputs,d)))

    def test_predictor_against_independent_enumeration(self):
        for d in range(1,5):
            for rows in product(range(1<<d),repeat=2):
                target=3&((1<<d)-1)
                labels=tuple(parity_mask(v,target) for v in rows)
                fast=fit_raw_system(rows,labels,d,1)
                check=independent_fit_predict(rows,labels,tuple(range(1<<d)),d,1)
                self.assertEqual(tuple(fast.predict_if_identified(v) for v in range(1<<d)),check)

    def test_sparse_collision_bound_beyond_grid(self):
        for d in (6,12,140,512):
            for n in (0,8,16,32,2048):
                b=sparse_collision_union_bound(d,6,n)
                self.assertGreaterEqual(b,Q(0))
                self.assertLessEqual(b,Q(1))
        self.assertEqual(sparse_collision_union_bound(6,6,0),Q(0))

    def test_sparse_collision_count_small(self):
        for n in range(1,4):
            # For a fixed nonzero parity difference on one bit, 2^n out of
            # 2^(2n) sequences are collision-compatible, exactly 2^-n.
            outcomes=list(product(range(4),repeat=n))
            collision=sum(all(parity_mask(x,1)==parity_mask(x,2) for x in row) for row in outcomes)
            self.assertEqual(Q(collision,len(outcomes)),Q(1,2**n))

    def test_observer_goal_floor(self):
        self.assertEqual(observation_goal_floor((1,),(2,),2),Q(1,2))
        self.assertEqual(observation_goal_floor((1,2),(1^2,),2),Q(1))
        self.assertEqual(observation_goal_floor((),(1,2),2),Q(1,4))

    def test_padding_and_zero(self):
        self.assertEqual(design_posterior_cardinality((),3,2),64)
        self.assertEqual(identified_fraction_uniform_query((),3),Q(1,8))
        self.assertEqual(design_posterior_cardinality((1,2,4),3,2),1)
        self.assertEqual(design_posterior_cardinality((1,2,4),1024,1),1<<1021)


if __name__=='__main__':unittest.main()
