"""Independent finite oracles for the HG-06 compositional-goal mathematics."""
import unittest
from fractions import Fraction as Q
from itertools import combinations
from random import Random

from spiral_ln.evaluation_hypergames_composition import (
    fragment_weight_floor, exact_shortest_xor, short_fragment_certificate,
    parity_disagreement_probability, independent_parity_collision,
    spurious_fit_union_bound, exact_signed_candidates,
    posterior_joint_predictive_accuracy, certified_joint_goal_capacity)
from spiral_ln.evaluation_hypergames_rank import independent_fibre_success

class HG06ExactMath(unittest.TestCase):
    def test_six_bit_goal_requires_three_two_bit_fragments(self):
        target=(1<<6)-1
        pairs=tuple((1<<i)|(1<<j) for i,j in combinations(range(6),2))
        self.assertEqual(fragment_weight_floor(target,2),3)
        self.assertIsNone(exact_shortest_xor(target,pairs,6,2))
        self.assertIsNotNone(exact_shortest_xor(target,pairs,6,3))
        self.assertEqual(exact_shortest_xor(target,(3,12,48),6,3),(0,1,2))
    def test_exact_uniform_fibre_and_padding(self):
        rng=Random(2026111706)
        for d in range(1,7):
            for _ in range(24):
                obs=tuple(rng.randrange(1<<d) for _ in range(rng.randrange(4)))
                tgt=tuple(rng.randrange(1<<d) for _ in range(rng.randrange(4)))
                info=certified_joint_goal_capacity(obs,tgt,d)
                self.assertEqual(info['optimal_joint_success'],independent_fibre_success(obs,tgt,d))
                self.assertEqual(info['remaining_entropy_bits'],
                                 certified_joint_goal_capacity(obs,tgt,d+7)['remaining_entropy_bits'])
    def test_exact_pair_collision_small(self):
        for d in range(1,5):
            for a in range(1<<d):
                for b in range(1<<d):
                    for n in (0,1,2):
                        self.assertEqual(parity_disagreement_probability(a,b,d,n),
                                         independent_parity_collision(a,b,d,n))
    def test_random_width_obstruction(self):
        rng=Random(61218)
        for _ in range(200):
            d=6
            t=rng.randrange(1<<d)
            rows=tuple((1<<i)|(1<<j) for i,j in combinations(range(d),2))
            floor=fragment_weight_floor(t,2)
            for budget in range(floor):
                self.assertIsNone(exact_shortest_xor(t,rows,d,budget))
    def test_posterior_bayes_nonidentifiability(self):
        prior=(1,2)
        matched=exact_signed_candidates(prior,(0,),(0,),2)
        self.assertEqual(matched,((1,0),(2,0)))
        self.assertEqual(posterior_joint_predictive_accuracy(matched,2),Q(3,4))
        complete=exact_signed_candidates(prior,(),(),2)
        self.assertEqual(posterior_joint_predictive_accuracy(complete,2),Q(1,2))
    def test_bound_counts_and_zero(self):
        self.assertEqual(spurious_fit_union_bound(1,1,8),Q(1,256))
        self.assertEqual(spurious_fit_union_bound(0,8,16),Q(0))
        self.assertEqual(spurious_fit_union_bound(100,1,2),Q(1))
        self.assertEqual(spurious_fit_union_bound(5,2,64),Q(18,1<<64))
    def test_exact_empty_and_small_budget(self):
        self.assertEqual(fragment_weight_floor(0,2),0)
        self.assertEqual(exact_shortest_xor(0,(),4,0),())
        self.assertEqual(short_fragment_certificate(63,(3,12,48),6,2)['witness'],None)
    def test_fail_closed(self):
        with self.assertRaises(ValueError): fragment_weight_floor(1,0)
        with self.assertRaises(ValueError): exact_shortest_xor(256,(1,),6)
        with self.assertRaises(ValueError): parity_disagreement_probability(1,2,3,-1)
        with self.assertRaises(ValueError): spurious_fit_union_bound(-1,1,8)
        with self.assertRaises(ValueError): exact_signed_candidates((1,1),(0,),(0,),3)
        with self.assertRaises(ValueError): posterior_joint_predictive_accuracy((),3)

if __name__=='__main__': unittest.main()
