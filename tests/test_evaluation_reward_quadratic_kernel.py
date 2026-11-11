"""RHT-18: sharp cubic stationary points on parabolic proxy boundaries.

Independent RHT-13 exact policy occupancy is evaluated at rational
(p,q) values and compared with the symbolic q-quadratic region certificate.
Closed-form calculus checks the interior sqrt(3)/3 witness; explicit
one-dimensional discriminant roots check the polynomial partition.
"""
from fractions import Fraction as Q
from itertools import product

import pytest

from spiral_ln.evaluation_reward_kernel_switching import ExactQuadratic
from spiral_ln.evaluation_reward_two_kernel import (
    BiPoly,TwoKernelEdge,TwoKernelGame,two_kernel_robust_certificate,
)
from spiral_ln.evaluation_reward_curved_kernel import curved_kernel_robust_certificate
from spiral_ln.evaluation_reward_two_kernel_fixture import (
    two_parameter_goodhart_fixture,curved_proxy_switch_fixture,
)
from spiral_ln.evaluation_reward_quadratic_kernel import (
    _quadratic_value,_cubic_extremum,_gold_value,
    quadratic_proxy_winner_region,quadratic_region_extreme,
    quadratic_kernel_robust_certificate,
)
from spiral_ln.evaluation_reward_quadratic_kernel_fixture import (
    quadratic_parabola_goodhart_fixture,
)
from spiral_ln.evaluation_reward_shared_kernel import enumerate_observation_policies
from spiral_ln.evaluation_reward_stochastic_closure import (
    optimize_stochastic_policy,policy_occupancy
)


ROOT=ExactQuadratic(Q(0),Q(1,3),Q(3))
VALUE=ExactQuadratic(Q(0),Q(2,9),Q(3))


def direct_rht13_at(game,p,q,theta):
    """Independent complete policy census through the numeric POMDP engine."""
    numeric=game.instantiate(p,q)
    values=[]
    for pi in enumerate_observation_policies(game):
        occ=policy_occupancy(numeric,pi)
        true=occ.gold_base+sum(
            (c*t for c,t in zip(occ.gold_feature_occupancy,theta)),Q(0)
        )
        values.append((occ.proxy,true,pi))
    proxy_best=max(x[0] for x in values)
    winners=tuple(x for x in values if x[0]==proxy_best)
    gold_best=max(x[1] for x in values)
    gold_chosen=min(x[1] for x in winners)
    gaps=tuple(x[0]-x[1] for x in values)
    return gold_best-gold_chosen,max(gaps)-min(gaps),gold_chosen,len(winners)


def test_cubic_exact_stationary_point_and_quadratic_algebraic_value():
    # Gold along q=p² is p-p³, maximized at p=sqrt(3)/3.
    poly=(Q(0),Q(1),Q(0),Q(-1))
    result=_cubic_extremum(poly,ExactQuadratic(0),ExactQuadratic(1),
                           maximize=True)
    assert result==(VALUE,ROOT)
    assert _quadratic_value((0,0,1),ROOT)==Q(1,3)
    assert _cubic_extremum(poly,ExactQuadratic(0),ExactQuadratic(Q(1,2)),
                           maximize=True)==(
                               ExactQuadratic(Q(3,8)),
                               ExactQuadratic(Q(1,2))
                           )
    assert _gold_value(
        BiPoly(((1,0,Q(1)),(1,1,Q(-1)))),
        ROOT,ExactQuadratic(Q(1,3))
    )==VALUE


def test_parabolic_proxy_switch_has_exact_interior_irrational_regret():
    game=quadratic_parabola_goodhart_fixture()
    with pytest.raises(ValueError,match="non-affine proxy"):
        two_kernel_robust_certificate(game,((1,1),))
    with pytest.raises(ValueError,match="non-multiaffine"):
        curved_kernel_robust_certificate(game,((1,1),))
    cert=quadratic_kernel_robust_certificate(
        game,((Q(1),Q(1)),),
        maximum_allowed_regret=Q(2,5),
        minimum_proxy_gold_return=0,
    )
    assert cert.maximum_gold_regret==VALUE
    assert cert.worst_transition_parameters==(
        ROOT,ExactQuadratic(Q(1,3))
    )
    assert cert.worst_gold_parameters==(Q(1),)
    assert cert.rectangle_corner_only_regret==0
    assert cert.maximum_expected_discrepancy_width==1
    assert cert.guaranteed_gold_floor==0
    assert cert.proxy_chosen_policy.action==1
    assert cert.challenger_policy.action==0
    assert cert.policy_count==8
    assert cert.passes
    assert not quadratic_kernel_robust_certificate(
        game,((1,1),),maximum_allowed_regret=Q(3,8)
    ).passes
    assert any(r.feasible_strips for r in cert.winning_regions)
    for p in (Q(0),Q(1,5),Q(1,3),Q(1,2),Q(2,3),Q(1)):
        for q in (Q(0),Q(1,4),Q(1,3),Q(1,2),Q(3,4),Q(1)):
            oracle=direct_rht13_at(game,p,q,(Q(1),))
            expected=p*(1-q) if q>=p*p else Q(0)
            assert oracle[0]==expected
            bellman=optimize_stochastic_policy(
                game.instantiate(p,q),(Q(1),),
                objective="proxy_worst_gold"
            )
            assert bellman.gold_return==oracle[2]


