"""RHT-12: independent path-census and interval-endpoint reward controls."""
from fractions import Fraction as Q
from itertools import product
from random import Random

import pytest

from spiral_ln.evaluation_reward_transition_closure import (
    TimedRewardEdge, TimedRewardGame, certify_relative_reward,
    robust_transition_certify,
)


def edge(u,v,g,p,name=""):
    return TimedRewardEdge(u,v,Q(g),Q(p),name)


def mutable_evaluator_diamond():
    # Vertices include the evaluator's clean/compromised state.
    # Layers 0: initial; 1: clean vs compromised; 2: safe vs bad outcome.
    return TimedRewardGame(
        layers=(0,1,1,2,2),start=0,terminals=(3,4),
        edges=(
            edge(0,1,0,0,"stay-intact"),
            edge(0,2,0,0,"compromise-evaluator"),
            edge(1,3,2,2,"intact-good"),
            edge(1,4,0,1,"intact-bad"),
            edge(2,3,2,0,"compromised-good-underreported"),
            edge(2,4,0,3,"compromised-bad-overreported"),
        )
    )


def independent_census(game):
    paths=game.complete_paths()
    values=tuple((p,*game.path_returns(p)) for p in paths)
    gaps=[proxy-gold for _,gold,proxy in values]
    top_proxy=max(proxy for _,_,proxy in values)
    gold_best=max(gold for _,gold,_ in values)
    lowest_proxy_gold=min(gold for _,gold,proxy in values
                          if proxy==top_proxy)
    return {
        "values":values,
        "minimum_gap":min(gaps),
        "maximum_gap":max(gaps),
        "width":max(gaps)-min(gaps),
        "best_gold":gold_best,
        "best_proxy":top_proxy,
        "proxy_regret":gold_best-lowest_proxy_gold,
    }


def gold_interval_census(game,low,high):
    """Independent exact endpoint enumeration of all licensed gold rewards."""
    paths=game.complete_paths()
    proxy={p:game.path_returns(p)[1] for p in paths}
    best_proxy=max(proxy.values())
    proxy_paths=tuple(p for p in paths if proxy[p]==best_proxy)
    width=regret=Q(0)
    witness=()
    floor=None
    for endpoints in product((0,1),repeat=len(game.edges)):
        chosen=tuple(Q(high[i] if endpoints[i] else low[i])
                     for i in range(len(endpoints)))
        returns={p:sum((chosen[i] for i in p),Q(0)) for p in paths}
        deltas=[proxy[p]-returns[p] for p in paths]
        width=max(width,max(deltas)-min(deltas))
        selected_gold=min(returns[p] for p in proxy_paths)
        regret=max(regret,max(returns.values())-selected_gold)
        floor=selected_gold if floor is None else min(floor,selected_gold)
    return width,regret,floor


def test_potential_exact_with_terminal_potentials_equal():
    # Gold values differ across paths. A time-indexed potential produces
    # the same +2 return offset on every complete path.
    phi=(Q(0),Q(1),Q(-1),Q(2),Q(2))
    costs=((0,1,0),(0,2,1),(1,3,3),(2,3,1),
           (1,4,2),(2,4,0))
    game=TimedRewardGame(
        layers=(0,1,1,2,2),start=0,terminals=(3,4),
        edges=tuple(edge(u,v,g,Q(g)+phi[v]-phi[u])
                    for u,v,g in costs)
    )
    cert=certify_relative_reward(game)
    assert cert.relative_exact
    assert cert.relative_potential is not None
    assert cert.minimum_discrepancy==cert.maximum_discrepancy==2
    assert cert.discrepancy_width==0
    assert cert.sum_absolute_fundamental_periods==0
    assert all(p==0 for _,p in cert.fundamental_periods)
    assert cert.worst_proxy_selected_regret==0
    assert cert.true_gold_optimum==independent_census(game)["best_gold"]
    for path,gold,proxy in independent_census(game)["values"]:
        assert proxy-gold==2
    assert cert.relative_potential[-1]==2


def test_terminal_gluing_detects_obstruction_in_an_acyclic_tree():
    game=TimedRewardGame(
        layers=(0,1,1),start=0,terminals=(1,2),
        edges=(edge(0,1,2,2),edge(0,2,0,3))
    )
    cert=certify_relative_reward(game)
    assert not cert.relative_exact
    assert cert.discrepancy_width==3
    assert cert.minimum_discrepancy==0
    assert cert.maximum_discrepancy==3
    assert cert.worst_proxy_selected_regret==2
    assert cert.true_gold_optimum==2
    assert cert.proxy_optimum==3
    assert cert.sum_absolute_fundamental_periods==3
    assert len(cert.fundamental_periods)==1
    # The original transition graph has only two edges and no cycle.
    # The required virtual terminal sink produces one relative cycle.
    assert cert.relative_potential is None


