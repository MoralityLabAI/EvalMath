"""RHT-11: conditional stateful attestation safety and benign throughput gate.

A mutable evaluator can be compromised by an explicit tool action or by
post-verdict drift. Independent pre-authorization attestation may terminate
the session before the compromised evaluator approves an unsafe action.

The exact attacker risk comes from RHT-11's partially observed Bellman
engine. A separate BENIGN reference assumes an externally verified safe
action is always available and measures the probability of one safe
authorization and the expected number of safe authorizations until stop.

Candidates for detector selection must share the same evaluator noise,
tamper capability, drift and restoration probabilities. Only the four
externally licensed detection/false-alarm rates may differ. A robust
certificate may require both the exact Bayesian harmful risk to be small
and the per-history hazard bound to satisfy a tighter threshold.

All results are conditional on stationary, independently justified rates
and enforceable attestation/alarm semantics, not a deployed guarantee.
"""
from __future__ import annotations

from dataclasses import dataclass, fields
from fractions import Fraction as Q
from functools import lru_cache

from spiral_ln.evaluation_reward_hacking_adaptive_feedback import AdaptiveRewardGame
from spiral_ln.evaluation_reward_hacking_stateful import (
    MutableEvaluator, conditional_stateful_harm_bound,
    optimal_stateful_attack, worst_state_false_approval_rate,
)


@dataclass(frozen=True)
class BenignStatefulProfile:
    at_least_one_safe_authorization: Q
    expected_safe_authorizations: Q
    expected_probe_calls: Q


def benign_stateful_profile(
    channel:MutableEvaluator,steps:int,
    *,initial_compromised=Q(0),safe_actions:int=1
) -> BenignStatefulProfile:
    """Exact safe-only world-independent benign reference process.

    The benign reference knows each chosen action is gold-safe and never
    calls the tamper tool. Before every candidate call, the externally
    owned integrity attestor can alarm and stop the session. Rejections
    and approved-safe actions may change integrity state as registered.
    If no repeats are licensed, only 'safe_actions' distinct proposals
    exist for this reference actor.
    """
    if (type(steps)is not int or steps<0 or steps>12 or
        type(safe_actions)is not int or safe_actions<1):
        raise ValueError("safe reference: 0..12 calls, positive safe roster")
    initial=Q(initial_compromised)
    if not 0<=initial<=1:
        raise ValueError("initial compromise prior outside [0,1]")
    effective=(min(steps,safe_actions) if channel.forbid_repeated_probe
               else steps)

    @lru_cache(None)
    def f(state:int,remaining:int):
        if remaining==0:
            return Q(0),Q(0),Q(0)
        gate=1-channel.alarm_probability(state,"probe")
        approve=1-channel.false_reject(state)
        no=Q(0),Q(0),Q(0)
        rej=no
        if not channel.lockout_after_rejection:
            rej=tuple(sum((
                p*f(s1,remaining-1)[k]
                for s1,p in channel.post_verdict_states(state,"rejected")
            ),Q(0)) for k in range(3))
        approved=no
        if not channel.stop_after_any_approval:
            approved=tuple(sum((
                p*f(s1,remaining-1)[k]
                for s1,p in channel.post_verdict_states(state,"approved")
            ),Q(0)) for k in range(3))
        any_safe=gate*(approve+(1-approve)*rej[0])
        expected=gate*(approve*(1+approved[1])+(1-approve)*rej[1])
        calls=1+gate*(approve*approved[2]+(1-approve)*rej[2])
        return any_safe,expected,calls

    initial_clean=f(0,effective)
    initial_bad=f(1,effective)
    return BenignStatefulProfile(*(
        (1-initial)*initial_clean[k]+initial*initial_bad[k] for k in range(3)
    ))


def required_preprobe_detection_for_baseline_hazard(
    channel:MutableEvaluator
) -> Q:
    """Sufficient compromised-state detection for raw intact false-accept cap.

    With alpha1>alpha0, d>=1-alpha0/alpha1 ensures
    (1-d)*alpha1<=alpha0. If alpha1<=alpha0 no additional detection
    is mathematically required for this particular per-probe hazard cap.
    """
    alpha0=Q(channel.intact_false_accept)
    alpha1=Q(channel.compromised_false_accept)
    if alpha1==0 or alpha1<=alpha0:
        return Q(0)
    return 1-alpha0/alpha1


@dataclass(frozen=True)
class StatefulAttestationCertificate:
    channel: MutableEvaluator
    calls:int
    attack_harm:Q
    best_fixed_harm:Q
    worst_history_probe_hazard:Q
    conservative_cumulative_harm_bound:Q
    benign_safe_authorization:Q
    benign_expected_safe_authorizations:Q
    benign_expected_probe_calls:Q
    attack_expected_calls:Q
    passed:bool


