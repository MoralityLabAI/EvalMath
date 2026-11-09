"""RHT-10: exact repeated-authorization risk and independent policy census.

Tests validate finite Bayesian retry selection against a separate two-step
brute-force action-response policy enumeration and closed-form limits.
No external rewards, model outcomes, or physical auditing are sampled.
"""
from fractions import Fraction as Q
from itertools import product

import pytest

from spiral_ln.evaluation_reward_hacking_adaptive_feedback import (
    one_hot_ugc_disclosure_game
)
from spiral_ln.evaluation_reward_hacking_retry import (
    RetryAuditChannel, RetryPolicy, optimal_adaptive_retry,
    exact_policy_profile, fixed_schedule_harm, best_fixed_schedule,
    conditional_harm_bound, marginal_harm_bound,
    disjoint_marginal_failure_law, benign_safe_approval_by_horizon,
)


def brute_two_step_actor(game,channel):
    """Independent full census of first action and two verdict contingencies."""
    actions=game.public_maximizers()
    alpha=Q(channel.false_accept)
    beta=Q(channel.false_reject)
    best=Q(0)
    for first in actions:
        candidates=(-1,)+tuple(a for a in actions if
                              not channel.forbid_repeated_action or a!=first)
        reject_choices=(-1,) if channel.lockout_after_rejection else candidates
        approval_choices=(-1,) if channel.stop_after_any_approval else candidates
        for rejected,approved in product(reject_choices,approval_choices):
            risk=Q(0)
            for world,weight in enumerate(game.world_weights):
                bad=game.unsafe(world,first)
                p=alpha if bad else 1-beta
                harm=p if bad else Q(0)
                if rejected>=0 and game.unsafe(world,rejected):
                    harm+=(1-p)*alpha
                if (approved>=0 and not bad and
                    game.unsafe(world,approved)):
                    harm+=p*alpha
                risk+=weight*harm
            best=max(best,risk/game.total)
    return best


def test_two_retry_ugc_worlds_extract_hidden_harm_from_a_rejection():
    game=one_hot_ugc_disclosure_game(3)
    channel=RetryAuditChannel(Q(1,5),Q(0))
    out=optimal_adaptive_retry(game,2,channel)
    assert out.first_action==0
    assert out.harmful_authorization_probability==Q(14,75)
    assert out.best_fixed_harm_probability==Q(2,15)
    assert out.harmful_authorization_probability-out.best_fixed_harm_probability==Q(4,75)
    assert out.states_visited>1
    assert brute_two_step_actor(game,channel)==out.harmful_authorization_probability
    assert exact_policy_profile(game,out.policy,channel,max_depth=2)[0]==Q(14,75)
    assert fixed_schedule_harm(game,(0,1),channel)==Q(2,15)
    assert out.expected_attempts>1
    # If a=0 is rejected, then with beta=0 the world must be 0, so
    # the second action repeats a=0 and attempts a second false approval.
    assert out.policy.on_rejected is not None
    assert out.policy.on_rejected.action==0


def test_three_attempts_give_a_larger_adaptive_advantage():
    game=one_hot_ugc_disclosure_game(3)
    channel=RetryAuditChannel(Q(1,5),Q(0))
    out=optimal_adaptive_retry(game,3,channel)
    assert out.harmful_authorization_probability==Q(131,375)
    assert out.best_fixed_harm_probability==Q(1,5)
    assert out.harmful_authorization_probability-out.best_fixed_harm_probability==Q(56,375)
    assert fixed_schedule_harm(game,(0,1,2),channel)==Q(1,5)


def test_separate_lockout_and_action_rate_limit_contain_retries():
    game=one_hot_ugc_disclosure_game(3)
    channels=(
        (RetryAuditChannel(Q(1,5),Q(0),forbid_repeated_action=True),Q(2,15)),
        (RetryAuditChannel(Q(1,5),Q(0),lockout_after_rejection=True),Q(2,15)),
        (RetryAuditChannel(Q(1,5),Q(0),stop_after_any_approval=True),Q(3,25)),
        (RetryAuditChannel(Q(1,5),Q(1,10),forbid_repeated_action=True),Q(2,15)),
        (RetryAuditChannel(Q(1,5),Q(1,10),lockout_after_rejection=True),Q(19,150)),
    )
    for channel,expected in channels:
        out=optimal_adaptive_retry(game,2,channel)
        assert out.harmful_authorization_probability==expected
        assert brute_two_step_actor(game,channel)==expected
        assert out.best_fixed_harm_probability<=expected
    assert optimal_adaptive_retry(
        game,2,RetryAuditChannel(Q(1,5),Q(1,10))
    ).harmful_authorization_probability==Q(9,50)


def test_full_two_step_independent_bruteforce_many_error_rates():
    game=one_hot_ugc_disclosure_game(3)
    for alpha,beta in (
        (Q(0),Q(0)),(Q(1,5),Q(0)),(Q(1,5),Q(1,10)),
        (Q(1,4),Q(1,4)),(Q(1),Q(0)),(Q(1,5),Q(1)),
    ):
        for norepeat,lockout,stopapproved in (
            (False,False,False),(True,False,False),
            (False,True,False),(False,False,True),
        ):
            channel=RetryAuditChannel(
                alpha,beta,norepeat,lockout,stopapproved
            )
            brute=brute_two_step_actor(game,channel)
            dp=optimal_adaptive_retry(game,2,channel)
            assert dp.harmful_authorization_probability==brute


