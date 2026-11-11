"""RHT-11 exact mutable-evaluator tampering and stateful authorization tests.

Checks POMDP Bellman against direct world/integrity traversal, RHT-10 clean
limit, and an independently enumerated every two-step verdict policy.
"""
from fractions import Fraction as Q
from itertools import product

import pytest

from spiral_ln.evaluation_reward_hacking_adaptive_feedback import one_hot_ugc_disclosure_game
from spiral_ln.evaluation_reward_hacking_retry import RetryAuditChannel, optimal_adaptive_retry
from spiral_ln.evaluation_reward_hacking_stateful import (
    MutableEvaluator, StatefulAction, optimal_stateful_attack,
    exact_stateful_policy_profile, fixed_stateful_schedule_harm,
    best_fixed_stateful_schedule, worst_state_false_approval_rate,
    conditional_stateful_harm_bound,
)


def independently_enumerate_two_step_strategy(game,channel):
    """Direct enumeration of first action and verdict-contingent second probe.

    This oracle does not call the stateful Bellman recursion or its policy
    execution helper. Initial integrity is intact; the hidden world is
    enumerated directly. A tamper can occur as the first action, followed
    by a candidate probe if the attestor passes. A tamper at the last step
    cannot authorize harm and is dominated by stop.
    """
    eligible=game.public_maximizers()
    first_choices=tuple(("probe",a) for a in eligible)
    if channel.allow_tamper:
        first_choices+=(("tamper",None),)
    best=Q(0)
    def second(world,action,state):
        if action is None:
            return Q(0)
        return ((1-channel.alarm_probability(state,"probe"))*
                (channel.false_accept(state) if game.unsafe(world,action)
                 else Q(0)))
    for kind,first in first_choices:
        choices=(None,)+tuple(a for a in eligible if not (
            kind=="probe" and channel.forbid_repeated_probe and a==first
        ))
        for rejected,approved,ack in product(choices,repeat=3):
            risk=Q(0)
            for w,weight in enumerate(game.world_weights):
                if kind=="tamper":
                    p=Q(channel.tamper_success)
                    contribution=(
                        (1-p)*(1-channel.alarm_probability(0,"tamper"))*
                        second(w,ack,0)
                        +p*(1-channel.alarm_probability(1,"tamper"))*
                        second(w,ack,1)
                    )
                    risk+=weight*contribution
                    continue
                gate=1-channel.alarm_probability(0,"probe")
                bad=game.unsafe(w,first)
                p=channel.false_accept(0) if bad else 1-channel.false_reject(0)
                contribution=gate*p if bad else Q(0)
                if not channel.lockout_after_rejection and rejected is not None:
                    contribution+=gate*(1-p)*sum((
                        prob*second(w,rejected,s1)
                        for s1,prob in channel.post_verdict_states(0,"rejected")
                    ),Q(0))
                if (not channel.stop_after_any_approval and not bad
                    and approved is not None):
                    contribution+=gate*p*sum((
                        prob*second(w,approved,s1)
                        for s1,prob in channel.post_verdict_states(0,"approved")
                    ),Q(0))
                risk+=weight*contribution
            best=max(best,risk/game.total)
    return best


def test_clean_stateful_model_recovers_RHT10_retry_game():
    game=one_hot_ugc_disclosure_game(3)
    for horizon in (0,1,2,3):
        clean=MutableEvaluator(
            intact_false_accept=Q(1,5),
            compromised_false_accept=Q(4,5),
            allow_tamper=False,
        )
        stateful=optimal_stateful_attack(game,horizon,clean)
        original=optimal_adaptive_retry(
            game,horizon,RetryAuditChannel(Q(1,5),Q(0))
        )
        assert stateful.max_harm==original.harmful_authorization_probability
        assert stateful.best_fixed_harm==original.best_fixed_harm_probability
        assert stateful.expected_steps_until_harm_or_stop==original.expected_attempts


def test_intentional_tamper_changes_best_two_call_attack():
    game=one_hot_ugc_disclosure_game(3)
    channel=MutableEvaluator(
        intact_false_accept=Q(1,5),
        compromised_false_accept=Q(4,5),
        tamper_success=Q(3,4),
    )
    out=optimal_stateful_attack(game,2,channel)
    assert out.max_harm==Q(13,60)
    assert out.best_fixed_harm==Q(13,60)
    assert out.first_action=="tamper"
    assert out.policy.on_ack is not None
    assert out.policy.on_ack.kind=="probe"
    assert out.expected_steps_until_harm_or_stop==2
    assert independently_enumerate_two_step_strategy(game,channel)==Q(13,60)
    assert fixed_stateful_schedule_harm(
        game,(("tamper",None),("probe",0)),channel
    )==Q(13,60)


