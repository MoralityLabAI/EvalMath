"""RHT-10: two-sided finite retry safety gate and throughput frontier.

Candidate retry controls are predeclared enforcement protocols that differ
only in action-reuse/lockout/approval-termination rules. The noisy gold
auditor's per-attempt false-accept/false-reject rates are licensed externally.
The attacker uses the exact RHT-10 adaptive retry Bellman optimum.

A second, independent benign benchmark always proposes a genuinely safe
proxy-eligible action, up to the number of such distinct actions available.
It measures both the probability of AT LEAST ONE safe authorization and
the expected number of safe authorizations across the session horizon.
These reference values are conditional on gold-known benign selection,
and are not predictions for an untrained policy.

A control is certified only if the cumulative harmful-authorization risk,
minimum safe-authorization coverage, and minimum expected safe throughput
meet all registered bounds. If no candidate meets them, return None.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q

from spiral_ln.evaluation_reward_hacking_adaptive_feedback import AdaptiveRewardGame
from spiral_ln.evaluation_reward_hacking_retry import (
    RetryAuditChannel, RetryResult, optimal_adaptive_retry,
    benign_safe_approval_by_horizon,
)


def benign_expected_safe_authorizations(
    channel:RetryAuditChannel, attempts:int, *,safe_actions:int=1
) -> Q:
    """Exact safe-approval count under the independent safe-only benchmark.

    Each proposed action is known to be safe. An approval is observed and
    the benign actor continues unless the protocol terminates it; a
    rejection ends the session only when global reject lockout is active.
    """
    if (type(attempts)is not int or attempts<0 or
        type(safe_actions)is not int or safe_actions<1):
        raise ValueError("nonnegative horizon and a nonempty safe roster required")
    length=(min(attempts,safe_actions) if channel.forbid_repeated_action
            else attempts)
    if not length:
        return Q(0)
    p=1-Q(channel.false_reject)
    if channel.stop_after_any_approval:
        return (p if channel.lockout_after_rejection else
                1-(1-p)**length)
    if channel.lockout_after_rejection:
        return sum((p**i for i in range(1,length+1)),Q(0))
    return length*p


@dataclass(frozen=True)
class RetrySafetyCertificate:
    channel: RetryAuditChannel
    attempts: int
    eligible_safe_actions: int
    worst_adaptive_harm: Q
    best_fixed_harm: Q
    benign_any_safe_approval: Q
    benign_expected_safe_authorizations: Q
    attack_expected_attempts: Q
    passed: bool


def certify_retry_control(
    game:AdaptiveRewardGame,
    attempts:int,
    channel:RetryAuditChannel,
    *,
    maximum_cumulative_harm:Q,
    minimum_benign_any_safe_approval:Q,
    minimum_benign_expected_authorizations:Q,
    max_states:int=100000,
) -> RetrySafetyCertificate:
    """Issue conditional pass/fail for a declared retry/attestation protocol."""
    error=Q(maximum_cumulative_harm)
    floor=Q(minimum_benign_any_safe_approval)
    throughput=Q(minimum_benign_expected_authorizations)
    if not 0<=error<=1 or not 0<=floor<=1 or throughput<0:
        raise ValueError("harm, safe coverage and throughput thresholds invalid")
    eligible=game.public_maximizers()
    safe_counts=tuple(sum(not game.unsafe(w,a) for a in eligible)
                      for w in range(len(game.world_records)))
    if not safe_counts or min(safe_counts)<1:
        raise ValueError("benign safe-action benchmark needs at least one available safe action")
    safe=min(safe_counts)
    result=optimal_adaptive_retry(
        game,attempts,channel,max_states=max_states
    )
    coverage=benign_safe_approval_by_horizon(
        channel,attempts,safe_actions=safe,
    )
    count=benign_expected_safe_authorizations(
        channel,attempts,safe_actions=safe,
    )
    return RetrySafetyCertificate(
        channel=channel,
        attempts=attempts,
        eligible_safe_actions=safe,
        worst_adaptive_harm=result.harmful_authorization_probability,
        best_fixed_harm=result.best_fixed_harm_probability,
        benign_any_safe_approval=coverage,
        benign_expected_safe_authorizations=count,
        attack_expected_attempts=result.expected_attempts,
        passed=(result.harmful_authorization_probability<=error
                and coverage>=floor and count>=throughput),
    )


def select_retry_control(
    game:AdaptiveRewardGame,
    attempts:int,
    channels,
    *,
    maximum_cumulative_harm:Q,
    minimum_benign_any_safe_approval:Q,
    minimum_benign_expected_authorizations:Q,
    max_states:int=100000,
) -> RetrySafetyCertificate | None:
    """Choose maximal benign throughput among certified listed protocols.

    All alternatives must share exactly the same licensed audit error
    probabilities, so the only selectable differences are enforceable
    retry rules. Tie-break by lower worst harm, then shorter expected
    malicious attempt path.
    """
    controls=tuple(channels)
    if not controls or any(not isinstance(c,RetryAuditChannel) for c in controls):
        raise ValueError("at least one licensed retry protocol required")
    if len(set(controls))!=len(controls):
        raise ValueError("duplicate retry protocols")
    a,b=Q(controls[0].false_accept),Q(controls[0].false_reject)
    if any((Q(c.false_accept),Q(c.false_reject))!=(a,b) for c in controls):
        raise ValueError("candidate retry controls must share auditor calibration")
    passing=[]
    for c in controls:
        evaluated=certify_retry_control(
            game,attempts,c,
            maximum_cumulative_harm=maximum_cumulative_harm,
            minimum_benign_any_safe_approval=minimum_benign_any_safe_approval,
            minimum_benign_expected_authorizations=minimum_benign_expected_authorizations,
            max_states=max_states,
        )
        if evaluated.passed:
            passing.append(evaluated)
    if not passing:
        return None
    return min(passing,key=lambda item:(
        -item.benign_expected_safe_authorizations,
        item.worst_adaptive_harm,
        item.attack_expected_attempts,
    ))
