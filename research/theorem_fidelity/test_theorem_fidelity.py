import unittest
from fractions import Fraction
from theorem_fidelity import (Edge, exp_polynomial_certificate, is_f2_translation,
                              optimum, permutation, satisfiable_3cnf,
                              score, simple_bipartite, validate)


class TheoremFidelityTests(unittest.TestCase):
    def test_all_cases(self):
        self.assertEqual(len(validate()), 6)

    def test_empty_game_rejected(self):
        with self.assertRaises(ValueError):
            optimum(2, 2, ())
        with self.assertRaises(ValueError):
            score((0, 0), ())

    def test_finite_witness_and_satisfiability(self):
        eq = Edge(0, 1, ((0, 0), (1, 1)))
        flip = Edge(0, 1, ((0, 1), (1, 0)))
        self.assertEqual(optimum(2, 2, (eq, flip)), Fraction(1, 2))
        self.assertFalse(simple_bipartite(2, (eq, flip)))
        self.assertTrue(satisfiable_3cnf(1, ((1, 1, 1),)))
        self.assertFalse(satisfiable_3cnf(1, ((1, 1, 1), (-1, -1, -1))))

    def test_nonpermutation_not_translation(self):
        self.assertFalse(permutation(((0, 0), (0, 1)), 2))
        self.assertTrue(is_f2_translation(((0, 1), (1, 0))))
        self.assertFalse(is_f2_translation(((0, 0), (0, 1), (1, 0), (1, 1))))

    def test_symbolic_exponential_bound(self):
        for c in (1, 2, 5):
            for d in (0, 1, 2, 3):
                proof = exp_polynomial_certificate(c, d)
                n = proof["n"]
                self.assertGreater(2 ** n, c * (n ** d))
        with self.assertRaises(ValueError):
            exp_polynomial_certificate(0, 3)


if __name__ == "__main__":
    unittest.main()
