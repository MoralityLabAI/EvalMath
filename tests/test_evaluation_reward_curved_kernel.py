"""RHT-17: exact curved semialgebraic proxy winners and gold regret.

Independently check the symbolic curved-region result against the older
RHT-13 numeric hidden-world/observation policy census. In addition to
a strict interior irrational optimum, test two bilinear boundaries with
an irrational intersection, exact lower-dimensional ties, signed gold,
gold/source identities and fail-closed degree/resource contracts.
"""
from dataclasses import replace
from fractions import Fraction as Q
from itertools import product

import pytest

from spiral_ln.evaluation_reward_two_kernel import BiPoly
from spiral_ln.evaluation_reward_two_kernel_fixture import (
    curved_proxy_switch_fixture,ugc_curved_proxy_switch_fixture,
    nonlinear_proxy_two_parameter_fixture,
    nonmultiaffine_gold_two_parameter_fixture,
    diagonal_only_proxy_tie_fixture,
    two_parameter_goodhart_fixture,
)
from spiral_ln.evaluation_reward_curved_kernel import (
    ExactQuadratic,_add,_mul,_div,_evaluate,_critical_points,
    _vertical_slice,curved_winner_region,curved_region_extreme,
    curved_kernel_robust_certificate,
)
from spiral_ln.evaluation_reward_shared_kernel import enumerate_observation_policies
from spiral_ln.evaluation_reward_stochastic_closure import policy_occupancy


ROOT=ExactQuadratic(Q(-1),Q(1),Q(2))
GOLD=ExactQuadratic(Q(6),Q(-4),Q(2))


def independent_rht13_scan(game,p,q,theta):
    """Brute numeric world/observation-policy return census at rational p,q."""
    model=game.instantiate(p,q)
    values=[]
    for policy in enumerate_observation_policies(game):
        occupation=policy_occupancy(model,policy)
        true=occupation.gold_base+sum(
            (Q(v)*Q(t) for v,t in zip(
                occupation.gold_feature_occupancy,theta
            )),Q(0)
        )
        values.append((occupation.proxy,true,policy))
    max_proxy=max(item[0] for item in values)
    min_selected_gold=min(g for p,g,_ in values if p==max_proxy)
    true_optimum=max(g for _,g,_ in values)
    gaps=tuple(p-g for p,g,_ in values)
    return (
        true_optimum-min_selected_gold,
        max(gaps)-min(gaps),min_selected_gold
    )


def test_exact_quadratic_field_arithmetic_and_curved_boundary_value():
    assert ROOT>Q(2,5) and ROOT<Q(1,2)
    assert _mul(ROOT,ROOT)==ExactQuadratic(Q(3),Q(-2),Q(2))
    assert _mul(_add(1,ROOT),_add(1,ROOT))==2
    assert _div(_add(1,_mul(-1,ROOT)),_add(1,ROOT))==ROOT
    f=BiPoly(((0,0,Q(1)),(1,0,Q(-1)),
              (0,1,Q(-1)),(1,1,Q(1))))
    assert _evaluate(f,ROOT,ROOT)==GOLD
    assert Q(1,4)<GOLD<Q(1,2)


def test_strict_curved_boundary_interior_irrational_maximum():
    game=curved_proxy_switch_fixture()
    cert=curved_kernel_robust_certificate(
        game,((1,1),),maximum_allowed_regret=Q(1,2),
        minimum_proxy_gold_return=0
    )
    assert cert.maximum_gold_regret==GOLD
    assert cert.worst_transition_parameters==(ROOT,ROOT)
    assert cert.worst_gold_parameters==(Q(1),)
    assert cert.rectangle_corner_only_regret==0
    assert cert.maximum_expected_discrepancy_width==2
    assert cert.guaranteed_gold_floor==0
    assert cert.worst_proxy_gold==0
    assert cert.proxy_chosen_policy.action==1
    assert cert.challenger_policy.action==0
    assert cert.policies_enumerated==8
    assert cert.passes
    assert not curved_kernel_robust_certificate(
        game,((1,1),),maximum_allowed_regret=Q(1,4)
    ).passes
    assert any(region.feasible_strips for region in cert.winning_regions)


