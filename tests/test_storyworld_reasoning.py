from fractions import Fraction as F
from itertools import product

import pytest

from spiral_ln.evaluation_storyworld_reasoning import (
    DecisionProblem, effect_audit, formula_audit, independent_fixed_value,
    linear_scores, parity_problem, squared_distance, winners,
)


def test_hg_geometry_and_effect_apportionment():
    assert squared_distance((0, 0), (1, 1), (F(1,2), 2)) == F(17,4)
    path = [(F(i,4),) for i in range(1,5)]
    gradual = effect_audit((0,), path, (1,), (1,))
    jump = effect_audit((0,), [(0,), (0,), (0,), (1,)], (1,), (1,))
    assert gradual["energy"] == [F(1,16)]*4
    assert gradual["progress"] == [F(7,16), F(5,16), F(3,16), F(1,16)]
    assert gradual["net_progress"] == jump["net_progress"] == 1
    assert gradual["max_energy_share"] == F(1,4)
    assert jump["max_energy_share"] == jump["max_positive_progress_share"] == 1


def test_direction_and_energy_are_distinct():
    a = effect_audit((0,0), [(1,0)], (1,0), (1,1))
    b = effect_audit((0,0), [(0,1)], (1,0), (1,1))
    assert a["energy"] == b["energy"] == [1]
    assert a["net_progress"] == 1 and b["net_progress"] == -1


def test_semantic_support_and_common_mode():
    states = tuple(product((0,1), repeat=3))
    scores = [linear_scores(x, ((1,1,0),(-1,1,0)), (-F(1,2), F(1,2)))
              for x in states]
    audit = formula_audit(states, scores)
    assert audit["feasible_pairs"] == [4,4,4]
    assert audit["relative_score_changes"] == [4,0,0]
    assert audit["winner_set_changes"] == [4,0,0]
    assert audit["margins"] == [1]*8
    assert winners((0,0,0)) == frozenset((0,1,2))


def test_missing_feasible_interventions_not_inactive():
    result = formula_audit([(0,0),(1,1)], [(0,1),(1,0)])
    assert result["unidentified"] == [0,1]


@pytest.mark.parametrize("k", [1,2,3,4])
def test_k_independent_information_coordinates(k):
    p = parity_problem(k)
    expected = [F(1,2)]*k+[F(1)]
    assert p.profile()["adaptive_curve"] == expected
    assert p.profile()["min_budget_full"] == k
    for b in range(k+1):
        if k <= 3:
            assert independent_fixed_value(p,b) == expected[b]


def test_hidden_gate_and_nuisance_control():
    hidden = parity_problem(3, visible=(0,1))
    assert hidden.profile()["unobservable_gap"] == F(1,2)
    assert hidden.profile()["min_budget_full"] is None
    padded = parity_problem(3, nuisance=2)
    assert padded.profile()["adaptive_curve"] == [F(1,2)]*3+[F(1)]*3
    assert padded.profile()["min_budget_full"] == 3


def test_adaptive_branching_has_value():
    states = tuple(product((0,1), repeat=3))
    rows = [(int(s[1+s[0]] == 0), int(s[1+s[0]] == 1)) for s in states]
    qs = [tuple(s[i] for s in states) for i in range(3)]
    p = DecisionProblem(rows, qs, [F(1,8)]*8)
    assert p.value(2) == 1
    assert independent_fixed_value(p,2) == F(3,4)
    assert p.full() == 1


def test_initial_information_and_nonuniform_prior():
    p = DecisionProblem([(1,0),(0,1)], [], [F(3,4),F(1,4)])
    assert p.value(0) == F(3,4)
    assert p.profile()["unobservable_gap"] == F(1,4)
    q = DecisionProblem(p.rows, [], p.prior, ("first","second"))
    assert q.value(0) == q.full() == 1


def test_invalid_contracts():
    with pytest.raises(ValueError):
        squared_distance((1,), (0,), (0,))
    with pytest.raises(ValueError):
        DecisionProblem([(1,0)], [], [F(1,2)])
    with pytest.raises(ValueError):
        parity_problem(2, visible=(2,))
    with pytest.raises(ValueError):
        parity_problem(1).value(-1)