def test_interval_gold_and_UGC_safe_reference_coupling():
    game=quadratic_parabola_goodhart_fixture()
    uncertain=quadratic_kernel_robust_certificate(game,((Q(1),Q(2)),))
    assert uncertain.maximum_gold_regret==ExactQuadratic(
        Q(0),Q(4,9),Q(3)
    )
    assert uncertain.worst_gold_parameters==(Q(2),)
    assert uncertain.worst_transition_parameters==(ROOT,ExactQuadratic(Q(1,3)))
    assert uncertain.maximum_expected_discrepancy_width==1
    ugc=quadratic_parabola_goodhart_fixture(ugc_worlds=True)
    grounded=quadratic_kernel_robust_certificate(ugc,((Q(1),Q(2)),))
    assert grounded.maximum_gold_regret==VALUE
    assert grounded.worst_gold_parameters==(Q(2),)
    assert grounded.worst_transition_parameters==(
        ROOT,ExactQuadratic(Q(1,3))
    )
    assert grounded.rectangle_corner_only_regret==0
    assert grounded.guaranteed_gold_floor==0
    assert grounded.maximum_expected_discrepancy_width==1
    for p,q in (
        (Q(0),Q(0)),(Q(1),Q(1)),(Q(1),Q(0)),
        (Q(1,4),Q(1,2)),(Q(1,2),Q(1,4)),
        (Q(2,3),Q(1,2)),(Q(3,4),Q(3,4)),
    ):
        expect=p*(1-q) if q>=p*p else Q(0)
        assert direct_rht13_at(ugc,p,q,(Q(2),))[0]==expect


def test_proxy_tie_only_on_curved_parabola_retained():
    game=quadratic_parabola_goodhart_fixture(extra_tangent_policy=True)
    cert=quadratic_kernel_robust_certificate(
        game,((1,1),),max_policies=100,
    )
    assert cert.maximum_gold_regret==VALUE
    assert cert.worst_transition_parameters==(
        ROOT,ExactQuadratic(Q(1,3))
    )
    policies=enumerate_observation_policies(game)
    tangent=tuple(
        r for r in cert.winning_regions if policies[r.policy_index].action==2
    )
    assert len(tangent)>0
    assert all(r.feasible_strips for r in tangent)
    for region in tangent:
        assert all(low==high for _,_,low,high in region.feasible_strips)
    for p,q in ((Q(0),Q(0)),(Q(1,2),Q(1,4)),(Q(1),Q(1)),
                (Q(1,2),Q(1,2)),(Q(1,2),Q(0))):
        gap=direct_rht13_at(game,p,q,(Q(1),))[0]
        assert gap==(p*(1-q) if q>=p*p else Q(0))


def test_exact_quadratic_boundary_intersection_with_golden_ratio():
    # Candidate policy 0 must satisfy q >= p² and q >= 1-p.
    p=BiPoly(((1,0,Q(1)),))
    p2=p*p
    q=BiPoly(((0,1,Q(1)),))
    winning=(BiPoly(),p2-q,BiPoly.constant(1)-p-q)
    region=quadratic_proxy_winner_region(
        quadratic_parabola_goodhart_fixture(),winning,0
    )
    golden=ExactQuadratic(Q(-1,2),Q(1,2),Q(5))
    assert golden in region.breakpoints
    assert len(region.feasible_strips)>=2
    assert any(pt==golden for pt,low,high in region.vertical_slices)
    for px,qy in product(
        (Q(0),Q(1,4),Q(1,2),Q(3,4),Q(1)),repeat=2
    ):
        possible=qy>=px*px and qy>=1-px
        from spiral_ln.evaluation_reward_quadratic_kernel import _selected
        # Compare analytic inequalities with union of strip/slice geometry.
        at=tuple(r for r in region.feasible_strips
                 if r[0]<=px<=r[1])
        slices=tuple(r for r in region.vertical_slices if r[0]==px)
        in_region=any(
            _quadratic_value(l,px)<=qy<=_quadratic_value(u,px)
            for _,_,l,u in at
        ) or any(low<=qy<=high for _,low,high in slices)
        assert in_region==possible