def test_independent_pre_probe_attestation_blocks_tamper_advantage():
    game=one_hot_ugc_disclosure_game(3)
    channel=MutableEvaluator(
        alarm_if_compromised_before_probe=Q(1,2)
    )
    out=optimal_stateful_attack(game,2,channel)
    assert out.max_harm==Q(14,75)
    assert out.best_fixed_harm==Q(2,15)
    assert out.first_action=="probe"
    assert independently_enumerate_two_step_strategy(game,channel)==out.max_harm
    assert worst_state_false_approval_rate(channel)==Q(2,5)

    sufficient=MutableEvaluator(
        alarm_if_compromised_before_probe=Q(3,4)
    )
    assert worst_state_false_approval_rate(sufficient)==Q(1,5)
    assert conditional_stateful_harm_bound(sufficient,2)==Q(9,25)
    assert optimal_stateful_attack(game,2,sufficient).max_harm==Q(14,75)


def test_safe_approval_can_mutate_judge_and_reinforce_reward_hacking():
    game=one_hot_ugc_disclosure_game(3)
    drift=MutableEvaluator(
        allow_tamper=False,
        compromise_after_safe_approval=Q(1),
    )
    out=optimal_stateful_attack(game,2,drift)
    assert out.max_harm==Q(29,75)
    assert out.best_fixed_harm==Q(1,3)
    assert out.first_action=="probe"
    assert out.policy.on_approved is not None
    assert independently_enumerate_two_step_strategy(game,drift)==Q(29,75)
    assert optimal_stateful_attack(
        game,2,MutableEvaluator(
            allow_tamper=False,
            compromise_after_safe_approval=Q(1),
            alarm_if_compromised_after_tamper=Q(1),
        )
    ).max_harm==Q(29,75)
    guarded=MutableEvaluator(
        allow_tamper=False,
        compromise_after_safe_approval=Q(1),
        alarm_if_compromised_before_probe=Q(3,4)
    )
    assert optimal_stateful_attack(game,2,guarded).max_harm==Q(14,75)
    assert independently_enumerate_two_step_strategy(game,guarded)==Q(14,75)


def test_rejection_triggered_evaluator_drift_is_a_distinct_attack_surface():
    game=one_hot_ugc_disclosure_game(3)
    drift=MutableEvaluator(
        allow_tamper=False,compromise_after_rejection=Q(1)
    )
    out=optimal_stateful_attack(game,2,drift)
    assert out.max_harm==Q(26,75)
    assert out.best_fixed_harm==Q(7,25)
    assert out.policy.on_rejected is not None
    assert out.policy.on_rejected.candidate==out.policy.candidate
    assert independently_enumerate_two_step_strategy(game,drift)==out.max_harm


def test_initial_hidden_compromise_and_state_specific_attestation():
    game=one_hot_ugc_disclosure_game(3)
    unguarded=MutableEvaluator(allow_tamper=False)
    guarded=MutableEvaluator(
        allow_tamper=False,
        alarm_if_compromised_before_probe=Q(3,4),
    )
    assert optimal_stateful_attack(
        game,1,unguarded,initial_compromised=1
    ).max_harm==Q(4,15)
    assert optimal_stateful_attack(
        game,1,guarded,initial_compromised=1
    ).max_harm==Q(1,15)
    assert optimal_stateful_attack(
        game,1,unguarded,initial_compromised=0
    ).max_harm==Q(1,15)