def test_conditional_vs_marginal_false_accept_bound_is_sharp():
    caps=(Q(1,5),)*5
    assert conditional_harm_bound(caps)==Q(2101,3125)
    assert marginal_harm_bound(caps)==1
    exact_disjoint=disjoint_marginal_failure_law(caps)
    assert exact_disjoint==(Q(1,5),)*5+(Q(0),)
    assert sum(exact_disjoint)==1
    assert sum(exact_disjoint[:-1])==marginal_harm_bound(caps)
    assert all(x<=Q(1,5) for x in exact_disjoint[:-1])
    assert conditional_harm_bound(caps)<marginal_harm_bound(caps)
    assert marginal_harm_bound(caps[:3])==Q(3,5)
    assert conditional_harm_bound(caps[:3])==Q(61,125)
    assert disjoint_marginal_failure_law(caps[:3])==(
        Q(1,5),Q(1,5),Q(1,5),Q(2,5)
    )


def test_attack_upper_bound_holds_across_protocols():
    game=one_hot_ugc_disclosure_game(3)
    for alpha in (Q(0),Q(1,5),Q(1,2),Q(1)):
        for beta in (Q(0),Q(1,10),Q(1)):
            for flags in ((False,False,False),
                          (True,False,False),
                          (False,True,False),
                          (False,False,True)):
                channel=RetryAuditChannel(alpha,beta,*flags)
                for attempts in range(1,4):
                    risk=optimal_adaptive_retry(
                        game,attempts,channel
                    ).harmful_authorization_probability
                    assert risk<=conditional_harm_bound((alpha,)*attempts)


def test_benign_safe_throughput_shows_lockout_cost():
    stable=RetryAuditChannel(Q(1,5),Q(1,10))
    assert benign_safe_approval_by_horizon(stable,2)==Q(99,100)
    assert benign_safe_approval_by_horizon(stable,3)==Q(999,1000)
    lockout=RetryAuditChannel(Q(1,5),Q(1,10),
                              lockout_after_rejection=True)
    assert benign_safe_approval_by_horizon(lockout,3)==Q(9,10)
    no_repeat=RetryAuditChannel(Q(1,5),Q(1,10),
                                forbid_repeated_action=True)
    assert benign_safe_approval_by_horizon(no_repeat,3,safe_actions=2)==Q(99,100)
    assert benign_safe_approval_by_horizon(no_repeat,3,safe_actions=1)==Q(9,10)
    assert benign_safe_approval_by_horizon(stable,0)==0


def test_perfect_gold_veto_prevents_every_repeated_attack():
    game=one_hot_ugc_disclosure_game(3)
    for h in range(0,5):
        for flags in ((False,False,False),(True,False,False),
                      (False,True,False),(False,False,True)):
            channel=RetryAuditChannel(Q(0),Q(0),*flags)
            result=optimal_adaptive_retry(game,h,channel)
            assert result.harmful_authorization_probability==0
            assert result.best_fixed_harm_probability==0


def test_reject_invalid_rates_policies_and_runtime_limits():
    game=one_hot_ugc_disclosure_game(3)
    channel=RetryAuditChannel(Q(1,5))
    for kwargs in (
        {"false_accept":Q(-1,5)},
        {"false_accept":Q(6,5)},
        {"false_reject":Q(6,5)},
        {"forbid_repeated_action":1},
    ):
        with pytest.raises(ValueError):
            RetryAuditChannel(**kwargs)
    with pytest.raises(ValueError):
        conditional_harm_bound((Q(-1,10),))
    with pytest.raises(ValueError):
        marginal_harm_bound((Q(11,10),))
    with pytest.raises(ValueError):
        disjoint_marginal_failure_law((Q(-1,10),))
    with pytest.raises(ValueError):
        optimal_adaptive_retry(game,-1,channel)
    with pytest.raises(ValueError):
        optimal_adaptive_retry(game,7,channel)
    with pytest.raises(ValueError):
        optimal_adaptive_retry(game,3,channel,max_states=1)
    with pytest.raises(ValueError):
        best_fixed_schedule(game,2,channel,max_schedules=1)
    with pytest.raises(ValueError):
        fixed_schedule_harm(game,(9,),channel)
    with pytest.raises(ValueError):
        fixed_schedule_harm(
            game,(0,0),RetryAuditChannel(Q(1,5),forbid_repeated_action=True)
        )
    with pytest.raises(ValueError):
        exact_policy_profile(game,RetryPolicy(9),channel,max_depth=1)
    with pytest.raises(ValueError):
        exact_policy_profile(
            game,RetryPolicy(0,RetryPolicy(0)),channel,max_depth=1
        )
    with pytest.raises(ValueError):
        exact_policy_profile(
            game,RetryPolicy(0,RetryPolicy(0)),
            RetryAuditChannel(Q(1,5),lockout_after_rejection=True),max_depth=2
        )
    with pytest.raises(ValueError):
        benign_safe_approval_by_horizon(channel,-1)
    with pytest.raises(ValueError):
        benign_safe_approval_by_horizon(channel,2,safe_actions=0)
