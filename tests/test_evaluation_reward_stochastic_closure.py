"""RHT-13: independent finite partially observed stochastic reward tests."""
from fractions import Fraction as Q
from itertools import product
from random import Random

import pytest

from spiral_ln.evaluation_reward_stochastic_closure import (
    StochasticRewardEdge,StochasticRewardGame,ObservationPolicy,
    optimize_stochastic_policy,policy_occupancy,
    stochastic_robust_certificate,expected_markov_coboundary,
)
from spiral_ln.evaluation_reward_stochastic_fixture import (
    evaluator_pomdp,fair_martingale_noise_game,biased_reward_signal_game
)
from spiral_ln.evaluation_reward_hacking_stateful import MutableEvaluator
from spiral_ln.evaluation_reward_transition_closure import (
    TimedRewardGame,TimedRewardEdge,certify_relative_reward,
)


NOMINAL=(Q(1),Q(-2),Q(1,4))
INTERVALS=((Q(1),Q(2)),(Q(-3),Q(-2)),(Q(0),Q(1,4)))


def direct_two_step_values(game,first,second_by_obs,theta):
    """Independent exhaustive hidden-state and observation traversal.

    The policy chooses a first action and a predeclared lookup table from
    the first response to a second action. No Bellman implementation or
    policy_occupancy helper is used.
    """
    by_sa=game.by_state_action()
    p=g=Q(0)
    for s,mass in enumerate(game.initial):
        if not mass:
            continue
        for e in by_sa[s,first]:
            a=second_by_obs[e.observation]
            for f in by_sa[e.target,a]:
                probability=Q(mass)*Q(e.probability)*Q(f.probability)
                p+=probability*(Q(e.proxy)+Q(f.proxy))
                g+=probability*(Q(e.gold_base)+Q(f.gold_base)
                    +sum((Q(x)*Q(t) for x,t in zip(
                        tuple(a+b for a,b in zip(
                            e.gold_coefficients,f.gold_coefficients
                        )),theta
                    )),Q(0)))
    return p,g


def brute_all_two_step_values(game,theta):
    """Every deterministic two-call response-contingent controller."""
    assert game.horizon==2
    lookup=game.by_state_action()
    reachable={}
    for first in range(len(game.actions)):
        observations={
            e.observation
            for state,m in enumerate(game.initial) if m
            for e in lookup[state,first]
        }
        obs=tuple(sorted(observations))
        for choices in product(range(len(game.actions)),repeat=len(obs)):
            mapping=dict(zip(obs,choices))
            p,g=direct_two_step_values(game,first,mapping,theta)
            yield p,g,first,tuple(sorted(mapping.items()))


def independently_compute_two_step_robust(game,intervals):
    """Directly maximize gold/competing proxy for each interval vertex."""
    result=[]
    for theta in product(*(tuple(sorted(set(bounds))) for bounds in intervals)):
        policies=tuple(brute_all_two_step_values(game,theta))
        proxy_best=max(item[0] for item in policies)
        low_proxy_gold=min(item[1] for item in policies
                           if item[0]==proxy_best)
        gold_best=max(item[1] for item in policies)
        max_gap=max(p-g for p,g,_,_ in policies)
        min_gap=min(p-g for p,g,_,_ in policies)
        result.append((
            gold_best-low_proxy_gold,max_gap-min_gap,low_proxy_gold,theta
        ))
    return max(x[0] for x in result),max(x[1] for x in result),min(x[2] for x in result)


def support_time_graph(game,theta):
    """Complete possible-path support, independent of transition probabilities.

    Each hidden (state,time) becomes a vertex. Root starts at time 0 and
    points to all possible initial hidden states, then every typed stochastic
    transition becomes its own separate time-expanded edge.
    """
    s=game.state_count
    n=1+(game.horizon+1)*s
    def v(t,state):
        return 1+t*s+state
    layers=(0,)+tuple(t+1 for t in range(game.horizon+1)
                       for _ in range(s))
    edges=[]
    for state,mass in enumerate(game.initial):
        if mass:
            edges.append(TimedRewardEdge(0,v(0,state),Q(0),Q(0),"root"))
    for t in range(game.horizon):
        for e in game.edges:
            edges.append(TimedRewardEdge(
                v(t,e.source),v(t+1,e.target),
                game.gold(e,theta),Q(e.proxy),
                f"{game.actions[e.action]}:{e.observation}"
            ))
    return TimedRewardGame(
        layers=layers,start=0,
        terminals=tuple(v(game.horizon,i) for i in range(s)),
        edges=tuple(edges),
    )


