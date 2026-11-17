"""Independent exact checks of HG04 observer quotients and audit Bellman values."""
import unittest
from fractions import Fraction as F
from itertools import product
from spiral_ln.evaluation_hypergame_quotient_math import (
    rank_gf2, uniform_parity_error, independently_enumerated_error,
    audited_release_expectation, prior_optimal_value,
)
from spiral_ln.hypergames_single_player import make_scenario, initial_state, optimal_value

class HG04ExactMath(unittest.TestCase):
    def test_rank(self):
        self.assertEqual(rank_gf2((1,3,2),3),2)
        self.assertEqual(rank_gf2((),0),0)
    def test_exhaustive_rank_fibre_oracle(self):
        for rows in ((),(0,),(1,2),(3,5),(1,2,4),(1,3,7)):
            for p in range(16):
                self.assertEqual(uniform_parity_error(rows,p,4),
                                 independently_enumerated_error(rows,p,4))
    def test_ambiguous_and_identifiable(self):
        self.assertEqual(uniform_parity_error((),1,4),F(1,2))
        self.assertEqual(uniform_parity_error((3,5),6,4),F(0))
        self.assertEqual(uniform_parity_error((1,2,4),8,4),F(1,2))
    def test_audit_threshold(self):
        self.assertEqual(audited_release_expectation(F(16,25)),F(0))
        self.assertEqual(audited_release_expectation(F(4,5)),F(4))
    def test_prior_value_against_bellman(self):
        s=make_scenario(17,140)
        for h,p in product((4,5),(F(1,2),F(3,5),F(4,5),F(24,25),F(1))):
            belief=tuple((initial_state(bit,h),mass)
                         for bit,mass in ((0,1-p),(1,p)) if mass>0)
            self.assertEqual(prior_optimal_value(p,h),optimal_value(s,belief))
    def test_reject_invalid(self):
        with self.assertRaises(ValueError):rank_gf2((-1,),4)
        with self.assertRaises(ValueError):uniform_parity_error((1,),16,4)
        with self.assertRaises(ValueError):independently_enumerated_error((1,),1,11)
        with self.assertRaises(ValueError):audited_release_expectation(F(-1,4))
        with self.assertRaises(ValueError):prior_optimal_value(F(1,2),6)

if __name__=='__main__':unittest.main()