def test_global_gold_box_is_exactly_optimized_at_its_vertices():
    game=curved_proxy_switch_fixture()
    cert=curved_kernel_robust_certificate(game,((Q(1),Q(2)),))
    assert cert.maximum_gold_regret==ExactQuadratic(Q(12),Q(-8),Q(2))
    assert cert.worst_transition_parameters==(ROOT,ROOT)
    assert cert.worst_gold_parameters==(Q(2),)
    assert cert.rectangle_corner_only_regret==0
    assert cert.maximum_expected_discrepancy_width==2
    assert cert.worst_proxy_gold==0
    assert not curved_kernel_robust_certificate(
        game,((1,2),),minimum_proxy_gold_return=Q(1,20)
    ).passes


def test_two_actual_UGC_worlds_preserve_curved_safety_obstruction():
    game=ugc_curved_proxy_switch_fixture()
    cert=curved_kernel_robust_certificate(
        game,((Q(1),Q(2)),),maximum_allowed_regret=Q(1,2)
    )
    assert cert.maximum_gold_regret==GOLD
    assert cert.worst_gold_parameters==(Q(2),)
    assert cert.worst_transition_parameters==(ROOT,ROOT)
    assert cert.rectangle_corner_only_regret==0
    assert cert.maximum_expected_discrepancy_width==2
    assert cert.challenger_policy.action==0
    assert cert.proxy_chosen_policy.action==1
    assert cert.passes
    for p,q in (
        (Q(0),Q(0)),(Q(0),Q(1)),(Q(1),Q(0)),(Q(1),Q(1)),
        (Q(1,4),Q(1,2)),(Q(1,2),Q(1,4)),
        (Q(2,5),Q(3,7)),(Q(3,5),Q(1,4))
    ):
        expected=((Q(1)-p)*(Q(1)-q)
                  if q*(1+p)>=1-p else Q(0))
        # At theta=2, the one UGC-safe reference world contributes
        # one-half the reward, recovering (1-p)*(1-q).
        assert independent_rht13_scan(game,p,q,(Q(2),))[0]==expected


def test_bilinear_boundary_intersection_has_irrational_critical_p():
    # The policy with proxy 0 must dominate two competitors, imposing
    #   q >= (1-p)/(1+p), and q >= p.
    # Their boundaries cross at the exact irrational p=sqrt(2)-1.
    h1=BiPoly(((0,0,Q(-1)),(1,0,Q(1)),
               (0,1,Q(1)),(1,1,Q(1))))
    h2=BiPoly(((1,0,Q(-1)),(0,1,Q(1))))
    candidates=(BiPoly(),-h1,-h2)
    game=curved_proxy_switch_fixture()
    region=curved_winner_region(game,candidates,0)
    assert ROOT in region.critical_p
    assert (ROOT,ROOT,ROOT) in region.feasible_vertical_slices
    protected=BiPoly(((0,0,Q(1)),(1,0,Q(-1)),
                      (0,1,Q(-1)),(1,1,Q(1))))
    result=curved_region_extreme(protected,region,maximize=True)
    assert result==(GOLD,(ROOT,ROOT))
    assert len(region.feasible_strips)>=2
    for p in (Q(0),Q(1,4),Q(1,2),Q(3,4),Q(1)):
        for q in (Q(0),Q(1,4),Q(1,2),Q(3,4),Q(1)):
            feasible=h1.value(p,q)>=0 and h2.value(p,q)>=0
            point=_vertical_slice(
                ((Q(-1),Q(1),Q(1),Q(1)),
                 (Q(0),Q(-1),Q(1),Q(0))),
                ExactQuadratic(p),Q(0),Q(1)
            )
            assert (point is not None and point[0][0]<=q<=point[1][0])==feasible


def test_formerly_rejected_nonlinear_proxy_is_now_certifiable():
    # RHT-16 rejected this model because first/second-step rewards
    # produce a pq proxy term. RHT-17 has a complete multiaffine proxy
    # winner analysis, including zero-area tie boundaries p=1 or q=0.
    game=nonlinear_proxy_two_parameter_fixture()
    cert=curved_kernel_robust_certificate(game,((Q(1),Q(1)),))
    assert cert.maximum_gold_regret==1
    assert cert.rectangle_corner_only_regret==1
    assert cert.maximum_expected_discrepancy_width>=1
    assert cert.proxy_chosen_policy.action==1
    assert cert.challenger_policy.action==0


