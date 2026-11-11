"""RHT-21 exact adaptive Bayesian observation/cue reward-hacking controls."""
from fractions import Fraction as Q
from itertools import product
import random

import pytest

from spiral_ln.evaluation_reward_training_awareness_adaptive import (
    EvaluationProbe, AdaptiveCuePolicy, AdaptiveEvaluationGame,
    PROTECT, EXPLOIT,
)


def binary_probe(name="signal", cost=Q(0)):
    return EvaluationProbe(
        name, ("eval_looking", "deploy_looking"),
        (Q(3, 4), Q(1, 4)), (Q(1, 4), Q(3, 4)), cost,
    )


def game(probes=None, horizon=1, prior=Q(1, 2), delta=Q(0), **kwargs):
    return AdaptiveEvaluationGame(
        (binary_probe(),) if probes is None else tuple(probes),
        prior, Q(1), Q(1), horizon, delta, **kwargs,
    )


def all_trees(probes, horizon):
    """Independent complete grammar enumeration without Bellman recursion."""
    terminal=(PROTECT,EXPLOIT)
    if horizon == 0:
        return terminal
    children=all_trees(probes,horizon-1)
    return terminal+tuple(
        AdaptiveCuePolicy("probe",p.name,branches)
        for p in probes
        for branches in product(children, repeat=len(p.observations))
    )


def direct_path_mass(policy, probes, world):
    """Independent leaf-path traversal with world-specific likelihood product."""
    lookup={p.name:p for p in probes}
    result=[]
    def rec(node, probability, depth):
        if node.kind != "probe":
            result.append((node.kind,probability,depth))
            return
        probe=lookup[node.probe]
        kernel=probe.evaluation if world=="E" else probe.deployment
        for i,child in enumerate(node.branches):
            rec(child,probability*kernel[i],depth+1)
    rec(policy,Q(1),0)
    return result


def test_one_probe_exact_posterior_policy_and_sharp_transfer():
    g=game()
    assert g.posterior()==Q(1,2)
    assert g.posterior((("signal","eval_looking"),))==Q(3,4)
    assert g.posterior((("signal","deploy_looking"),))==Q(1,4)
    assert g.posterior_martingale((), "signal")== (Q(1,2), Q(1,2))
    result=g.bayes_optimal()
    assert result.policy==AdaptiveCuePolicy("probe","signal",(PROTECT,EXPLOIT))
    assert result.subjective_value==Q(3,4)
    assert result.audit.evaluation_compliance==Q(3,4)
    assert result.audit.deployment_compliance==Q(1,4)
    assert result.audit.transcript_total_variation==Q(1,2)
    assert result.audit.guaranteed_deployment_compliance==Q(1,4)
    assert result.audit.evaluation_expected_probes==1
    assert result.audit.deployment_expected_probes==1
    controlled=g.controlled_audit_gap()
    assert controlled.maximum_audit_deployment_gap==Q(1,2)
    assert controlled.maximum_coupling_bound==Q(1,2)


def test_active_probe_selection_pays_cost_for_more_information():
    weak=EvaluationProbe(
        "weak", ("one","zero"),
        (Q(3,5),Q(2,5)),(Q(2,5),Q(3,5)), Q(0),
    )
    strong=EvaluationProbe(
        "strong", ("one","zero"),
        (Q(9,10),Q(1,10)),(Q(1,10),Q(9,10)),Q(1,10),
    )
    g=game((weak,strong))
    result=g.bayes_optimal()
    assert result.policy.probe=="strong"
    assert result.subjective_value==Q(4,5)
    assert result.audit.evaluation_compliance==Q(9,10)
    assert result.audit.deployment_compliance==Q(1,10)
    assert result.audit.transcript_total_variation==Q(4,5)
    assert g.controlled_audit_gap().maximum_audit_deployment_gap==Q(4,5)


def test_three_repeated_probes_improve_on_one_step_and_coupling_bound():
    one=game(horizon=1)
    three=game(horizon=3)
    first=one.bayes_optimal()
    later=three.bayes_optimal()
    assert first.subjective_value==Q(3,4)
    assert later.subjective_value==Q(27,32)
    assert later.audit.evaluation_compliance==Q(27,32)
    assert later.audit.deployment_compliance==Q(5,32)
    assert later.audit.observed_gap==Q(11,16)
    controlled=three.controlled_audit_gap()
    assert controlled.maximum_audit_deployment_gap==Q(11,16)
    assert controlled.maximum_coupling_bound==Q(7,8)
    assert later.audit.transcript_total_variation<=controlled.maximum_coupling_bound
    # The agent may stop as soon as further observations cannot change choice.
    assert later.audit.evaluation_expected_probes<3


