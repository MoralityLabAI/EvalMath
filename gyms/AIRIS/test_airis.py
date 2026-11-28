import unittest
from fractions import Fraction as F
from itertools import product
from airis_gym import (AFFINE, MASKS, Belief, passive_belief, roots, outcome,
                       collision, trial, random_value, POLICIES, GOALS, receipt)


class AirisTests(unittest.TestCase):
    def test_grammar_and_passive_alias(self):
        self.assertEqual(len(AFFINE), 8)
        worlds = tuple(roots())
        self.assertEqual(len(set(worlds)), 64)
        for w in worlds:
            for a, m in enumerate(MASKS):
                self.assertEqual(outcome(w, 0, a), 0)
                self.assertEqual(outcome(w, 3, a), m)
        self.assertEqual({outcome(w, 1, 1) for w in worlds}, {0,1,2,3})

    def test_observation_is_atomic(self):
        b = passive_belief()
        before = b.rules
        with self.assertRaises(ValueError):
            b.observe(1, 0, 0, 1)
        self.assertEqual(b.rules, before)

    def test_outcome_partitions_against_world_enumeration(self):
        b = passive_belief()
        worlds = tuple(roots())
        for c, a in product(range(4), range(3)):
            p = b.predict(c, a)
            self.assertEqual(sum(p.values()), 1)
            brute = {d: F(sum(outcome(w, c, a) == d for w in worlds), len(worlds))
                     for d in range(8)}
            self.assertEqual(p, {d:v for d,v in brute.items() if v})
            self.assertEqual(collision(p), F(sum(outcome(w,c,a) != outcome(v,c,a)
                                                 for w in worlds for v in worlds),
                                             len(worlds)**2))

    def test_composition_and_goal_change(self):
        b = passive_belief()
        b.observe(1, 1, 0, 1)
        b.observe(1, 0, 0, 2)
        self.assertEqual(b.plan(1, 0, 1, 1), (1,))
        self.assertEqual(b.plan(1, 0, 3, 3), (0,1))
        self.assertIsNone(b.plan(1, 0, 4, 4))

    def test_planner_against_subset_oracle(self):
        for w in roots():
            b = passive_belief()
            for a in range(3):
                b.observe(1, a, 0, outcome(w, 1, a))
            for c in range(4):
                ds = [outcome(w, c, a) for a in range(3)]
                for mask, target in (*GOALS, (7,7), (7,0)):
                    reachable = {0}
                    for d in ds:
                        reachable |= {v ^ d for v in reachable}
                    plan = b.plan(c, 0, mask, target)
                    self.assertEqual(plan is not None, any(v & mask == target for v in reachable))
                    if plan is not None:
                        self.assertLessEqual(len(plan), 3)
                        s = 0
                        for a in plan:
                            s ^= ds[a]
                        self.assertEqual(s & mask, target)

    def test_matched_budgets_and_primary_witness(self):
        worlds = tuple(roots())
        for budget, expected in ((0,(0,0)),(1,(0,32)),(2,(32,48))):
            for policy in POLICIES:
                runs = [trial(w, policy, GOALS[0], budget) for w in worlds]
                self.assertTrue(all(len(t) == budget for _,t in runs))
                self.assertEqual(sum(s for s,_ in runs), expected[policy == "goal"])
        for budget, expected in ((0,F(0)),(1,F(1,3)),(2,F(7,12))):
            total = sum(random_value(w, passive_belief(), GOALS[0], budget) for w in worlds)
            self.assertEqual(total/len(worlds), expected)

    def test_receipt_replay(self):
        r = receipt()
        self.assertEqual(r["n_roots"], 64)
        self.assertEqual(len(r["rows"]), 384)
        self.assertEqual(r["aggregates"]["1:1:budget2"]["goal"], "3/4")
        self.assertEqual(r, receipt())


if __name__ == "__main__":
    unittest.main()