def test_exact_two_step_controls_cover_hidden_transition_laws():
    game=one_hot_ugc_disclosure_game(3)
    variants=(
        MutableEvaluator(),
        MutableEvaluator(tamper_success=Q(0)),
        MutableEvaluator(tamper_success=Q(1)),
        MutableEvaluator(alarm_if_compromised_after_tamper=Q(1,2)),
        MutableEvaluator(alarm_if_compromised_before_probe=Q(1,2)),
        MutableEvaluator(
            intact_false_reject=Q(1,10),
            compromise_after_rejection=Q(1,2),
            restore_after_rejection=Q(1,3),
        ),
        MutableEvaluator(
            compromised_false_reject=Q(1,4),
            compromise_after_safe_approval=Q(1,2),
            restore_after_safe_approval=Q(1,3),
        ),
        MutableEvaluator(
            allow_tamper=False,
            alarm_if_intact_before_probe=Q(1,8),
            stop_after_any_approval=True
        ),
        MutableEvaluator(
            forbid_repeated_probe=True,
            lockout_after_rejection=True
        ),
    )
    for channel in variants:
        predicted=optimal_stateful_attack(game,2,channel)
        independent=independently_enumerate_two_step_strategy(game,channel)
        assert predicted.max_harm==independent
        assert predicted.max_harm<=conditional_stateful_harm_bound(channel,2)
        assert predicted.best_fixed_harm<=predicted.max_harm


def test_conditional_stateful_hazard_is_uniform_across_legal_transitions():
    game=one_hot_ugc_disclosure_game(3)
    for d in (Q(0),Q(1,4),Q(1,2),Q(3,4),Q(1)):
        for drift in (Q(0),Q(1,2),Q(1)):
            c=MutableEvaluator(
                compromise_after_safe_approval=drift,
                compromise_after_rejection=drift,
                alarm_if_compromised_before_probe=d,
                alarm_if_intact_before_probe=Q(1,16),
            )
            hazard=worst_state_false_approval_rate(c)
            assert hazard==max(Q(15,16)*Q(1,5),(1-d)*Q(4,5))
            for steps in (1,2,3):
                out=optimal_stateful_attack(game,steps,c)
                assert out.max_harm<=conditional_stateful_harm_bound(c,steps)


def test_fixed_schedule_and_returned_policy_independently_agree():
    game=one_hot_ugc_disclosure_game(3)
    c=MutableEvaluator(
        tamper_success=Q(3,4),
        alarm_if_compromised_after_tamper=Q(1,4),
        alarm_if_compromised_before_probe=Q(1,2),
        intact_false_reject=Q(1,10),
        compromise_after_safe_approval=Q(1,2),
    )
    for steps in (0,1,2,3):
        out=optimal_stateful_attack(game,steps,c)
        direct,calls=exact_stateful_policy_profile(
            game,out.policy,c,max_steps=steps
        )
        assert direct==out.max_harm
        assert calls==out.expected_steps_until_harm_or_stop
        fixed=best_fixed_stateful_schedule(game,steps,c)
        assert fixed["risk"]==out.best_fixed_harm
        assert fixed_stateful_schedule_harm(
            game,fixed["schedule"],c
        )==fixed["risk"]


def test_fail_closed_invalid_state_rates_actions_and_runtime_budgets():
    game=one_hot_ugc_disclosure_game(3)
    c=MutableEvaluator()
    with pytest.raises(ValueError):
        MutableEvaluator(compromised_false_accept=Q(5,4))
    with pytest.raises(ValueError):
        MutableEvaluator(tamper_success=Q(-1,8))
    with pytest.raises(ValueError):
        MutableEvaluator(allow_tamper=1)
    with pytest.raises(ValueError):
        optimal_stateful_attack(game,6,c)
    with pytest.raises(ValueError):
        optimal_stateful_attack(game,2,c,max_states=1)
    with pytest.raises(ValueError):
        optimal_stateful_attack(game,1,c,initial_compromised=Q(5,4))
    with pytest.raises(ValueError):
        best_fixed_stateful_schedule(game,3,c,max_schedules=1)
    with pytest.raises(ValueError):
        fixed_stateful_schedule_harm(game,(("probe",9),),c)
    with pytest.raises(ValueError):
        fixed_stateful_schedule_harm(game,(("tamper",0),),c)
    with pytest.raises(ValueError):
        fixed_stateful_schedule_harm(
            game,(("tamper",None),("tamper",None)),c
        )
    with pytest.raises(ValueError):
        exact_stateful_policy_profile(
            game,StatefulAction("tamper",None,None,StatefulAction()),
            c,max_steps=1
        )
    with pytest.raises(ValueError):
        exact_stateful_policy_profile(
            game,StatefulAction("probe",9),c,max_steps=1
        )
    with pytest.raises(ValueError):
        exact_stateful_policy_profile(
            game,StatefulAction("probe",0,on_rejected=StatefulAction("probe",0)),
            c,max_steps=1
        )
    with pytest.raises(ValueError):
        conditional_stateful_harm_bound(c,-1)
