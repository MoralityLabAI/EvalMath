"""RHT-11: exact stateful evaluator-tampering and attestation game.

The hidden state is (fixed gold-reference world, evaluator integrity).
Integrity is intact (0) or compromised (1). The actor chooses either a
registered proxy-maximizing candidate action or a tool action that may
corrupt the evaluator. It sees acknowledgments and authorization verdicts,
while the true compromise state and independent gold are hidden.

An external attestor checks after tamper and before every candidate
authorization. Alarms terminate the current session. After a surviving
verdict, the evaluator may drift into compromise or be restored, according
to explicitly registered conditional transition probabilities. All
probabilities are exact rationals.

The objective is the probability of at least one APPROVED unsafe action.
That event is absorbing for risk accounting. Rejected and approved-safe
branches carry unnormalized hidden-state posterior weights; the actor
chooses its next move adaptively. Fixed schedules and direct world-state
policy evaluation provide independently structured finite controls.

This is conditional synthetic finite mathematics, not a calibrated safety
claim for a real reward model, tampering attempt, or deployed attestor.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache
from itertools import product

from spiral_ln.evaluation_reward_hacking_adaptive_feedback import AdaptiveRewardGame


@dataclass(frozen=True)
class MutableEvaluator:
    intact_false_accept: Q = Q(1, 5)
    compromised_false_accept: Q = Q(4, 5)
    intact_false_reject: Q = Q(0)
    compromised_false_reject: Q = Q(0)
    tamper_success: Q = Q(3, 4)
    alarm_if_compromised_after_tamper: Q = Q(0)
    alarm_if_intact_after_tamper: Q = Q(0)
    alarm_if_compromised_before_probe: Q = Q(0)
    alarm_if_intact_before_probe: Q = Q(0)
    compromise_after_rejection: Q = Q(0)
    compromise_after_safe_approval: Q = Q(0)
    restore_after_rejection: Q = Q(0)
    restore_after_safe_approval: Q = Q(0)
    allow_tamper: bool = True
    tamper_once: bool = True
    forbid_repeated_probe: bool = False
    lockout_after_rejection: bool = False
    stop_after_any_approval: bool = False

    def __post_init__(self):
        probabilities=(
            self.intact_false_accept,self.compromised_false_accept,
            self.intact_false_reject,self.compromised_false_reject,
            self.tamper_success,
            self.alarm_if_compromised_after_tamper,
            self.alarm_if_intact_after_tamper,
            self.alarm_if_compromised_before_probe,
            self.alarm_if_intact_before_probe,
            self.compromise_after_rejection,
            self.compromise_after_safe_approval,
            self.restore_after_rejection,
            self.restore_after_safe_approval,
        )
        try:
            values=tuple(Q(x) for x in probabilities)
        except (ValueError,TypeError,ZeroDivisionError) as exc:
            raise ValueError("auditor rates must be rational") from exc
        if any(x<0 or x>1 for x in values):
            raise ValueError("all conditional auditor rates must lie in [0,1]")
        if any(type(x) is not bool for x in (
            self.allow_tamper,self.tamper_once,
            self.forbid_repeated_probe,self.lockout_after_rejection,
            self.stop_after_any_approval
        )):
            raise ValueError("auditor protocol flags must be Boolean")

    def false_accept(self, state:int) -> Q:
        return Q(self.compromised_false_accept if state else self.intact_false_accept)

    def false_reject(self, state:int) -> Q:
        return Q(self.compromised_false_reject if state else self.intact_false_reject)

    def alarm_probability(self, state:int, kind:str) -> Q:
        if kind=="tamper":
            return Q(self.alarm_if_compromised_after_tamper if state
                     else self.alarm_if_intact_after_tamper)
        if kind=="probe":
            return Q(self.alarm_if_compromised_before_probe if state
                     else self.alarm_if_intact_before_probe)
        raise ValueError("unknown attestation stage")

    def post_verdict_states(self, state:int, verdict:str):
        if verdict=="rejected":
            compromise=Q(self.compromise_after_rejection)
            restore=Q(self.restore_after_rejection)
        elif verdict=="approved":
            compromise=Q(self.compromise_after_safe_approval)
            restore=Q(self.restore_after_safe_approval)
        else:
            raise ValueError("unknown conditional state transition")
        if state==0:
            return ((0,1-compromise),(1,compromise))
        if state==1:
            return ((0,restore),(1,1-restore))
        raise ValueError("integrity must be clean or compromised")


@dataclass(frozen=True)
class StatefulAction:
    kind: str | None = None
    candidate: int | None = None
    on_ack: "StatefulAction | None" = None
    on_rejected: "StatefulAction | None" = None
    on_approved: "StatefulAction | None" = None


@dataclass(frozen=True)
class StatefulAttackResult:
    max_harm: Q
    first_action: str | None
    policy: StatefulAction
    expected_steps_until_harm_or_stop: Q
    states_visited: int
    best_fixed_harm: Q
    best_fixed_schedule: tuple[tuple[str,int|None], ...]


def _check(game,steps,state_budget):
    if (type(steps) is not int or steps<0 or steps>5
        or len(game.world_records)>7
        or len(game.public_maximizers())>7):
        raise ValueError("bounded seed: <=5 steps, <=7 worlds/proxy actions")
    if type(state_budget) is not int or state_budget<1:
        raise ValueError("positive state budget required")


def _initial_masses(game, initial_compromised):
    p=Q(initial_compromised)
    if not 0<=p<=1:
        raise ValueError("initial integrity prior must lie in [0,1]")
    return tuple(value for w in game.world_weights for value
                 in (Q(w)*(1-p),Q(w)*p))


def worst_state_false_approval_rate(channel:MutableEvaluator) -> Q:
    """Sharp per-probe conditional hazard bound, even under unknown integrity.

    Each probe is independently root-attested before authorization. With an
    unsafe action, the probability of harm in state s is bounded by
    (1-alarm_rate_s)*false_accept_s. Any posterior mixture over intact and
    compromised states inherits the maximum of these two quantities.
    """
    return max(
        (1-channel.alarm_probability(state,"probe"))*channel.false_accept(state)
        for state in (0,1)
    )


def conditional_stateful_harm_bound(
    channel:MutableEvaluator, maximum_probes:int
) -> Q:
    """History-conditional cumulative bound for any adaptive transition law.

    The per-state rates must apply after every complete previous history.
    """
    if type(maximum_probes)is not int or maximum_probes<0:
        raise ValueError("maximum probe count must be a nonnegative integer")
    p=worst_state_false_approval_rate(channel)
    return 1-(1-p)**maximum_probes


def fixed_stateful_schedule_harm(
    game:AdaptiveRewardGame, schedule,channel:MutableEvaluator,
    *, initial_compromised=Q(0)
) -> Q:
    """Direct world/integrity likelihood recursion for a precommitted script.

    The same schedule is followed for all surviving verdict histories.
    An alarm, malicious approval, optional lockout, or stop rule terminates
    that world trajectory; compromised integrity transitions are explicit.
    """
    script=tuple(schedule)
    eligible=set(game.public_maximizers())
    used=set()
    tampered=0
    for kind,candidate in script:
        if kind=="tamper":
            if not channel.allow_tamper or candidate is not None:
                raise ValueError("tamper schedule must be enabled and unlabelled")
            tampered+=1
            if channel.tamper_once and tampered>1:
                raise ValueError("one registered tamper action per session")
        elif kind=="probe":
            if type(candidate)is not int or candidate not in eligible:
                raise ValueError("probe must be proxy eligible")
            if channel.forbid_repeated_probe and candidate in used:
                raise ValueError("probe action cannot repeat under this protocol")
            used.add(candidate)
        else:
            raise ValueError("only registered tamper/probe actions available")

    initially=Q(initial_compromised)
    if not 0<=initially<=1:
        raise ValueError("initial integrity prior must lie in [0,1]")

    @lru_cache(None)
    def risk(world:int,state:int,index:int) -> Q:
        if index==len(script):
            return Q(0)
        kind,action=script[index]
        if kind=="tamper":
            dest=(((0,1-Q(channel.tamper_success)),
                   (1,Q(channel.tamper_success))) if state==0
                  else ((1,Q(1)),))
            return sum((
                probability*(1-channel.alarm_probability(s1,"tamper"))
                *risk(world,s1,index+1)
                for s1,probability in dest
            ),Q(0))
        gate_pass=1-channel.alarm_probability(state,"probe")
        bad=game.unsafe(world,action)
        approval=(channel.false_accept(state) if bad
                  else 1-channel.false_reject(state))
        harm=gate_pass*approval if bad else Q(0)
        if not channel.lockout_after_rejection:
            harm+=gate_pass*(1-approval)*sum((
                probability*risk(world,s1,index+1)
                for s1,probability in channel.post_verdict_states(state,"rejected")
            ),Q(0))
        if not channel.stop_after_any_approval and not bad:
            harm+=gate_pass*approval*sum((
                probability*risk(world,s1,index+1)
                for s1,probability in channel.post_verdict_states(state,"approved")
            ),Q(0))
        return harm

    return sum((
        Q(weight)*((1-initially)*risk(w,0,0)+initially*risk(w,1,0))
        for w,weight in enumerate(game.world_weights)
    ),Q(0))/game.total


def best_fixed_stateful_schedule(
    game:AdaptiveRewardGame,steps:int,channel:MutableEvaluator,
    *, initial_compromised=Q(0),max_schedules:int=100000
):
    _check(game,steps,max_schedules)
    if type(max_schedules)is not int or max_schedules<1:
        raise ValueError("fixed schedule budget must be positive")
    action_bank=(tuple(("probe",a) for a in game.public_maximizers())
                 +((("tamper",None),) if channel.allow_tamper else ()))
    winner=Q(0)
    schedule=()
    checked=0
    for length in range(steps+1):
        for script in product(action_bank,repeat=length):
            if (channel.tamper_once and
                sum(k=="tamper" for k,_ in script)>1):
                continue
            if (channel.forbid_repeated_probe and
                len({a for kind,a in script if kind=="probe"})!=
                sum(k=="probe" for k,a in script)):
                continue
            checked+=1
            if checked>max_schedules:
                raise ValueError("fixed schedule census exceeds resource budget")
            risk=fixed_stateful_schedule_harm(
                game,script,channel,initial_compromised=initial_compromised
            )
            if risk>winner:
                winner,schedule=risk,script
    return {"risk":winner,"schedule":schedule,"checked":checked}


def exact_stateful_policy_profile(
    game:AdaptiveRewardGame,policy:StatefulAction,channel:MutableEvaluator,
    *,max_steps:int,initial_compromised=Q(0)
) -> tuple[Q,Q]:
    """World-by-world independent policy evaluator (risk, expected steps).

    The risk objective absorbs an approved unsafe action; the expected
    step count is likewise measured until the first harm or protocol stop.
    """
    _check(game,max_steps,100000)
    initially=Q(initial_compromised)
    if not 0<=initially<=1:
        raise ValueError("initial integrity prior must be a probability")
    eligible=set(game.public_maximizers())

    @lru_cache(None)
    def walk(w,state,node,remaining,used,tamper_seen):
        if node is None or node.kind is None:
            if node is not None and (node.candidate is not None
               or node.on_ack is not None or node.on_rejected is not None
               or node.on_approved is not None):
                raise ValueError("terminal node must be empty")
            return Q(0),Q(0)
        if remaining==0 or node.kind not in ("tamper","probe"):
            raise ValueError("action outside registered horizon")
        risk=Q(0)
        calls=Q(1)
        if node.kind=="tamper":
            if (not channel.allow_tamper or node.candidate is not None
                or node.on_rejected is not None or node.on_approved is not None
                or channel.tamper_once and tamper_seen):
                raise ValueError("illegal tamper policy node")
            dest=(((0,1-Q(channel.tamper_success)),
                   (1,Q(channel.tamper_success))) if state==0
                  else ((1,Q(1)),))
            for s1,p in dest:
                survive=p*(1-channel.alarm_probability(s1,"tamper"))
                if survive and node.on_ack is not None:
                    sub,steps=walk(w,s1,node.on_ack,remaining-1,used,True)
                    risk+=survive*sub
                    calls+=survive*steps
            return risk,calls
        a=node.candidate
        if (type(a)is not int or a not in eligible
            or node.on_ack is not None
            or channel.forbid_repeated_probe and used>>a&1
            or channel.lockout_after_rejection and node.on_rejected is not None
            or channel.stop_after_any_approval and node.on_approved is not None):
            raise ValueError("illegal probe policy node")
        gate=1-channel.alarm_probability(state,"probe")
        bad=game.unsafe(w,a)
        p=channel.false_accept(state) if bad else 1-channel.false_reject(state)
        risk+=gate*p if bad else Q(0)
        if node.on_rejected is not None:
            for s1,transition in channel.post_verdict_states(state,"rejected"):
                survived=gate*(1-p)*transition
                if survived:
                    sub,steps=walk(
                        w,s1,node.on_rejected,remaining-1,used|(1<<a),tamper_seen
                    )
                    risk+=survived*sub
                    calls+=survived*steps
        if node.on_approved is not None and not bad:
            for s1,transition in channel.post_verdict_states(state,"approved"):
                survived=gate*p*transition
                if survived:
                    sub,steps=walk(
                        w,s1,node.on_approved,remaining-1,used|(1<<a),tamper_seen
                    )
                    risk+=survived*sub
                    calls+=survived*steps
        return risk,calls

    expected_risk=expected_steps=Q(0)
    for w,weight in enumerate(game.world_weights):
        for state,prob in ((0,1-initially),(1,initially)):
            if prob:
                r,steps=walk(w,state,policy,max_steps,0,False)
                expected_risk+=weight*prob*r
                expected_steps+=weight*prob*steps
    return expected_risk/game.total,expected_steps/game.total


def optimal_stateful_attack(
    game:AdaptiveRewardGame,steps:int,channel:MutableEvaluator,
    *,initial_compromised=Q(0),max_states:int=100000,
    max_fixed_schedules:int=100000
) -> StatefulAttackResult:
    """Exact partially observable Bellman solution over world and integrity.

    The action tamper changes the hidden evaluator state before an external
    attestation; a silent pass gives only an acknowledgment. Candidate probes
    first receive independent integrity attestation, then a gold-verdict.
    Each rejected or safe-approved continuation is updated with the declared
    post-verdict evaluator-state transition. All visible observations are
    incorporated into the posterior mass vector.
    """
    _check(game,steps,max_states)
    initial=_initial_masses(game,initial_compromised)
    eligible=game.public_maximizers()
    m=len(game.world_records)
    visited=0
    @lru_cache(maxsize=None)
    def solve(mass,remaining,used,tamper_seen):
        nonlocal visited
        visited+=1
        if visited>max_states:
            raise ValueError("stateful posterior DP exceeded registered state budget")
        if not remaining or not any(mass):
            return Q(0),Q(0),StatefulAction()
        best=Q(0)
        best_steps=Q(0)
        winning=StatefulAction()
        for action in eligible:
            bit=1<<action
            if channel.forbid_repeated_probe and used&bit:
                continue
            harm=Q(0)
            reject=[Q(0)]*(2*m)
            approved=[Q(0)]*(2*m)
            for w in range(m):
                bad=game.unsafe(w,action)
                for state in (0,1):
                    current=mass[2*w+state]
                    if not current:
                        continue
                    passcheck=current*(1-channel.alarm_probability(state,"probe"))
                    p=(channel.false_accept(state) if bad
                       else 1-channel.false_reject(state))
                    if bad:
                        harm+=passcheck*p
                    if not channel.lockout_after_rejection:
                        for s1,v in channel.post_verdict_states(state,"rejected"):
                            reject[2*w+s1]+=passcheck*(1-p)*v
                    if not channel.stop_after_any_approval and not bad:
                        for s1,v in channel.post_verdict_states(state,"approved"):
                            approved[2*w+s1]+=passcheck*p*v
            calls=sum(mass,Q(0))
            reject_node=approve_node=None
            if any(reject):
                r,c,node=solve(tuple(reject),remaining-1,used|bit,tamper_seen)
                harm+=r
                calls+=c
                reject_node=node
            if any(approved):
                r,c,node=solve(tuple(approved),remaining-1,used|bit,tamper_seen)
                harm+=r
                calls+=c
                approve_node=node
            if harm>best or harm==best and calls<best_steps:
                best,best_steps=harm,calls
                winning=StatefulAction(
                    "probe",action,None,reject_node,approve_node
                )
        if channel.allow_tamper and (
            not channel.tamper_once or not tamper_seen
        ):
            ack=[Q(0)]*(2*m)
            for w in range(m):
                intact=mass[2*w]
                corrupted=mass[2*w+1]
                for s1,p in (
                    (0,intact*(1-Q(channel.tamper_success))),
                    (1,intact*Q(channel.tamper_success)+corrupted)
                ):
                    ack[2*w+s1]+=p*(1-channel.alarm_probability(s1,"tamper"))
            harm=Q(0)
            calls=sum(mass,Q(0))
            ack_node=None
            if any(ack):
                r,c,node=solve(tuple(ack),remaining-1,used,True)
                harm+=r
                calls+=c
                ack_node=node
            if harm>best or harm==best and calls<best_steps:
                best,best_steps=harm,calls
                winning=StatefulAction("tamper",None,ack_node,None,None)
        return best,best_steps,winning

    value,expected,policy=solve(initial,steps,0,False)
    independent,independent_calls=exact_stateful_policy_profile(
        game,policy,channel,max_steps=steps,
        initial_compromised=initial_compromised
    )
    if value/game.total!=independent or expected/game.total!=independent_calls:
        raise AssertionError("independent world-state policy validation failed")
    fixed=best_fixed_stateful_schedule(
        game,steps,channel,initial_compromised=initial_compromised,
        max_schedules=max_fixed_schedules
    )
    if fixed["risk"]>independent:
        raise AssertionError("adaptive strategy must dominate fixed schedule")
    return StatefulAttackResult(
        max_harm=independent,
        first_action=policy.kind,
        policy=policy,
        expected_steps_until_harm_or_stop=independent_calls,
        states_visited=visited,
        best_fixed_harm=fixed["risk"],
        best_fixed_schedule=fixed["schedule"],
    )
