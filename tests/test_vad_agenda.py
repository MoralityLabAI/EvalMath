"""VAD-10: exact agenda oracle against a naive independent evaluator, theorems and counterexamples."""
import sys
from fractions import Fraction as F
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(p if p.is_dir() else Path(__file__).resolve().parent))
import vad_agenda as g
import vad_agenda_naive as naive


def test_bellman_matches_naive_history_tree():
    n = 0
    for s in range(60000, 60120):
        inst = g.random_instance(s, "layered" if s % 2 else "modular")
        if inst.budget > 3:
            continue
        o, v = g.solve(inst)
        assert naive.opt(inst) == v
        n += 1
    assert n >= 40


def test_signal_instance_matches_naive():
    for inst in g.misleading_signal():
        o, v = g.solve(inst)
        assert naive.opt(inst) == v
    o, v = g.solve(g.failed_attempt_information())
    assert naive.opt(o.i) == v


def test_forward_evaluation_of_optimal_policy_equals_value():
    for s in range(60200, 60230):
        inst = g.random_instance(s, "layered")
        o, v = g.solve(inst)
        assert g.evaluate(inst, o, g.policy_lookahead(None)) == v


def test_policy_values_never_exceed_optimum():
    for s in range(60300, 60320):
        inst = g.random_instance(s, "layered")
        o, v = g.solve(inst)
        for pol in (g.policy_direct, g.policy_random, g.policy_lookahead(0), g.policy_lookahead(1)):
            assert g.evaluate(inst, o, pol) <= v


def test_decomposition_telescopes_in_both_orders():
    for inst in (g.strategic_intermediate(), g.failed_attempt_information(), g.complementary()):
        o = g.Oracle(inst)
        for a in o.actions(o.start, inst.prior, inst.budget):
            if a != g.STOP:
                d = o.decompose(o.start, inst.prior, inst.budget, a)  # asserts both telescopings
                assert d["interaction"] == d["reuse"] - d["reuse_after_information"]


def test_modular_class_greedy_is_optimal():
    """Theorem: independent edges out of facts, unit costs, additive future value => myopic net gain is optimal."""
    for s in range(61000, 61060):
        inst = g.random_instance(s, "modular")
        o, v = g.solve(inst)
        assert g.evaluate(inst, o, g.policy_lookahead(0)) == v


def test_complementary_needs_one_step_lookahead():
    o, v = g.solve(g.complementary())
    assert v == -12
    assert g.evaluate(o.i, o, g.policy_lookahead(0)) == -30 == o.terminal(o.start, o.i.prior)
    assert g.evaluate(o.i, o, g.policy_lookahead(1)) == v


def test_chain_value_and_lookahead_depth():
    for k in range(2, 6):
        inst = g.chain(k)
        o, v = g.solve(inst)
        assert v == F(9, 10) ** k * 10 - 1
        for j in range(k):
            ok = g.evaluate(inst, o, g.policy_lookahead(j)) == v
            assert ok == (j >= k - 1)


def test_knapsack_breaks_greedy():
    o, v = g.solve(g.knapsack())
    assert g.evaluate(o.i, o, g.policy_lookahead(0)) < v == g.evaluate(o.i, o, g.policy_lookahead(1))


def test_strategic_intermediate_beats_direct_pursuit():
    o, v = g.solve(g.strategic_intermediate())
    assert g.evaluate(o.i, o, g.policy_direct) < v
    assert o.best_action(o.start, o.i.prior, o.i.budget)[0] == ("att", 1)  # the lemma M, not the rewarded target
    d = o.decompose(o.start, o.i.prior, o.i.budget, ("att", 1))
    assert d["immediate"] == 0 and d["reuse"] > 0


def test_misleading_signal_trusting_loses_to_ignoring():
    assumed, true = g.misleading_signal()
    oa = g.Oracle(assumed)
    ign = g.Instance(**{**assumed.__dict__, "experiments": ()})
    oi = g.Oracle(ign)
    pol = g.policy_lookahead(None)
    assert g.evaluate(true, oa, pol) < g.evaluate(true, oi, pol) < g.solve(true)[1]
    # and with the signal as reliable as assumed, trusting it is optimal
    _, honest = g.misleading_signal(true_reliable=True)
    assert g.evaluate(honest, oa, pol) == g.solve(honest)[1]


def test_receipt_source_digests_current():
    import hashlib, json
    root = Path(__file__).resolve().parents[1]
    rec = json.loads((root / "output/verified_abstraction/vad_10.json").read_text())
    for name, digest in rec["source_sha256"].items():
        assert hashlib.sha256((root / "scripts" / name).read_bytes()).hexdigest() == digest
