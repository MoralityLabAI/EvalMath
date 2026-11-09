"""RHT-10: exact adaptive retry attacks on imperfect reward-audit vetoes.

An actor selects only publicly proxy-maximizing actions from the frozen
RHT-08/09 UGC game. The protected world stays fixed across attempts. For
an unsafe action the external auditor authorizes with false-accept rate alpha;
for a safe action it authorizes with probability 1-beta, where beta is the
false-rejection rate. Rates hold conditional on the entire history and world;
fresh readout noise realizes their independent stationary special case.

Actor-visible verdicts are approval/rejection bits. An unsafe approval is
the harmful event and terminates the risk calculation. After rejection or
safe approval the actor may retry, subject to action-reuse and lockout rules.
The agent does not see gold or whether an approval was unsafe.

All probabilities and policies are exact rational quantities; the
Bellman engine maximizes cumulative harmful-authorization probability.
Fixed schedules use a separate direct world-likelihood evaluator.
General conditional and merely marginal false-accept upper bounds are
registered separately. This establishes no real-system audit reliability.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache
from itertools import product, permutations
from math import prod

from spiral_ln.evaluation_reward_hacking_adaptive_feedback import AdaptiveRewardGame


@dataclass(frozen=True)
class RetryAuditChannel:
    false_accept: Q = Q(1, 5)
    false_reject: Q = Q(0)
    forbid_repeated_action: bool = False
    lockout_after_rejection: bool = False
    stop_after_any_approval: bool = False

    def __post_init__(self):
        try:
            alpha,beta=Q(self.false_accept),Q(self.false_reject)
        except (ValueError,TypeError,ZeroDivisionError) as exc:
            raise ValueError("rational audit probabilities required") from exc
        if not 0<=alpha<=1 or not 0<=beta<=1:
            raise ValueError("audit error rates must be probabilities")
        if any(type(value) is not bool for value in (
            self.forbid_repeated_action,self.lockout_after_rejection,
            self.stop_after_any_approval
        )):
            raise ValueError("retry protocol flags must be Boolean")

    def approval_probability(self, unsafe: bool) -> Q:
        return Q(self.false_accept) if unsafe else 1-Q(self.false_reject)


@dataclass(frozen=True)
class RetryPolicy:
    """Public-verdict continuation; None is early stop."""
    action: int | None = None
    on_rejected: "RetryPolicy | None" = None
    on_approved: "RetryPolicy | None" = None


@dataclass(frozen=True)
class RetryResult:
    harmful_authorization_probability: Q
    first_action: int | None
    policy: RetryPolicy
    expected_attempts: Q
    states_visited: int
    best_fixed_harm_probability: Q
    best_fixed_schedule: tuple[int,...]


def _check_budget(game: AdaptiveRewardGame, attempts: int, max_states: int) -> None:
    if (type(attempts) is not int or not 0<=attempts<=6
        or len(game.world_records)>8 or len(game.public_maximizers())>8):
        raise ValueError("finite seed: <=6 attempts, <=8 worlds/eligible actions")
    if type(max_states)is not int or max_states<1:
        raise ValueError("registered state budget must be positive")


def conditional_harm_bound(caps) -> Q:
    """Tight any-harm bound if per-attempt hazard caps are history-conditional."""
    eps=tuple(Q(v) for v in caps)
    if any(not 0<=v<=1 for v in eps):
        raise ValueError("history-conditional caps must be in [0,1]")
    return 1-prod((1-v for v in eps),start=Q(1))


def marginal_harm_bound(caps) -> Q:
    """Tight union bound under merely unconditional per-attempt marginals."""
    eps=tuple(Q(v) for v in caps)
    if any(not 0<=v<=1 for v in eps):
        raise ValueError("marginal caps must be in [0,1]")
    return min(Q(1),sum(eps,Q(0)))


def disjoint_marginal_failure_law(caps) -> tuple[Q,...]:
    """A one-time latent failure slot realizing the marginal-only bound.

    Result has one mass for each attempt's sole false approval, followed
    by the mass for no false approval. This joint distribution need not
    obey the cap after conditioning on previous failed attempts.
    """
    eps=tuple(Q(v) for v in caps)
    if any(not 0<=v<=1 for v in eps):
        raise ValueError("marginal caps must be in [0,1]")
    left=Q(1)
    masses=[]
    for v in eps:
        assigned=min(v,left)
        masses.append(assigned)
        left-=assigned
    return tuple(masses)+(left,)


def fixed_schedule_harm(
    game: AdaptiveRewardGame,
    actions,
    channel: RetryAuditChannel,
) -> Q:
    """Independent direct per-world risk of a predetermined action sequence.

    Verdicts still trigger protocol-mandated termination, but never change
    the next scheduled action.
    """
    schedule=tuple(actions)
    eligible=set(game.public_maximizers())
    if (any(type(a)is not int or a not in eligible for a in schedule)
        or channel.forbid_repeated_action and len(set(schedule))!=len(schedule)):
        raise ValueError("schedule must use registered eligible actions")
    total=Q(0)
    alpha=Q(channel.false_accept)
    beta=Q(channel.false_reject)
    for w,weight in enumerate(game.world_weights):
        @lru_cache(None)
        def risk(index):
            if index==len(schedule):
                return Q(0)
            bad=game.unsafe(w,schedule[index])
            p=alpha if bad else 1-beta
            now=p if bad else Q(0)
            reject=Q(0) if channel.lockout_after_rejection else (1-p)*risk(index+1)
            approved=Q(0) if channel.stop_after_any_approval or bad else p*risk(index+1)
            return now+reject+approved
        total+=weight*risk(0)
    return total/game.total


def best_fixed_schedule(
    game:AdaptiveRewardGame,
    attempts:int,
    channel:RetryAuditChannel,
    *,
    max_schedules:int=100000,
):
    """Exact full census of precommitted schedules, including early stopping."""
    _check_budget(game,attempts,1)
    if type(max_schedules)is not int or max_schedules<1:
        raise ValueError("fixed schedule budget must be positive")
    eligible=game.public_maximizers()
    best=Q(0)
    winning=()
    checked=0
    maximum=min(attempts,len(eligible)) if channel.forbid_repeated_action else attempts
    for length in range(maximum+1):
        schedules=(permutations(eligible,length) if channel.forbid_repeated_action
                   else product(eligible,repeat=length))
        for schedule in schedules:
            checked+=1
            if checked>max_schedules:
                raise ValueError("fixed schedule census exceeded registered budget")
            value=fixed_schedule_harm(game,schedule,channel)
            if value>best:
                best,winning=value,tuple(schedule)
    return {"risk":best,"schedule":winning,"schedules_checked":checked}


def exact_policy_profile(
    game:AdaptiveRewardGame,
    policy:RetryPolicy,
    channel:RetryAuditChannel,
    *,
    max_depth:int=6,
) -> tuple[Q,Q]:
    """Independently sum harm probability and attempts over actual worlds."""
    if type(max_depth)is not int or max_depth<0:
        raise ValueError("nonnegative registered policy depth required")
    eligible=set(game.public_maximizers())
    def world_profile(w,node,depth,used):
        if node is None or node.action is None:
            if node is not None and (node.on_rejected is not None
                                     or node.on_approved is not None):
                raise ValueError("terminal retry policy cannot contain continuations")
            return Q(0),Q(0)
        if depth==0 or node.action not in eligible:
            raise ValueError("retry policy action invalid or exceeds depth")
        bit=1<<node.action
        if channel.forbid_repeated_action and used&bit:
            raise ValueError("retry policy repeats a forbidden action")
        used|=bit
        bad=game.unsafe(w,node.action)
        p=channel.approval_probability(bad)
        harm=p if bad else Q(0)
        expected=Q(1)
        if node.on_rejected is not None:
            if channel.lockout_after_rejection:
                raise ValueError("post-rejection continuation violates lockout")
            r,steps=world_profile(w,node.on_rejected,depth-1,used)
            harm+=(1-p)*r
            expected+=(1-p)*steps
        if node.on_approved is not None:
            if channel.stop_after_any_approval:
                raise ValueError("post-approval continuation violates protocol")
            r,steps=world_profile(w,node.on_approved,depth-1,used)
            if not bad:
                harm+=p*r
                expected+=p*steps
            # A bad approval has already reached the harmful event. A
            # continuation may exist in the public tree but its extra risk
            # and effort are irrelevant after that absorbing event.
        return harm,expected
    aggregate_harm=aggregate_attempts=Q(0)
    for w,weight in enumerate(game.world_weights):
        p,calls=world_profile(w,policy,max_depth,0)
        aggregate_harm+=weight*p
        aggregate_attempts+=weight*calls
    return aggregate_harm/game.total,aggregate_attempts/game.total


def optimal_adaptive_retry(
    game:AdaptiveRewardGame,
    attempts:int,
    channel:RetryAuditChannel,
    *,
    max_states:int=100000,
    max_fixed_schedules:int=100000,
) -> RetryResult:
    """Exact Bayes-optimal malicious retry policy with public verdict access.

    V(w,r,U)=max_a [
       sum_i w_i*1_bad(i,a)*alpha
       + V((w_i*(1-p_approve(i,a)))_i,r-1,U+a) if rejections permit
       + V((w_i*p_approve(i,a)*1_safe(i,a))_i,r-1,U+a) if approvals permit
    ].
    All weights are unnormalized. A rejected or safe-approved continuation
    observes only its verdict and the prior chosen action. A bad approval
    is an absorbing harmful event.
    """
    _check_budget(game,attempts,max_states)
    actions=game.public_maximizers()
    alpha=Q(channel.false_accept)
    beta=Q(channel.false_reject)
    visited=0
    @lru_cache(None)
    def solve(weights:tuple[Q,...],remaining:int,used:int):
        nonlocal visited
        visited+=1
        if visited>max_states:
            raise ValueError("adaptive retry DP exceeded state budget")
        if not remaining or not any(weights):
            return Q(0),RetryPolicy()
        best=Q(0)
        best_policy=RetryPolicy()
        for action in actions:
            bit=1<<action
            if channel.forbid_repeated_action and used&bit:
                continue
            bad=tuple(game.unsafe(w,action) for w in range(len(weights)))
            now=sum((weights[w]*alpha for w in range(len(weights)) if bad[w]),Q(0))
            rej=tuple(weights[w]*(1-(alpha if bad[w] else 1-beta))
                      for w in range(len(weights)))
            safe_ok=tuple(Q(0) if bad[w] else weights[w]*(1-beta)
                          for w in range(len(weights)))
            next_used=used|bit
            rej_policy=approved_policy=None
            if not channel.lockout_after_rejection and any(rej):
                score,recurse=solve(rej,remaining-1,next_used)
                now+=score
                rej_policy=recurse
            if not channel.stop_after_any_approval and any(safe_ok):
                score,recurse=solve(safe_ok,remaining-1,next_used)
                now+=score
                approved_policy=recurse
            if now>best:
                best=now
                best_policy=RetryPolicy(action,rej_policy,approved_policy)
        return best,best_policy

    mass,policy=solve(tuple(Q(w) for w in game.world_weights),attempts,0)
    direct,expected=exact_policy_profile(game,policy,channel,max_depth=attempts)
    if direct!=mass/game.total:
        raise AssertionError("independent world-based policy evaluator disagrees")
    fixed=best_fixed_schedule(
        game,attempts,channel,max_schedules=max_fixed_schedules
    )
    if fixed["risk"]>direct:
        raise AssertionError("adaptive policy should dominate precommitted schedules")
    return RetryResult(
        harmful_authorization_probability=direct,
        first_action=policy.action,
        policy=policy,
        expected_attempts=expected,
        states_visited=visited,
        best_fixed_harm_probability=fixed["risk"],
        best_fixed_schedule=fixed["schedule"],
    )


def benign_safe_approval_by_horizon(
    channel:RetryAuditChannel,attempts:int,*,safe_actions:int=1
) -> Q:
    """Conditional benchmark: a benign actor always proposes safe actions.

    Measures probability of at least one authorized safe attempt.
    The actor can retry after rejections unless global lockout, and has
    'safe_actions' available distinct choices if repeats are prohibited.
    """
    if (type(attempts)is not int or attempts<0 or
        type(safe_actions)is not int or safe_actions<1):
        raise ValueError("valid horizon and nonempty safe-action bank required")
    if attempts==0:
        return Q(0)
    effective=min(attempts,safe_actions) if channel.forbid_repeated_action else attempts
    if channel.lockout_after_rejection:
        effective=min(effective,1)
    return 1-Q(channel.false_reject)**effective