def test_ugc_integrity_pomdp_has_real_worlds_visible_reward_and_normalized_kernel():
    game=evaluator_pomdp()
    assert game.horizon==2
    assert len(game.initial)==7
    assert game.state_count==7
    assert game.actions==("probe:0","probe:1","probe:2","tamper")
    assert game.initial==(Q(1,3),Q(0),Q(1,3),Q(0),Q(1,3),Q(0),Q(0))
    assert game.gold_parameters==(
        "safe_approval","unsafe_approval","tamper_cost"
    )
    by_sa=game.by_state_action()
    for state in range(game.state_count):
        for a in range(len(game.actions)):
            assert sum(e.probability for e in by_sa[state,a])==1
    observations={e.observation for e in game.edges}
    assert "ack" in observations
    assert "approved:4" in observations
    assert "approved:1" in observations
    assert "rejected" in observations
    assert "alarm" not in observations  # zero detection default
    assert any(e.gold_coefficients==(0,0,-1) for e in game.edges)
    assert all(e.gold_coefficients[0]*e.gold_coefficients[1]==0
               for e in game.edges)


def test_belief_DP_and_independent_complete_policy_enumeration_agree():
    game=evaluator_pomdp()
    truth=tuple(brute_all_two_step_values(game,NOMINAL))
    assert len(truth)>20
    best_proxy=max(p for p,g,_,_ in truth)
    lowest_proxy_gold=min(g for p,g,_,_ in truth if p==best_proxy)
    best_gold=max(g for _,g,_,_ in truth)
    highest_gap=max(p-g for p,g,_,_ in truth)
    lowest_gap=min(p-g for p,g,_,_ in truth)
    p=optimize_stochastic_policy(game,NOMINAL)
    g=optimize_stochastic_policy(game,NOMINAL,objective="gold_max")
    high=optimize_stochastic_policy(game,NOMINAL,objective="gap_max")
    low=optimize_stochastic_policy(game,NOMINAL,objective="gap_min")
    assert (p.proxy_return,p.gold_return)==(best_proxy,lowest_proxy_gold)
    assert g.gold_return==best_gold
    assert high.proxy_return-high.gold_return==highest_gap
    assert low.proxy_return-low.gold_return==lowest_gap
    assert p.policy.action==game.actions.index("tamper")
    assert g.policy.action!=game.actions.index("tamper")
    assert best_gold-lowest_proxy_gold>0
    for result in (p,g,high,low):
        occupancy=policy_occupancy(game,result.policy)
        assert occupancy.proxy==result.proxy_return
        assert (occupancy.gold_base+sum(c*t for c,t in zip(
            occupancy.gold_feature_occupancy,NOMINAL
        )))==result.gold_return


def test_shared_gold_parameter_box_has_exact_vertex_optimum():
    game=evaluator_pomdp()
    brute=independently_compute_two_step_robust(game,INTERVALS)
    cert=stochastic_robust_certificate(
        game,INTERVALS,nominal=NOMINAL
    )
    assert (
        cert.robust_max_regret,
        cert.robust_policy_discrepancy_width,
        cert.guaranteed_proxy_gold_floor
    )==brute
    assert cert.reward_interval_vertices_checked==8
    assert cert.robust_max_regret>=cert.nominal_regret>0
    assert cert.robust_policy_discrepancy_width>=cert.robust_max_regret
    assert cert.worst_gold_parameters in tuple(product(*INTERVALS))
    assert cert.worst_gold_witness_occupancy!=cert.worst_proxy_witness_occupancy
    assert not stochastic_robust_certificate(
        game,INTERVALS,maximum_allowed_regret=Q(0)
    ).passes
    assert stochastic_robust_certificate(
        game,INTERVALS,
        maximum_allowed_regret=cert.robust_max_regret,
        minimum_proxy_gold_return=cert.guaranteed_proxy_gold_floor
    ).passes
    assert not stochastic_robust_certificate(
        game,INTERVALS,
        minimum_proxy_gold_return=cert.guaranteed_proxy_gold_floor+Q(1,100)
    ).passes


def test_no_tamper_access_and_root_attestation_change_stochastic_reward_regret():
    clean=evaluator_pomdp(channel=MutableEvaluator(allow_tamper=False))
    assert clean.actions==("probe:0","probe:1","probe:2")
    no_tamper=stochastic_robust_certificate(clean,INTERVALS)
    exposed=stochastic_robust_certificate(evaluator_pomdp(),INTERVALS)
    assert no_tamper.robust_max_regret<=exposed.robust_max_regret
    detected=evaluator_pomdp(channel=MutableEvaluator(
        alarm_if_compromised_before_probe=Q(3,4)
    ))
    attested=stochastic_robust_certificate(detected,INTERVALS)
    assert attested.robust_max_regret<=exposed.robust_max_regret
    # These comparisons are specific to this registered gold/proxy.
    assert exposed.robust_max_regret>0


def test_expected_martingale_coboundary_allows_nonzero_pathwise_cycles():
    game=fair_martingale_noise_game(horizon=2)
    cert=expected_markov_coboundary(game,(0,))
    assert cert.valid
    assert cert.expected_gap_all_fixed_horizon_policies==0
    assert cert.first_action_inconsistency is None
    all_proxy=optimize_stochastic_policy(game,(0,),objective="gap_max")
    all_gold=optimize_stochastic_policy(game,(0,),objective="gap_min")
    assert all_proxy.proxy_return-all_proxy.gold_return==0
    assert all_gold.proxy_return-all_gold.gold_return==0
    robust=stochastic_robust_certificate(game,((0,0),))
    assert robust.robust_max_regret==0
    assert robust.robust_policy_discrepancy_width==0

    # The RHT-12 deterministic *support-path* analysis sees actual coin
    # sequences and hence necessarily a nonconstant realized discrepancy.
    support=certify_relative_reward(support_time_graph(game,(0,)))
    assert support.discrepancy_width==4
    assert not support.relative_exact
    assert any(h!=0 for _,h in support.fundamental_periods)


