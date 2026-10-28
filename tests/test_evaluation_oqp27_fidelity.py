from collections import Counter
from fractions import Fraction as Q

import pytest

from spiral_ln.evaluation_oqp27_fidelity import (
    BGP_H, BGP_L, audit_transfer, bgp_nonlocal_witness, bgp_saturator_average,
    bgp_strategy, bgp_table, cglmp_strategy, cglmp_table, linear_combo,
    residual, strategies, table_of, valid_no_signalling, verify,
)


def test_all_256_vertices_against_independent_probability_table():
    vertices = strategies()
    assert len(vertices) == len(set(vertices)) == 256
    assert len(BGP_L) == 6 and len(BGP_H) == 6
    for row in BGP_H:
        assert len(row) == 6
    for s in vertices:
        q = table_of(s)
        assert valid_no_signalling(q)
        assert cglmp_strategy(s) == cglmp_table(q)
        assert bgp_strategy(s) == bgp_table(q)


def test_exact_histograms_and_local_bounds():
    assert Counter(cglmp_strategy(s) for s in strategies()) == {Q(2): 80, Q(-2, 3): 160, Q(-10, 3): 16}
    assert Counter(bgp_strategy(s) for s in strategies()) == {0: 72, -1: 144, -2: 40}
    # Affine inequalities holding on every vertex hold on their convex hull.
    assert all(cglmp_strategy(s) <= 2 and bgp_strategy(s) <= 0 for s in strategies())
    # For local deterministic assignments the cyclic residual sum is -1 mod 4.
    for s in strategies():
        assert sum(residual(x, y, s[x], s[2 + y]) for x in (0, 1) for y in (0, 1)) % 4 == 3


def test_exact_rational_nonlocal_box():
    bar = bgp_saturator_average()
    plus = bgp_nonlocal_witness()
    assert valid_no_signalling(bar) and valid_no_signalling(plus)
    assert min(bar.values()) == min(plus.values()) == Q(1, 72)
    assert bgp_table(bar) == 0
    assert bgp_table(plus) == Q(1, 144)
    assert cglmp_table(plus) == Q(1, 9) < 2
    changed = {idx for idx in bar if plus[idx] != bar[idx]}
    assert changed == {(0, 0, 0, 1), (0, 0, 3, 3), (0, 0, 0, 3), (0, 0, 3, 1)}
    assert all(abs(plus[idx]-bar[idx]) == Q(1, 144) for idx in changed)


def test_cross_objective_transfer_tie_semantics_and_witness():
    ss = strategies()
    c = {s: cglmp_strategy(s) for s in ss}
    b = {s: Q(bgp_strategy(s)) for s in ss}
    fwd = audit_transfer(c, b)
    rev = audit_transfer(b, c)
    assert (fwd.source_winners, fwd.target_winners, fwd.shared_winners) == (80, 72, 24)
    assert (rev.source_winners, rev.target_winners, rev.shared_winners) == (72, 80, 24)
    assert fwd.existential_transfer and rev.existential_transfer
    assert not fwd.universal_transfer and not rev.universal_transfer
    assert fwd.worst_target_regret == 2 and rev.worst_target_regret == Q(16, 3)
    assert c[fwd.counterexample] == 2 and b[fwd.counterexample] < 0
    assert b[rev.counterexample] == 0 and c[rev.counterexample] < 2


def test_optimizer_transfer_validated_universe_and_ties():
    s0, s1, s2 = strategies()[:3]
    assert audit_transfer({s0: Q(1), s1: Q(1)}, {s0: Q(1), s1: Q(1)}).universal_transfer
    mismatch = audit_transfer({s0: Q(1), s1: Q(1)}, {s0: Q(0), s1: Q(1)})
    assert mismatch.existential_transfer and not mismatch.universal_transfer
    assert mismatch.counterexample == s0
    with pytest.raises(ValueError):
        audit_transfer({}, {})
    with pytest.raises(ValueError):
        audit_transfer({s0: Q(1)}, {s2: Q(1)})


def test_mutant_residual_omits_shift():
    assert residual(0, 1, 0, 0) == 3
    assert residual(0, 1, 0, 0, missing_shift=True) == 0
    actual = Counter(cglmp_strategy(s) for s in strategies())
    corrupt = Counter(cglmp_strategy(s, missing_shift=True) for s in strategies())
    assert corrupt != actual
    assert max(corrupt) != 2


def test_mutant_bgp_changes_saturation_histogram():
    original = Counter(bgp_strategy(s) for s in strategies())
    for mutant in (dict(omit_marginals=True), dict(altered_h=True)):
        assert Counter(bgp_strategy(s, **mutant) for s in strategies()) != original


def test_mutant_signalling_box_rejected():
    q = bgp_nonlocal_witness()
    q[0, 0, 0, 0] += Q(1, 144)
    assert not valid_no_signalling(q)
    q = bgp_nonlocal_witness()
    q[0, 0, 0, 0] = Q(-1, 144)
    assert not valid_no_signalling(q)
    q = bgp_nonlocal_witness()
    del q[0, 0, 0, 0]
    assert not valid_no_signalling(q)


def test_nontrivial_convex_mixture_preserves_linear_scores():
    s0, s1 = strategies()[11], strategies()[57]
    mix = linear_combo({s0: Q(2, 7), s1: Q(5, 7)})
    assert valid_no_signalling(mix)
    assert cglmp_table(mix) == Q(2, 7)*cglmp_strategy(s0) + Q(5, 7)*cglmp_strategy(s1)
    assert bgp_table(mix) == Q(2, 7)*bgp_strategy(s0) + Q(5, 7)*bgp_strategy(s1)


def test_verifier_checks_are_true_and_source_scope_preserved():
    r = verify()
    assert r["all_passed"] and len(r["checks"]) >= 20
    assert all(r["checks"].values())
    assert r["external_theorems_not_replayed"]
    assert r["optimizer_transfer"]["cglmp_to_bgp"]["shared"] == 24
