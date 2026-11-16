"""SRB-01 exact scenario, information-fibre, tail, and feedback audits."""
from copy import deepcopy
from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import random
import unittest

from spiral_ln.evaluation_systemic_risk import (
    SCHEMA, binary_collision_floor, expected_loss, json_exact, load_bank,
    optimal_observable, parse_bank, rational, score, total_loss, weighted_cvar,
)

FIXTURE = (Path(__file__).resolve().parents[1] /
           "fixtures/systemic_risk_evalmath/synthetic_two_worlds.json")


class SystemicRiskTests(unittest.TestCase):
    def test_hidden_cross_sector_shock_witness(self):
        bank = load_bank(FIXTURE)
        r = score(bank)
        self.assertEqual(r["fixed_loss"], Fraction(4))
        self.assertEqual(r["observable_loss"], Fraction(4))
        self.assertEqual(r["oracle_loss"], Fraction(0))
        self.assertEqual(r["unobservable_regret"], Fraction(4))
        self.assertEqual(r["binary_collision_certificate"], Fraction(4))
        self.assertEqual(r["query_disclosure_loss"], {"reveal_shock": Fraction(0)})
        self.assertEqual(r["baseline_harm_cvar"], Fraction(8))
        self.assertEqual(r["trace_replay_loss"], Fraction(4))
        self.assertEqual(r["trace_replay_false_authorization"], Fraction(1, 2))
        self.assertEqual(r["false_authorization_selection"], {
            "no_disclosure": Fraction(1, 2),
            "one_query_optimum": Fraction(1),
            "two_adaptive_queries": Fraction(1),
            "full_disclosure": Fraction(1),
        })
        self.assertEqual(json_exact({"regret": Fraction(4, 3)}), {"regret": "4/3"})

    def test_finite_two_action_collision_certificate_independent(self):
        rng = random.Random(20261116)
        for _ in range(96):
            bank = random_bank(rng, n=rng.randrange(1, 7), actions=2)
            r = score(bank)
            self.assertEqual(r["unobservable_regret"], binary_collision_floor(bank))
            self.assertGreaterEqual(r["fixed_loss"], r["observable_loss"])
            self.assertGreaterEqual(r["observable_loss"], r["oracle_loss"])

    def test_exhaustive_policy_oracle_three_actions(self):
        rng = random.Random(4411)
        for _ in range(64):
            bank = random_bank(rng, n=rng.randrange(1, 6), actions=3)
            classes = sorted(set(w.visible for w in bank.worlds))
            brute = min(
                expected_loss(bank, tuple(plan[classes.index(w.visible)] for w in bank.worlds))
                for plan in product(range(3), repeat=len(classes))
            )
            self.assertEqual(expected_loss(bank, optimal_observable(bank)), brute)
            self.assertIsNone(score(bank)["binary_collision_certificate"])
            for q in range(len(bank.query_names)):
                self.assertLessEqual(expected_loss(bank, optimal_observable(bank, q)), brute)

    def test_exact_cvar_and_alpha_boundaries(self):
        vals = ((Fraction(0), 3), (Fraction(8), 1))
        self.assertEqual(weighted_cvar(vals, Fraction(0)), Fraction(2))
        self.assertEqual(weighted_cvar(vals, Fraction(1, 2)), Fraction(4))
        self.assertEqual(weighted_cvar(vals, Fraction(3, 4)), Fraction(8))
        self.assertEqual(weighted_cvar(((Fraction(5), 1),), Fraction(99, 100)), Fraction(5))
        for alpha in (Fraction(-1), Fraction(1)):
            with self.assertRaises(ValueError):
                weighted_cvar(vals, alpha)

    def test_malformed_schemas_rejected(self):
        original = json.loads(FIXTURE.read_text())
        mutants = []
        for key, value in (("schema", "old"), ("tail_alpha", "1"),
                           ("harm_threshold", 5.0), ("baseline", "unknown"),
                           ("nodes", ["x", "x"]), ("query_names", ["x", "x"])):
            d = deepcopy(original); d[key] = value; mutants.append(d)
        for key, value in (("mass", 0), ("visible", [0, 1]),
                           ("queries", []), ("selected", "bad")):
            d = deepcopy(original); d["worlds"][0][key] = value; mutants.append(d)
        d = deepcopy(original); d["worlds"][0]["outcomes"]["cut_a"]["node_loss"][0] = -1; mutants.append(d)
        d = deepcopy(original); d["worlds"][0]["outcomes"]["cut_a"]["claimed_safe"] = 1; mutants.append(d)
        d = deepcopy(original); del d["worlds"][1]["selected"]; mutants.append(d)
        d = deepcopy(original); d["worlds"][0]["outcomes"].pop("cut_b"); mutants.append(d)
        for d in mutants:
            with self.subTest(d=d), self.assertRaises(ValueError):
                parse_bank(d)
        for value in (True, 1.2, None, "-1", "invalid"):
            with self.assertRaises(ValueError):
                rational(value)

    def test_single_world_one_action_and_missing_selected(self):
        data = json.loads(FIXTURE.read_text())
        data["actions"] = [data["actions"][0]]
        data["worlds"] = [data["worlds"][0]]
        data["worlds"][0]["outcomes"].pop("cut_b")
        del data["worlds"][0]["selected"]
        bank = parse_bank(data)
        r = score(bank)
        self.assertEqual(r["unobservable_regret"], 0)
        self.assertEqual(r["baseline_harm_cvar"], 0)
        self.assertNotIn("trace_replay_loss", r)
        self.assertIsNone(r["binary_collision_certificate"])
        self.assertEqual(r["false_authorization_selection"]["no_disclosure"], 0)


def random_bank(rng: random.Random, n: int, actions: int):
    names = [f"a{i}" for i in range(actions)]
    data = {
        "schema": SCHEMA, "nodes": ["n0", "n1"],
        "actions": [{"name": a, "cost": str(rng.randrange(3))} for a in names],
        "baseline": names[0], "query_names": ["q0"],
        "harm_threshold": "6", "tail_alpha": "1/2", "worlds": [],
    }
    for i in range(n):
        data["worlds"].append({
            "id": f"w{i}", "mass": rng.randrange(1, 5),
            "visible": [rng.randrange(2)], "queries": [rng.randrange(2)],
            "outcomes": {a: {"node_loss": [str(rng.randrange(7)), str(rng.randrange(7))],
                             "claimed_safe": rng.choice([True, False])} for a in names},
        })
    return parse_bank(data)


if __name__ == "__main__":
    unittest.main()
