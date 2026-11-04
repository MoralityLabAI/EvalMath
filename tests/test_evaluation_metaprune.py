import unittest
from fractions import Fraction
from spiral_ln.evaluation_metaprune import (
    four_state_examples, optimal_choice, predict_and_update, terminal_value,
)

class MetaPruneTests(unittest.TestCase):
    def test_bayesian_updates_normalize(self):
        prior, experiments = four_state_examples()
        for _, _, likelihood in experiments:
            observations = list(predict_and_update(prior, likelihood))
            self.assertEqual(sum(o[1] for o in observations), 1)
            self.assertTrue(all(sum(posterior) == 1 for _, _, posterior in observations))

    def test_exact_information_vs_decision_value(self):
        prior, experiments = four_state_examples()
        split = sum((mass * terminal_value(post) for _, mass, post in
                     predict_and_update(prior, experiments[0][2])), Fraction(0))
        reveal = sum((mass * terminal_value(post) for _, mass, post in
                      predict_and_update(prior, experiments[1][2])), Fraction(0))
        self.assertEqual(split, Fraction(1, 2))
        self.assertEqual(reveal, Fraction(11, 20))
        self.assertEqual(optimal_choice(prior, experiments, 0), (Fraction(1, 4), "stop"))
        self.assertEqual(optimal_choice(prior, experiments, 1), (Fraction(11, 20), "reveal"))

    def test_cost_can_justify_stopping(self):
        prior, experiments = four_state_examples()
        self.assertEqual(optimal_choice(prior, experiments, 1, Fraction(1, 3)),
                         (Fraction(1, 4), "stop"))

    def test_expected_information_cannot_hurt_free_classification(self):
        prior, experiments = four_state_examples()
        for _, _, likelihood in experiments:
            expected = sum((mass * terminal_value(post) for _, mass, post
                            in predict_and_update(prior, likelihood)), Fraction(0))
            self.assertGreaterEqual(expected, terminal_value(prior))

if __name__ == "__main__":
    unittest.main()
