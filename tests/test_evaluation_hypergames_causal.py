"""Independent finite GF(2) checks for HG-08 causal masks and entropy bounds."""
import unittest
from fractions import Fraction as Q
from itertools import combinations, product
from math import comb, ceil, log2

from spiral_ln.evaluation_hypergames_causal import (
    parity, causal_difference, direct_difference, peel_known,
    support_certified, information_lower_bound, ideal_joint_code_success,
    forced_release_utility,
)


class CausalExactMathTests(unittest.TestCase):
    def test_finite_derivative_exhaustion(self):
        n=0
        for d in range(1,5):
            for p in range(1<<d):
                for x in range(1<<d):
                    for s in range(1<<d):
                        expected=((p&s).bit_count()&1,)
                        self.assertEqual(direct_difference((p,),x,s,d),expected)
                        self.assertEqual(causal_difference((p,),s,d),expected)
                        n+=1
        self.assertEqual(n, 8 + 64 + 512 + 4096)

    def test_multi_output_delta(self):
        d=12;goal=(0b100101,0b11100001001)
        for s in (0,1,5,13,(1<<d)-1):
            for x in (0,7,200,4095):
                self.assertEqual(causal_difference(goal,s,d),direct_difference(goal,x,s,d))

    def test_known_peel_exact(self):
        d=8; targets=(0b01011001,0b10100101)
        subset=0b11101111
        known=(frozenset([0,3]),frozenset([2,5]))
        raw=causal_difference(targets,subset,d)
        residual=peel_known(raw,subset,known,d)
        expected=causal_difference(tuple(p ^ sum(1<<i for i in k) for p,k in zip(targets,known)),subset,d)
        self.assertEqual(residual,expected)

    def test_singleton_certificate(self):
        d=10
        goals=(0b0010111,0b0111000)
        witness={i:causal_difference(goals,1<<i,d) for i in range(d)}
        self.assertEqual(tuple(sum(row[j] for row in witness.values()) for j in (0,1)),(4,3))
        self.assertFalse(support_certified(witness,d,2,4))
        self.assertTrue(support_certified({i: (int(i in {0,1,2}),int(i in {4,5,6})) for i in range(d)},d,2,3))
        with self.assertRaises(ValueError):support_certified({-1:(1,)},d,1,1)
        with self.assertRaises(ValueError):support_certified({0:(2,)},d,1,1)

    def test_information_lower_bounds(self):
        self.assertEqual([information_lower_bound(d,6) for d in (140,512,1024)], [34,45,51])
        for d in range(2,10):
            for s in range(d+1):
                target=comb(d,s)
                lb=information_lower_bound(d,s)
                self.assertGreaterEqual(1<<lb,target)
                if lb:self.assertLess(1<<(lb-1),target)
        with self.assertRaises(ValueError):information_lower_bound(10,11)

    def test_independent_posterior_fibres(self):
        # Independently partition all possible binary world states, no library ranks.
        for d in (2,3,4):
            for obs in ((1,), (1,2), (1,3), ()): 
                for tar in ((1,), (2,), (1,2), (3,)):
                    fibres={}
                    for x in range(1<<d):
                        ob=tuple((x&m).bit_count()&1 for m in obs)
                        label=tuple((x&m).bit_count()&1 for m in tar)
                        counts=fibres.setdefault(ob,{})
                        counts[label]=counts.get(label,0)+1
                    truth=Q(sum(max(counts.values()) for counts in fibres.values()),1<<d)
                    self.assertEqual(ideal_joint_code_success(obs,tar,d),truth)

    def test_abstention_threshold(self):
        self.assertEqual(forced_release_utility(Q(1,2)),Q(-5,2))
        self.assertEqual(forced_release_utility(Q(3,5)),Q(0))
        self.assertEqual(forced_release_utility(Q(1)),Q(10))
        with self.assertRaises(ValueError):forced_release_utility(.5)

    def test_fail_closed_invalid_masks(self):
        with self.assertRaises(ValueError):causal_difference((1,),-1,6)
        with self.assertRaises(ValueError):causal_difference((1,),1,0)
        with self.assertRaises(ValueError):causal_difference((64,),1,6)
        with self.assertRaises(ValueError):parity(1,64,6)
        with self.assertRaises(ValueError):peel_known((1,),1,(frozenset([-1]),),6)


if __name__ == '__main__':unittest.main()
