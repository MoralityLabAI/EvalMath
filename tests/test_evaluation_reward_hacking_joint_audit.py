"""RHT-09 exact joint public/private audit and terminal-veto games.

Independent brute one-query strategy enumerator checks every query, every
visibility class, all terminal veto masks, both error and benign-liveness
constraints. The separate analytic one-hot control uses EvalMath's
adaptive-disclosure posterior collision statistic as its oracle.
"""
from fractions import Fraction as Q
from itertools import product

import pytest

from spiral_ln.evaluation_adaptive_disclosure import (
    FinitePrior, Node, transcript_profile,
)
from spiral_ln.evaluation_reward_hacking_adaptive_feedback import (
    MixedAuditNode, one_hot_ugc_disclosure_game,
)
from spiral_ln.evaluation_reward_hacking_joint_audit import (
    evaluate_joint_audit, optimum_joint_audit, policy_transcripts,
    one_hot_sealed_zero_harm_frontier,
)


def singleton_query(game, col):
    return game.queries.index(
        tuple(int(r==0 and c==col) for r,c in game.space.cells)
    )


def independent_brute_one_query(game, *, floor, leakcap, costcap, harmcap=Q(1)):
    """Direct likelihood arithmetic; never uses the joint optimizer internals."""
    n=len(game.world_records)
    eligible=game.public_maximizers()
    options=[(None,"sealed")]
    for q in range(len(game.queries)):
        responses=tuple(game.query_answer(w,q) for w in range(n))
        if len(set(responses))>1:
            options.extend(((q,"sealed"),(q,"public")))
    best=None
    checks=0
    for q,visibility in options:
        if q is None:
            private=((0,)*n)
            visible=((0,)*n)
            private_keys=(0,)
            cost=Q(0)
        else:
            answers=tuple(game.query_answer(w,q) for w in range(n))
            private=tuple((q,ans) for ans in answers)
            private_keys=tuple(sorted(set(private)))
            visible=(private if visibility=="public" else ((0,)*n))
            cost=Q(1)
        if cost>costcap:
            continue
        vis_groups={}
        for w,vis in enumerate(visible):
            vis_groups.setdefault(vis,[]).append(w)
        without_veto=Q(sum(
            max(sum(game.world_weights[w] for w in ws if game.unsafe(w,a))
                for a in eligible)
            for ws in vis_groups.values()
        ),game.total)
        if without_veto>leakcap:
            continue
        safe_den=sum(game.world_weights[w]
                     for w in range(n) for a in eligible if not game.unsafe(w,a))
        for bits_by_leaf in product(range(1<<len(eligible)),repeat=len(private_keys)):
            checks+=1
            masks=dict(zip(private_keys,bits_by_leaf))
            safe_num=sum(
                game.world_weights[w]
                for w in range(n) for ai,a in enumerate(eligible)
                if not game.unsafe(w,a) and (masks[private[w]]>>ai)&1
            )
            liveness=Q(safe_num,safe_den)
            if liveness<floor:
                continue
            attack_mass=sum(max(
                sum(game.world_weights[w] for w in worlds
                    if game.unsafe(w,a) and (masks[private[w]]>>ai)&1)
                for ai,a in enumerate(eligible)
            ) for worlds in vis_groups.values())
            harm=Q(attack_mass,game.total)
            if harm>harmcap:
                continue
            candidate=(harm,cost,without_veto,-liveness)
            if best is None or candidate<best:
                best=candidate
    return best,checks


def naive_no_query_rule(game, allow):
    return evaluate_joint_audit(
        game,MixedAuditNode(),{():tuple(allow)},max_depth=0
    )


def test_baseline_public_attack_and_private_zero_harm_two_thirds_liveness():
    game=one_hot_ugc_disclosure_game(3)
    q0=singleton_query(game,0)
    stop=MixedAuditNode()
    sealed=MixedAuditNode(q0,"sealed",((0,stop),(1,stop)))
    protected=evaluate_joint_audit(game,sealed,{
        ((q0,0),):(0,),
        ((q0,1),):(1,2),
    },max_depth=1)
    assert protected.authorized_unsafe_risk==0
    assert protected.benign_safe_authorization==Q(2,3)
    assert protected.public_attack_risk_without_veto==Q(1,3)
    assert protected.expected_query_cost==1
    assert protected.private_leaves==2 and protected.public_leaves==1
    assert naive_no_query_rule(game,(0,1)).authorized_unsafe_risk==Q(1,3)
    assert naive_no_query_rule(game,(0,1)).benign_safe_authorization==Q(2,3)
    assert naive_no_query_rule(game,()).benign_safe_authorization==0


