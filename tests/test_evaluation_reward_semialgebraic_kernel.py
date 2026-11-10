"""Independent exact/algebraic and ordinary Bernoulli-tree controls for RHT-19."""
from fractions import Fraction as Q
from itertools import product
import random

import pytest

from spiral_ln.evaluation_reward_two_kernel import BiPoly,PolicySurface
from spiral_ln.evaluation_reward_quadratic_kernel_fixture import quadratic_parabola_goodhart_fixture
from spiral_ln.evaluation_reward_two_kernel_fixture import curved_proxy_switch_fixture
from spiral_ln.evaluation_reward_curved_kernel import curved_kernel_robust_certificate
from spiral_ln.evaluation_reward_quadratic_kernel import quadratic_kernel_robust_certificate
from spiral_ln.evaluation_reward_semialgebraic_fixture import higher_degree_parabolic_surfaces
from spiral_ln.evaluation_reward_semialgebraic_kernel import (
    RealRoot,AtRoot,cmp_root,cmp_value,sign_at,isolate,
    semialgebraic_certificate,two_kernel_semialgebraic_certificate,
)


def independent_bernoulli_tree(degree,p,q,theta=Q(1),*,ugc=False):
    """Enumerate all d-step proxy histories and separate protected-gold trials."""
    proxy=Q(0)
    for bits in product((0,1),repeat=degree):
        pr=Q(1)
        for bit in bits:
            pr*=p if bit else (1-p)
        if all(bits):
            proxy+=pr
    gold=Q(0)
    for world in ((0,1) if ugc else (1,)):
        world_mass=Q(1,2) if ugc else Q(1)
        for pass_p,pass_q in product((0,1),repeat=2):
            pr=(p if pass_p else 1-p)*(q if pass_q else 1-q)
            if pass_p and not pass_q and world==1:
                gold+=world_mass*pr*theta
    return proxy,gold


def test_quartic_algebraic_certificate_and_four_corners():
    surfaces=higher_degree_parabolic_surfaces(degree=4)
    cert=semialgebraic_certificate(surfaces,((1,1),),
        maximum_allowed_regret=Q(3,5),minimum_proxy_gold_return=0)
    assert cert.passes
    assert cmp_root(cert.worst_p,isolate((-1,0,0,0,5))[0])==0
    assert cmp_value(cert.worst_q,AtRoot.constant(Q(1,5)))==0
    assert cmp_root(cert.maximum_gold_regret.as_root(),
                    isolate((-256,0,0,0,3125))[0])==0
    assert cert.corner_only_regret==0
    assert cmp_value(cert.guaranteed_gold_floor,AtRoot.constant(0))==0
    assert cmp_value(cert.maximum_expected_discrepancy_width,AtRoot.constant(1))==0
    assert cert.challenger_policy=="protected_gold"
    assert cert.proxy_chosen_policy=="proxy_only"
    assert not semialgebraic_certificate(surfaces,((1,1),),
        maximum_allowed_regret=Q(1,2)).passes


def test_cubic_and_parabolic_tie_only_and_UGC_world():
    for degree in (2,3,4):
        cert=semialgebraic_certificate(
            higher_degree_parabolic_surfaces(degree=degree,extra_tangent=True),((1,1),))
        # Stationary root (d+1)*p**d=1; reward = d*p/(d+1).
        assert cmp_root(cert.worst_p,
            isolate((-1,)+(Q(0),)*(degree-1)+(Q(degree+1),))[0])==0
        assert cmp_value(cert.maximum_gold_regret,
            AtRoot(cert.worst_p,(Q(0),Q(degree,degree+1))))==0
        assert any(r.policy_index==2 and r.strips for r in cert.regions)
        assert cert.corner_only_regret==0
    ugc=semialgebraic_certificate(
        higher_degree_parabolic_surfaces(degree=4,ugc_worlds=True),((1,2),))
    regular=semialgebraic_certificate(
        higher_degree_parabolic_surfaces(degree=4),((1,1),))
    assert cmp_value(ugc.maximum_gold_regret,regular.maximum_gold_regret)==0
    assert ugc.gold_vertex==(Q(2),)
    assert ugc.corner_only_regret==0


def test_ordinary_stochastic_tree_cross_check():
    for degree in (2,3,4):
        for pv,qv in product((Q(0),Q(1,4),Q(1,2),Q(3,4),Q(1)),repeat=2):
            proxy,gold=independent_bernoulli_tree(degree,pv,qv)
            assert proxy==pv**degree
            assert gold==pv*(1-qv)
            expected=gold if qv>=proxy else Q(0)
            cert=semialgebraic_certificate(
                higher_degree_parabolic_surfaces(degree=degree),((1,1),))
            assert cmp_value(cert.maximum_gold_regret,AtRoot.constant(expected))>=0
            pu,gu=independent_bernoulli_tree(degree,pv,qv,Q(2),ugc=True)
            assert pu==proxy and gu==gold


def test_rht18_parabola_regression_with_complete_policy_census():
    game=quadratic_parabola_goodhart_fixture()
    old=quadratic_kernel_robust_certificate(game,((1,1),))
    new=two_kernel_semialgebraic_certificate(game,((1,1),))
    assert cmp_value(new.maximum_gold_regret,
                     AtRoot.constant(0))>0
    # Both have the same exact algebraic root of 27*x*x-4.
    assert cmp_root(new.maximum_gold_regret.as_root(),
                    isolate((-4,0,27))[0])==0
    assert cmp_value(new.worst_q,AtRoot.constant(Q(1,3)))==0
    assert new.corner_only_regret==old.rectangle_corner_only_regret


