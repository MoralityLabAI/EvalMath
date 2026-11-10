"""RHT-16: independent stochastic policy checks for exact 2D robust gold regret.

The product POMDP evaluation is independently computed using the old
RHT-13 world/observation occupancy oracle at multiple rational (p,q)
values and licensed gold vertices. The new bivariate symbolic solver,
convex polygon witness and rational edge stationary points must agree.
"""
from fractions import Fraction as Q
from itertools import product
from random import Random

import pytest

from spiral_ln.evaluation_reward_two_kernel import (
    BiPoly,TwoKernelGame,TwoKernelEdge,
    clip_polygon,bilinear_extreme,policy_surface,
    winning_polygon,two_kernel_robust_certificate,
)
from spiral_ln.evaluation_reward_two_kernel_fixture import (
    two_parameter_goodhart_fixture,
    ugc_two_parameter_goodhart_fixture,
    proxy_aligned_two_parameter_fixture,
    nonlinear_proxy_two_parameter_fixture,
    nonmultiaffine_gold_two_parameter_fixture,
    diagonal_only_proxy_tie_fixture,
)
from spiral_ln.evaluation_reward_shared_kernel import enumerate_observation_policies
from spiral_ln.evaluation_reward_stochastic_closure import (
    policy_occupancy,optimize_stochastic_policy,
)


def direct_policy_census(game,p,q,theta):
    """Independent full policy census through RHT-13's numeric occupancy."""
    numeric=game.instantiate(p,q)
    data=[]
    for policy in enumerate_observation_policies(game):
        occ=policy_occupancy(numeric,policy)
        true=occ.gold_base+sum(
            (v*t for v,t in zip(occ.gold_feature_occupancy,theta)),Q(0)
        )
        data.append((occ.proxy,true,policy))
    best_proxy=max(v[0] for v in data)
    winners=tuple(v for v in data if v[0]==best_proxy)
    gold_best=max(v[1] for v in data)
    chosen_gold=min(v[1] for v in winners)
    gaps=[p-g for p,g,_ in data]
    return gold_best-chosen_gold,max(gaps)-min(gaps),chosen_gold,len(winners)


def test_bivariate_polynomial_and_exact_diagonal_witness():
    p=BiPoly(((1,0,Q(1)),))
    q=BiPoly(((0,1,Q(1)),))
    f=p*(BiPoly.constant(1)-q)
    assert f.value(Q(1,2),Q(1,2))==Q(1,4)
    assert f.coefficient(1,0)==1
    assert f.coefficient(1,1)==-1
    assert f.affine is False and f.multiaffine
    assert (p-q).affine
    triangle=((Q(0),Q(0)),(Q(0),Q(1)),(Q(1),Q(1)))
    value,witness=bilinear_extreme(f,triangle,maximize=True)
    assert (value,witness)==(Q(1,4),(Q(1,2),Q(1,2)))
    assert bilinear_extreme(f,triangle,maximize=False)[0]==0
    assert bilinear_extreme(f,((Q(0),Q(0)),),maximize=True)==(
        Q(0),(Q(0),Q(0))
    )
    assert (p*q).multiaffine
    assert not (p*p).multiaffine
    assert (p+q)*BiPoly.constant(0)==BiPoly()


def test_switching_diagonal_interior_regret_and_endpoint_miss():
    game=two_parameter_goodhart_fixture()
    cert=two_kernel_robust_certificate(
        game,((1,1),),maximum_allowed_regret=Q(1,4),
        minimum_proxy_gold_return=0,
    )
    assert cert.maximum_gold_regret==Q(1,4)
    assert cert.worst_transition_parameters==(Q(1,2),Q(1,2))
    assert cert.worst_gold_parameters==(Q(1),)
    assert cert.rectangle_corner_only_regret==0
    assert cert.maximum_expected_discrepancy_width==1
    assert cert.guaranteed_gold_floor==0
    assert cert.challenger_policy.action==0
    assert cert.proxy_chosen_policy.action==1
    assert cert.policies_enumerated==6
    assert cert.passes
    assert not two_kernel_robust_certificate(
        game,((1,1),),maximum_allowed_regret=Q(1,5)
    ).passes
    assert len(cert.winning_polygons)==6
    assert any(
        (Q(1,2),Q(1,2)) in tuple(
            tuple(v) for v in (cert.worst_transition_parameters,)
        )
        for _,poly in cert.winning_polygons if poly
    )
    assert all(
        all(0<=x<=1 and 0<=y<=1 for x,y in poly)
        for _,poly in cert.winning_polygons
    )


