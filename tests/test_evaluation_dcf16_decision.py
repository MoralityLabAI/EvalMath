"""Hand-computed rational checks and fixture invariants for the DCF-16 decision evaluation."""
from __future__ import annotations

from fractions import Fraction as Q
from itertools import product
from pathlib import Path

import pytest

from spiral_ln.evaluation_dcf16_decision import (
    REFERENCE_PREDICTORS, aggregate, calibration, expected_utility, load_records, oracle_utility,
    paired, predict_abstain, predict_symbolic, predict_unary, realized_utility, report, score,
    score_record, sign_test_p, validate_predictions,
)

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "dcf16_heldout_sample.jsonl"


def op(name, ops, p, action, exact=False):
    return dict(name=name, exact=exact, ops=ops, within_budget=True, p=p, action=action, regret=0.0)


def rec(rid, fam, B, pen, ref, truth, ops, selected, hard=False, unary=0.5):
    return dict(id=rid, family=fam, budget_log2_ops=B,
                decision_rule=dict(reward=dict(correct=1, wrong=-pen, abstain=0)),
                operators=ops, selected=dict(operator=selected),
                verification=dict(reference_p=ref, truth_parity=truth),
                hard_negative=dict(unary_shortcut_wrong=hard, one_hop_wrong=False, bp_wrong=False),
                candidate_representations=[dict(name="unary_evidence_only", p=unary)])


# budget 2**4 = 16 ops, penalty 4: act threshold 4/5, low 1/5
A = rec("a", "f1", 4, 4, 0.875, 1, [op("ve_min_fill", 10, 0.875, 1, True), op("mbe", 6, 0.75, -1)], "ve_min_fill", unary=0.9)
B = rec("b", "f1", 4, 4, 0.125, 1, [op("ve_min_fill", 40, 0.125, 0, True), op("mbe", 8, 0.25, -1)], "abstain", hard=True, unary=0.1)
C = rec("c", "f2", 4, 4, 0.5, 0, [op("ve_min_fill", 3, 0.5, -1, True)], "ve_min_fill", unary=0.5)
RECS = [A, B, C]


def preds(*items):
    return [dict(id=i, algorithm=a, action=x, **kw) for i, a, x, kw in items]


def test_expected_utility_is_linear_and_exact():
    pen = Q(4)
    q = Q(7, 8)
    assert expected_utility(1, q, pen) == Q(7, 8) - 4 * Q(1, 8) == Q(3, 8)
    assert expected_utility(0, q, pen) == Q(1, 8) - 4 * Q(7, 8) == Q(-27, 8)
    assert expected_utility(-1, q, pen) == 0
    assert oracle_utility(q, pen) == Q(3, 8)
    assert oracle_utility(Q(1, 2), pen) == 0
    # linearity in q: EU(1, mixture) = mixture of EU(1)
    for q1, q2, w in product((Q(1, 10), Q(9, 10)), (Q(1, 2), Q(3, 4)), (Q(1, 3), Q(2, 3))):
        assert expected_utility(1, w * q1 + (1 - w) * q2, pen) == w * expected_utility(1, q1, pen) + (1 - w) * expected_utility(1, q2, pen)
    with pytest.raises(ValueError):
        expected_utility(2, q, pen)


def test_float_inputs_enter_exactly():
    q = Q(0.1)
    assert q != Q(1, 10)
    assert expected_utility(1, q, Q(4)) == q - 4 * (1 - q)


def test_realized_utility():
    assert realized_utility(1, 1, Q(4)) == 1
    assert realized_utility(1, 0, Q(4)) == -4
    assert realized_utility(0, 0, Q(4)) == 1
    assert realized_utility(-1, 1, Q(4)) == 0


def test_scores_by_hand():
    # A: act 1 (correct, EU 3/8); B: act 1 (correct draw, EU = 1/8 - 4*7/8 = -27/8); C: abstain.
    pr = preds(("a", "ve_min_fill", 1, {"p": 0.875, "claimed_ops": 10}),
               ("b", "ve_min_fill", 1, {"p": 0.875}),
               ("c", "abstain", -1, {}))
    r = score(RECS, pr)["overall"]
    assert r["n"] == 3
    assert r["eu"] == (Q(3, 8) + Q(-27, 8) + 0) / 3 == Q(-1, 1)
    assert r["realized"] == Q(1 + 1 + 0, 3)  # b: truth 1, so acting 1 is correct despite EU -27/8
    assert r["oracle_eu"] == (Q(3, 8) + Q(3, 8) + 0) / 3  # B: oracle acts 0 at q=1/8, EU(0)=3/8
    assert r["regret"] == r["oracle_eu"] - r["eu"]
    assert r["coverage"] == Q(2, 3)
    assert r["selective_risk"] == 0
    # selected: a ve_min_fill (match), b abstain (no match), c ve_min_fill (no match)
    assert r["algorithm_accuracy"] == Q(1, 3)
    # b: ve_min_fill costs 40 > 16 -> non-compliant; a ok; c abstain ok
    assert r["budget_compliance"] == Q(2, 3)
    assert r["eu_budget_enforced"] == (Q(3, 8) + 0 + 0) / 3
    assert r["claimed_ops_given"] == 1 and r["claimed_ops_match"] == 1