def test_joint_optimum_one_probe_is_secret_under_strict_leak_cap():
    game=one_hot_ugc_disclosure_game(3)
    solved=optimum_joint_audit(
        game,max_queries=1,
        minimum_benign_safe_authorization=Q(2,3),
        maximum_public_attack_risk=Q(1,3),
        maximum_expected_query_cost=Q(1),
        maximum_authorized_unsafe_risk=Q(0),
    )
    assert solved is not None
    assert solved.authorized_unsafe_risk==0
    assert solved.benign_safe_authorization>=Q(2,3)
    assert solved.expected_query_cost==1
    assert solved.public_attack_risk_without_veto==Q(1,3)
    assert solved.public_leaves==1
    assert solved.private_leaves==2
    assert solved.policy.visibility=="sealed"
    reconstructed=evaluate_joint_audit(
        game,solved.policy,dict(solved.allowed_actions_by_private_trace),
        max_depth=1
    )
    assert reconstructed.authorized_unsafe_risk==solved.authorized_unsafe_risk
    assert reconstructed.benign_safe_authorization==solved.benign_safe_authorization


def test_joint_search_matches_independent_exhaustive_one_probe_all_floors():
    game=one_hot_ugc_disclosure_game(3)
    for floor,leakcap,costcap,harmcap in (
        (Q(0),Q(1,3),Q(1),Q(1)),
        (Q(2,3),Q(1,3),Q(1),Q(1)),
        (Q(2,3),Q(1,3),Q(1),Q(0)),
        (Q(1),Q(1,3),Q(1),Q(1)),
        (Q(2,3),Q(1),Q(1),Q(0)),
        (Q(2,3),Q(1,3),Q(0),Q(1)),
        (Q(2,3),Q(1,3),Q(0),Q(0)),
    ):
        brute,checked=independent_brute_one_query(
            game,floor=floor,leakcap=leakcap,
            costcap=costcap,harmcap=harmcap
        )
        out=optimum_joint_audit(
            game,max_queries=1,
            minimum_benign_safe_authorization=floor,
            maximum_public_attack_risk=leakcap,
            maximum_expected_query_cost=costcap,
            maximum_authorized_unsafe_risk=harmcap
        )
        assert checked>0
        assert (out is None)==(brute is None)
        if out:
            assert (out.authorized_unsafe_risk,
                    out.expected_query_cost,
                    out.public_attack_risk_without_veto,
                    -out.benign_safe_authorization)==brute


def test_two_sealed_queries_can_certify_all_safe_actions():
    game=one_hot_ugc_disclosure_game(3)
    result=optimum_joint_audit(
        game,max_queries=2,
        minimum_benign_safe_authorization=Q(1),
        maximum_authorized_unsafe_risk=Q(0),
        maximum_public_attack_risk=Q(1,3),
        maximum_expected_query_cost=Q(2),
        max_gate_assignments=200000
    )
    assert result is not None
    assert result.authorized_unsafe_risk==0
    assert result.benign_safe_authorization==1
    assert result.public_attack_risk_without_veto==Q(1,3)
    assert result.private_leaves==3
    assert result.max_queries==2
    assert result.expected_query_cost==Q(5,3)


def test_mixed_visibility_query_identity_leaks_in_terminal_risk():
    game=one_hot_ugc_disclosure_game(3)
    q0=singleton_query(game,0)
    q1=singleton_query(game,1)
    stop=MixedAuditNode()
    sealed=MixedAuditNode(q0,"sealed",((0,stop),(1,stop)))
    all_allowed=(0,1,2)
    a=evaluate_joint_audit(game,sealed,{
        ((q0,0),):all_allowed,
        ((q0,1),):all_allowed,
    },max_depth=2)
    mixed=MixedAuditNode(q0,"sealed",(
        (0,MixedAuditNode(q0,"public",((0,stop),))),
        (1,MixedAuditNode(q1,"public",((0,stop),)))
    ))
    b=evaluate_joint_audit(game,mixed,{
        ((q0,0),(q0,0)):all_allowed,
        ((q0,1),(q1,0)):all_allowed
    },max_depth=2)
    assert a.authorized_unsafe_risk==Q(1,3)
    assert b.authorized_unsafe_risk==Q(2,3)
    assert b.public_attack_risk_without_veto==Q(2,3)
    assert a.benign_safe_authorization==b.benign_safe_authorization==1
    assert b.expected_query_cost==2