def test_genuinely_gold_aligned_nonlinear_proxy_has_zero_regret():
    game=curved_proxy_switch_fixture()
    aligned=replace(game,edges=tuple(
        replace(e,gold_coefficients=(Q(e.proxy),))
        for e in game.edges
    ))
    cert=curved_kernel_robust_certificate(aligned,((Q(1),Q(2)),))
    assert cert.maximum_gold_regret==0
    assert cert.guaranteed_gold_floor==0
    assert cert.maximum_expected_discrepancy_width==2
    assert cert.passes


def test_signed_gold_and_subinterval_controls():
    signed=curved_kernel_robust_certificate(
        curved_proxy_switch_fixture(),((Q(-1),Q(1)),)
    )
    assert signed.maximum_gold_regret==1
    assert signed.worst_gold_parameters==(Q(-1),)
    blocked=curved_kernel_robust_certificate(
        curved_proxy_switch_fixture(
            p_interval=(Q(0),Q(1,4)),q_interval=(Q(0),Q(1,2))
        ),((Q(1),Q(1)),)
    )
    assert blocked.maximum_gold_regret==0
    inner=curved_kernel_robust_certificate(
        curved_proxy_switch_fixture(
            p_interval=(Q(0),Q(1,2)),q_interval=(Q(0),Q(1,2))
        ),((Q(1),Q(1)),)
    )
    assert inner.maximum_gold_regret==GOLD
    assert inner.worst_transition_parameters==(ROOT,ROOT)


def test_all_rational_grid_points_agree_with_independent_stochastic_oracle():
    for fixture in (
        curved_proxy_switch_fixture,ugc_curved_proxy_switch_fixture,
        nonlinear_proxy_two_parameter_fixture,diagonal_only_proxy_tie_fixture,
        two_parameter_goodhart_fixture
    ):
        game=fixture()
        for p,q in product(
            (Q(0),Q(1,5),Q(1,3),Q(2,5),Q(1,2),Q(3,5),Q(1)),
            repeat=2
        ):
            for theta in ((Q(1),),(Q(2),)):
                observed=independent_rht13_scan(game,p,q,theta)
                surfaces=tuple(
                    __import__("spiral_ln.evaluation_reward_two_kernel",
                               fromlist=["policy_surface"]).policy_surface(
                        game,policy
                    ) for policy in enumerate_observation_policies(game)
                )
                vals=tuple(
                    (s.proxy.value(p,q),s.gold(theta).value(p,q))
                    for s in surfaces
                )
                max_proxy=max(v[0] for v in vals)
                chosen=min(v[1] for v in vals if v[0]==max_proxy)
                gold_best=max(v[1] for v in vals)
                gaps=[v[0]-v[1] for v in vals]
                assert observed==(
                    gold_best-chosen,max(gaps)-min(gaps),chosen
                )


def test_fail_closed_high_degree_and_resource_caps():
    with pytest.raises(ValueError,match="non-multiaffine"):
        curved_kernel_robust_certificate(
            nonmultiaffine_gold_two_parameter_fixture(),((1,1),)
        )
    game=curved_proxy_switch_fixture()
    with pytest.raises(ValueError):
        curved_kernel_robust_certificate(game,())
    with pytest.raises(ValueError):
        curved_kernel_robust_certificate(game,((2,1),))
    with pytest.raises(ValueError):
        curved_kernel_robust_certificate(game,((1,1),),max_policies=1)
    with pytest.raises(ValueError):
        curved_kernel_robust_certificate(game,((1,1),),max_reward_pairs=1)
    with pytest.raises(ValueError):
        curved_kernel_robust_certificate(game,((1,1),),max_roots=1)
    with pytest.raises(ValueError):
        curved_kernel_robust_certificate(
            game,((1,1),),maximum_allowed_regret=-1
        )
    assert not curved_kernel_robust_certificate(
        game,((1,1),),minimum_proxy_gold_return=1
    ).passes