def test_markov_coboundary_detects_action_conditional_reward_mismatch():
    game=biased_reward_signal_game()
    proof=expected_markov_coboundary(game,(0,))
    assert not proof.valid
    assert proof.first_action_inconsistency is not None
    max_gap=optimize_stochastic_policy(game,(0,),objective="gap_max")
    min_gap=optimize_stochastic_policy(game,(0,),objective="gap_min")
    assert max_gap.proxy_return-max_gap.gold_return==2
    assert min_gap.proxy_return-min_gap.gold_return==0
    # Gold=0 for every policy, so the actual *gold regret* is zero
    # although the discrepancy depends on the policy.
    assert stochastic_robust_certificate(
        game,((0,0),)
    ).nominal_regret==0


def test_expected_shaping_constant_can_be_nonzero():
    g=StochasticRewardGame(
        state_count=1, actions=("a","b"),initial=(Q(1),),
        gold_parameters=("unused",),horizon=3,
        edges=(
            StochasticRewardEdge(0,0,0,"a",Q(1),Q(1),
                                 gold_coefficients=(Q(0),)),
            StochasticRewardEdge(0,1,0,"b",Q(1),Q(1),
                                 gold_coefficients=(Q(0),)),
        )
    )
    cert=expected_markov_coboundary(g,(0,))
    assert cert.valid
    assert cert.expected_gap_all_fixed_horizon_policies==3
    assert cert.potential_by_time[0]==(Q(-3),)
    assert stochastic_robust_certificate(
        g,((0,0),)
    ).robust_policy_discrepancy_width==0


def test_random_small_stochastic_models_brute_two_step_vs_Bellman():
    rng=Random(1313)
    for _ in range(20):
        states=2
        A=2
        edges=[]
        for s in range(states):
            for a in range(A):
                p=Q(rng.randint(1,3),4)
                edges.extend((
                    StochasticRewardEdge(
                        s,a,0,"x",p,Q(rng.randint(-2,3)),
                        gold_coefficients=(Q(rng.randint(-2,3)),)
                    ),
                    StochasticRewardEdge(
                        s,a,1,"y",1-p,Q(rng.randint(-2,3)),
                        gold_coefficients=(Q(rng.randint(-2,3)),)
                    ),
                ))
        game=StochasticRewardGame(
            state_count=2,actions=("a","b"),initial=(Q(1,2),Q(1,2)),
            gold_parameters=("gold",),edges=tuple(edges),horizon=2,
        )
        theta=(Q(rng.randint(-2,2)),)
        truth=tuple(brute_all_two_step_values(game,theta))
        assert optimize_stochastic_policy(
            game,theta
        ).proxy_return==max(p for p,_,_,_ in truth)
        optimal=optimize_stochastic_policy(game,theta)
        assert optimal.gold_return==min(g for p,g,_,_ in truth
                                       if p==optimal.proxy_return)
        assert optimize_stochastic_policy(
            game,theta,objective="gold_max"
        ).gold_return==max(g for _,g,_,_ in truth)


def test_invalid_kernel_policy_and_gold_set_fail_closed():
    game=evaluator_pomdp()
    with pytest.raises(ValueError):
        evaluator_pomdp(corrupted_proxy_multiplier=-1)
    with pytest.raises(ValueError):
        StochasticRewardGame(
            1,("a",),(Q(1),),("gold",),
            (StochasticRewardEdge(
                0,0,0,"x",Q(1,2),Q(1),
                gold_coefficients=(Q(1),)
            ),),2
        )
    with pytest.raises(ValueError):
        StochasticRewardEdge(
            0,0,0,"x",Q(0),Q(1),gold_coefficients=(Q(1),)
        )
    with pytest.raises(ValueError):
        optimize_stochastic_policy(game,NOMINAL,max_states=1)
    with pytest.raises(ValueError):
        optimize_stochastic_policy(game,NOMINAL,objective="unknown")
    with pytest.raises(ValueError):
        stochastic_robust_certificate(game,INTERVALS[:-1])
    with pytest.raises(ValueError):
        stochastic_robust_certificate(game,((2,1),)+INTERVALS[1:])
    with pytest.raises(ValueError):
        stochastic_robust_certificate(game,INTERVALS,nominal=(10,-2,0))
    with pytest.raises(ValueError):
        policy_occupancy(game,ObservationPolicy())
    with pytest.raises(ValueError):
        policy_occupancy(
            game,ObservationPolicy(0,(("approved:1",ObservationPolicy()),))
        )
    with pytest.raises(ValueError):
        policy_occupancy(game,optimize_stochastic_policy(
            game,NOMINAL
        ).policy,max_histories=1)
