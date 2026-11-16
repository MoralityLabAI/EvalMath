"""HG-01 adversarial and independent finite-oracle tests."""
import unittest
from fractions import Fraction as F
from itertools import product

from spiral_ln.evaluation_hypergames import (
    rational, dirac_distance_squared, categorical_overlap, categorical_chord_squared,
    infer_goals, hypergame_view_gap, minimum_robust_probe_cover, minimizers, regret,
    projection_margin_certificate, diplomacy_v2_visible_numeric, observer_nested_beliefs,
    exact_row_rank, inverse_voronoi_halfspaces, halfspaces_accept,
)


def _world():
    return {"visible_state": {"active_node": "node_start", "beliefs": {
        actor: {"trust": {target: 0 for target in "ABC"}, "expected_payoff": 0}
        for actor in "ABC"}, "coalitions": [], "world_vars": {"round": 0, "seed": 7}},
        "hidden_state_reveal": [{"key": "secret_payoff", "value": 777}],
        "realized_outcome": {"outcome": "betrayal"}}


class Hypergames01(unittest.TestCase):
    def test_clifford_2_exact_gamma_matrices(self):
        p, q = F(3, 5), F(-7, 11)
        a, b = ((F(1), F(0)), (F(0), F(-1))), ((F(0), F(1)), (F(1), F(0)))
        def mul(x, y):
            return tuple(tuple(sum((x[i][k] * y[k][j] for k in range(2)), F(0))
                               for j in range(2)) for i in range(2))
        ab, ba = mul(a, b), mul(b, a)
        self.assertEqual(tuple(tuple(ab[i][j] + ba[i][j] for j in range(2)) for i in range(2)),
                         ((F(0), F(0)), (F(0), F(0))))
        mat = tuple(tuple(p * a[i][j] + q * b[i][j] for j in range(2)) for i in range(2))
        self.assertEqual(mul(mat, mat), ((p*p+q*q, F(0)), (F(0), p*p+q*q)))
        self.assertEqual(dirac_distance_squared({"p": p, "q": q}, {"p": F(0), "q": F(0)}), p*p+q*q)

    def test_high_dimension_sparse_exact(self):
        x = {f"c{i:03d}": F(0) for i in range(140)}
        y = dict(x); y["c139"] = F(3, 5)
        weights = {k: F(2) for k in x}
        self.assertEqual(dirac_distance_squared(x, y, weights), F(36, 25))
        self.assertEqual(dirac_distance_squared(x, x, weights), 0)
        self.assertEqual(dirac_distance_squared(y, x, weights), F(36, 25))

    def test_categorical_tensor_exact_bruteforce(self):
        a, b = F(3, 5), F(4, 5)
        for n in range(1, 5):
            for left in product("01", repeat=n):
                for right in product("01", repeat=n):
                    # Independent explicit tensor contraction on orthonormal 3-ary basis.
                    def coef(bits, basis):
                        z = F(1)
                        for bit, slot in zip(bits, basis):
                            z *= (a if slot == 2 else b if slot == int(bit) else F(0))
                        return z
                    direct = sum((coef(left, basis) * coef(right, basis)
                                  for basis in product(range(3), repeat=n)), F(0))
                    self.assertEqual(categorical_overlap(left, right), direct)
                    self.assertEqual(categorical_chord_squared(left, right), 2-2*direct)
        self.assertEqual(categorical_overlap(["0"]*140, ["1"]*140), F(9, 25)**140)
        self.assertEqual(categorical_chord_squared(["0"]*140, ["0"]*140), 0)

    def test_inverse_goals_and_no_hypothesis(self):
        goals = {"g00": {"x": F(0), "y": F(0)}, "g01": {"x": F(0), "y": F(1)},
                 "g10": {"x": F(1), "y": F(0)}, "g11": {"x": F(1), "y": F(1)}}
        probe_x = {"x0": {"x": F(0), "y": F(1, 2)}, "x1": {"x": F(1), "y": F(1, 2)}}
        probe_y = {"y0": {"x": F(1, 2), "y": F(0)}, "y1": {"x": F(1, 2), "y": F(1)}}
        self.assertEqual(infer_goals([("x0", probe_x)], goals)["compatible"], ("g00", "g01"))
        self.assertEqual(infer_goals([("x0", probe_x), ("y0", probe_y)], goals)["compatible"], ("g00",))
        self.assertEqual(infer_goals([("x0", probe_x), ("x1", probe_x)], goals)["status"], "no_hypothesis_fits")
        cover = minimum_robust_probe_cover({"x": probe_x, "y": probe_y}, goals, {"x": 2, "y": 3})
        self.assertEqual((cover["min_cost"], cover["probes"]), (5, ("x", "y")))
        self.assertFalse(minimum_robust_probe_cover({"x": probe_x}, goals)["feasible"])

    def test_ties_never_falsely_separate(self):
        goals = {"left": {"x": F(-1)}, "right": {"x": F(1)}}
        tied = {"A": {"x": F(0)}, "B": {"x": F(0)}}
        self.assertEqual(minimizers(tied, goals["left"]), ("A", "B"))
        self.assertFalse(minimum_robust_probe_cover({"tie": tied}, goals)["feasible"])
        self.assertEqual(regret(tied, "B", goals["right"]), 0)
        self.assertEqual(minimum_robust_probe_cover({}, {"one": goals["left"]})["min_cost"], 0)

    def test_misperception_changes_regret(self):
        goal = {"trust": F(1)}
        subj = {"ally": {"trust": F(1)}, "wait": {"trust": F(0)}}
        real = {"ally": {"trust": F(-1)}, "wait": {"trust": F(0)}}
        self.assertEqual(hypergame_view_gap("ally", goal, subj, real), {
            "subjective_regret": "0", "objective_regret": "3",
            "subjectively_optimal": True, "objectively_optimal": False})

    def test_projection_margin_and_witness(self):
        goal = {"x": F(0), "y": F(0)}
        stable = {"a": {"x": F(0), "y": F(1, 5)}, "b": {"x": F(1), "y": F(0)}}
        c = projection_margin_certificate(stable, goal, ["x"])
        self.assertEqual((c["full_gap"], c["omitted_energy_range"]), ("24/25", "1/25"))
        self.assertTrue(c["certified_stable"])
        self.assertEqual(c["projected_minimizers"], ("a",))
        reversed_ = {"a": {"x": F(0), "y": F(1)}, "b": {"x": F(1, 2), "y": F(0)}}
        c = projection_margin_certificate(reversed_, goal, ["x"])
        self.assertFalse(c["certified_stable"])
        self.assertEqual(c["winner"], "b")
        self.assertEqual(c["projected_minimizers"], ("a",))

    def test_source_trace_visibility_boundary(self):
        row = _world()
        baseline = diplomacy_v2_visible_numeric(row, ["round"])
        self.assertEqual(len(baseline), 16)  # 3x3 trust + 3 payoff + 3 coalition + 1 round
        self.assertNotIn("world.seed", baseline)
        row["hidden_state_reveal"][0]["value"] = -100000
        row["realized_outcome"]["outcome"] = "coalition_formed"
        row["belief_delta"] = {"after": {"A": {"trust": 100}}}
        self.assertEqual(diplomacy_v2_visible_numeric(row, ["round"]), baseline)
        row["visible_state"]["beliefs"]["A"]["trust"].pop("B")
        with self.assertRaises(ValueError):
            diplomacy_v2_visible_numeric(row, ["round"])

    def test_inverse_voronoi_polyhedron_and_rank_140(self):
        zs = {f"z{j:03d}": F(0) for j in range(138)}
        goals = {"g00": {"x": F(0), "y": F(0), **zs},
                 "g01": {"x": F(0), "y": F(1), **zs},
                 "g10": {"x": F(1), "y": F(0), **zs},
                 "g11": {"x": F(1), "y": F(1), **zs}}
        x = {"x0": {"x": F(0), "y": F(1, 2), **zs},
             "x1": {"x": F(1), "y": F(1, 2), **zs}}
        y = {"y0": {"x": F(1, 2), "y": F(0), **zs},
             "y1": {"x": F(1, 2), "y": F(1), **zs}}
        half = inverse_voronoi_halfspaces([("x0", x), ("y1", y)])
        self.assertEqual((half["comparison_rank"], half["blind_linear_dimensions"]), (2, 138))
        self.assertEqual(len(half["constraints"]), 2)
        for target in goals.values():
            self.assertEqual(halfspaces_accept(half, target),
                             all(regret(actions, chosen, target) == 0 for chosen, actions in [("x0", x), ("y1", y)]))
        self.assertTrue(halfspaces_accept(half, {"x": F(1, 2), "y": F(1, 2), **zs}))
        self.assertEqual(exact_row_rank([[F(1), F(2)], [F(2), F(4)]]), 1)
        self.assertEqual(exact_row_rank([]), 0)

    def test_second_order_observer_isolation(self):
        snapshot = {"p": {"A": {"B": {"loyalty": 0.75}},
                           "B": {"A": {"secret": -0.25}}},
                    "p2": {"A": {"B": {"C": {"promise_keeping": "1/2"}}},
                            "B": {"A": {"C": {"secret": 1}}}}}
        self.assertEqual(observer_nested_beliefs(snapshot, "A"), {
            "p.B.loyalty": F(3, 4), "p2.B.C.promise_keeping": F(1, 2)})
        with self.assertRaises(ValueError): observer_nested_beliefs(snapshot, "unknown")

    def test_single_action_margin(self):
        self.assertTrue(projection_margin_certificate({"a": {"x": F(1)}},
                           {"x": F(0)}, ["x"])["certified_stable"])

    def test_fail_closed(self):
        with self.assertRaises(ValueError): rational(float("nan"))
        with self.assertRaises(ValueError): rational(True)
        with self.assertRaises(ValueError): dirac_distance_squared({"x": F(0)}, {"y": F(0)})
        with self.assertRaises(ValueError): dirac_distance_squared({"x": F(0)}, {"x": F(1)}, {"x": F(0)})
        with self.assertRaises(ValueError): categorical_overlap(["a"], ["b"], F(1, 2), F(1, 2))
        with self.assertRaises(ValueError): regret({"ok": {"x": F(0)}}, "missing", {"x": F(0)})
        with self.assertRaises(ValueError): projection_margin_certificate({"x": {"a": F(0)}}, {"a": F(0)}, ["bad"])
        with self.assertRaises(ValueError): minimum_robust_probe_cover({}, {"A": {"x": F(0)}}, {"bad": 1})


if __name__ == "__main__":
    unittest.main()
