import unittest
from fractions import Fraction as Q
from itertools import product

from spiral_ln.evaluation_active_quotient_identification import (
    exact_transient_classes, decision_tree, evaluate_decision_tree,
    under_budget, single_flip_worlds, first_row_support_worlds,
    stochastic_reset_trace_probability,
)
from spiral_ln.evaluation_metaprune_cover import (
    min_cover_dp, min_cover_bruteforce, adaptive_minimax_depth,
)


class QuotientIdentityDecisionTests(unittest.TestCase):
    def test_single_flip_all_cells_must_be_probed_on_baseline(self):
        for d in range(1, 6):
            worlds = single_flip_worlds(d)
            self.assertEqual(exact_transient_classes(worlds[0]), 1)
            self.assertTrue(all(exact_transient_classes(w)==2 for w in worlds[1:]))
            depth, tree = decision_tree(worlds, 1)
            self.assertEqual(depth, 2*d)
            self.assertEqual(evaluate_decision_tree(tree, worlds[0]), (True, 2*d))
            for world in worlds[1:]:
                result, used = evaluate_decision_tree(tree, world)
                self.assertFalse(result)
                self.assertLessEqual(used, depth)
            self.assertFalse(under_budget(worlds,1,2*d-1))
            self.assertTrue(under_budget(worlds,1,2*d))
            self.assertEqual(decision_tree(worlds,2)[0],0)

    def test_set_cover_bridge_for_every_three_action_alternative_family(self):
        """127 nonempty collections of the 7 possible nonzero rate patterns."""
        count = 0
        supports = tuple(range(1,8))
        for family in product((False,True), repeat=len(supports)):
            masks = tuple(s for s,take in zip(supports,family) if take)
            if not masks:
                continue
            worlds = first_row_support_worlds(3,masks)
            minimum = min_cover_dp(
                len(masks),tuple(
                    sum(1<<i for i,m in enumerate(masks) if m & (1<<a))
                    for a in range(3)))
            direct = min_cover_bruteforce(
                len(masks),tuple(
                    sum(1<<i for i,m in enumerate(masks) if m & (1<<a))
                    for a in range(3)))
            self.assertIsNotNone(minimum)
            depth, tree=decision_tree(worlds,1)
            self.assertEqual(depth,len(minimum))
            self.assertEqual(len(minimum),len(direct))
            for world in worlds:
                got,used=evaluate_decision_tree(tree,world)
                self.assertEqual(got,exact_transient_classes(world)<=1)
                self.assertLessEqual(used,depth)
            count+=1
        self.assertEqual(count,127)

    def test_limited_actions_can_make_exact_status_unidentifiable(self):
        worlds=(((0,0),(0,0)),((0,0),(0,1)))
        self.assertIsNone(decision_tree(worlds,1,probes=((0,0),(0,1))))
        self.assertEqual(decision_tree(worlds,1,probes=((1,1),))[0],1)
        self.assertFalse(under_budget(worlds,1,100,probes=((0,0),)))

    def test_no_test_needed_for_constant_property(self):
        worlds=single_flip_worlds(4)
        depth,tree=decision_tree(worlds,2)
        self.assertEqual(depth,0)
        self.assertEqual(tree,("answer",True))
        self.assertEqual(evaluate_decision_tree(tree,worlds[0]),(True,0))

    def test_zero_error_noisy_identification_impossible_at_finite_horizon(self):
        """All finite addressed Bernoulli transcripts overlap in support."""
        base=((Q(1,2),),(Q(1,2),))
        alternative=((Q(1,2),),(Q(5,8),))
        self.assertEqual(len(set(base)),1)
        self.assertEqual(len(set(alternative)),2)
        cases=0
        for T in range(0,6):
            for actions in product((0,1),repeat=T):
                probes=tuple((i,0) for i in actions)
                for outputs in product((0,1),repeat=T):
                    p0=stochastic_reset_trace_probability(base,probes,outputs)
                    p1=stochastic_reset_trace_probability(alternative,probes,outputs)
                    self.assertGreater(p0,0)
                    self.assertGreater(p1,0)
                    cases+=1
        self.assertEqual(cases,sum(4**t for t in range(6)))

    def test_invalid_contracts(self):
        with self.assertRaises(ValueError):
            single_flip_worlds(0)
        with self.assertRaises(ValueError):
            first_row_support_worlds(3,(0,))
        with self.assertRaises(ValueError):
            decision_tree((),1)
        with self.assertRaises(ValueError):
            decision_tree(single_flip_worlds(2),0)
        with self.assertRaises(ValueError):
            decision_tree(single_flip_worlds(2),1,probes=((5,0),))
        with self.assertRaises(ValueError):
            under_budget(single_flip_worlds(2),1,-1)
        with self.assertRaises(ValueError):
            stochastic_reset_trace_probability(((Q(1,2),),),
                                              ((0,0),),(2,))


if __name__=="__main__":
    unittest.main()
