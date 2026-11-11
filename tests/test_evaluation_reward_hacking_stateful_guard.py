"""RHT-11 exact attestation and benign throughput certificates.

Independent enumerator traverses every alarm/verdict/hidden-integrity path
for the benign reference. The adversarial side uses the independently
verified RHT-11 POMDP with an exact conditional-hazard inequality.
"""
from fractions import Fraction as Q
from itertools import product

import pytest

from spiral_ln.evaluation_reward_hacking_adaptive_feedback import one_hot_ugc_disclosure_game
from spiral_ln.evaluation_reward_hacking_stateful import (
    MutableEvaluator, optimal_stateful_attack,
    worst_state_false_approval_rate,
)
from spiral_ln.evaluation_reward_hacking_stateful_guard import (
    benign_stateful_profile,
    required_preprobe_detection_for_baseline_hazard,
    certify_stateful_attestation, choose_stateful_attestor,
)


def exhaustive_safe_verdict_tree(channel, horizon, safe_actions=2, start=Q(0)):
    """Enumerate every hidden-state/attestation/verdict sequence from scratch."""
    allowed=(min(horizon,safe_actions) if channel.forbid_repeated_probe
             else horizon)
    total_any=total_approved=total_calls=Q(0)

    def visit(state,left,p,any_approved,n_approved,n_calls):
        nonlocal total_any,total_approved,total_calls
        if left==0 or not p:
            total_any+=p*int(any_approved)
            total_approved+=p*n_approved
            total_calls+=p*n_calls
            return
        fail=(Q(channel.alarm_if_compromised_before_probe) if state
              else Q(channel.alarm_if_intact_before_probe))
        # An alarm ends the session without an accepted action.
        visit(state,0,p*fail,any_approved,n_approved,n_calls+1)
        passprob=p*(1-fail)
        approval=1-(Q(channel.compromised_false_reject) if state
                    else Q(channel.intact_false_reject))
        for verdict,weight in ((True,approval),(False,1-approval)):
            if not weight:
                continue
            count=n_approved+int(verdict)
            got=any_approved or verdict
            if ((verdict and channel.stop_after_any_approval)
                or (not verdict and channel.lockout_after_rejection)):
                visit(state,0,passprob*weight,got,count,n_calls+1)
                continue
            if state==0:
                drift=(Q(channel.compromise_after_safe_approval) if verdict
                       else Q(channel.compromise_after_rejection))
                branch=((0,1-drift),(1,drift))
            else:
                recovery=(Q(channel.restore_after_safe_approval) if verdict
                          else Q(channel.restore_after_rejection))
                branch=((0,recovery),(1,1-recovery))
            for new_state,transition in branch:
                visit(new_state,left-1,passprob*weight*transition,
                      got,count,n_calls+1)

    for state,p in ((0,1-Q(start)),(1,Q(start))):
        if p:
            visit(state,allowed,p,False,0,0)
    return total_any,total_approved,total_calls


def detector_variants():
    base=dict(
        intact_false_accept=Q(1,5),
        compromised_false_accept=Q(4,5),
        tamper_success=Q(3,4),
    )
    weak=MutableEvaluator(**base)
    medium=MutableEvaluator(
        **base,
        alarm_if_compromised_before_probe=Q(1,2),
        alarm_if_intact_before_probe=Q(1,20),
    )
    strong=MutableEvaluator(
        **base,
        alarm_if_compromised_before_probe=Q(3,4),
        alarm_if_intact_before_probe=Q(1,10),
    )
    return weak,medium,strong


def test_benign_profile_agrees_with_complete_external_branch_enumeration():
    for beta0,beta1 in (
        (Q(0),Q(0)),(Q(1,10),Q(1,4)),(Q(1),Q(0))
    ):
        for flags in ((False,False,False),(True,False,False),
                      (False,True,False),(False,False,True)):
            channel=MutableEvaluator(
                intact_false_reject=beta0,
                compromised_false_reject=beta1,
                alarm_if_intact_before_probe=Q(1,8),
                alarm_if_compromised_before_probe=Q(1,2),
                compromise_after_rejection=Q(1,3),
                compromise_after_safe_approval=Q(1,2),
                restore_after_rejection=Q(1,4),
                restore_after_safe_approval=Q(1,5),
                forbid_repeated_probe=flags[0],
                lockout_after_rejection=flags[1],
                stop_after_any_approval=flags[2],
            )
            for horizon in range(4):
                for start in (Q(0),Q(1,2),Q(1)):
                    reported=benign_stateful_profile(
                        channel,horizon,initial_compromised=start,
                        safe_actions=2,
                    )
                    oracle=exhaustive_safe_verdict_tree(
                        channel,horizon,2,start
                    )
                    assert (
                        reported.at_least_one_safe_authorization,
                        reported.expected_safe_authorizations,
                        reported.expected_probe_calls,
                    )==oracle


def test_detection_threshold_from_external_root_attestation():
    weak,medium,strong=detector_variants()
    for channel in (weak,medium,strong):
        assert required_preprobe_detection_for_baseline_hazard(channel)==Q(3,4)
    assert required_preprobe_detection_for_baseline_hazard(
        MutableEvaluator(
            intact_false_accept=Q(4,5),
            compromised_false_accept=Q(1,5)
        )
    )==0
    assert required_preprobe_detection_for_baseline_hazard(
        MutableEvaluator(
            intact_false_accept=Q(0),
            compromised_false_accept=Q(4,5)
        )
    )==1
    assert (worst_state_false_approval_rate(weak),
            worst_state_false_approval_rate(medium),
            worst_state_false_approval_rate(strong))==(
                Q(4,5),Q(2,5),Q(1,5)
            )


