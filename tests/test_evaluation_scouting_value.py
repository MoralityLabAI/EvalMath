"""SCOUT-01 finite Bellman, provenance, weak-policy and custody checks."""
from __future__ import annotations

import unittest
from dataclasses import replace
from fractions import Fraction as F
from itertools import product

from spiral_ln import evaluation_scouting_value as s


class ScoutingValueTests(unittest.TestCase):
    def by_name(self, root, name):
        return next(w for w in s.development_cases() if w.root_id == root and w.case_id == name)

    def test_cost_boundary_and_ties(self):
        cheap = self.by_name("scout-cost-001", "cheap")
        self.assertEqual(s.values(cheap), {s.LEFT: F(1, 2), s.RIGHT: F(1, 2), s.SCOUT: F(7, 10)})
        self.assertEqual(s.information_value(cheap), F(3, 10))
        self.assertEqual(s.optimal_actions(cheap), (s.SCOUT,))
        self.assertEqual(s.optimal_actions(self.by_name("scout-cost-001", "break_even")), s.ACTIONS)
        expensive = self.by_name("scout-cost-001", "expensive")
        self.assertEqual(s.optimal_actions(expensive), (s.LEFT, s.RIGHT))
        self.assertEqual(s.regret(expensive, s.SCOUT), F(1, 10))

    def test_relay_collapse_and_independent_witness_flip(self):
        repeated = self.by_name("provenance-003", "shared_relays")
        separate = self.by_name("provenance-003", "independent_witnesses")
        self.assertEqual(s.posterior_right(repeated), F(2, 5))
        self.assertEqual(s.posterior_right(separate), F(8, 35))
        self.assertEqual(s.posterior_right(repeated, count_relays=True), F(8, 35))
        self.assertEqual(s.optimal_actions(repeated), (s.SCOUT,))
        self.assertEqual(s.optimal_actions(separate), (s.LEFT,))
        self.assertEqual(s.policy_action(repeated, "double_count_relays"), s.LEFT)
        self.assertEqual(s.regret(repeated, s.LEFT), F(1, 10))
        self.assertEqual(s.regret(separate, s.SCOUT), F(1, 14))

    def test_cosmetic_sham_invariance(self):
        for root, a, b in (("cue-trap-002", "cue_conflict", "cosmetic_cue"),
                           ("provenance-003", "shared_relays", "cosmetic_cue")):
            x, y = self.by_name(root, a), self.by_name(root, b)
            self.assertNotEqual(x.cue_favors_right, y.cue_favors_right)
            self.assertEqual(s.values(x), s.values(y))
            self.assertEqual(s.optimal_actions(x), s.optimal_actions(y))
        cue = self.by_name("cue-trap-002", "cue_conflict")
        self.assertEqual(s.optimal_actions(cue), (s.RIGHT,))
        self.assertEqual(s.regret(cue, s.policy_action(cue, "cue_following")), F(3, 5))

    def test_information_access_and_signal_quality(self):
        no_access = self.by_name("access-004", "scout_unavailable")
        self.assertNotIn(s.SCOUT, s.values(no_access))
        self.assertEqual(s.information_value(no_access), 0)
        with self.assertRaises(ValueError):
            s.realized_reward(no_access, s.SCOUT, False, False)
        no_info = self.by_name("signal-quality-005", "uninformative_scout")
        self.assertEqual(s.information_value(no_info), 0)
        self.assertEqual(s.values(no_info)[s.SCOUT], F(2, 5))

    def test_bellman_independently_equals_latent_signal_enumeration(self):
        for prior, accuracy, cost, signal, report_reliability in product(
                (F(0), F(1, 4), F(1, 2), F(4, 5), F(1)),
                (F(1, 2), F(3, 5), F(4, 5), F(1)),
                (F(0), F(1, 10), F(3, 10), F(2)),
                (False, True), (F(1, 2), F(3, 5), F(1))):
            try:
                world = s.World("enum", "grid", "game", False, cost, accuracy, prior,
                                True, (s.Report("x", signal, report_reliability),))
            except ValueError:  # Zero-probability conditional report
                continue
            for action, v in s.values(world).items():
                self.assertEqual(v, s.enumerated_expected_reward(world, action))
                self.assertGreaterEqual(s.regret(world, action), 0)
            self.assertEqual(s.regret(world, s.policy_action(world, "exact")), 0)

    def test_two_source_posterior_against_direct_joint_enumeration(self):
        for a, b, rel in product((False, True), repeat=3):
            accuracy = F(4, 5) if rel else F(3, 5)
            world = s.World("brute", "two", "council", False, F(1, 10),
                            reports=(s.Report("source1", a, accuracy),
                                     s.Report("source2", b, accuracy)))
            likelihood_right = ((accuracy if a else 1-accuracy)
                                * (accuracy if b else 1-accuracy))
            likelihood_left = ((1-accuracy if a else accuracy)
                               * (1-accuracy if b else accuracy))
            self.assertEqual(s.posterior_right(world), likelihood_right/(likelihood_right+likelihood_left))

    def test_invalid_provenance_and_impossible_histories(self):
        with self.assertRaises(ValueError):
            s.World("x", "x", "s", False, F(0), reports=(
                s.Report("same", False, F(3, 5)), s.Report("same", True, F(3, 5))))
        with self.assertRaises(ValueError):
            s.World("x", "x", "s", False, F(0), reports=(
                s.Report("a", False, F(1)), s.Report("b", True, F(1))))
        with self.assertRaises(ValueError):
            s.Report("", True, F(3, 4))
        with self.assertRaises(ValueError):
            s.Report("valid", True, F(2, 5))
        with self.assertRaises(ValueError):
            replace(self.by_name("scout-cost-001", "cheap"), scout_cost=F(-1))
        with self.assertRaises(ValueError):
            s.posterior_after_scout(F(1), False, F(1))

    def test_public_private_custody_and_four_linked_views(self):
        worlds = s.development_cases()
        self.assertEqual(len(worlds), 12)
        self.assertEqual(len({w.root_id for w in worlds}), 5)
        for w in worlds:
            task = s.public_task(w)
            self.assertNotIn("root_id", task)
            self.assertNotIn("case_id", task)
            self.assertNotIn("optimal_actions", task)
            self.assertNotIn("posterior_right", task)
            self.assertEqual(len(task["reports"]), len(w.reports))
            self.assertEqual(set(task["legal_actions"]), set(s.values(w)))
            self.assertEqual(s.private_grade(w)["root_id"], w.root_id)
        views = s.development_views()
        self.assertEqual(len(views), 8)
        self.assertEqual(len({v["parent_root"] for v in views}), 2)
        for root in {v["parent_root"] for v in views}:
            self.assertEqual({v["view"] for v in views if v["parent_root"] == root},
                             {"play", "revise", "hold_steady", "repair"})
        for v in views:
            world = next(w for w in worlds if w.root_id == v["parent_root"]
                         and w.case_id == v["grader_case_id"])
            if v["view"] == "hold_steady":
                self.assertEqual(v["public_task"]["legal_actions"], list(s.values(world)))
            if v["view"] == "repair":
                self.assertGreater(s.regret(world, v["recorded_bad_action"]), 0)

    def test_development_baseline_failure_patterns(self):
        worlds = s.development_cases()
        expected = {
            "cue_following": {"cheap", "cue_conflict", "shared_relays", "scout_available", "informative_scout"},
            "always_scout": {"expensive", "cue_conflict", "independent_witnesses", "uninformative_scout", "cosmetic_cue"},
            "double_count_relays": {"shared_relays"},
        }
        for name in ("cue_following", "always_scout", "always_commit", "double_count_relays"):
            failures = {w.case_id for w in worlds if s.regret(w, s.policy_action(w, name)) > 0}
            if name in expected:
                self.assertTrue(expected[name] <= failures if name != "always_scout" else
                                {"expensive", "cue_conflict", "independent_witnesses", "uninformative_scout"} <= failures)
        self.assertTrue(all(s.regret(w, s.policy_action(w, "exact")) == 0 for w in worlds))


if __name__ == "__main__":
    unittest.main()
