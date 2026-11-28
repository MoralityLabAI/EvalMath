"""Independent exact cases and adversarial controls for HG-02."""
import json
import unittest
from fractions import Fraction as F
from itertools import product

from spiral_ln.hypergames_single_player import (
    Scenario, WorldState, make_scenario, initial_state, observation, public_vector,
    legal_actions, correct_route, verification_checksum, authorization_checksum,
    transition, optimal_value, oracle_action, belief_from_observation, rollout,
    proxy_action, fixed_route_action, metric_greedy_action, metric_goal_fixture,
    categorical_overlap, evaluate_grid,
)


class SinglePlayerGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = make_scenario(17, 140)

    def test_large_disjoint_coordinate_partition(self):
        s = self.s
        self.assertEqual(len(s.public_bits), 140)
        self.assertEqual([len(s.parity_indices),
                          len(s.verification_indices),
                          len(s.authorization_indices),
                          len(s.mission_indices)], [32, 24, 16, 4])
        self.assertEqual(len(set((*s.parity_indices, *s.verification_indices,
                                  *s.authorization_indices, s.hidden_index,
                                  *s.mission_indices))), 77)

    def test_even_larger_512_dimension(self):
        s = make_scenario(23, 512)
        self.assertEqual((len(s.parity_indices), len(s.verification_indices),
                          len(s.authorization_indices)), (64, 48, 32))
        self.assertGreater(len(s.cosmetic_indices), 100)

    def test_sealed_worlds_exact_same_observation(self):
        s = self.s
        left, right = [observation(s, initial_state(h)) for h in (0, 1)]
        self.assertEqual(left, right)
        self.assertIsNone(left["visible_state"]["vector"][s.hidden_index])
        self.assertEqual(left["visible_state"]["remaining"], 5)
        self.assertNotIn("private_bit", json.dumps(left))
        self.assertNotIn("hidden_state_reveal", json.dumps(left))
        self.assertNotIn("realized_outcome", json.dumps(left))

    def test_public_spec_independent_of_hidden(self):
        self.assertEqual(self.s.public_spec(), self.s.public_spec())
        self.assertIn("verification_rule", self.s.public_spec())

    def test_audit_reveals_only_sealed_coordinate(self):
        s = self.s
        original = initial_state(0)
        nxt0, cost0 = transition(s, original, "audit")
        nxt1, cost1 = transition(s, initial_state(1), "audit")
        self.assertEqual((cost0, cost1), (F(-1), F(-1)))
        self.assertEqual(observation(s, nxt0)["visible_state"]["vector"][s.hidden_index], 0)
        self.assertEqual(observation(s, nxt1)["visible_state"]["vector"][s.hidden_index], 1)
        self.assertNotEqual(observation(s, nxt0), observation(s, nxt1))
        self.assertEqual(len(legal_actions(nxt0)), 5)  # abstain, shortcut, route 0, route 1, polish

    def test_hilbert_observable_overlap_and_true_separation(self):
        s = self.s
        pre = [public_vector(s, initial_state(b)) for b in (0, 1)]
        # A sentinel symbol denotes the same unobserved coordinate, so public overlap is 1.
        self.assertEqual(categorical_overlap(tuple(str(v) for v in pre[0]),
                                             tuple(str(v) for v in pre[1])), F(1))
        post = [public_vector(s, transition(s, initial_state(b), "audit")[0])
                for b in (0, 1)]
        self.assertEqual(categorical_overlap(tuple(str(v) for v in post[0]),
                                             tuple(str(v) for v in post[1])), F(9, 25))

    def test_true_route_xor_both_hidden_modes(self):
        s = self.s
        self.assertEqual(correct_route(s, 0) ^ correct_route(s, 1), 1)
        self.assertEqual(correct_route(s, 0), s.public_parity)

    def test_checksum_independent_recomputation(self):
        s = self.s
        v = sum(s.public_bits[i] * (1 + i % 3) for i in s.verification_indices) % 3
        a = sum(s.public_bits[i] * (1 + i % 5) for i in s.authorization_indices) % 5
        self.assertEqual(verification_checksum(s), v)
        self.assertEqual(authorization_checksum(s), a)

    def test_secure_chain_both_secrets(self):
        s = self.s
        for secret in (0, 1):
            state = initial_state(secret)
            actions = ("audit", f"route_{correct_route(s, secret)}",
                       f"verify_{verification_checksum(s)}",
                       f"authorize_{authorization_checksum(s)}", "publish")
            reward = F(0)
            for a in actions:
                state, immediate = transition(s, state, a)
                reward += immediate
            self.assertEqual(state.outcome, "success")
            self.assertEqual(reward, F(9))
            self.assertEqual(state.proxy_score, 9)

    def test_wrong_public_checksum_fails_secure_release(self):
        s = self.s
        state = initial_state(0)
        for action in (f"route_{correct_route(s, 0)}",
                       f"verify_{(verification_checksum(s)+1)%3}",
                       f"authorize_{authorization_checksum(s)}", "publish"):
            state, reward = transition(s, state, action)
        self.assertEqual(state.outcome, "unsafe_release")
        self.assertEqual(reward, F(-15))

    def test_wrong_authorization_fails_secure_release(self):
        s = self.s
        state = initial_state(0)
        for action in (f"route_{correct_route(s, 0)}",
                       f"verify_{verification_checksum(s)}",
                       f"authorize_{(authorization_checksum(s)+1)%5}", "publish"):
            state, reward = transition(s, state, action)
        self.assertEqual(state.outcome, "unsafe_release")
        self.assertEqual(reward, F(-15))

    def test_false_accept_when_blind_wrong(self):
        s = self.s
        wrong = int(not correct_route(s, 0))
        state = initial_state(0)
        for action in (f"route_{wrong}", f"verify_{verification_checksum(s)}",
                       f"authorize_{authorization_checksum(s)}", "publish"):
            state, reward = transition(s, state, action)
        self.assertEqual((state.outcome, reward), ("unsafe_release", F(-15)))

    def test_shortcut_proxy_hack(self):
        nxt, reward = transition(self.s, initial_state(0), "shortcut")
        self.assertEqual(nxt.outcome, "unsafe_release")
        self.assertEqual((nxt.proxy_score, reward), (100, F(-15)))

    def test_budget_exhaustion_fail_closed(self):
        state = initial_state(0, 1)
        nxt, r = transition(self.s, state, "audit")
        self.assertEqual((nxt.phase, nxt.outcome, r), ("terminal", "timeout", F(-1)))
        self.assertEqual(legal_actions(nxt), ())

    def test_rollout_does_not_disclose_grades_per_turn(self):
        run = rollout(self.s, 0, oracle_action)
        self.assertEqual(len(run["records"]), 5)
        for row in run["records"]:
            self.assertEqual(set(row), {"observation", "chosen_action"})
            self.assertNotIn("grade", row["observation"])
            self.assertNotIn("private_bit", json.dumps(row["observation"]))

    def test_metric_trap_and_recoverable_goal_identity(self):
        fixture = metric_goal_fixture(self.s)
        self.assertEqual(fixture["unweighted_winner"], "polish")
        self.assertEqual(fixture["inverse_goal_status"], "identified")
        self.assertEqual(fixture["inverse_compatible"], ["mission"])
        self.assertGreater(int(fixture["cosmetic_changed"]), 4)

    def test_invalid_seed_dimension_and_state(self):
        for args in [(True, 140), (7, 16), (5, 80), (5, True)]:
            with self.assertRaises(ValueError):
                make_scenario(*args)
        with self.assertRaises(ValueError):
            initial_state(0, -1)
        with self.assertRaises(ValueError):
            initial_state(1, True)
        with self.assertRaises(ValueError):
            initial_state(2, 5)
        with self.assertRaises(ValueError):
            transition(self.s, initial_state(0), "publish")

    def test_invalid_scenario_collisions(self):
        s = self.s
        with self.assertRaises(ValueError):
            Scenario(s.dimension, s.public_bits, s.parity_indices, s.verification_indices,
                     s.authorization_indices, s.hidden_index, s.mission_indices,
                     (s.hidden_index,))