def test_budget_taken_from_record_not_prediction():
    pr = preds(("a", "ve_min_fill", 1, {"claimed_ops": 1}), ("b", "ve_min_fill", 0, {"claimed_ops": 1}), ("c", "abstain", -1, {}))
    r = score(RECS, pr)["overall"]
    assert r["budget_compliance"] == Q(2, 3)  # the lie about b's ops does not help
    assert r["claimed_ops_match"] == 0
    # boundary: ops exactly equal to the cap complies
    edge = rec("e", "f1", 4, 4, 0.5, 0, [op("bp", 16, 0.5, -1)], "bp")
    assert score_record(edge, dict(id="e", algorithm="bp", action=-1))["compliant"]
    over = rec("o", "f1", 4, 4, 0.5, 0, [op("bp", 17, 0.5, -1)], "bp")
    assert not score_record(over, dict(id="o", algorithm="bp", action=-1))["compliant"]


def test_unknown_algorithm_is_noncompliant():
    r = score_record(A, dict(id="a", algorithm="gf2", action=-1))
    assert not r["compliant"] and not r["known_algorithm"]


def test_hard_negative_slice_and_families():
    pr = preds(("a", "ve_min_fill", 1, {}), ("b", "ve_min_fill", 1, {}), ("c", "abstain", -1, {}))
    s = score(RECS, pr)
    assert s["hard_negative"]["n"] == 1 and s["easy"]["n"] == 2
    assert s["hard_negative"]["eu"] == Q(-27, 8)
    assert set(s["per_family"]) == {"f1", "f2"}
    assert s["per_family"]["f1"]["n"] == 2 and s["per_family"]["f2"]["n"] == 1
    assert s["per_family"]["f2"]["selective_risk"] is None  # empty index range: nothing acted on


def test_calibration_by_hand():
    rows = [dict(p=Q(1, 10), truth=0), dict(p=Q(1, 10), truth=1), dict(p=Q(9, 10), truth=1), dict(p=Q(1), truth=1)]
    c = calibration(rows)
    assert c["n_p"] == 4
    assert c["brier"] == (Q(1, 100) + Q(81, 100) + Q(1, 100) + 0) / 4
    # bins: 0.1 -> bin 1 (mean truth 1/2 vs 1/10); 0.9 -> bin 9; 1.0 -> bin 9 (last bin closed)
    # bin 9: truth mean 1, p mean 19/20
    assert c["ece"] == Q(2, 4) * abs(Q(1, 2) - Q(1, 10)) + Q(2, 4) * abs(1 - Q(19, 20))
    assert calibration([dict(p=None, truth=1)]) == dict(n_p=0, brier=None, ece=None)
    perfect = calibration([dict(p=Q(1), truth=1), dict(p=Q(0), truth=0)])
    assert perfect["brier"] == 0 and perfect["ece"] == 0


def test_sign_test_enumerated():
    for n in range(0, 9):
        for k in range(n + 1):
            wins, losses = k, n - k
            low = min(wins, losses)
            extreme = sum(1 for bits in product((0, 1), repeat=n) if sum(bits) <= low or sum(bits) >= n - low)
            assert sign_test_p(wins, losses) == Q(extreme, 2 ** n) or n == 0
    assert sign_test_p(0, 0) == 1
    assert sign_test_p(15, 3) == Q(247, 32768)


def test_paired_comparison():
    good = preds(("a", "ve_min_fill", 1, {}), ("b", "abstain", -1, {}), ("c", "ve_min_fill", -1, {}))
    bad = preds(("a", "abstain", -1, {}), ("b", "ve_min_fill", 1, {}), ("c", "abstain", -1, {}))
    d = paired(RECS, good, bad)
    e = d["eu"]
    assert (e["wins"], e["losses"], e["ties"]) == (2, 0, 1)
    assert e["sign_test_p"] == Q(1, 2)
    assert e["mean_diff"] == (Q(3, 8) + Q(27, 8)) / 3
    # antisymmetry and self-comparison
    assert paired(RECS, bad, good)["eu"]["mean_diff"] == -e["mean_diff"]
    z = paired(RECS, good, good)
    assert all(z[k]["mean_diff"] == 0 and z[k]["ties"] == 3 and z[k]["sign_test_p"] == 1 for k in z)


def test_paired_mean_diff_exact():
    good = preds(("a", "ve_min_fill", 1, {}), ("b", "abstain", -1, {}), ("c", "abstain", -1, {}))
    bad = preds(("a", "abstain", -1, {}), ("b", "ve_min_fill", 1, {}), ("c", "abstain", -1, {}))
    e = paired(RECS, good, bad)["eu"]
    # a: 3/8 - 0 ; b: 0 - (-27/8) ; c: 0
    assert e["mean_diff"] == (Q(3, 8) + Q(27, 8)) / 3 == Q(5, 4)
    assert e["per_family_mean_diff"] == {"f1": Q(30, 8) / 2, "f2": Q(0)}


