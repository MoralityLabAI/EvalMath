"""RHT-08 exact strategic disclosure risks from game-space reward fibres."""
from fractions import Fraction as Q
from itertools import product

import pytest

from spiral_ln.evaluation_adaptive_disclosure import (
    FinitePrior, one_hot_interval_law, adaptive_optimum as atlas_adaptive,
    fixed_optimum as atlas_fixed,
)
from spiral_ln.evaluation_reward_hacking_adaptive_feedback import (
    AdaptiveRewardGame, MixedAuditNode, mixed_disclosure_attack_risk,
    one_hot_ugc_disclosure_game, protected_auditor_optimum,
    public_attack_risks, visible_transcript,
)
from spiral_ln.evaluation_selection_risk import (
    no_feedback_risk, policy_risk, full_information_risk,
    policy_fibres, QueryNode, exhaustive_two_round_optimum,
)
from spiral_ln.unique_games_topology import TranslationGame, Edge


def direct_actor_risk(game, records):
    """Independent arithmetic over actual cochain utilities and gold regret.

    Input is an externally specified visible transcript label per world.
    It directly enumerates all proxy-optimal candidate actions per leaf.
    """
    groups={}
    for i,label in enumerate(records):
        groups.setdefault(label,[]).append(i)
    max_proxy=max(game.proxy_score(x) for x in game.actions)
    best=Q(0)
    for indices in groups.values():
        choices=[]
        for a,x in enumerate(game.actions):
            if game.proxy_score(x)!=max_proxy:
                continue
            damaging=Q(0)
            for i in indices:
                true_best=max(game.gold(i,j) for j in range(len(game.actions)))
                if true_best-game.gold(i,a)>=Q(game.unsafe_regret):
                    damaging+=game.world_weights[i]
            choices.append(damaging)
        best+=max(choices)
    return best/game.total


def q_singleton(game, col):
    target=tuple(int(r==0 and c==col) for r,c in game.space.cells)
    return game.queries.index(target)


def build_mixed_policy_for_3_worlds(game):
    # Root privately queries whether hidden reference world is 0.
    # If yes, choose public query 'is world 1?' (guaranteed answer 0).
    # Otherwise choose public query 'is world 0?' (also answer 0).
    # The later query ID alone reveals the sealed answer.
    q0=q_singleton(game,0)
    q1=q_singleton(game,1)
    public0=MixedAuditNode(
        q0,"public",((0,MixedAuditNode()),)
    )
    public1=MixedAuditNode(
        q1,"public",((0,MixedAuditNode()),)
    )
    return MixedAuditNode(q0,"sealed",((0,public0),(1,public1)))


def test_ugc_k2n_golds_are_real_constraint_satisfaction_worlds():
    for n in (2,3,5,7):
        game=one_hot_ugc_disclosure_game(n)
        edges=(tuple(Edge(0,2+j,0) for j in range(n))
               +tuple(Edge(1,2+j,0) for j in range(n)))
        ugc=TranslationGame(n+2,1,edges)
        assert len(ugc.edges)==2*n
        assert len({game.space.feedback(x) for x in game.world_records})==1
        for i,world in enumerate(game.world_records):
            labels=(0,1)+tuple(0 if j==i else 1 for j in range(n))
            recorded=tuple(int(labels[e.v]==(labels[e.u]^e.shift))
                           for e in ugc.edges)
            assert recorded==world
            assert game.proxy_score(world)==n
            assert all(game.gold(i,a)==int(a!=i) for a in range(n))
        assert game.public_maximizers()==tuple(range(n))


def test_7_world_interval_feedback_strict_adaptive_hacking_advantage():
    game=one_hot_ugc_disclosure_game(7)
    null=game.attack_null()
    assert no_feedback_risk(null)==Q(1,7)
    assert full_information_risk(null)==1
    assert game.space.rational_nullity==6
    risk0=public_attack_risks(game,0)
    risk1=public_attack_risks(game,1)
    risk2=public_attack_risks(game,2)
    risk3=public_attack_risks(game,3)
    assert (risk0["baseline"],risk1["adaptive"],
            risk2["adaptive"],risk3["adaptive"])==(
                Q(1,7),Q(2,7),Q(4,7),1)
    assert risk3["fixed"]==Q(6,7)
    assert risk3["adaptive"]-risk3["fixed"]==Q(1,7)
    assert len(policy_fibres(null,risk3["adaptive_tree"]))==7
    assert policy_risk(null,risk3["adaptive_tree"])==1
    assert risk3["adaptive_subproblems"]>1
    # Independent established EvalMath one-hot interval law:
    assert one_hot_interval_law(7,3)=={"adaptive":7,"fixed":6}
    prior=FinitePrior(game.space.capacities,game.world_records,game.world_weights)
    independent_adaptive=atlas_adaptive(prior,game.queries,3)
    independent_fixed=atlas_fixed(prior,game.queries,3)
    assert independent_adaptive["bayes_success"]==risk3["adaptive"]
    assert independent_fixed["bayes_success"]==risk3["fixed"]


def test_private_one_interval_query_prevents_all_modelled_bad_actions():
    game=one_hot_ugc_disclosure_game(7)
    zero=protected_auditor_optimum(game,0)
    one=protected_auditor_optimum(game,1)
    assert zero["risk"]==Q(1,7)
    assert one["risk"]==0
    assert one["first_private_query"] is not None
    # Publicly disclosing the same probe to the malicious proxy optimizer
    # raises the expected harm probability to 2/7.
    assert public_attack_risks(game,1)["adaptive"]==Q(2,7)


