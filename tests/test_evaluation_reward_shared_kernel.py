"""RHT-14: exact shared-transition polynomial witness and nonrectangular controls.

The production polynomial policy evaluator is checked against the
independent RHT-13 world/observation occupancy enumerator at rational p.
A second independent full policy census checks worst-case regret
directly at multiple p and gold points. Closed-form p(1-p) witnesses
expose the failure of endpoint-only transition uncertainty.
"""
from fractions import Fraction as Q
from itertools import product

import pytest

from spiral_ln.evaluation_reward_shared_kernel import (
    SharedTransitionEdge, SharedTransitionGame,
    enumerate_observation_policies, polynomial_policy_returns,
    shared_kernel_robust_certificate,
)
from spiral_ln.evaluation_reward_shared_kernel_fixture import (
    interior_transition_hack_fixture,
    ugc_coupled_shared_transition_fixture,
    proxy_switching_fixture,
)
from spiral_ln.evaluation_reward_stochastic_closure import (
    optimize_stochastic_policy, policy_occupancy,
)


def direct_census_at(game,p,theta):
    """Independent complete policy scan using ordinary RHT-13 transitions."""
    instant=game.instantiate(p)
    data=[]
    for policy in enumerate_observation_policies(game):
        occupancy=policy_occupancy(instant,policy)
        gold=occupancy.gold_base+sum(
            (coefficient*value for coefficient,value
             in zip(occupancy.gold_feature_occupancy,theta)),Q(0)
        )
        data.append((occupancy.proxy,gold,policy))
    best_proxy=max(x[0] for x in data)
    proxy_winners=[x for x in data if x[0]==best_proxy]
    gold_best=max(x[1] for x in data)
    low_gold=min(x[1] for x in proxy_winners)
    gaps=[x[0]-x[1] for x in data]
    return (
        gold_best-low_gold,max(gaps)-min(gaps),low_gold,
        len(proxy_winners),len(data),
    )


def test_strict_interior_worst_case_missed_by_transition_endpoints():
    game=interior_transition_hack_fixture()
    exact=shared_kernel_robust_certificate(
        game,((1,1),),maximum_allowed_regret=Q(1,4)
    )
    assert exact.maximum_gold_regret==Q(1,4)
    assert exact.worst_transition_probability==Q(1,2)
    assert exact.worst_gold_parameters==(Q(1),)
    assert exact.endpoint_only_max_regret==0
    assert exact.guaranteed_gold_floor==0
    assert exact.maximum_expected_discrepancy_width==Q(5,4)
    assert exact.proxy_optimal_policies==4
    assert exact.total_policies==8
    assert exact.passes
    assert exact.gold_challenger_policy.action==1
    assert exact.proxy_chosen_policy.action==0
    assert direct_census_at(game,Q(1,2),(Q(1),))[:3]==(
        Q(1,4),Q(5,4),Q(0)
    )
    assert direct_census_at(game,Q(0),(Q(1),))[:3]==(
        Q(0),Q(1),Q(0)
    )
    assert direct_census_at(game,Q(1),(Q(1),))[:3]==(
        Q(0),Q(1),Q(0)
    )
    assert not shared_kernel_robust_certificate(
        game,((1,1),),maximum_allowed_regret=Q(1,5)
    ).passes


def test_independently_licensed_gold_vertex_remains_exact_with_shared_p():
    game=interior_transition_hack_fixture()
    exact=shared_kernel_robust_certificate(
        game,((Q(1),Q(2)),),
        maximum_allowed_regret=Q(1,2),
        minimum_proxy_gold_return=Q(0),
    )
    assert exact.maximum_gold_regret==Q(1,2)
    assert exact.worst_transition_probability==Q(1,2)
    assert exact.worst_gold_parameters==(Q(2),)
    assert exact.maximum_expected_discrepancy_width==Q(3,2)
    assert exact.endpoint_only_max_regret==0
    assert exact.guaranteed_gold_floor==0
    assert exact.passes
    assert not shared_kernel_robust_certificate(
        game,((1,2),),minimum_proxy_gold_return=Q(1,10)
    ).passes


