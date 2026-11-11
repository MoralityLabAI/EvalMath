"""RHT-21: independent exhaustive rational decision-tree and cue-transfer tests."""
from fractions import Fraction as Q
from itertools import product
import random
import pytest

from spiral_ln.evaluation_reward_active_awareness import (
    ObservationLaw, Probe, ActiveEvaluationGame, PolicyNode, ActivePolicy,
    PROTECT, EXPLOIT, optimize_active_policy, terminal_traces,
    certify_active_transfer, sharp_transfer_relabel,
)


def example_game(horizon=1, cost=Q(1,10)):
    law=ObservationLaw("looks_like",("deployment","evaluation"),
                       (Q(1,4),Q(3,4)),(Q(3,4),Q(1,4)))
    return ActiveEvaluationGame(Q(1,8),Q(8),Q(1),horizon,
                                (Probe("inspection",law,cost),))


def exhaustive_trees(game,remaining):
    """Enumerate all deterministic registered policies without Bellman recursion."""
    leaves=(EXPLOIT,PROTECT)
    if not remaining:
        return leaves
    smaller=exhaustive_trees(game,remaining-1)
    variants=list(leaves)
    for i,probe in enumerate(game.probes):
        for branches in product(smaller,repeat=len(probe.law.outcomes)):
            variants.append(PolicyNode("probe",i,branches))
    return tuple(variants)


def independent_world_value(game,node,evaluation):
    """An ordinary conditional expectation oracle, with no belief-state DP."""
    if node.action=="protect":
        return (game.protect_reward if evaluation else Q(0))+game.terminal_future_delta
    if node.action=="exploit":
        return Q(0) if evaluation else game.exploit_gain
    probe=game.probes[node.probe_index]
    probs=probe.law.evaluation if evaluation else probe.law.deployment
    return (probe.subjective_future_influence-probe.cost+
            sum((mass*independent_world_value(game,child,evaluation)
                 for mass,child in zip(probs,node.children)),Q(0)))


def test_rht20_is_exact_zero_probe_boundary():
    game=example_game(horizon=0)
    baseline=ActiveEvaluationGame(
        game.prior,game.protect_reward,game.exploit_gain,0,(),game.probes[0].law)
    optimal=optimize_active_policy(baseline)
    assert tuple(t.action for t in optimal.policy.initial_branches)==("exploit","protect")
    report=certify_active_transfer(baseline,optimal.policy)
    assert (report.evaluation_protection,report.deployment_protection)==(Q(3,4),Q(1,4))
    assert report.exact_transcript_tv==report.transcript_tv_bound==Q(1,2)
    assert report.likelihood_coverage==Q(1,3)
    assert report.policy_value==optimal.subjective_value==Q(45,32)


def test_one_probe_value_of_information_and_tie_cost():
    game=example_game()
    optimal=optimize_active_policy(game)
    report=certify_active_transfer(game,optimal.policy)
    assert optimal.subjective_value==report.policy_value==Q(209,160)
    assert optimal.policy.initial_branches[0].action=="probe"
    assert (report.evaluation_protection,report.deployment_protection)==(Q(3,4),Q(1,4))
    assert report.realized_gap==report.exact_transcript_tv==Q(1,2)
    assert report.transcript_tv_bound==Q(1,2)
    assert (report.evaluation_expected_probes,report.deployment_expected_probes)==(1,1)
    assert tuple(t.posterior(game.prior) for t in terminal_traces(game,optimal.policy))==(
        Q(1,22),Q(3,10),
    )
    for price in (Q(13,32),Q(1,2)):
        costly=example_game(cost=price)
        assert optimize_active_policy(costly).policy.initial_branches==(PROTECT,)
    cheap=example_game(cost=Q(13,32)-Q(1,100))
    assert optimize_active_policy(cheap).policy.initial_branches[0].action=="probe"


def test_adaptive_three_probe_contingency_improves_bayes_value():
    h1=optimize_active_policy(example_game(1))
    h2=optimize_active_policy(example_game(2))
    h3=optimize_active_policy(example_game(3))
    assert h1.subjective_value==h2.subjective_value==Q(209,160)
    assert h3.subjective_value==Q(1721,1280)>h2.subjective_value
    report=certify_active_transfer(example_game(3),h3.policy)
    assert report.exact_transcript_tv==Q(11,16)
    assert (report.evaluation_protection,report.deployment_protection)==(
        Q(27,32),Q(5,32),
    )
    assert report.policy_value==h3.subjective_value
    assert report.realized_gap==report.exact_transcript_tv
    assert report.transcript_tv_bound==Q(7,8)