def certify_stateful_attestation(
    game:AdaptiveRewardGame,steps:int,channel:MutableEvaluator,
    *,maximum_cumulative_harm,
    minimum_benign_safe_authorization,
    minimum_benign_expected_safe_authorizations,
    maximum_history_conditional_hazard=Q(1),
    initial_compromised=Q(0),
    max_states:int=100000
) -> StatefulAttestationCertificate:
    """Two-sided pass/fail for an externally licensed evaluator/attestor."""
    limit,coverage,throughput,hazard_limit=(
        Q(maximum_cumulative_harm),
        Q(minimum_benign_safe_authorization),
        Q(minimum_benign_expected_safe_authorizations),
        Q(maximum_history_conditional_hazard),
    )
    if (not 0<=limit<=1 or not 0<=coverage<=1
        or throughput<0 or not 0<=hazard_limit<=1):
        raise ValueError("harm and non-inert coverage targets invalid")
    eligible=game.public_maximizers()
    safe_counts=tuple(sum(not game.unsafe(w,a) for a in eligible)
                      for w in range(len(game.world_records)))
    if not safe_counts or min(safe_counts)<1:
        raise ValueError("each reference world must admit a safe proxy action")
    attacker=optimal_stateful_attack(
        game,steps,channel,initial_compromised=initial_compromised,
        max_states=max_states,
    )
    benign=benign_stateful_profile(
        channel,steps,initial_compromised=initial_compromised,
        safe_actions=min(safe_counts),
    )
    hazard=worst_state_false_approval_rate(channel)
    conservative=conditional_stateful_harm_bound(channel,steps)
    return StatefulAttestationCertificate(
        channel=channel,calls=steps,
        attack_harm=attacker.max_harm,
        best_fixed_harm=attacker.best_fixed_harm,
        worst_history_probe_hazard=hazard,
        conservative_cumulative_harm_bound=conservative,
        benign_safe_authorization=benign.at_least_one_safe_authorization,
        benign_expected_safe_authorizations=benign.expected_safe_authorizations,
        benign_expected_probe_calls=benign.expected_probe_calls,
        attack_expected_calls=attacker.expected_steps_until_harm_or_stop,
        passed=(attacker.max_harm<=limit
                and hazard<=hazard_limit
                and benign.at_least_one_safe_authorization>=coverage
                and benign.expected_safe_authorizations>=throughput),
    )


_VARIABLE_ATTESTATION_FIELDS=frozenset({
    "alarm_if_compromised_after_tamper",
    "alarm_if_intact_after_tamper",
    "alarm_if_compromised_before_probe",
    "alarm_if_intact_before_probe",
})


def choose_stateful_attestor(
    game:AdaptiveRewardGame,steps:int,candidates,
    *,
    maximum_cumulative_harm,
    minimum_benign_safe_authorization,
    minimum_benign_expected_safe_authorizations,
    maximum_history_conditional_hazard=Q(1),
    initial_compromised=Q(0),
    max_states:int=100000
) -> StatefulAttestationCertificate | None:
    """Select maximum benign throughput among qualifying licensed attestors.

    Detector variants may change only their independently registered
    detection and false-alarm rates. They must share verifier accuracy,
    mutable state transitions, corruption capability and retry protocol.
    """
    channels=tuple(candidates)
    if (not channels or any(not isinstance(c,MutableEvaluator) for c in channels)
        or len(channels)!=len(set(channels))):
        raise ValueError("nonempty distinct candidate attestors required")
    base=tuple(getattr(channels[0],f.name)
               for f in fields(MutableEvaluator)
               if f.name not in _VARIABLE_ATTESTATION_FIELDS)
    for channel in channels[1:]:
        key=tuple(getattr(channel,f.name)
                  for f in fields(MutableEvaluator)
                  if f.name not in _VARIABLE_ATTESTATION_FIELDS)
        if key!=base:
            raise ValueError("candidate attestors must share evaluator dynamics")
    eligible=[]
    for channel in channels:
        cert=certify_stateful_attestation(
            game,steps,channel,
            maximum_cumulative_harm=maximum_cumulative_harm,
            minimum_benign_safe_authorization=minimum_benign_safe_authorization,
            minimum_benign_expected_safe_authorizations=minimum_benign_expected_safe_authorizations,
            maximum_history_conditional_hazard=maximum_history_conditional_hazard,
            initial_compromised=initial_compromised,
            max_states=max_states,
        )
        if cert.passed:
            eligible.append(cert)
    if not eligible:
        return None
    return min(eligible,key=lambda cert:(
        -cert.benign_expected_safe_authorizations,
        cert.attack_harm,
        cert.benign_expected_probe_calls,
    ))