def test_constant_proxy_and_affine_proxy_baselines_match_RHT16():
    game=two_parameter_goodhart_fixture()
    for values in (((Q(1),Q(1)),),((Q(1),Q(2)),)):
        earlier=two_kernel_robust_certificate(game,values)
        latest=quadratic_kernel_robust_certificate(game,values)
        assert latest.maximum_gold_regret==earlier.maximum_gold_regret
        assert latest.guaranteed_gold_floor==earlier.guaranteed_gold_floor
        assert (latest.maximum_expected_discrepancy_width==
                earlier.maximum_expected_discrepancy_width)
        assert latest.rectangle_corner_only_regret==earlier.rectangle_corner_only_regret
    return


def test_licensed_kernel_subrectangles_and_exact_boundaries():
    lower=quadratic_parabola_goodhart_fixture(
        p_interval=(Q(0),Q(1,2))
    )
    c=quadratic_kernel_robust_certificate(lower,((1,1),))
    assert c.maximum_gold_regret==Q(3,8)
    assert c.worst_transition_parameters==(
        ExactQuadratic(Q(1,2)),ExactQuadratic(Q(1,4))
    )
    disjoint=quadratic_parabola_goodhart_fixture(
        p_interval=(Q(3,4),Q(1)),q_interval=(Q(0),Q(1,4))
    )
    no=quadratic_kernel_robust_certificate(disjoint,((1,1),))
    assert no.maximum_gold_regret==0
    assert no.guaranteed_gold_floor>=0
    upper=quadratic_parabola_goodhart_fixture(
        p_interval=(Q(0),Q(1,4)),q_interval=(Q(1,2),Q(1))
    )
    up=quadratic_kernel_robust_certificate(upper,((1,1),))
    assert up.maximum_gold_regret==Q(1,8)
    assert up.worst_transition_parameters==(
        ExactQuadratic(Q(1,4)),ExactQuadratic(Q(1,2))
    )


def test_nonq_affine_proxy_and_q_squared_gold_fail_closed():
    with pytest.raises(ValueError,match="proxy must be q-affine"):
        quadratic_kernel_robust_certificate(
            curved_proxy_switch_fixture(),((1,1),)
        )
    edges=[]
    def add(s,a,t,o,b=0,dq=0,gold=0):
        edges.append(TwoKernelEdge(
            s,a,t,o,Q(b),Q(0),Q(dq),Q(0),Q(0),(Q(gold),)
        ))
    add(0,0,1,"first-pass",dq=1)
    add(0,0,2,"first-fail",b=1,dq=-1)
    add(1,0,2,"second-pass",dq=1,gold=1)
    add(1,0,2,"second-fail",b=1,dq=-1)
    add(2,0,2,"done",b=1)
    gold_q2=TwoKernelGame(
        state_count=3,actions=("only",),initial=(Q(1),Q(0),Q(0)),
        gold_parameters=("gold",),
        p_interval=(Q(0),Q(1)),q_interval=(Q(0),Q(1)),
        edges=tuple(edges),horizon=2
    )
    with pytest.raises(ValueError,match="gold must"):
        quadratic_kernel_robust_certificate(gold_q2,((1,1),))


def test_invalid_gold_intervals_and_resource_caps_fail_closed():
    g=quadratic_parabola_goodhart_fixture()
    with pytest.raises(ValueError):
        quadratic_kernel_robust_certificate(g,())
    with pytest.raises(ValueError):
        quadratic_kernel_robust_certificate(g,((2,1),))
    with pytest.raises(ValueError):
        quadratic_kernel_robust_certificate(g,((1,1),),max_policies=1)
    with pytest.raises(ValueError):
        quadratic_kernel_robust_certificate(g,((1,1),),max_reward_pairs=1)
    with pytest.raises(ValueError):
        quadratic_kernel_robust_certificate(g,((1,1),),max_breakpoints=1)
    with pytest.raises(ValueError):
        quadratic_kernel_robust_certificate(g,((1,1),),maximum_allowed_regret=-1)
    assert not quadratic_kernel_robust_certificate(
        g,((1,1),),minimum_proxy_gold_return=1
    ).passes
