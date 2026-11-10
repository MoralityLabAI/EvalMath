"""RHT-15: proxy policy switching, algebraic crossings and isolated ties.

Exact independent fixed-p RHT-13 occupancy evaluation checks every policy
against the new symbolic region optimizer at rational samples. Algebraic
crossings are checked by exact polynomial relations and radical arithmetic.
"""
from fractions import Fraction as Q
from itertools import product
from random import Random

import pytest

from spiral_ln.evaluation_reward_kernel_switching import (
    ExactQuadratic,_value,_poly_roots,_extreme_quadratic,
    _fraction_strictly_between, switching_kernel_robust_certificate,
)
from spiral_ln.evaluation_reward_shared_kernel import (
    enumerate_observation_policies,polynomial_policy_returns,
    shared_kernel_robust_certificate,
)
from spiral_ln.evaluation_reward_shared_kernel_fixture import (
    rational_proxy_crossing_fixture,
    irrational_proxy_crossing_fixture,
    ugc_irrational_proxy_crossing_fixture,
    isolated_tangent_proxy_tie_fixture,
    interior_transition_hack_fixture,
    ugc_coupled_shared_transition_fixture,
    proxy_switching_fixture,
)
from spiral_ln.evaluation_reward_stochastic_closure import (
    optimize_stochastic_policy,policy_occupancy,
)


def direct_rational_policy_scan(game,p,theta):
    """Independent policy occupancy census using original RHT-13 kernel."""
    kernel=game.instantiate(p)
    candidates=[]
    for policy in enumerate_observation_policies(game):
        occ=policy_occupancy(kernel,policy)
        gold=occ.gold_base+sum((
            c*t for c,t in zip(occ.gold_feature_occupancy,theta)
        ),Q(0))
        candidates.append((occ.proxy,gold,policy))
    best_proxy=max(item[0] for item in candidates)
    best_gold=max(item[1] for item in candidates)
    proxy_winners=tuple(item for item in candidates
                        if item[0]==best_proxy)
    low_gold=min(item[1] for item in proxy_winners)
    gap=tuple(p-g for p,g,_ in candidates)
    return (best_gold-low_gold,
            max(gap)-min(gap),low_gold,
            len(proxy_winners),best_proxy)


def test_exact_radical_comparison_and_polynomial_evaluation():
    golden=ExactQuadratic(Q(-1,2),Q(1,2),Q(5))
    squared=ExactQuadratic(Q(3,2),Q(-1,2),Q(5))
    assert golden>Q(1,2) and golden<Q(3,4)
    assert squared>Q(3,8) and squared<Q(2,5)
    assert _value((Q(-1),Q(1),Q(1)),golden)==0
    assert _value((Q(0),Q(0),Q(1)),golden)==squared
    assert len(_poly_roots((Q(-1),Q(1),Q(1)),0,1))==1
    assert _poly_roots((Q(-1),Q(1),Q(1)),0,1)[0]==golden
    assert _fraction_strictly_between(golden,ExactQuadratic(Q(1)))==Q(3,4)
    assert ExactQuadratic(Q(0),Q(1),Q(2)) < ExactQuadratic(
        Q(0),Q(1),Q(3)
    )
    assert ExactQuadratic(Q(0),Q(-1),Q(2)) > ExactQuadratic(
        Q(0),Q(-1),Q(3)
    )
    assert ExactQuadratic(Q(1),Q(1),Q(2)) > ExactQuadratic(
        Q(1),Q(1),Q(1)
    )
    assert ExactQuadratic(Q(-1),Q(1),Q(1))==0
    assert ExactQuadratic(Q(0),Q(1),Q(4))==2
    assert str(ExactQuadratic(Q(1,3)))=="1/3"
    assert "sqrt(5)" in str(golden)
    assert _extreme_quadratic(
        (Q(0),Q(1),Q(-1)),Q(0),Q(1),maximize=True
    )==(ExactQuadratic(Q(1,4)),ExactQuadratic(Q(1,2)))