def test_two_distinct_probes_can_be_adaptively_selected():
    la=ObservationLaw("a",("0","1"),(Q(1,5),Q(4,5)),(Q(2,5),Q(3,5)))
    lb=ObservationLaw("b",("0","1"),(Q(2,5),Q(3,5)),(Q(1,5),Q(4,5)))
    game=ActiveEvaluationGame(Q(1,2),Q(5),Q(4),2,
        (Probe("A",la,0),Probe("B",lb,Q(1,10))))
    optimal=optimize_active_policy(game)
    root=optimal.policy.initial_branches[0]
    assert optimal.subjective_value==Q(289,100)
    assert root.action=="probe" and root.probe_index==0
    assert tuple(branch.probe_index for branch in root.children)==(1,0)
    cert=certify_active_transfer(game,optimal.policy)
    assert cert.policy_value==optimal.subjective_value
    assert cert.exact_transcript_tv<=cert.transcript_tv_bound


def test_probe_which_cannot_discriminate_types_is_ignored():
    identical=ObservationLaw("noise",("a","b"),(Q(1,3),Q(2,3)),
                             (Q(1,3),Q(2,3)))
    for price in (Q(0),Q(1,100)):
        game=ActiveEvaluationGame(Q(1,8),Q(8),Q(1),4,
                                  (Probe("noise",identical,price),))
        result=optimize_active_policy(game)
        assert result.policy.initial_branches==(PROTECT,)
        assert result.subjective_value==1
        cert=certify_active_transfer(game,result.policy)
        assert cert.exact_transcript_tv==cert.transcript_tv_bound==0


def test_deployment_only_signal_is_an_exact_bad_case():
    purely=ObservationLaw("perfect",("eval_only","deploy_only"),
        (Q(1),Q(0)),(Q(0),Q(1)))
    game=ActiveEvaluationGame(Q(1,2),Q(1),Q(1),2,(Probe("test",purely,0),))
    cert=certify_active_transfer(game,optimize_active_policy(game).policy)
    assert cert.evaluation_protection==1
    assert cert.deployment_protection==0
    assert cert.exact_transcript_tv==cert.transcript_tv_bound==1
    assert cert.likelihood_coverage==0
    assert cert.policy_value==1


def test_sharp_transfer_relabel_works_under_adaptive_stopping():
    for horizon in range(4):
        game=example_game(horizon)
        relabeled=sharp_transfer_relabel(game,optimize_active_policy(game).policy)
        cert=certify_active_transfer(game,relabeled)
        assert cert.realized_gap==cert.exact_transcript_tv


def test_independent_exhaustive_policy_tree_oracle():
    rng=random.Random(210011)
    for nprobes,horizon in ((0,0),(1,1),(1,2),(1,3),(2,1),(2,2)):
        for rep in range(4):
            probes=[]
            for k in range(nprobes):
                a,b=rng.randrange(1,6),rng.randrange(1,6)
                law=ObservationLaw(f"law{k}",("lo","hi"),
                    (Q(a,6),Q(6-a,6)),(Q(b,6),Q(6-b,6)))
                probes.append(Probe(f"pr{k}",law,Q(rng.randrange(5),20)))
            init=ObservationLaw("initial",("first","second"),
                (Q(1,4),Q(3,4)),(Q(3,4),Q(1,4))) if rep%2 else ObservationLaw(
                    "initial",("start",),(Q(1),),(Q(1),))
            game=ActiveEvaluationGame(Q(rng.randrange(9),8),Q(rng.randrange(1,9)),
                  Q(rng.randrange(1,6)),horizon,tuple(probes),init,
                  Q(rng.randrange(-3,4),4))
            optimal=optimize_active_policy(game)
            policies=exhaustive_trees(game,horizon)
            independent=Q(0)
            for pe,pd in zip(init.evaluation,init.deployment):
                independent+=max(
                  game.prior*pe*independent_world_value(game,node,True)+
                  (1-game.prior)*pd*independent_world_value(game,node,False)
                  for node in policies)
            assert optimal.subjective_value==independent
            cert=certify_active_transfer(game,optimal.policy)
            assert cert.policy_value==optimal.subjective_value
            assert cert.exact_transcript_tv<=cert.transcript_tv_bound
            assert abs(cert.realized_gap)<=cert.exact_transcript_tv
            assert cert.likelihood_coverage>=0
            relabeled=sharp_transfer_relabel(game,optimal.policy)
            assert certify_active_transfer(game,relabeled).realized_gap==cert.exact_transcript_tv