def test_analytic_zero_harm_frontier_seven_worlds_tracks_collision():
    for budget,expected,groups in (
        (0,Q(0),(7,)),
        (1,Q(4,7),(4,3)),
        (2,Q(6,7),(2,2,2,1)),
        (3,Q(1),(1,1,1,1,1,1,1))
    ):
        report=one_hot_sealed_zero_harm_frontier(7,budget)
        assert report.maximum_zero_harm_benign_liveness==expected
        assert report.private_leaf_sizes==groups
        assert report.posterior_collision_probability==(
            1-Q(6,7)*expected
        )
        game=one_hot_ugc_disclosure_game(7)
        traces=policy_transcripts(game,report.query_tree,max_depth=budget)
        full_keys=tuple(sorted({tr[0] for tr in traces}))
        allowed={}
        for key in full_keys:
            inside={w for w,tr in enumerate(traces) if tr[0]==key}
            allowed[key]=tuple(a for a in range(7) if a not in inside)
        exact=evaluate_joint_audit(game,report.query_tree,allowed,
                                   max_depth=budget)
        assert exact.authorized_unsafe_risk==0
        assert exact.benign_safe_authorization==expected
        assert exact.public_attack_risk_without_veto==Q(1,7)
        assert exact.public_leaves==1

        def as_original(node):
            return Node(node.query,tuple((answer,as_original(child))
                                         for answer,child in node.branches))
        prior=FinitePrior(game.space.capacities,game.world_records,game.world_weights)
        oracle=transcript_profile(prior,game.queries,as_original(report.query_tree))
        assert oracle["observed_collision_probability"]==report.posterior_collision_probability


def test_first_sealed_query_three_world_frontier_is_two_thirds():
    for budget,expected in ((0,Q(0)),(1,Q(2,3)),(2,Q(1))):
        r=one_hot_sealed_zero_harm_frontier(3,budget)
        assert r.maximum_zero_harm_benign_liveness==expected
    assert one_hot_sealed_zero_harm_frontier(7,1).expected_query_count==1
    assert one_hot_sealed_zero_harm_frontier(7,2).expected_query_count==2
    assert one_hot_sealed_zero_harm_frontier(7,3).expected_query_count<=3


def test_fail_closed_budgets_unknown_actions_and_no_liveness():
    game=one_hot_ugc_disclosure_game(3)
    with pytest.raises(ValueError):
        optimum_joint_audit(game,max_queries=4)
    with pytest.raises(ValueError):
        optimum_joint_audit(game,max_queries=1,max_trees=1)
    with pytest.raises(ValueError):
        optimum_joint_audit(game,max_queries=1,max_gate_assignments=1)
    with pytest.raises(ValueError):
        optimum_joint_audit(game,minimum_benign_safe_authorization=Q(6,5))
    with pytest.raises(ValueError):
        optimum_joint_audit(game,maximum_authorized_unsafe_risk=Q(-1))
    with pytest.raises(ValueError):
        optimum_joint_audit(game,maximum_expected_query_cost=Q(-1))
    with pytest.raises(ValueError):
        policy_transcripts(game,MixedAuditNode(),sealed_query_cost=0)
    with pytest.raises(ValueError):
        policy_transcripts(game,MixedAuditNode(),max_depth=-1)
    with pytest.raises(ValueError):
        evaluate_joint_audit(game,MixedAuditNode(),{})
    with pytest.raises(ValueError):
        evaluate_joint_audit(game,MixedAuditNode(),{(): (0,0)})
    with pytest.raises(ValueError):
        evaluate_joint_audit(game,MixedAuditNode(),{(): (9,)})
    with pytest.raises(ValueError):
        one_hot_sealed_zero_harm_frontier(1,2)
    with pytest.raises(ValueError):
        one_hot_sealed_zero_harm_frontier(7,6)