def test_grounded_UGC_two_worlds_have_interior_nonrectangular_regret():
    game=ugc_coupled_shared_transition_fixture()
    cert=shared_kernel_robust_certificate(game,((1,2),))
    assert cert.maximum_gold_regret==Q(1,4)
    assert cert.worst_transition_probability==Q(1,2)
    assert cert.worst_gold_parameters==(Q(2),)
    assert cert.maximum_expected_discrepancy_width==Q(5,4)
    assert cert.endpoint_only_max_regret==0
    assert cert.proxy_optimal_policies==2
    assert cert.total_policies==6
    assert cert.gold_challenger_policy.action==1
    assert cert.proxy_chosen_policy.action==0
    for p,expected in (
        (Q(0),Q(0)),(Q(1,4),Q(3,16)),(Q(1,2),Q(1,4)),
        (Q(3,4),Q(3,16)),(Q(1),Q(0))
    ):
        # Theta=2, a successful gold result is permitted in precisely
        # one of the two actual K2,2 UGC reference worlds.
        assert direct_census_at(game,p,(Q(2),))[0]==expected


def test_analytic_stationary_check_matches_independent_POMDP_oracle():
    for fixture in (interior_transition_hack_fixture,
                    ugc_coupled_shared_transition_fixture):
        game=fixture()
        for p in (
            Q(0),Q(1,10),Q(1,4),Q(1,3),Q(1,2),
            Q(2,3),Q(3,4),Q(9,10),Q(1)
        ):
            for theta in (Q(1),Q(3,2),Q(2)):
                expected=direct_census_at(game,p,(theta,))
                policies=enumerate_observation_policies(game)
                symbolics=tuple(polynomial_policy_returns(game,pi) for pi in policies)
                evaluations=tuple((
                    sum((coefficient*(p**i)
                         for i,coefficient in enumerate(item.proxy)),Q(0)),
                    sum((coefficient*(p**i)
                         for i,coefficient in enumerate(item.gold((theta,)))),Q(0)),
                ) for item in symbolics)
                best_proxy=max(x[0] for x in evaluations)
                selected=[x[1] for x in evaluations if x[0]==best_proxy]
                gold_best=max(x[1] for x in evaluations)
                gap=[x[0]-x[1] for x in evaluations]
                actual=(gold_best-min(selected),max(gap)-min(gap),
                        min(selected),len(selected),len(symbolics))
                assert actual==expected
                # Crosscheck the existing RHT-13 Bellman optimum.
                result=optimize_stochastic_policy(
                    game.instantiate(p),(theta,),objective="proxy_worst_gold"
                )
                assert result.proxy_return==best_proxy
                assert result.gold_return==min(selected)


def test_same_uncertain_probability_is_shared_across_two_transitions():
    game=interior_transition_hack_fixture()
    policies=enumerate_observation_policies(game)
    act_B=next(p for p in policies if p.action==1)
    polynomials=polynomial_policy_returns(game,act_B)
    assert polynomials.proxy==(Q(0),)
    assert polynomials.gold_base==(Q(0),)
    assert polynomials.gold_features[0]==(Q(0),Q(1),Q(-1))
    ugc=ugc_coupled_shared_transition_fixture()
    act=next(p for p in enumerate_observation_policies(ugc) if p.action==1)
    assert polynomial_policy_returns(ugc,act).gold_features[0]==(
        Q(0),Q(1,2),Q(-1,2)
    )


def test_proxy_winner_switching_raises_instead_of_falsely_certifying():
    game=proxy_switching_fixture()
    assert len(enumerate_observation_policies(game))>1
    with pytest.raises(ValueError,match="proxy winner crosses or ties"):
        shared_kernel_robust_certificate(game,((0,0),))
    # Here the proxy prefers action A for large p and B for small p.
    a=game.instantiate(Q(1,4))
    b=game.instantiate(Q(3,4))
    first_a=optimize_stochastic_policy(a,(0,)).policy.action
    first_b=optimize_stochastic_policy(b,(0,)).policy.action
    assert first_a!=first_b