def test_true_gold_interval_vertices_and_nontrivial_progress_floor():
    game=two_parameter_goodhart_fixture()
    cert=two_kernel_robust_certificate(
        game,((Q(1),Q(2)),),
        maximum_allowed_regret=Q(1,2),
        minimum_proxy_gold_return=0,
    )
    assert cert.maximum_gold_regret==Q(1,2)
    assert cert.worst_gold_parameters==(Q(2),)
    assert cert.worst_transition_parameters==(Q(1,2),Q(1,2))
    assert cert.maximum_expected_discrepancy_width==1
    assert cert.rectangle_corner_only_regret==0
    assert cert.guaranteed_gold_floor==0
    assert cert.worst_proxy_gold==0
    assert cert.passes
    assert not two_kernel_robust_certificate(
        game,((1,2),),minimum_proxy_gold_return=Q(1,100)
    ).passes
    assert not two_kernel_robust_certificate(
        game,((1,2),),maximum_allowed_regret=Q(2,5)
    ).passes


def test_UGC_world_bipartite_gold_variation_preserves_diagonal_maximum():
    game=ugc_two_parameter_goodhart_fixture()
    cert=two_kernel_robust_certificate(game,((Q(1),Q(2)),))
    assert cert.maximum_gold_regret==Q(1,4)
    assert cert.worst_transition_parameters==(Q(1,2),Q(1,2))
    assert cert.worst_gold_parameters==(Q(2),)
    assert cert.rectangle_corner_only_regret==0
    assert cert.maximum_expected_discrepancy_width==1
    assert cert.challenger_policy.action==0
    assert cert.proxy_chosen_policy.action==1
    for p,q in (
        (Q(0),Q(0)),(Q(1,4),Q(1,4)),(Q(1,2),Q(1,2)),
        (Q(3,4),Q(3,4)),(Q(1),Q(1)),(Q(1,4),Q(3,4)),
        (Q(3,4),Q(1,4))
    ):
        expected=Q(1)*p*(1-q) if q>=p else Q(0)
        assert direct_policy_census(game,p,q,(Q(2),))[0]==expected


def test_independent_numeric_RHT13_occupancy_matches_bivariate_surfaces():
    rng=Random(16016)
    for fixture in (
        two_parameter_goodhart_fixture,ugc_two_parameter_goodhart_fixture,
        proxy_aligned_two_parameter_fixture,diagonal_only_proxy_tie_fixture,
    ):
        game=fixture()
        policies=enumerate_observation_policies(game)
        symbols=tuple(policy_surface(game,policy) for policy in policies)
        for p,q in (
            (Q(0),Q(0)),(Q(1),Q(1)),(Q(0),Q(1)),(Q(1),Q(0)),
            (Q(1,4),Q(1,2)),(Q(1,2),Q(1,2)),(Q(3,4),Q(3,4)),
        )+tuple((Q(rng.randint(1,9),10),Q(rng.randint(1,9),10))
                for _ in range(10)):
            numeric=game.instantiate(p,q)
            for theta in (Q(1),Q(2)):
                for symbolic,policy in zip(symbols,policies):
                    occ=policy_occupancy(numeric,policy)
                    gold=occ.gold_base+sum(
                        (v*theta for v in occ.gold_feature_occupancy),Q(0)
                    )
                    assert symbolic.proxy.value(p,q)==occ.proxy
                    assert symbolic.gold((theta,)).value(p,q)==gold
                assert max(s.proxy.value(p,q) for s in symbols)==(
                    optimize_stochastic_policy(
                        numeric,(theta,),objective="proxy_worst_gold"
                    ).proxy_return
                )


def test_proxy_tie_only_along_diagonal_has_lower_dimensional_polygon():
    game=diagonal_only_proxy_tie_fixture()
    cert=two_kernel_robust_certificate(game,((Q(1),Q(1)),))
    assert cert.maximum_gold_regret==1
    assert cert.maximum_expected_discrepancy_width>=1
    assert cert.guaranteed_gold_floor==0
    bad_winners=tuple(poly for i,poly in cert.winning_polygons
                      if enumerate_observation_policies(game)[i].action==2)
    assert bad_winners==(
        ((Q(0),Q(0)),(Q(1),Q(1))),
    )
    for p,q in (
        (Q(0),Q(0)),(Q(1,2),Q(1,2)),(Q(1),Q(1)),
        (Q(1,4),Q(3,4)),(Q(3,4),Q(1,4))
    ):
        expected=Q(1) if p==q else Q(0)
        assert direct_policy_census(game,p,q,(Q(1),))[0]==expected