def test_rational_switch_and_vertical_degenerate_tie():
    p=BiPoly(((1,0,Q(1)),))
    q=BiPoly(((0,1,Q(1)),))
    zero=BiPoly()
    rational=(PolicySurface("gold",p,zero,(p-p*q,)),
              PolicySurface("proxy",q+p*q,zero,(zero,)))
    cert=semialgebraic_certificate(rational,((1,1),))
    assert cmp_value(cert.maximum_gold_regret,AtRoot.constant(Q(1,2)))==0
    assert cmp_root(cert.worst_p,RealRoot.rational(1))==0
    assert cmp_value(cert.worst_q,AtRoot.constant(Q(1,2)))==0
    # Policy 0 wins only on p=0 or q=0 and is preserved at the p=0 slice.
    vertical=(PolicySurface("tie",zero,zero,(zero,)),
              PolicySurface("other",p*q,zero,(q,)))
    extra=semialgebraic_certificate(vertical,((1,1),))
    assert cmp_value(extra.maximum_gold_regret,AtRoot.constant(1))==0
    assert cmp_root(extra.worst_p,RealRoot.rational(0))==0
    assert cmp_value(extra.worst_q,AtRoot.constant(1))==0


def test_same_value_at_distinct_algebraic_parameters():
    roots=isolate((-Q(1,4),0,1),-1,1)
    assert len(roots)==2
    a,b=(AtRoot(r,(Q(0),Q(0),Q(1))) for r in roots)
    assert cmp_value(a,b)==0
    assert cmp_root(a.as_root(),b.as_root())==0
    assert sign_at((Q(-1,4),Q(0),Q(1)),roots[0])==0


def test_closed_region_random_rational_grid_lower_bound():
    rng=random.Random(29)
    p=BiPoly(((1,0,Q(1)),))
    q=BiPoly(((0,1,Q(1)),))
    for _ in range(6):
        # An exact arbitrary q-affine surface grammar with degree up to 3.
        surfaces=[]
        for k in range(3):
            terms=lambda:tuple((i,j,Q(rng.randrange(-2,3),3))
                    for j in (0,1) for i in range(4))
            surfaces.append(PolicySurface(k,BiPoly(terms()),BiPoly(),(BiPoly(terms()),)))
        result=semialgebraic_certificate(surfaces,((1,1),))
        for pp,qq in product((Q(0),Q(1,2),Q(1)),repeat=2):
            scores=[s.proxy.value(pp,qq) for s in surfaces]
            gold=[s.gold((Q(1),)).value(pp,qq) for s in surfaces]
            gap=max(gold)-min(v for u,v in zip(scores,gold) if u==max(scores))
            assert cmp_value(result.maximum_gold_regret,AtRoot.constant(gap))>=0


def test_invalid_degrees_rosters_and_caps_fail_closed():
    q=BiPoly(((0,1,Q(1)),))
    z=BiPoly()
    with pytest.raises(ValueError,match="q-affine"):
        semialgebraic_certificate((PolicySurface("bad",q*q,z,(z,)),),((1,1),))
    with pytest.raises(ValueError):
        semialgebraic_certificate(higher_degree_parabolic_surfaces(),((2,1),))
    with pytest.raises(ValueError,match="pair cap"):
        semialgebraic_certificate(higher_degree_parabolic_surfaces(),((1,1),),max_pairs=1)
    with pytest.raises(ValueError):
        higher_degree_parabolic_surfaces(degree=13)

def test_rht17_curved_pq_regression_with_complete_observation_policies():
    game=curved_proxy_switch_fixture()
    previous=curved_kernel_robust_certificate(game,((1,1),))
    latest=two_kernel_semialgebraic_certificate(game,((1,1),))
    assert cmp_root(latest.worst_p,isolate((-1,2,1))[0])==0
    assert cmp_value(latest.worst_q,AtRoot(latest.worst_p,(Q(0),Q(1))))==0
    assert cmp_root(latest.maximum_gold_regret.as_root(),
                    isolate((4,-12,1),0,1)[0])==0
    assert latest.corner_only_regret==previous.rectangle_corner_only_regret
    assert cmp_value(latest.maximum_expected_discrepancy_width,
                     AtRoot.constant(2))==0


def test_degree_eight_and_twelve_exact_root_family():
    for degree in (8,12):
        cert=semialgebraic_certificate(
            higher_degree_parabolic_surfaces(degree=degree),((1,1),))
        stationary=(-1,)+(Q(0),)*(degree-1)+(Q(degree+1),)
        assert cmp_root(cert.worst_p,isolate(stationary)[0])==0
        assert cmp_value(cert.worst_q,
                         AtRoot.constant(Q(1,degree+1)))==0
        assert cmp_value(cert.maximum_gold_regret,
                         AtRoot(cert.worst_p,(Q(0),Q(degree,degree+1))))==0
        assert cert.corner_only_regret==0


def test_root_isolation_cap_includes_endpoints_and_dyadic_roots():
    with pytest.raises(ValueError, match="root cap"):
        isolate((Q(0),Q(-1),Q(1)),max_roots=1)
    with pytest.raises(ValueError, match="root cap"):
        isolate((Q(1,8),Q(-3,4),Q(1)),max_roots=1)
    with pytest.raises(ValueError, match="positive Sturm isolation"):
        isolate((Q(-1),Q(2)),max_roots=0)