def test_validation_fails_closed():
    ok = preds(("a", "abstain", -1, {}), ("b", "abstain", -1, {}), ("c", "abstain", -1, {}))
    validate_predictions(RECS, ok)
    with pytest.raises(ValueError, match="missing"):
        validate_predictions(RECS, ok[:2])
    with pytest.raises(ValueError, match="unknown"):
        validate_predictions(RECS, ok + preds(("zz", "abstain", -1, {})))
    with pytest.raises(ValueError, match="duplicate"):
        validate_predictions(RECS, ok + ok[:1])
    for bad in (dict(id="a", algorithm="abstain", action=2), dict(id="a", algorithm="abstain", action=True),
                dict(id="a", algorithm="abstain", action=-1, p=1.5), dict(id="a", algorithm="abstain", action=-1, claimed_ops=-1),
                dict(id="a", algorithm=3, action=-1)):
        with pytest.raises(ValueError):
            validate_predictions(RECS, [bad] + ok[1:])


def test_reference_predictors_by_hand():
    # A: cheapest exact within budget is ve_min_fill (10 <= 16), acts 1
    assert predict_symbolic(A)["algorithm"] == "ve_min_fill" and predict_symbolic(A)["action"] == 1
    # B: exact costs 40 > 16, mbe 8 within budget but stored action -1: acts on mbe, abstains
    sb = predict_symbolic(B)
    assert (sb["algorithm"], sb["action"], sb["p"]) == ("mbe", -1, 0.25)
    # no exact and no mbe within budget: abstain
    far = rec("x", "f", 2, 4, 0.9, 1, [op("ve_min_fill", 100, 0.9, 1, True), op("mbe", 50, 0.9, 1)], "abstain")
    assert predict_symbolic(far)["algorithm"] == "abstain"
    assert predict_abstain(A)["action"] == -1
    # unary: p=0.9 >= 4/5 -> 1; p=0.1 <= 1/5 -> 0; p=0.5 -> abstain
    assert [predict_unary(r)["action"] for r in RECS] == [1, 0, -1]


def test_reference_predictors_ignore_reference_p_and_truth():
    import copy
    for r in RECS:
        r2 = copy.deepcopy(r)
        r2["verification"] = dict(reference_p=0.3, truth_parity=1 - r["verification"]["truth_parity"])
        for f in REFERENCE_PREDICTORS.values():
            assert f(r) == f(r2)


def test_fixture_invariants():
    recs = load_records(FIXTURE)
    assert len(recs) == 36
    assert len({r["family"] for r in recs}) == 9
    for name, f in REFERENCE_PREDICTORS.items():
        pr = [f(r) for r in recs]
        s = score(recs, pr)
        o = s["overall"]
        assert o["regret"] >= 0 and o["eu"] <= o["oracle_eu"]
        assert all(r["regret"] >= 0 for r in s["rows"])
        assert o["budget_compliance"] == 1
        assert o["claimed_ops_match"] == o["claimed_ops_given"] == 36
        assert s["hard_negative"]["n"] + s["easy"]["n"] == 36
        assert sum(v["n"] for v in s["per_family"].values()) == 36
        # recompute the mean EU independently of score(): float agreement within 1e-12
        fl = 0.0
        for r, p in zip(recs, pr):
            q, pen = r["verification"]["reference_p"], -r["decision_rule"]["reward"]["wrong"]
            a = p["action"]
            fl += 0.0 if a == -1 else (q if a == 1 else 1 - q) - pen * (1 - (q if a == 1 else 1 - q))
        assert abs(float(o["eu"]) - fl / 36) < 1e-12
    assert score(recs, [predict_abstain(r) for r in recs])["overall"]["eu"] == 0
    # symbolic acts only on stored actions, so its selective risk and the stored regret field agree in sign
    sym = score(recs, [predict_symbolic(r) for r in recs])["overall"]
    assert sym["coverage"] > 0
    rep = report(recs, [predict_symbolic(r) for r in recs])
    assert "rows" not in rep and set(rep) == {"overall", "hard_negative", "easy", "per_family"}


def test_fixture_stored_regret_matches_oracle_selection():
    """The record's regret field is the oracle label's regret; the exact scorer reproduces it to float precision."""
    recs = load_records(FIXTURE)
    pr = [dict(id=r["id"], algorithm=r["selected"]["operator"], action=r["final"]["action"]) for r in recs]
    rows = score(recs, pr)["rows"]
    for r, row in zip(recs, rows):
        assert abs(float(row["regret"]) - r["regret"]) < 1e-9
        assert row["alg_match"]


def test_selective_risk_counts_only_acted_wrong():
    pr = preds(("a", "ve_min_fill", 0, {}), ("b", "ve_min_fill", 1, {}), ("c", "abstain", -1, {}))
    r = score(RECS, pr)["overall"]
    assert r["selective_risk"] == Q(1, 2)  # a: truth 1, acted 0 (wrong); b: truth 1, acted 1
    assert r["realized"] == Q(-4 + 1, 3)