def test_rational_switching_boundary_has_adversarial_proxy_tie():
    game=rational_proxy_crossing_fixture()
    with pytest.raises(ValueError,match="proxy winner crosses or ties"):
        shared_kernel_robust_certificate(game,((Q(1),Q(1)),))
    cert=switching_kernel_robust_certificate(
        game,((Q(1),Q(1)),),
        maximum_allowed_regret=Q(1,2),
        minimum_proxy_gold_return=0,
    )
    assert cert.maximum_gold_regret==Q(1,2)
    assert cert.worst_transition_probability==Q(1,2)
    assert cert.endpoint_only_max_regret==0
    assert cert.transition_breakpoints==(
        ExactQuadratic(Q(0)),ExactQuadratic(Q(1,2)),
        ExactQuadratic(Q(1))
    )
    assert len(cert.proxy_regions)==2
    assert cert.isolated_tie_points==()
    assert cert.total_policies==2
    assert cert.distinct_proxy_winning_policies==2
    assert cert.gold_challenger_policy.action==0
    assert cert.proxy_chosen_policy.action==1
    assert cert.guaranteed_gold_floor==0
    assert cert.maximum_expected_discrepancy_width==1
    assert cert.passes
    assert not switching_kernel_robust_certificate(
        game,((1,1),),maximum_allowed_regret=Q(2,5)
    ).passes
    for p,expected in (
        (Q(0),Q(0)),(Q(1,4),Q(1,4)),
        (Q(1,2),Q(1,2)),(Q(3,4),Q(0)),(Q(1),Q(0))
    ):
        assert direct_rational_policy_scan(game,p,(Q(1),))[0]==expected


def test_irrational_proxy_crossing_is_handled_exactly():
    game=irrational_proxy_crossing_fixture()
    root=ExactQuadratic(Q(-1,2),Q(1,2),Q(5))
    exact_worst=ExactQuadratic(Q(3,2),Q(-1,2),Q(5))
    assert _value((Q(-1),Q(1),Q(1)),root)==0
    cert=switching_kernel_robust_certificate(
        game,((1,1),),maximum_allowed_regret=Q(2,5)
    )
    assert cert.maximum_gold_regret==exact_worst
    assert cert.worst_transition_probability==root
    assert cert.endpoint_only_max_regret==0
    assert cert.transition_breakpoints==(
        ExactQuadratic(0),root,ExactQuadratic(1)
    )
    assert cert.gold_challenger_policy.action==0
    assert cert.proxy_chosen_policy.action==1
    assert cert.isolated_tie_points==()
    assert len(cert.proxy_regions)==2
    assert cert.passes
    assert not switching_kernel_robust_certificate(
        game,((1,1),),maximum_allowed_regret=Q(3,8)
    ).passes
    for p in (Q(0),Q(1,4),Q(1,2),Q(2,3),Q(3,4),Q(1)):
        brute=direct_rational_policy_scan(game,p,(Q(1),))
        assert brute[0]==(
            p*p if p*p<=1-p else Q(0)
        )
    assert str(cert.worst_transition_probability)==(
        "-1/2 + (1/2)*sqrt(5)"
    )


def test_irrational_switch_with_actual_UGC_gold_worlds():
    game=ugc_irrational_proxy_crossing_fixture()
    golden=ExactQuadratic(Q(-1,2),Q(1,2),Q(5))
    fixed=ExactQuadratic(Q(3,4),Q(-1,4),Q(5))
    robust=ExactQuadratic(Q(3,2),Q(-1,2),Q(5))
    result=switching_kernel_robust_certificate(game,((Q(1),Q(2)),))
    assert result.worst_transition_probability==golden
    assert result.maximum_gold_regret==robust
    assert result.worst_gold_parameters==(Q(2),)
    assert result.endpoint_only_max_regret==0
    assert result.gold_challenger_policy.action==0
    assert result.proxy_chosen_policy.action==1
    assert len(result.transition_breakpoints)==3
    assert len(result.proxy_regions)==2
    assert not result.isolated_tie_points
    for p in (Q(0),Q(1,4),Q(1,2),Q(2,3),Q(3,4),Q(1)):
        expected=(Q(1,2)*p*p if p*p<=1-p else Q(0))
        values=direct_rational_policy_scan(game,p,(Q(1),))
        assert values[0]==expected
        assert values[2]>=0
    # The uniform reference prior grants gold only in the UGC world
    # where the declared constraint-satisfaction action is safe.
    point=switching_kernel_robust_certificate(game,((Q(1),Q(1)),))
    assert point.maximum_gold_regret==fixed
    assert point.maximum_gold_regret < result.maximum_gold_regret


def test_irrational_switch_gold_uncertainty_vertices():
    game=irrational_proxy_crossing_fixture()
    cert=switching_kernel_robust_certificate(
        game,((Q(1),Q(2)),),
    )
    expected=ExactQuadratic(Q(3),Q(-1),Q(5))
    assert cert.maximum_gold_regret==expected
    assert cert.worst_transition_probability==ExactQuadratic(
        Q(-1,2),Q(1,2),Q(5)
    )
    assert cert.worst_gold_parameters==(Q(2),)
    assert cert.endpoint_only_max_regret==0
    assert cert.maximum_expected_discrepancy_width>=cert.maximum_gold_regret
    assert cert.guaranteed_gold_floor==0