def test_mutable_evaluator_diamond_has_explicit_proxy_hack_and_holonomy():
    game=mutable_evaluator_diamond()
    cert=certify_relative_reward(game)
    assert len(game.complete_paths())==4
    assert (cert.minimum_discrepancy,cert.maximum_discrepancy)==(-2,3)
    assert cert.discrepancy_width==5
    assert cert.true_gold_optimum==2
    assert cert.proxy_optimum==3
    assert cert.worst_proxy_selected_gold==0
    assert cert.worst_proxy_selected_regret==2
    assert cert.proxy_selected_path==(1,5)
    assert cert.gold_optimum_path in ((0,2),(1,4))
    assert not cert.relative_exact
    assert cert.sum_absolute_fundamental_periods>=5
    assert any(period for _,period in cert.fundamental_periods)
    assert cert.worst_proxy_selected_regret<=cert.discrepancy_width


def test_reward_regret_bound_is_sharp_with_adversarial_proxy_tie():
    game=TimedRewardGame(
        layers=(0,1),start=0,terminals=(1,),
        edges=(edge(0,1,2,2,"good"),edge(0,1,0,2,"bad"))
    )
    cert=certify_relative_reward(game)
    assert cert.discrepancy_width==2
    assert cert.worst_proxy_selected_regret==2
    assert cert.true_gold_optimum==2
    assert cert.proxy_optimum==2
    assert cert.relative_exact is False


def test_random_dag_census_agrees_with_cohomology_and_proxy_regret():
    rng=Random(12011)
    pairs=((0,1),(0,2),(1,3),(2,3),(1,4),(2,4))
    for _ in range(60):
        rewards=tuple((rng.randint(-3,3),rng.randint(-3,3))
                      for _ in pairs)
        game=TimedRewardGame(
            (0,1,1,2,2),0,(3,4),
            tuple(edge(u,v,g,p) for (u,v),(g,p) in zip(pairs,rewards))
        )
        actual=independent_census(game)
        cert=certify_relative_reward(game)
        assert cert.minimum_discrepancy==actual["minimum_gap"]
        assert cert.maximum_discrepancy==actual["maximum_gap"]
        assert cert.discrepancy_width==actual["width"]
        assert cert.true_gold_optimum==actual["best_gold"]
        assert cert.proxy_optimum==actual["best_proxy"]
        assert cert.worst_proxy_selected_regret==actual["proxy_regret"]
        assert cert.relative_exact==(actual["width"]==0)
        assert cert.discrepancy_width<=cert.sum_absolute_fundamental_periods
        if cert.relative_exact:
            assert cert.relative_potential is not None
            assert all(period==0 for _,period in cert.fundamental_periods)


def test_independent_gold_interval_endpoints_confirm_sharp_robust_DP():
    rng=Random(1412)
    game=mutable_evaluator_diamond()
    low=(0,0,1,0,1,0)
    high=(0,0,3,0,3,0)
    result=robust_transition_certify(
        game,low,high,maximum_allowed_regret=3,
        minimum_required_true_return=0,
    )
    assert (result.maximum_width,result.maximum_proxy_regret)==(6,3)
    assert result.guaranteed_proxy_gold_floor==0
    assert result.passes
    assert result.maximum_proxy_regret<result.maximum_width
    assert gold_interval_census(game,low,high)==(6,3,0)
    assert result.regret_proxy_path==(1,5)
    assert result.states_visited>0

    for _ in range(40):
        lo=tuple(Q(rng.randint(-2,2)) for _ in game.edges)
        hi=tuple(v+Q(rng.randint(0,2)) for v in lo)
        brute=gold_interval_census(game,lo,hi)
        exact=robust_transition_certify(game,lo,hi)
        assert (
            exact.maximum_width,
            exact.maximum_proxy_regret,
            exact.guaranteed_proxy_gold_floor,
        )==brute
        assert exact.maximum_proxy_regret<=exact.maximum_width
        assert exact.passes


