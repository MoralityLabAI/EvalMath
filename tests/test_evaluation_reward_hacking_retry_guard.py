"""RHT-10: exact throughput-aware retry guard against an adaptive attacker."""
from fractions import Fraction as Q
from itertools import product

import pytest

from spiral_ln.evaluation_reward_hacking_adaptive_feedback import one_hot_ugc_disclosure_game
from spiral_ln.evaluation_reward_hacking_retry import RetryAuditChannel
from spiral_ln.evaluation_reward_hacking_retry_guard import (
    benign_expected_safe_authorizations, certify_retry_control,
    select_retry_control,
)


def independently_enumerate_benign_verdicts(channel, horizon, safe_actions):
    """Brute full 2^H sequences of iid safe-action approval outcomes."""
    length=min(horizon,safe_actions) if channel.forbid_repeated_action else horizon
    approve=1-Q(channel.false_reject)
    rejected=Q(channel.false_reject)
    success=Q(0)
    expected=Q(0)
    for possible in product((False,True),repeat=length):
        mass=Q(1)
        for ans in possible:
            mass*=approve if ans else rejected
        accepted=0
        for ans in possible:
            if ans:
                accepted+=1
                if channel.stop_after_any_approval:
                    break
            elif channel.lockout_after_rejection:
                break
        success+=mass*int(accepted>0)
        expected+=mass*accepted
    return success,expected


def test_safe_benign_throughput_matches_full_verdict_enumeration():
    for beta in (Q(0),Q(1,10),Q(1,2),Q(1)):
        for flags in product((False,True),repeat=3):
            channel=RetryAuditChannel(Q(1,5),beta,*flags)
            for horizon in range(0,5):
                safe_ones=2
                p,expected=independently_enumerate_benign_verdicts(
                    channel,horizon,safe_ones
                )
                from spiral_ln.evaluation_reward_hacking_retry import benign_safe_approval_by_horizon
                assert benign_safe_approval_by_horizon(
                    channel,horizon,safe_actions=safe_ones
                )==p
                assert benign_expected_safe_authorizations(
                    channel,horizon,safe_actions=safe_ones
                )==expected


def test_exact_two_sided_control_frontier_yields_no_repeat_rule():
    game=one_hot_ugc_disclosure_game(3)
    a,b=Q(1,5),Q(1,10)
    normal=RetryAuditChannel(a,b)
    no_repeat=RetryAuditChannel(a,b,forbid_repeated_action=True)
    lockout=RetryAuditChannel(a,b,lockout_after_rejection=True)
    terminal=RetryAuditChannel(a,b,stop_after_any_approval=True)
    controls=(normal,no_repeat,lockout,terminal)

    certificates=tuple(certify_retry_control(
        game,2,c,maximum_cumulative_harm=Q(7,50),
        minimum_benign_any_safe_approval=Q(9,10),
        minimum_benign_expected_authorizations=Q(3,2),
    ) for c in controls)
    assert [v.worst_adaptive_harm for v in certificates]==[
        Q(9,50), Q(2,15), Q(19,150), Q(3,25)
    ]
    assert [v.benign_expected_safe_authorizations for v in certificates]==[
        Q(9,5),Q(9,5),Q(171,100),Q(99,100)
    ]
    assert [v.benign_any_safe_approval for v in certificates]==[
        Q(99,100),Q(99,100),Q(9,10),Q(99,100)
    ]
    assert [c.passed for c in certificates]==[False,True,True,False]
    selected=select_retry_control(
        game,2,controls,maximum_cumulative_harm=Q(7,50),
        minimum_benign_any_safe_approval=Q(9,10),
        minimum_benign_expected_authorizations=Q(3,2),
    )
    assert selected==certificates[1]
    assert selected.eligible_safe_actions==2


def test_stricter_risk_ceiling_changes_optimal_retry_control():
    game=one_hot_ugc_disclosure_game(3)
    a,b=Q(1,5),Q(1,10)
    no_repeat=RetryAuditChannel(a,b,forbid_repeated_action=True)
    lockout=RetryAuditChannel(a,b,lockout_after_rejection=True)
    terminal=RetryAuditChannel(a,b,stop_after_any_approval=True)
    best=select_retry_control(
        game,2,(no_repeat,lockout,terminal),
        maximum_cumulative_harm=Q(13,100),
        minimum_benign_any_safe_approval=Q(9,10),
        minimum_benign_expected_authorizations=Q(3,2),
    )
    assert best is not None
    assert best.channel==lockout
    assert best.worst_adaptive_harm==Q(19,150)
    assert best.benign_expected_safe_authorizations==Q(171,100)
    assert select_retry_control(
        game,2,(no_repeat,lockout,terminal),
        maximum_cumulative_harm=Q(1,10),
        minimum_benign_any_safe_approval=Q(9,10),
        minimum_benign_expected_authorizations=Q(3,2),
    ) is None
    assert select_retry_control(
        game,2,(no_repeat,lockout,terminal),
        maximum_cumulative_harm=Q(13,100),
        minimum_benign_any_safe_approval=Q(9,10),
        minimum_benign_expected_authorizations=Q(7,4),
    ) is None


def test_a_perfect_gold_gate_can_satisfy_strict_harm_and_benign_targets():
    game=one_hot_ugc_disclosure_game(3)
    channel=RetryAuditChannel(Q(0),Q(0))
    c=certify_retry_control(
        game,3,channel,
        maximum_cumulative_harm=0,
        minimum_benign_any_safe_approval=1,
        minimum_benign_expected_authorizations=3,
    )
    assert c.passed
    assert c.worst_adaptive_harm==0
    assert c.benign_any_safe_approval==1
    assert c.benign_expected_safe_authorizations==3


def test_control_gate_fails_closed_on_invalid_calibration_and_threshold():
    game=one_hot_ugc_disclosure_game(3)
    channel=RetryAuditChannel(Q(1,5),Q(1,10))
    with pytest.raises(ValueError):
        benign_expected_safe_authorizations(channel,-1)
    with pytest.raises(ValueError):
        benign_expected_safe_authorizations(channel,2,safe_actions=0)
    with pytest.raises(ValueError):
        certify_retry_control(
            game,2,channel,maximum_cumulative_harm=Q(-1,10),
            minimum_benign_any_safe_approval=0,
            minimum_benign_expected_authorizations=0,
        )
    with pytest.raises(ValueError):
        certify_retry_control(
            game,2,channel,maximum_cumulative_harm=Q(1),
            minimum_benign_any_safe_approval=Q(11,10),
            minimum_benign_expected_authorizations=0,
        )
    with pytest.raises(ValueError):
        certify_retry_control(
            game,2,channel,maximum_cumulative_harm=Q(1),
            minimum_benign_any_safe_approval=0,
            minimum_benign_expected_authorizations=-1,
        )
    constraints=dict(
        maximum_cumulative_harm=Q(1),
        minimum_benign_any_safe_approval=Q(0),
        minimum_benign_expected_authorizations=Q(0),
    )
    with pytest.raises(ValueError):
        select_retry_control(game,2,(),**constraints)
    with pytest.raises(ValueError):
        select_retry_control(game,2,(channel,channel),**constraints)
    with pytest.raises(ValueError):
        select_retry_control(
            game,2,(channel,RetryAuditChannel(Q(1,4),Q(1,10))),
            **constraints,
        )
