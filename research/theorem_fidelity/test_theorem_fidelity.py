"""Standard-library tests, no network or third-party requirements."""
import unittest
from fractions import Fraction
from theorem_fidelity import Edge, is_permutation, optimum, score, validate


class TheoremFidelityTests(unittest.TestCase):
    def test_all_six_fixtures(self):
        self.assertEqual(len(validate()), 6)

    def test_exact_fraction(self):
        eq = Edge(0, 1, ((0, 0), (1, 1)))
        ne = Edge(0, 1, ((0, 1), (1, 0)))
        self.assertEqual(optimum(2, 2, (eq, ne)), Fraction(1, 2))
        self.assertEqual(score((0, 0), (eq, ne)), Fraction(1, 2))

    def test_permutation_contract(self):
        self.assertTrue(is_permutation(((0, 1), (1, 0)), 2))
        self.assertFalse(is_permutation(((0, 0), (0, 1)), 2))

    def test_empty_edge_set(self):
        self.assertEqual(optimum(1, 2, ()), 1)


if __name__ == "__main__":
    unittest.main()