def test_shared_uncertain_stem_cancels_in_every_pair_difference():
    game=TimedRewardGame(
        layers=(0,1,2,2),start=0,terminals=(2,3),
        edges=(
            edge(0,1,0,0,"common-stem"),
            edge(1,2,2,0,"good"),
            edge(1,3,0,1,"bad"),
        )
    )
    low=(0,1,0)
    high=(100,2,0)
    cert=robust_transition_certify(
        game,low,high,maximum_allowed_regret=2,
        minimum_required_true_return=0,
    )
    assert cert.maximum_width==3
    assert cert.maximum_proxy_regret==2
    assert cert.passes
    assert gold_interval_census(game,low,high)==(3,2,0)
    assert game.path_returns(cert.regret_proxy_path)[1]==1
    assert not robust_transition_certify(
        game,low,high,maximum_allowed_regret=1
    ).passes


def test_exact_relative_and_robust_guards_respond_to_uncertainty():
    game=mutable_evaluator_diamond()
    low=(0,0,1,0,1,0)
    high=(0,0,3,0,3,0)
    assert robust_transition_certify(
        game,low,high,maximum_allowed_regret=3,
        minimum_required_true_return=0
    ).passes
    assert not robust_transition_certify(
        game,low,high,maximum_allowed_regret=2
    ).passes
    assert not robust_transition_certify(
        game,low,high,minimum_required_true_return=1
    ).passes
    assert robust_transition_certify(
        game,low,high,maximum_allowed_regret=3,
        minimum_required_true_return=-1
    ).passes


def test_irrelevant_dead_branch_cannot_create_a_spurious_obstruction():
    game=TimedRewardGame(
        layers=(0,1,1,2),start=0,terminals=(3,),
        edges=(
            edge(0,1,0,0),edge(1,3,2,2),
            edge(0,2,0,0),  # no completed path from vertex 2
        )
    )
    cert=certify_relative_reward(game)
    assert cert.relative_exact
    assert cert.discrepancy_width==0
    assert cert.true_gold_optimum==2
    assert cert.fundamental_periods==()
    assert game.complete_paths()==((0,1),)


def test_unsynchronized_terminal_horizon_rejects_product_DP():
    game=TimedRewardGame(
        layers=(0,1,1,2),start=0,terminals=(1,3),
        edges=(edge(0,1,1,1),edge(0,2,0,0),edge(2,3,0,1))
    )
    assert certify_relative_reward(game).discrepancy_width==1
    with pytest.raises(ValueError):
        robust_transition_certify(
            game,(1,0,0),(1,0,0)
        )


def test_huge_negative_proxy_rewards_preserve_exact_interval_optima():
    # No finite sentinel should substitute for rational minus infinity.
    n=10**150
    game=TimedRewardGame(
        layers=(0,1),start=0,terminals=(1,),
        edges=(edge(0,1,2,-n,"gold-best"),
               edge(0,1,0,-n+1,"proxy-best"))
    )
    nominal=certify_relative_reward(game)
    assert nominal.true_gold_optimum==2
    assert nominal.proxy_optimum==-n+1
    assert nominal.worst_proxy_selected_regret==2
    uncertainty=robust_transition_certify(
        game,(2,0),(2,0),maximum_allowed_regret=2,
        minimum_required_true_return=0
    )
    assert uncertainty.maximum_proxy_regret==2
    assert uncertainty.maximum_width==3
    assert uncertainty.guaranteed_proxy_gold_floor==0
    assert uncertainty.passes


def test_invalid_time_graph_paths_rewards_and_gold_intervals():
    with pytest.raises(ValueError):
        TimedRewardGame((0,0),0,(1,),(edge(0,1,0,0),))
    with pytest.raises(ValueError):
        TimedRewardGame((0,1),0,(1,),(edge(1,1,0,0),))
    with pytest.raises(ValueError):
        TimedRewardGame(
            (0,1,2),0,(1,),(edge(0,1,0,0),edge(1,2,0,0))
        )  # Terminal nodes cannot have outgoing transitions.
    game=mutable_evaluator_diamond()
    with pytest.raises(ValueError):
        game.path_returns((5,))
    with pytest.raises(ValueError):
        game.path_returns((0,))
    with pytest.raises(ValueError):
        game.complete_paths(max_paths=1)
    with pytest.raises(ValueError):
        robust_transition_certify(game,(0,)*5,(1,)*6)
    with pytest.raises(ValueError):
        robust_transition_certify(game,(2,)*6,(1,)*6)
    with pytest.raises(ValueError):
        robust_transition_certify(
            game,(0,)*6,(1,)*6,maximum_allowed_regret=-1
        )
