"""Exact-rational NW01 paired truth observability and sham gate tests."""
from __future__ import annotations
import unittest
from fractions import Fraction
from itertools import product

from spiral_ln import evaluation_nw01_paired_information as e


class PairedInformationTests(unittest.TestCase):
    def roots(self):
        return tuple(e.PairedWorld(str(i),(1,i%3,(i//3)%2),(-2,-1,1,2)[i%4])
                     for i in range(64))

    def test_exact_equal_prior_brier_identity(self):
        for num in range(101):
            p=Fraction(num,100)
            self.assertEqual(e.exact_brier_excess(p),
                             (p-Fraction(1,2))**2)
            self.assertGreaterEqual(e.brier_on_pair(p),Fraction(1,4))
        self.assertEqual(e.brier_on_pair(Fraction(1,2)),Fraction(1,4))
        self.assertEqual(e.brier_on_pair(Fraction(0)),Fraction(1,2))
        self.assertEqual(e.brier_on_pair(Fraction(1)),Fraction(1,2))

    def test_exact_64_source_brier_and_public_accuracy(self):
        probs=[Fraction((i*7)%100,100) for i in range(64)]
        result=e.equal_prior_public_only_summary(probs)
        self.assertEqual(result["source_pairs"],64)
        self.assertEqual(result["world_cases"],128)
        self.assertEqual(result["exact_argmax_accuracy"],Fraction(1,2))
        self.assertEqual(result["mean_brier"],
                         Fraction(1,4)+result["mean_brier_excess"])
        self.assertGreaterEqual(result["mean_brier"],Fraction(1,4))
        self.assertEqual(e.balanced_pair_predictions([i%2 for i in range(64)]),
                         Fraction(1,2))

    def test_any_binary_public_labeling_has_exact_half_accuracy(self):
        for bits in product((0,1),repeat=10):
            self.assertEqual(e.balanced_pair_predictions(bits),Fraction(1,2))

    def test_witness_reveals_label_and_sham_is_paired_null(self):
        roots=self.roots()
        self.assertEqual(e.witness_classification_responses(roots),1)
        for sham in ([0]*64, [1]*64, [(-2,-1,0,1,2)[i%5] for i in range(64)]):
            self.assertEqual(e.source_matched_sham_accuracy(roots,sham),
                             Fraction(1,2))
        for root in roots:
            self.assertEqual(e.hypothetical_true_witness(root,0),0)
            self.assertNotEqual(e.hypothetical_true_witness(root,1),0)

    def test_public_only_recurrence_cannot_gain_hidden_world_information(self):
        roots=self.roots()
        for depth in (0,1,2,4,8,16):
            result=e.finite_world_check(roots,depth)
            self.assertEqual(result["public_only_accuracy"],"1/2")
            self.assertEqual(result["source_matched_sham_accuracy"],"1/2")
            self.assertEqual(result["hypothetical_true_witness_accuracy"],"1")
            self.assertEqual(result["public_recurrent_depth"],depth)

    def test_malformed_sources_rejected(self):
        with self.assertRaises(ValueError):
            e.validate([])
        with self.assertRaises(ValueError):
            e.validate([e.PairedWorld("x",(1,),1),
                        e.PairedWorld("x",(1,),-1)])
        with self.assertRaises(ValueError):
            e.validate([e.PairedWorld("x",(1,),0)])
        with self.assertRaises(ValueError):
            e.equal_prior_public_only_summary([Fraction(3,2)])
        with self.assertRaises(ValueError):
            e.source_matched_sham_accuracy(self.roots(),[0])
        with self.assertRaises(ValueError):
            e.balanced_pair_predictions([2])


if __name__=="__main__":
    unittest.main()