def test_three_attestor_variants_have_exact_harm_throughput_frontier():
    game=one_hot_ugc_disclosure_game(3)
    weak,medium,strong=detector_variants()
    reports=tuple(certify_stateful_attestation(
        game,2,c,
        maximum_cumulative_harm=Q(7,40),
        minimum_benign_safe_authorization=Q(9,10),
        minimum_benign_expected_safe_authorizations=Q(17,10),
    ) for c in (weak,medium,strong))
    assert [r.attack_harm for r in reports]==[
        Q(13,60),Q(5149,30000),Q(393,2500)
    ]
    assert [r.benign_safe_authorization for r in reports]==[
        Q(1),Q(19,20),Q(9,10)
    ]
    assert [r.benign_expected_safe_authorizations for r in reports]==[
        Q(2),Q(741,400),Q(171,100)
    ]
    assert [r.benign_expected_probe_calls for r in reports]==[
        Q(2),Q(39,20),Q(19,10)
    ]
    assert [r.passed for r in reports]==[False,True,True]
    for report in reports:
        assert report.attack_harm<=report.conservative_cumulative_harm_bound
        assert report.best_fixed_harm<=report.attack_harm


def test_joint_safety_and_liveness_thresholds_choose_exact_detector():
    game=one_hot_ugc_disclosure_game(3)
    controls=detector_variants()
    common=dict(
        minimum_benign_safe_authorization=Q(9,10),
        minimum_benign_expected_safe_authorizations=Q(17,10),
    )
    moderate=choose_stateful_attestor(
        game,2,controls,
        maximum_cumulative_harm=Q(7,40),
        **common
    )
    assert moderate is not None
    assert moderate.channel==controls[1]
    assert moderate.attack_harm==Q(5149,30000)
    strict=choose_stateful_attestor(
        game,2,controls,
        maximum_cumulative_harm=Q(4,25),
        **common
    )
    assert strict is not None
    assert strict.channel==controls[2]
    assert strict.attack_harm==Q(393,2500)
    hazard_guard=choose_stateful_attestor(
        game,2,controls,
        maximum_cumulative_harm=Q(7,40),
        maximum_history_conditional_hazard=Q(1,5),
        **common
    )
    assert hazard_guard is not None and hazard_guard.channel==controls[2]
    assert choose_stateful_attestor(
        game,2,controls,
        maximum_cumulative_harm=Q(7,50),
        **common
    ) is None
    assert choose_stateful_attestor(
        game,2,controls,
        maximum_cumulative_harm=Q(7,40),
        maximum_history_conditional_hazard=Q(1,5),
        minimum_benign_safe_authorization=Q(9,10),
        minimum_benign_expected_safe_authorizations=Q(9,5)
    ) is None


def test_stateful_liveness_is_not_trivially_restored_by_perfect_detection():
    # If every compromised evaluator is caught, harm from that state
    # disappears. A false alarm on an intact state still reduces
    # genuinely safe authorizations, so the gate must enforce both sides.
    game=one_hot_ugc_disclosure_game(3)
    channel=MutableEvaluator(
        alarm_if_compromised_before_probe=Q(1),
        alarm_if_intact_before_probe=Q(1,4),
        allow_tamper=False,
    )
    cert=certify_stateful_attestation(
        game,2,channel,
        maximum_cumulative_harm=Q(1),
        minimum_benign_safe_authorization=Q(9,10),
        minimum_benign_expected_safe_authorizations=Q(1),
    )
    assert cert.benign_safe_authorization==Q(3,4)
    assert not cert.passed


def test_bad_detector_calibration_and_gate_contracts_fail_closed():
    game=one_hot_ugc_disclosure_game(3)
    weak,medium,strong=detector_variants()
    with pytest.raises(ValueError):
        benign_stateful_profile(weak,-1)
    with pytest.raises(ValueError):
        benign_stateful_profile(weak,2,initial_compromised=Q(3,2))
    with pytest.raises(ValueError):
        benign_stateful_profile(weak,2,safe_actions=0)
    with pytest.raises(ValueError):
        certify_stateful_attestation(
            game,2,weak,maximum_cumulative_harm=Q(-1),
            minimum_benign_safe_authorization=0,
            minimum_benign_expected_safe_authorizations=0
        )
    kwargs=dict(
        maximum_cumulative_harm=Q(1),
        minimum_benign_safe_authorization=Q(0),
        minimum_benign_expected_safe_authorizations=Q(0)
    )
    with pytest.raises(ValueError):
        choose_stateful_attestor(game,2,(),**kwargs)
    with pytest.raises(ValueError):
        choose_stateful_attestor(game,2,(weak,weak),**kwargs)
    with pytest.raises(ValueError):
        choose_stateful_attestor(
            game,2,(weak,MutableEvaluator(tamper_success=Q(1,2))),
            **kwargs
        )
    with pytest.raises(ValueError):
        choose_stateful_attestor(
            game,2,(weak,strong),
            maximum_cumulative_harm=Q(1),
            minimum_benign_safe_authorization=Q(0),
            minimum_benign_expected_safe_authorizations=Q(0),
            maximum_history_conditional_hazard=Q(2),
        )