def test_fail_closed_invalid_protocols_and_belief_cap():
    eq=ObservationLaw("eq",("one",),(Q(1),),(Q(1),))
    with pytest.raises(ValueError,match="exact rational"):
        ObservationLaw("bad",("x",),(1.0,),(1,))
    with pytest.raises(ValueError,match="normalized"):
        ObservationLaw("bad",("x",),(Q(1,2),),(Q(1),))
    with pytest.raises(ValueError,match="unique"):
        ObservationLaw("bad",("x","x"),(Q(1,2),Q(1,2)),(Q(1,2),Q(1,2)))
    with pytest.raises(ValueError,match="nonnegative"):
        Probe("bad",eq,Q(-1))
    with pytest.raises(ValueError,match="distinct"):
        ActiveEvaluationGame(Q(1,2),1,1,1,(Probe("dup",eq),Probe("dup",eq)))
    with pytest.raises(ValueError,match="horizon"):
        ActiveEvaluationGame(Q(1,2),1,1,-1,())
    with pytest.raises(ValueError,match="positive integer"):
        ActiveEvaluationGame(Q(1,2),1,1,1,(),max_states=0)
    with pytest.raises(ValueError,match="cap"):
        optimize_active_policy(ActiveEvaluationGame(Q(1,8),8,1,1,
                          example_game().probes,max_states=1))
    game=example_game()
    with pytest.raises(ValueError,match="branch count"):
        terminal_traces(game,ActivePolicy((PolicyNode("probe",0,()),)))
    with pytest.raises(ValueError,match="past horizon"):
        terminal_traces(ActiveEvaluationGame(Q(1,8),8,1,0,game.probes),
                        ActivePolicy((PolicyNode("probe",0,(PROTECT,EXPLOIT)),)))
    with pytest.raises(ValueError,match="unregistered"):
        terminal_traces(game,ActivePolicy((PolicyNode("arbitrary"),)))


def test_coupling_bound_is_exactly_attainable_for_repeated_disjoint_evidence():
    epsilon=Q(1,4)
    law=ObservationLaw("one_sided",("shared","eval_only"),
        (1-epsilon,epsilon),(Q(1),Q(0)))
    for horizon in (0,1,2,3,4):
        game=ActiveEvaluationGame(Q(1,2),1,1,horizon,(Probe("trial",law,0),))
        tree=EXPLOIT
        for _ in range(horizon):
            tree=PolicyNode("probe",0,(tree,tree))
        policy=ActivePolicy((tree,))
        cert=certify_active_transfer(game,policy)
        predicted=1-(1-epsilon)**horizon
        assert cert.exact_transcript_tv==cert.transcript_tv_bound==predicted
        relabeled=sharp_transfer_relabel(game,policy)
        witness=certify_active_transfer(game,relabeled)
        assert witness.realized_gap==predicted
        assert witness.deployment_protection==0


def test_hypothetical_future_influence_is_separable_from_information():
    identical=ObservationLaw("noise",("a","b"),(Q(1,2),Q(1,2)),
                             (Q(1,2),Q(1,2)))
    game=ActiveEvaluationGame(Q(1,8),8,1,2,
        (Probe("future_training",identical,Q(1,10),Q(1,5)),))
    optimal=optimize_active_policy(game)
    report=certify_active_transfer(game,optimal.policy)
    assert optimal.subjective_value==Q(6,5)
    assert report.policy_value==optimal.subjective_value
    assert report.evaluation_protection==report.deployment_protection==1
    assert report.exact_transcript_tv==0
    assert report.evaluation_expected_probes==report.deployment_expected_probes==2
