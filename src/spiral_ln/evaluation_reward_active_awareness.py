"""RHT-21: finite exact Bayesian active evaluator awareness.

The latent world type (evaluation or deployment) is fixed. An agent observes
one exogenous cue then may select bounded-cost probes, receive observations,
and finally choose PROTECT or EXPLOIT. Both conditional observation kernels,
utilities, and the fixed subjective terminal future-policy influence are
externally specified and exact rational. This is a synthetic model.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache

from spiral_ln.evaluation_reward_training_awareness import _distribution, _rational


@dataclass(frozen=True)
class ObservationLaw:
    name: str
    outcomes: tuple[str, ...]
    evaluation: tuple[Q, ...]
    deployment: tuple[Q, ...]

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("observation source needs a nonempty name")
        if (not self.outcomes or any(type(x) is not str or not x for x in self.outcomes)
                or len(set(self.outcomes)) != len(self.outcomes)):
            raise ValueError("observation outcomes must be unique nonempty strings")
        e = _distribution(self.evaluation, "evaluation observation law")
        d = _distribution(self.deployment, "deployment observation law")
        if len(e) != len(self.outcomes) or len(d) != len(self.outcomes):
            raise ValueError("observation distributions must match outcome roster")
        object.__setattr__(self, "evaluation", e)
        object.__setattr__(self, "deployment", d)

    @property
    def total_variation(self) -> Q:
        return sum((abs(x-y) for x,y in zip(self.evaluation,self.deployment)), Q(0)) / 2


START = ObservationLaw("initial", ("start",), (Q(1),), (Q(1),))


@dataclass(frozen=True)
class Probe:
    name: str
    law: ObservationLaw
    cost: Q = Q(0)
    subjective_future_influence: Q = Q(0)

    def __post_init__(self):
        if not isinstance(self.name,str) or not self.name:
            raise ValueError("probe name must be nonempty")
        if not isinstance(self.law, ObservationLaw):
            raise ValueError("probe law must be an ObservationLaw")
        cost = _rational(self.cost,"probe cost")
        change = _rational(self.subjective_future_influence,"probe future influence")
        if cost < 0:
            raise ValueError("probe cost must be nonnegative")
        object.__setattr__(self,"cost",cost)
        object.__setattr__(self,"subjective_future_influence",change)


@dataclass(frozen=True)
class ActiveEvaluationGame:
    prior: Q
    protect_reward: Q
    exploit_gain: Q
    horizon: int
    probes: tuple[Probe, ...]
    initial: ObservationLaw = START
    terminal_future_delta: Q = Q(0)
    max_states: int = 40000

    def __post_init__(self):
        p=_rational(self.prior,"evaluation prior")
        r=_rational(self.protect_reward,"protect reward")
        g=_rational(self.exploit_gain,"exploit gain")
        delta=_rational(self.terminal_future_delta,"terminal future delta")
        if not 0<=p<=1 or r<=0 or g<=0:
            raise ValueError("invalid prior, reward, or gain")
        if type(self.horizon) is not int or not 0<=self.horizon<=12:
            raise ValueError("horizon must be an integer between zero and twelve")
        if type(self.max_states) is not int or self.max_states<=0:
            raise ValueError("max_states must be a positive integer")
        if not isinstance(self.initial,ObservationLaw):
            raise ValueError("initial cue must be an ObservationLaw")
        probes=tuple(self.probes)
        if any(not isinstance(pr,Probe) for pr in probes):
            raise ValueError("each probe must be typed")
        if len(set(pr.name for pr in probes))!=len(probes):
            raise ValueError("probe names must be distinct")
        for name,value in (("prior",p),("protect_reward",r),("exploit_gain",g),
                           ("terminal_future_delta",delta),("probes",probes)):
            object.__setattr__(self,name,value)


@dataclass(frozen=True)
class PolicyNode:
    action: str
    probe_index: int | None = None
    children: tuple["PolicyNode",...] = ()


PROTECT = PolicyNode("protect")
EXPLOIT = PolicyNode("exploit")


@dataclass(frozen=True)
class ActivePolicy:
    initial_branches: tuple[PolicyNode,...]


@dataclass(frozen=True)
class OptimalActivePolicy:
    policy: ActivePolicy
    subjective_value: Q
    states_visited: int


@dataclass(frozen=True)
class TerminalTrace:
    initial_index: int
    history: tuple[tuple[int,int], ...]
    action: str
    evaluation_probability: Q
    deployment_probability: Q
    cumulative_probe_net_cost: Q

    def posterior(self, prior: Q) -> Q | None:
        prior=_rational(prior,"evaluation prior")
        if not 0<=prior<=1:
            raise ValueError("prior must be in [0,1]")
        num=prior*self.evaluation_probability
        den=num+(1-prior)*self.deployment_probability
        return num/den if den else None


@dataclass(frozen=True)
class ActiveTransferCertificate:
    policy_value: Q
    evaluation_protection: Q
    deployment_protection: Q
    realized_gap: Q
    exact_transcript_tv: Q
    transcript_tv_bound: Q
    guaranteed_deployment_protection: Q
    weaker_uniform_guarantee: Q
    likelihood_coverage: Q
    evaluation_expected_probes: Q
    deployment_expected_probes: Q
    transcript_count: int


def optimize_active_policy(game: ActiveEvaluationGame) -> OptimalActivePolicy:
    """Exact Bellman recursion on unnormalized hidden-world belief weights.

    At a zero or negative tie, terminal EXPLOIT wins; a probe must strictly
    improve on the best terminal action and earlier probe index breaks equal
    probe scores. The state cap fails closed before expanding extra states.
    """
    seen=0

    @lru_cache(maxsize=None)
    def solve(remaining: int, e_mass: Q, d_mass: Q):
        nonlocal seen
        seen+=1
        if seen>game.max_states:
            raise ValueError("Bayesian belief-state cap exceeded")
        pval=e_mass*game.protect_reward+(e_mass+d_mass)*game.terminal_future_delta
        xval=d_mass*game.exploit_gain
        if pval>xval:
            val,node=pval,PROTECT
        else:
            val,node=xval,EXPLOIT
        if remaining:
            for i,probe in enumerate(game.probes):
                children=tuple(solve(remaining-1,e_mass*pe,d_mass*pd)
                       for pe,pd in zip(probe.law.evaluation,probe.law.deployment))
                trial=(sum((v for v,_ in children), Q(0))+
                      (e_mass+d_mass)*(probe.subjective_future_influence-probe.cost))
                if trial>val:
                    val,node=trial,PolicyNode("probe",i,tuple(t for _,t in children))
        return val,node

    branches=[]
    objective=Q(0)
    for pe,pd in zip(game.initial.evaluation,game.initial.deployment):
        val,node=solve(game.horizon,game.prior*pe,(1-game.prior)*pd)
        objective+=val
        branches.append(node)
    return OptimalActivePolicy(ActivePolicy(tuple(branches)),objective,seen)


def terminal_traces(game: ActiveEvaluationGame, policy: ActivePolicy) -> tuple[TerminalTrace,...]:
    if not isinstance(policy,ActivePolicy) or len(policy.initial_branches)!=len(game.initial.outcomes):
        raise ValueError("policy must provide one branch per initial cue")
    result=[]

    def walk(node:PolicyNode, initial_i:int, history:tuple, pe:Q,pd:Q,remaining:int,
             cumulative:Q):
        if not isinstance(node,PolicyNode):
            raise ValueError("policy nodes must be typed")
        if node.action in ("protect","exploit"):
            if node.probe_index is not None or node.children:
                raise ValueError("terminal policy node cannot have children")
            result.append(TerminalTrace(initial_i,history,node.action,pe,pd,cumulative))
            return
        if node.action!="probe" or remaining<=0:
            raise ValueError("unregistered action or probe past horizon")
        i=node.probe_index
        if type(i) is not int or not 0<=i<len(game.probes):
            raise ValueError("probe index outside roster")
        probe=game.probes[i]
        if len(node.children)!=len(probe.law.outcomes):
            raise ValueError("policy branch count differs from observation kernel")
        for j,child in enumerate(node.children):
            walk(child,initial_i,history+((i,j),),
                 pe*probe.law.evaluation[j],pd*probe.law.deployment[j],remaining-1,
                 cumulative+probe.cost-probe.subjective_future_influence)

    for k,node in enumerate(policy.initial_branches):
        walk(node,k,(),game.initial.evaluation[k],game.initial.deployment[k],
             game.horizon,Q(0))
    if sum((t.evaluation_probability for t in result),Q(0))!=1 or \
       sum((t.deployment_probability for t in result),Q(0))!=1:
        raise AssertionError("normalized laws must remain normalized under valid policy")
    return tuple(result)


def certify_active_transfer(game:ActiveEvaluationGame, policy:ActivePolicy) -> ActiveTransferCertificate:
    """Exact world-conditional terminal transcript law and sharp transfer TV."""
    traces=terminal_traces(game,policy)
    ev=sum((t.evaluation_probability for t in traces if t.action=="protect"),Q(0))
    de=sum((t.deployment_probability for t in traces if t.action=="protect"),Q(0))
    actual_tv=sum((abs(t.evaluation_probability-t.deployment_probability)
                   for t in traces),Q(0))/2
    per_step_tv=max((p.law.total_variation for p in game.probes),default=Q(0))
    uniform=1-(1-game.initial.total_variation)*(1-per_step_tv)**game.horizon
    if actual_tv>uniform or abs(ev-de)>actual_tv:
        raise AssertionError("adaptive transcript coupling inequality failed")
    margin=Q(0)
    for t in traces:
        mixed=game.prior*t.evaluation_probability+(1-game.prior)*t.deployment_probability
        if t.action=="protect":
            margin+=game.prior*t.evaluation_probability*game.protect_reward
            margin+=mixed*game.terminal_future_delta
        else:
            margin+=(1-game.prior)*t.deployment_probability*game.exploit_gain
        margin-=mixed*t.cumulative_probe_net_cost
    ratio=min((t.evaluation_probability/t.deployment_probability for t in traces
               if t.deployment_probability>0),default=Q(0))
    expected_e=sum((len(t.history)*t.evaluation_probability for t in traces),Q(0))
    expected_d=sum((len(t.history)*t.deployment_probability for t in traces),Q(0))
    return ActiveTransferCertificate(
        margin,ev,de,ev-de,actual_tv,uniform,
        max(Q(0),ev-actual_tv),max(Q(0),ev-uniform),ratio,
        expected_e,expected_d,len(traces),
    )


def sharp_transfer_relabel(game:ActiveEvaluationGame, policy:ActivePolicy) -> ActivePolicy:
    """Keep probe/stopping decisions fixed; choose protection on e>d leaves."""
    traces=terminal_traces(game,policy)
    choices={(t.initial_index,t.history):t.evaluation_probability>t.deployment_probability
             for t in traces}

    def relabel(node:PolicyNode,initial:int,history:tuple) -> PolicyNode:
        if node.action in ("protect","exploit"):
            return PROTECT if choices[(initial,history)] else EXPLOIT
        return PolicyNode("probe",node.probe_index,tuple(
            relabel(child,initial,history+((node.probe_index,j),))
            for j,child in enumerate(node.children)))

    return ActivePolicy(tuple(relabel(node,i,()) for i,node in enumerate(policy.initial_branches)))