def test_gold_aligned_proxy_switch_has_zero_regret():
    game=proxy_aligned_two_parameter_fixture()
    result=two_kernel_robust_certificate(game,((Q(1),Q(2)),))
    assert result.maximum_gold_regret==0
    assert result.rectangle_corner_only_regret==0
    assert result.maximum_expected_discrepancy_width==1
    assert result.passes
    for p,q in (
        (Q(0),Q(1)),(Q(1),Q(0)),(Q(1,2),Q(1,2)),
        (Q(1,3),Q(2,3))
    ):
        assert direct_policy_census(game,p,q,(Q(2),))[0]==0


def test_exact_subrectangles_and_signed_gold_vertex():
    game=two_parameter_goodhart_fixture(
        p_interval=(Q(0),Q(1,4)),q_interval=(Q(0),Q(1,4))
    )
    cert=two_kernel_robust_certificate(game,((Q(1),Q(1)),))
    assert cert.maximum_gold_regret==Q(3,16)
    assert cert.worst_transition_parameters==(Q(1,4),Q(1,4))
    assert cert.rectangle_corner_only_regret==Q(3,16)
    different=two_parameter_goodhart_fixture(
        p_interval=(Q(0),Q(1,4)),q_interval=(Q(1,2),Q(1))
    )
    cap=two_kernel_robust_certificate(different,((Q(1),Q(1)),))
    assert cap.maximum_gold_regret==Q(1,8)
    assert cap.worst_transition_parameters==(Q(1,4),Q(1,2))
    signed=two_kernel_robust_certificate(
        two_parameter_goodhart_fixture(),((Q(-1),Q(1)),)
    )
    assert signed.maximum_gold_regret==1
    assert signed.worst_gold_parameters==(Q(-1),)
    assert signed.maximum_expected_discrepancy_width>=1


def test_non_affine_proxy_and_non_multiaffine_gold_fail_closed():
    with pytest.raises(ValueError,match="non-affine proxy"):
        two_kernel_robust_certificate(
            nonlinear_proxy_two_parameter_fixture(),((1,1),)
        )
    with pytest.raises(ValueError,match="non-multiaffine gold"):
        two_kernel_robust_certificate(
            nonmultiaffine_gold_two_parameter_fixture(),((1,1),)
        )


def test_invalid_normalization_probabilities_gold_contracts_and_caps():
    game=two_parameter_goodhart_fixture()
    with pytest.raises(ValueError):
        game.instantiate(Q(-1),Q(1,2))
    with pytest.raises(ValueError):
        game.instantiate(Q(1,2),Q(11,10))
    with pytest.raises(ValueError):
        two_kernel_robust_certificate(game,())
    with pytest.raises(ValueError):
        two_kernel_robust_certificate(game,((2,1),))
    with pytest.raises(ValueError):
        two_kernel_robust_certificate(game,((1,1),),max_policies=1)
    with pytest.raises(ValueError):
        two_kernel_robust_certificate(game,((1,1),),max_reward_pairs=1)
    with pytest.raises(ValueError):
        two_kernel_robust_certificate(game,((1,1),),maximum_allowed_regret=-1)
    with pytest.raises(ValueError):
        bilinear_extreme(BiPoly(((2,0,Q(1)),)),(
            (Q(0),Q(0)),(Q(1),Q(1))
        ),maximize=True)
    with pytest.raises(ValueError):
        bilinear_extreme(BiPoly(),(),maximize=True)
    with pytest.raises(ValueError):
        TwoKernelGame(
            1,("a",),(Q(1),),("gold",),
            (Q(0),Q(1)),(Q(0),Q(1)),
            (TwoKernelEdge(0,0,0,"bad",Q(1),Q(1),
                           gold_coefficients=(Q(0),)),),1
        )
    with pytest.raises(ValueError):
        TwoKernelGame(
            1,("a",),(Q(1),),("gold",),
            (Q(0),Q(1)),(Q(0),Q(1)),
            (TwoKernelEdge(0,0,0,"bad",Q(1,2),
                           gold_coefficients=(Q(0),)),),1
        )