def test_world_identical_and_fully_revealing_negative_controls():
    identical=EvaluationProbe("same",("0","1"),(Q(1,2),Q(1,2)),(Q(1,2),Q(1,2)),Q(1,10))
    neutral=game((identical,),3)
    assert neutral.bayes_optimal().policy==EXPLOIT
    assert neutral.bayes_optimal().subjective_value==Q(1,2)
    assert neutral.controlled_audit_gap().maximum_audit_deployment_gap==0
    assert neutral.maximal_coupling_bound()==0
    reveal=EvaluationProbe("reveal",("E","D"),(Q(1),Q(0)),(Q(0),Q(1)))
    g=game((reveal,),1)
    result=g.bayes_optimal()
    assert result.subjective_value==1
    assert result.audit.evaluation_compliance==1
    assert result.audit.deployment_compliance==0
    assert g.controlled_audit_gap().maximum_audit_deployment_gap==1
    assert g.posterior((("reveal","E"),))==1
    assert g.posterior((("reveal","D"),))==0
    absent=game((reveal,),1,prior=Q(0))
    assert absent.posterior((("reveal","E"),)) is None


def test_future_policy_delta_changes_bayesian_terminal_action():
    no_probe=game((),0)
    assert no_probe.bayes_optimal().policy==EXPLOIT
    positive=game((),0,delta=Q(5,2))
    negative=game((),0,delta=-Q(5,2))
    assert positive.bayes_optimal().policy==PROTECT
    assert negative.bayes_optimal().policy==EXPLOIT
    assert positive.policy_value(PROTECT)==Q(3)
    assert positive.policy_value(EXPLOIT)==Q(1,2)


def test_random_complete_policy_census_and_independent_world_paths():
    rng=random.Random(21021)
    for _ in range(24):
        probes=[]
        for j in range(2):
            e=Q(rng.randrange(5),4)
            d=Q(rng.randrange(5),4)
            probes.append(EvaluationProbe(
                "probe_"+str(j),("1","0"),(e,1-e),(d,1-d),
                Q(rng.randrange(3),8),
            ))
        g=AdaptiveEvaluationGame(
            tuple(probes),Q(rng.randrange(9),8),Q(rng.randrange(1,7),2),
            Q(rng.randrange(1,7),2),2,
            Q(rng.randrange(-3,4),4),
        )
        policies=all_trees(g.probes,2)
        assert len(policies)==202
        result=g.bayes_optimal()
        assert result.subjective_value==max(g.policy_value(p) for p in policies)
        controlled=g.controlled_audit_gap()
        assert controlled.maximum_audit_deployment_gap==max(
            g.audit(p).observed_gap for p in policies
        )
        assert controlled.maximum_audit_deployment_gap<=g.maximal_coupling_bound()
        sample=rng.choice(policies)
        leaf_e=direct_path_mass(sample,g.probes,"E")
        leaf_d=direct_path_mass(sample,g.probes,"D")
        audit=g.audit(sample)
        assert sum((v for kind,v,depth in leaf_e if kind=="protect"),Q(0))==audit.evaluation_compliance
        assert sum((v for kind,v,depth in leaf_d if kind=="protect"),Q(0))==audit.deployment_compliance
        assert sum((depth*v for _,v,depth in leaf_e),Q(0))==audit.evaluation_expected_probes
        assert sum((depth*v for _,v,depth in leaf_d),Q(0))==audit.deployment_expected_probes
        assert audit.observed_gap <= audit.transcript_total_variation
        assert audit.transcript_total_variation <= controlled.maximum_coupling_bound


def test_bayes_posterior_does_not_drift_in_expectation():
    g=game((binary_probe("a"),binary_probe("b")),2,prior=Q(2,5))
    for hist in ((),(("a","eval_looking"),),(("a","deploy_looking"),)):
        current, after=g.posterior_martingale(hist,"b")
        assert current==after
    assert g.posterior((("a","eval_looking"),("b","deploy_looking")))==Q(2,5)


def test_invalid_kernel_policy_history_and_caps_fail_closed():
    with pytest.raises(ValueError,match="normalized"):
        EvaluationProbe("bad",("x","y"),(Q(1,2),Q(1,4)),(Q(1),Q(0)))
    with pytest.raises(ValueError,match="kernel dimensions"):
        EvaluationProbe("bad",("x","y"),(Q(1),),(Q(1),Q(0)))
    with pytest.raises(ValueError,match="nonnegative"):
        EvaluationProbe("bad",("x",),(Q(1),),(Q(1),),-Q(1,2))
    with pytest.raises(ValueError,match="unique"):
        game((binary_probe("dup"),binary_probe("dup")))
    with pytest.raises(ValueError,match="max_probes"):
        game(horizon=-1)
    with pytest.raises(ValueError,match="positive integer"):
        game(max_states=0)
    g=game()
    with pytest.raises(ValueError,match="observation branch"):
        g.audit(AdaptiveCuePolicy("probe","signal",(PROTECT,)))
    with pytest.raises(ValueError,match="unknown probe"):
        g.audit(AdaptiveCuePolicy("probe","missing",(PROTECT,EXPLOIT)))
    with pytest.raises(ValueError,match="exhausted probe budget"):
        game(horizon=0).audit(AdaptiveCuePolicy("probe","signal",(PROTECT,EXPLOIT)))
    with pytest.raises(ValueError,match="unknown observation"):
        g.posterior((("signal","wrong"),))
    with pytest.raises(ValueError,match="state budget"):
        game(max_states=1).bayes_optimal()
    with pytest.raises(ValueError,match="state budget"):
        game(max_states=1).controlled_audit_gap()