def test_sealed_answers_leak_through_subsequent_public_query_identity():
    game=one_hot_ugc_disclosure_game(3)
    q0=q_singleton(game,0)
    sealed=MixedAuditNode(
        q0,"sealed",((0,MixedAuditNode()),(1,MixedAuditNode()))
    )
    attack0=mixed_disclosure_attack_risk(game,sealed)
    assert attack0["visible_leaves"]==1
    assert attack0["risk"]==Q(1,3)
    for i in range(3):
        assert visible_transcript(game,i,sealed)==()
    mixed=build_mixed_policy_for_3_worlds(game)
    attack1=mixed_disclosure_attack_risk(game,mixed)
    assert attack1["visible_leaves"]==2
    assert attack1["risk"]==Q(2,3)
    visible=tuple(visible_transcript(game,i,mixed) for i in range(3))
    assert all(len(x)==1 and x[0][1]==0 for x in visible)
    assert len({x[0][0] for x in visible})==2
    assert direct_actor_risk(game,visible)==attack1["risk"]
    assert protected_auditor_optimum(game,1)["risk"]==0


def test_public_feedback_risk_matches_independent_harm_event_enumeration():
    game=one_hot_ugc_disclosure_game(3)
    null=game.attack_null()
    q0=q_singleton(game,0)
    public=MixedAuditNode(
        q0,"public",((0,MixedAuditNode()),(1,MixedAuditNode()))
    )
    visible=tuple(visible_transcript(game,i,public) for i in range(3))
    assert direct_actor_risk(game,visible)==Q(2,3)
    assert mixed_disclosure_attack_risk(game,public)["risk"]==Q(2,3)
    # Public two-query policy is checked with an independently exhaustive
    # search over every second-query decision tree.
    assert exhaustive_two_round_optimum(null)==public_attack_risks(game,2)["adaptive"]
    assert public_attack_risks(game,2)["adaptive"]==1


def test_actor_confined_to_proxy_maximizers_with_strict_proxy_preference():
    game=one_hot_ugc_disclosure_game(3)
    high=game.actions[0]
    # Create an additional, strictly lower proxy action by declaring a
    # zero record, which would have gold zero and might be unsafe.
    altered=AdaptiveRewardGame(
        space=game.space,world_records=game.world_records,
        world_weights=game.world_weights,
        actions=game.actions+(tuple(0 for _ in high),),
        gold_by_world=game.gold_by_world,
        proxy_margin_weights=game.proxy_margin_weights,
        queries=game.queries,unsafe_regret=Q(1),
    )
    assert altered.public_maximizers()==(0,1,2)
    assert public_attack_risks(altered,0)["baseline"]==Q(1,3)
    assert public_attack_risks(altered,1)["adaptive"]==Q(2,3)


def test_regret_threshold_oracle_vs_direct_full_enumeration():
    game=one_hot_ugc_disclosure_game(3)
    for threshold in (Q(1,2),Q(1),Q(3,2)):
        altered=AdaptiveRewardGame(
            space=game.space,world_records=game.world_records,
            world_weights=(1,2,3),actions=game.actions,
            gold_by_world=game.gold_by_world,
            proxy_margin_weights=game.proxy_margin_weights,
            queries=game.queries,unsafe_regret=threshold,
        )
        labels=(0,0,0)
        predicted=direct_actor_risk(altered,labels)
        actual=public_attack_risks(altered,0)["baseline"]
        assert predicted==actual
        if threshold>1:
            assert actual==0
        else:
            assert actual==Q(3,6)


def test_invalid_worlds_queries_policy_and_public_margin_contracts():
    game=one_hot_ugc_disclosure_game(3)
    with pytest.raises(ValueError):
        one_hot_ugc_disclosure_game(1)
    with pytest.raises(ValueError):
        one_hot_ugc_disclosure_game(13)
    with pytest.raises(ValueError):
        AdaptiveRewardGame(
            space=game.space,
            world_records=game.world_records[:-1]+(tuple(0 for _ in game.space.cells),),
            world_weights=game.world_weights,actions=game.actions,
            gold_by_world=game.gold_by_world,
            proxy_margin_weights=game.proxy_margin_weights,
            queries=game.queries,
        )
    with pytest.raises(ValueError):
        AdaptiveRewardGame(
            space=game.space,world_records=game.world_records,
            world_weights=game.world_weights,actions=game.actions,
            gold_by_world=game.gold_by_world,
            proxy_margin_weights=game.proxy_margin_weights,
            queries=(tuple(2 for _ in game.space.cells),),
        )
    with pytest.raises(ValueError):
        protected_auditor_optimum(game,-1)
    with pytest.raises(ValueError):
        visible_transcript(game,9,MixedAuditNode())
    q0=q_singleton(game,0)
    with pytest.raises(ValueError):
        visible_transcript(game,0,MixedAuditNode(q0,"public",()))
    with pytest.raises(ValueError):
        visible_transcript(
            game,0,MixedAuditNode(q0,"public",
                 ((1,MixedAuditNode()),(1,MixedAuditNode())))
        )
    with pytest.raises(ValueError):
        visible_transcript(game,0,MixedAuditNode(
            q0,"readout",((1,MixedAuditNode()),)
        ))
    with pytest.raises(ValueError):
        visible_transcript(game,0,MixedAuditNode(
            999,"public",((1,MixedAuditNode()),)
        ))
    with pytest.raises(ValueError):
        visible_transcript(game,0,MixedAuditNode(
            None,"sealed",((0,MixedAuditNode()),)
        ))
