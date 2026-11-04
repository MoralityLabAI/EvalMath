"""QI-03 independent brute and exact dual-certificate tests."""
import random
import unittest
from fractions import Fraction as Q
from itertools import combinations

from spiral_ln.evaluation_quotient_fractional_cover import (
    fractional_information_cover, integral_hitting_cover,
    independent_half_grid_oracle, information_cost_lower_bound,
    bernoulli_kl, _solve_square,
)


class FractionalInformationCoverTests(unittest.TestCase):
    def test_three_way_triangle_integrality_gap(self):
        masks=(0b011,0b110,0b101)
        cert=fractional_information_cover(3,masks)
        self.assertEqual(cert["optimum"],Q(3,2))
        self.assertEqual(cert["primal"],(Q(1,2),)*3)
        self.assertEqual(cert["dual"],(Q(1,2),)*3)
        self.assertEqual(integral_hitting_cover(3,masks)[0],Q(2))
        self.assertEqual(independent_half_grid_oracle(3,masks)[0],Q(3,2))
        info=information_cost_lower_bound(3,masks,Q(1,20))
        self.assertGreater(info["expected_cost_lower"],123)
        self.assertLess(info["expected_cost_lower"],124)
        self.assertEqual(info["integer_hard_budget_floor"],124)

    def test_distinct_single_cell_alternatives_direct_sum(self):
        for n in range(1,7):
            masks=tuple(1<<i for i in range(n))
            c=fractional_information_cover(n,masks)
            self.assertEqual(c["optimum"],Q(n))
            self.assertEqual(c["primal"],(Q(1),)*n)
            self.assertEqual(c["dual"],(Q(1),)*n)
            lower=information_cost_lower_bound(n,masks,Q(1,20))
            self.assertAlmostEqual(
                lower["expected_cost_lower"],
                n * bernoulli_kl(Q(19,20),Q(1,20))
                / bernoulli_kl(Q(1,2),Q(5,8)), places=9)
        self.assertEqual(
            information_cost_lower_bound(3,(1,2,4),Q(1,20))
            ["integer_hard_budget_floor"],247)

    def test_all_127_three_cell_alternative_families(self):
        """Independent {0,1/2,1} grid gives exact vertices for 3 binary cells."""
        nonempty=tuple(range(1,8))
        count=0
        strict_gaps=0
        for family in range(1,1<<len(nonempty)):
            masks=tuple(mask for i,mask in enumerate(nonempty)
                        if family & (1<<i))
            cert=fractional_information_cover(3,masks)
            grid=independent_half_grid_oracle(3,masks)
            integral=integral_hitting_cover(3,masks)
            self.assertIsNotNone(cert)
            self.assertEqual(cert["optimum"],grid[0])
            self.assertLessEqual(cert["optimum"],integral[0])
            self.assertEqual(sum(cert["dual"],Q(0)),cert["optimum"])
            self.assertTrue(all(
                sum((cert["primal"][c] for c in range(3)
                     if mask & (1<<c)),Q(0))>=1 for mask in masks))
            self.assertTrue(all(
                sum((cert["dual"][j] for j,mask in enumerate(masks)
                     if mask & (1<<c)),Q(0))<=1 for c in range(3)))
            if cert["optimum"]<integral[0]:
                strict_gaps+=1
            count+=1
        self.assertEqual(count,127)
        self.assertGreater(strict_gaps,0)

    def test_seeded_heterogeneous_costs_and_dual_optimality(self):
        rng=random.Random(20261104)
        cases=0
        for n in (3,4,5):
            for _ in range(8):
                masks=tuple(rng.randrange(1,1<<n) for _ in range(5))
                costs=tuple(Q(rng.randrange(1,8),rng.randrange(1,5))
                            for _ in range(n))
                sol=fractional_information_cover(n,masks,costs)
                discrete=integral_hitting_cover(n,masks,costs)
                self.assertLessEqual(sol["optimum"],discrete[0])
                self.assertEqual(
                    sum((a*x for a,x in zip(costs,sol["primal"])),Q(0)),
                    sol["optimum"])
                self.assertEqual(sum(sol["dual"],Q(0)),sol["optimum"])
                for c in range(n):
                    self.assertLessEqual(
                        sum((sol["dual"][j] for j,mask in enumerate(masks)
                             if mask & (1<<c)),Q(0)),costs[c])
                cases+=1
        self.assertEqual(cases,24)

    def test_empty_and_impossible_alternative_families(self):
        empty=fractional_information_cover(3,())
        self.assertEqual(empty["optimum"],Q(0))
        self.assertEqual(empty["primal"],(Q(0),)*3)
        self.assertEqual(empty["dual"],())
        self.assertIsNone(fractional_information_cover(3,(0,2)))
        self.assertIsNone(integral_hitting_cover(3,(0,2)))
        self.assertIsNone(information_cost_lower_bound(3,(0,2),Q(1,20)))

    def test_exact_gaussian_solver(self):
        v=_solve_square(((Q(1),Q(1)),(Q(1),Q(-1))), (Q(3),Q(1)))
        self.assertEqual(v,(Q(2),Q(1)))
        self.assertIsNone(_solve_square(((Q(1),Q(1)),(Q(2),Q(2))),
                                         (Q(1),Q(2))))

    def test_invalid_contracts(self):
        bad=[
            (0,(1,),None), (7,(1,),None), (2,(-1,),None),
            (2,(4,),None), (2,(1,),(-1,1)),
            (2,(1,),(Q(0),Q(1))), (2,(1,),(Q(1),)),
            (2,tuple([1]*11),None)
        ]
        for n,masks,costs in bad:
            with self.assertRaises(ValueError):
                fractional_information_cover(n,masks,costs)
        for delta in (0,Q(1,2),1):
            with self.assertRaises(ValueError):
                information_cost_lower_bound(2,(1,),delta)
        with self.assertRaises(ValueError):
            information_cost_lower_bound(2,(1,),Q(1,20),Q(1,2),Q(1,2))
        with self.assertRaises(ValueError):
            independent_half_grid_oracle(4,(1,))


if __name__=="__main__":
    unittest.main()
