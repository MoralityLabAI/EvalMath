"""QI-02 finite adaptive-experiment information inequality checks."""
import unittest
from fractions import Fraction as Q
from itertools import product
from math import isclose

from spiral_ln.evaluation_quotient_information_budget import (
    bernoulli_kl, binary_event_kl, expected_diagnostic_cell_lower_bound,
    expected_probe_integer_floor, paired_adaptive_transcript,
    event_probability_by_world, exact_transcript_total_variation,
    pinsker_transcript_upper,
)


class QuotientInformationTests(unittest.TestCase):
    def test_known_one_cell_minimum_expected_samples(self):
        result = expected_diagnostic_cell_lower_bound(Q(1,2),Q(5,8),Q(1,20))
        self.assertGreater(result, 82)
        self.assertLess(result, 83)
        self.assertEqual(expected_probe_integer_floor(Q(1,2),Q(5,8),Q(1,20)),
                         83)
        for delta in (Q(1,10), Q(1,20), Q(1,100)):
            bound=expected_diagnostic_cell_lower_bound(Q(1,2),Q(5,8),delta)
            self.assertGreater(bound, 0)
        self.assertGreater(
            expected_diagnostic_cell_lower_bound(Q(1,2),Q(9,16),Q(1,20)),
            result)

    def test_fixed_query_chain_rule_at_many_horizons(self):
        for horizon in range(8):
            for action in (0, 1, 2):
                model0=(Q(1,2),Q(1,3),Q(3,4))
                model1=(Q(5,8),Q(1,3),Q(2,3))
                policy=lambda hist,a=action: a
                result=paired_adaptive_transcript(model0,model1,policy,horizon)
                self.assertAlmostEqual(result["transcript_KL"],
                                       horizon*bernoulli_kl(model0[action],model1[action]),
                                       places=11)
                self.assertAlmostEqual(result["KL_chain_rule_residual"],0,
                                       places=11)
                self.assertEqual(sum(result["expected_cell_queries_under_world0"]),horizon)
                self.assertLessEqual(exact_transcript_total_variation(result),
                                     pinsker_transcript_upper(result)+1e-12)

    def test_adaptive_early_stopping_chain_rule(self):
        p=(Q(1,2),Q(1,3),Q(3,4))
        q=(Q(5,8),Q(1,3),Q(2,3))
        def policy(history):
            if not history:
                return 0
            if len(history) == 1:
                return 1 if history[-1][1] else 0
            if history[-1][1] and len(history) >= 2:
                return None
            return 2 if len(history) % 2 == 0 else 0
        for n in range(1,7):
            result=paired_adaptive_transcript(p,q,policy,n)
            self.assertAlmostEqual(result["KL_chain_rule_residual"],0,
                                   places=11)
            self.assertLessEqual(sum(result["expected_cell_queries_under_world0"]),n)
            self.assertLessEqual(exact_transcript_total_variation(result),
                                 pinsker_transcript_upper(result)+1e-12)
            event=lambda hist: any(bit for cell,bit in hist)
            prob0,prob1=event_probability_by_world(result,event)
            self.assertLessEqual(
                binary_event_kl(prob0,prob1),
                result["transcript_KL"]+1e-12)
            self.assertGreaterEqual(prob0,0)
            self.assertLessEqual(prob1,1)

    def test_public_decision_event_data_processing(self):
        def policy(history):
            if len(history) < 2:
                return len(history)
            return 1 if history[-1][1] else 0
        result=paired_adaptive_transcript(
            (Q(1,2),Q(1,2)),
            (Q(1,2),Q(5,8)),
            policy,4)
        for decision in (
            lambda hist: sum(o for c,o in hist)>=2,
            lambda hist: hist[-1][1]==1,
            lambda hist: all(o==0 for c,o in hist),
        ):
            probability0,probability1=event_probability_by_world(result,decision)
            self.assertLessEqual(binary_event_kl(probability0,probability1),
                                 result["transcript_KL"]+1e-12)

    def test_expected_probe_lower_bound_is_necessary_for_low_error(self):
        # At 10 probes the transcript distributions are far too close to
        # allow both false-positive and false-negative risks <= 0.05.
        result=paired_adaptive_transcript(
            (Q(1,2),Q(1,3)),
            (Q(5,8),Q(1,3)),
            lambda history: 0,10)
        delta=.05
        self.assertLess(result["transcript_KL"],
                        binary_event_kl(1-delta,delta))
        self.assertLess(exact_transcript_total_variation(result),1-2*delta)

    def test_zero_information_from_common_probe(self):
        result=paired_adaptive_transcript(
            (Q(1,2),Q(1,3)),(Q(5,8),Q(1,3)),
            lambda h: 1,6)
        self.assertAlmostEqual(result["transcript_KL"],0,places=14)
        self.assertAlmostEqual(exact_transcript_total_variation(result),0,
                               places=14)
        self.assertEqual(result["expected_cell_queries_under_world0"],
                         (Q(0),Q(6)))

    def test_boundary_kl_and_invalid_contracts(self):
        self.assertEqual(bernoulli_kl(Q(1,2),Q(1,2)),0)
        self.assertEqual(bernoulli_kl(Q(1),Q(0)),float("inf"))
        self.assertEqual(bernoulli_kl(Q(0),Q(1,2)),
                         -__import__("math").log(Q(1,2)))
        for p,q in ((-0.1,0.1),(0.1,1.1)):
            with self.assertRaises(ValueError):
                bernoulli_kl(p,q)
        for delta in (0, .5, 1):
            with self.assertRaises(ValueError):
                expected_diagnostic_cell_lower_bound(Q(1,2),Q(5,8),delta)
        with self.assertRaises(ValueError):
            paired_adaptive_transcript((),(),lambda h:0,2)
        with self.assertRaises(ValueError):
            paired_adaptive_transcript((Q(0),),(Q(1,2),),lambda h:0,2)
        with self.assertRaises(ValueError):
            paired_adaptive_transcript((Q(1,2),),(Q(1,3),),lambda h:2,2)
        with self.assertRaises(ValueError):
            paired_adaptive_transcript((Q(1,2),),(Q(1,3),),lambda h:0,-1)


if __name__=="__main__":
    unittest.main()