def test_single_parameter_tangency_creates_an_isolated_bad_proxy_tie():
    game=isolated_tangent_proxy_tie_fixture()
    cert=switching_kernel_robust_certificate(game,((Q(1),Q(1)),))
    assert cert.maximum_gold_regret==1
    assert cert.worst_transition_probability==Q(1,2)
    assert cert.endpoint_only_max_regret==0
    assert cert.isolated_tie_points==(ExactQuadratic(Q(1,2)),)
    assert len(cert.proxy_regions)==2
    assert cert.gold_challenger_policy.action==0
    assert cert.proxy_chosen_policy.action==1
    assert cert.maximum_expected_discrepancy_width==1
    assert cert.guaranteed_gold_floor==0
    for p in (Q(0),Q(1,4),Q(1,2),Q(3,4),Q(1)):
        direct=direct_rational_policy_scan(game,p,(Q(1),))
        assert direct[0]==(Q(1) if p==Q(1,2) else Q(0))


def test_existing_constant_winner_baselines_agree_exactly():
    for fixture in (interior_transition_hack_fixture,
                    ugc_coupled_shared_transition_fixture):
        game=fixture()
        prior=shared_kernel_robust_certificate(
            game,((Q(1),Q(2)),)
        )
        new=switching_kernel_robust_certificate(
            game,((Q(1),Q(2)),)
        )
        assert new.maximum_gold_regret==prior.maximum_gold_regret
        assert new.worst_transition_probability==prior.worst_transition_probability
        assert new.endpoint_only_max_regret==prior.endpoint_only_max_regret
        assert new.guaranteed_gold_floor==prior.guaranteed_gold_floor
        assert (new.maximum_expected_discrepancy_width==
                prior.maximum_expected_discrepancy_width)
        assert len(new.proxy_regions)==1
        assert new.isolated_tie_points==()


def test_existing_switching_fixture_now_certifies_all_regions():
    game=proxy_switching_fixture()
    cert=switching_kernel_robust_certificate(game,((0,0),))
    assert cert.maximum_gold_regret==0
    assert cert.maximum_expected_discrepancy_width>0
    assert ExactQuadratic(Q(1,2)) in cert.transition_breakpoints
    assert cert.distinct_proxy_winning_policies>=2
    assert cert.total_policies>2
    for p in (Q(1,4),Q(3,8),Q(1,2),Q(5,8),Q(3,4)):
        brute=direct_rational_policy_scan(game,p,(Q(0),))
        assert brute[0]==0


def test_switching_UGC_frozen_gold_contract_enforces_limits():
    game=rational_proxy_crossing_fixture()
    with pytest.raises(ValueError):
        switching_kernel_robust_certificate(game,())
    with pytest.raises(ValueError):
        switching_kernel_robust_certificate(game,((2,1),))
    with pytest.raises(ValueError):
        switching_kernel_robust_certificate(game,((1,1),),max_policies=1)
    with pytest.raises(ValueError):
        switching_kernel_robust_certificate(
            game,((1,1),),max_reward_comparisons=1
        )
    with pytest.raises(ValueError):
        switching_kernel_robust_certificate(
            game,((1,1),),max_breakpoints=2
        )
    with pytest.raises(ValueError):
        switching_kernel_robust_certificate(
            irrational_proxy_crossing_fixture(),((1,1),),isolation_bits=1
        )
    with pytest.raises(ValueError):
        switching_kernel_robust_certificate(
            game,((1,1),),maximum_allowed_regret=-1
        )
    assert not switching_kernel_robust_certificate(
        game,((1,1),),minimum_proxy_gold_return=2
    ).passes


def test_algebraic_radical_ordering_regressions_are_exact():
    rng=Random(1515)
    roots=(
        ExactQuadratic(Q(1,5),Q(1,2),Q(2)),
        ExactQuadratic(Q(2,7),Q(-1,3),Q(3)),
        ExactQuadratic(Q(0),Q(1,2),Q(5)),
        ExactQuadratic(Q(3,4)),
        ExactQuadratic(Q(-1,2),Q(1,2),Q(5)),
        ExactQuadratic(Q(7,10)),
    )
    for a,b in product(roots,repeat=2):
        expected=(float(a.rational)+float(a.coefficient)*
                  float(a.radicand)**0.5) < (
                  float(b.rational)+float(b.coefficient)*
                  float(b.radicand)**0.5)
        assert (a<b)==expected
        assert (a==b)==(not a<b and not b<a)
    for _ in range(50):
        p=Q(rng.randint(0,100),100)
        assert ExactQuadratic(p)==p
        assert not ExactQuadratic(p)<p