def test_rational_parameter_subinterval_has_correct_interior_max():
    g=interior_transition_hack_fixture(interval=(Q(1,4),Q(3,4)))
    cert=shared_kernel_robust_certificate(g,((1,1),))
    assert cert.maximum_gold_regret==Q(1,4)
    assert cert.endpoint_only_max_regret==Q(3,16)
    assert cert.worst_transition_probability==Q(1,2)
    short=interior_transition_hack_fixture(interval=(Q(0),Q(1,4)))
    result=shared_kernel_robust_certificate(short,((1,1),))
    assert result.maximum_gold_regret==Q(3,16)
    assert result.worst_transition_probability==Q(1,4)
    assert result.endpoint_only_max_regret==Q(3,16)


def test_independent_transition_rectangularization_is_overconservative():
    # Two independent Bernoulli parameters permit first trial success
    # with probability one and second trial failure with probability one.
    # A physically shared p forces the gold event probability p*(1-p),
    # with a sharp interior ceiling of 1/4 instead of one.
    shared=shared_kernel_robust_certificate(
        interior_transition_hack_fixture(),((1,1),)
    )
    independent=max(p*(1-q) for p,q in product(
        (Q(0),Q(1)),repeat=2
    ))
    assert shared.maximum_gold_regret==Q(1,4)
    assert shared.endpoint_only_max_regret==0
    assert independent==1
    assert independent==4*shared.maximum_gold_regret


def test_gold_uncertainty_signs_and_nominal_policies():
    g=interior_transition_hack_fixture()
    cert=shared_kernel_robust_certificate(
        g,((Q(-1),Q(1)),),
    )
    assert cert.maximum_gold_regret==Q(1,4)
    assert cert.worst_gold_parameters==(Q(1),)
    assert cert.endpoint_only_max_regret==0
    assert cert.guaranteed_gold_floor==0


def test_invalid_nonrectangular_model_and_resource_caps_fail_closed():
    g=interior_transition_hack_fixture()
    with pytest.raises(ValueError):
        shared_kernel_robust_certificate(g,())
    with pytest.raises(ValueError):
        shared_kernel_robust_certificate(g,((2,1),))
    with pytest.raises(ValueError):
        shared_kernel_robust_certificate(g,((1,1),),max_policies=1)
    with pytest.raises(ValueError):
        shared_kernel_robust_certificate(
            g,((1,1),),maximum_allowed_regret=-1
        )
    with pytest.raises(ValueError):
        g.instantiate(Q(2))
    with pytest.raises(ValueError):
        SharedTransitionGame(
            1,("x",),(Q(1),),("gold",),(Q(0),Q(1)),
            (SharedTransitionEdge(
                0,0,0,"bad",Q(1),Q(-2),gold_coefficients=(Q(0),)
            ),),2
        )
    with pytest.raises(ValueError):
        SharedTransitionGame(
            1,("x",),(Q(1),),("gold",),(Q(0),Q(1)),
            (SharedTransitionEdge(
                0,0,0,"bad",Q(1),Q(1),gold_coefficients=(Q(0),)
            ),),2
        )
    with pytest.raises(ValueError):
        SharedTransitionGame(
            1,("x",),(Q(1),),("gold",),(Q(0),Q(1)),
            (SharedTransitionEdge(
                0,0,0,"bad",Q(0),Q(0),gold_coefficients=(Q(0),)
            ),),2
        )
    with pytest.raises(ValueError):
        SharedTransitionGame(
            1,("x",),(Q(1),),("gold",),(Q(-1),Q(1)),
            (SharedTransitionEdge(
                0,0,0,"good",Q(1),Q(0),gold_coefficients=(Q(0),)
            ),),2
        )