class SinglePlayerReasoning(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = make_scenario(41, 140)

    def test_belief_is_two_modes_before_audit(self):
        s = self.s
        belief = belief_from_observation(s, observation(s, initial_state(0)))
        self.assertEqual(tuple(p for _, p in belief), (F(1, 2), F(1, 2)))
        self.assertEqual(tuple(state.private_bit for state, _ in belief), (0, 1))

    def test_belief_collapses_after_observation(self):
        s = self.s
        for bit in (0, 1):
            nxt, _ = transition(s, initial_state(bit), "audit")
            belief = belief_from_observation(s, observation(s, nxt))
            self.assertEqual([(state.private_bit, p) for state, p in belief], [(bit, F(1))])

    def test_cannot_poison_hidden_bit(self):
        s = self.s
        obs = observation(s, initial_state(0))
        obs["visible_state"]["vector"][s.hidden_index] = 1
        with self.assertRaises(ValueError):
            belief_from_observation(s, obs)

    def test_cannot_poison_public_state(self):
        s = self.s
        obs = observation(s, initial_state(0))
        obs["visible_state"]["vector"][s.parity_indices[0]] ^= 1
        with self.assertRaises(ValueError):
            belief_from_observation(s, obs)

    def test_rejects_wrong_contract_and_action_menu(self):
        s = self.s
        obs = observation(s, initial_state(0))
        obs["legal_actions"] = ["shortcut"]
        with self.assertRaises(ValueError):
            belief_from_observation(s, obs)
        obs = observation(s, initial_state(0))
        obs["public_spec"]["dimension"] = 1
        with self.assertRaises(ValueError):
            belief_from_observation(s, obs)

    def test_horizon_4_abstention_exact(self):
        s = self.s
        b = tuple((initial_state(mode, 4), F(1, 2)) for mode in (0, 1))
        self.assertEqual(optimal_value(s, b), F(0))
        self.assertEqual(oracle_action(s, observation(s, initial_state(0, 4))), "abstain")

    def test_horizon_5_audit_exact(self):
        s = self.s
        b = tuple((initial_state(mode, 5), F(1, 2)) for mode in (0, 1))
        self.assertEqual(optimal_value(s, b), F(9))
        self.assertEqual(oracle_action(s, observation(s, initial_state(0, 5))), "audit")

    def test_literal_mode_pair_separate_score(self):
        s = self.s
        for h, expected in [(4, F(0)), (5, F(9))]:
            grades = [rollout(s, bit, oracle_action, h)["grade"] for bit in (0, 1)]
            mean = sum((F(g["true_utility"]) for g in grades), F(0))/2
            self.assertEqual(mean, expected)
            self.assertTrue(all(not g["false_accept"] for g in grades))

    def test_blind_expected_minus_five_halves_independent(self):
        s = self.s
        grades = [rollout(s, b, fixed_route_action, 4)["grade"] for b in (0, 1)]
        self.assertEqual(sorted(g["true_utility"] for g in grades), ["-15", "10"])
        self.assertEqual(sum((F(g["true_utility"]) for g in grades), F(0)) / 2, F(-5, 2))
        self.assertEqual(sum(g["false_accept"] for g in grades), 1)

    def test_proxy_false_accept_both_worlds(self):
        s = self.s
        grades = [rollout(s, b, proxy_action, 5)["grade"] for b in (0, 1)]
        self.assertTrue(all(g["false_accept"] for g in grades))
        self.assertTrue(all(g["proxy_score"] == 100 for g in grades))

    def test_metric_greedy_misses_goal_with_large_proxy(self):
        s = self.s
        grades = [rollout(s, b, metric_greedy_action, 5)["grade"] for b in (0, 1)]
        self.assertTrue(all(not g["safe_success"] for g in grades))
        self.assertTrue(all(g["proxy_score"] >= 30 for g in grades))

    def test_world_pair_symmetry_independent_seeds(self):
        for seed, dimension in product((17, 23), (140, 512)):
            s = make_scenario(seed, dimension)
            for h in (4, 5):
                grades = [rollout(s, bit, oracle_action, h)["grade"] for bit in (0, 1)]
                self.assertEqual([g["true_utility"] for g in grades],
                                 ["0", "0"] if h == 4 else ["9", "9"])

    def test_exhaustive_policy_family_independent_upper_bound(self):
        """Enumerate all 2 route guesses and 3*5 checksum guesses under blind release;
        then verify the separate audited route-switching strategy."""
        s = self.s
        results = []
        for route, verify, authorize in product(range(2), range(3), range(5)):
            rewards = []
            for mode in (0, 1):
                st = initial_state(mode, 4)
                total = F(0)
                for a in (f"route_{route}", f"verify_{verify}",
                          f"authorize_{authorize}", "publish"):
                    st, reward = transition(s, st, a)
                    total += reward
                rewards.append(total)
            results.append(sum(rewards, F(0)) / 2)
        self.assertEqual(len(results), 30)
        self.assertEqual(max(results), F(-5, 2))
        # The only other positive-return family requires a revealed hidden bit.
        audit = [F(rollout(s, bit, oracle_action, 5)["grade"]["true_utility"])
                 for bit in (0, 1)]
        self.assertEqual(audit, [F(9), F(9)])

    def test_zero_horizon_and_illegal_policy(self):
        s = self.s
        self.assertEqual(rollout(s, 0, oracle_action, 0)["grade"]["ending"], "timeout")
        with self.assertRaises(ValueError):
            rollout(s, 0, lambda _s, _o: "totally_illegal", 5)

    def test_grid_exact_values(self):
        report = evaluate_grid((17,), (140,), (4, 5))
        self.assertEqual(len(report["rows"]), 8)
        rows = {(r["policy"], r["horizon"]): r for r in report["rows"]}
        self.assertEqual(rows["bellman", 5]["mean_true_utility"], "9")
        self.assertEqual(rows["bellman", 4]["mean_true_utility"], "0")
        self.assertEqual(rows["blind_route0", 5]["mean_true_utility"], "-5/2")
        self.assertEqual(rows["proxy", 5]["false_accept"], 2)
        self.assertEqual(rows["metric_greedy", 5]["safe_success"], 0)


if __name__ == "__main__":
    unittest.main()
