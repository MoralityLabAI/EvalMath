"""RHT-25: sealed private attestation of publicly aliased evaluator integrity.

A fixed public actor policy runs against either of two four-state RHT-24
evaluator models. The public transcript laws are required to agree in *both*
evaluation and deployment. After the actor stops, a sealed auditor obtains n
conditionally independent binary reports of the SAME terminal integrity bit.

This persistent-hidden-state experiment has a mixture-of-binomial law.
Treating integrity as independently redrawn between audit reports would
produce a different experiment and an unsound discrimination certificate.
All quantities are exact rationals. No real auditor or trained model is run.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from math import comb

from spiral_ln.evaluation_reward_training_awareness import _rational
from spiral_ln.evaluation_reward_stateful_awareness import (
    StatefulAwarenessGame, PolicyNode, terminal_traces, visible_trace_distance,
)


def _report_count(n: int) -> int:
    if type(n) is not int or not 0 <= n <= 64:
        raise ValueError("report count must be an integer between 0 and 64")
    return n


@dataclass(frozen=True)
class SealedAttestor:
    """P(+|intact)=false_positive and P(+|compromised)=sensitivity."""
    false_positive: Q
    sensitivity: Q

    def __post_init__(self):
        f = _rational(self.false_positive, "attestor false positive")
        t = _rational(self.sensitivity, "attestor sensitivity")
        if not 0 <= f <= 1 or not 0 <= t <= 1:
            raise ValueError("attestor rates must lie in [0,1]")
        object.__setattr__(self, "false_positive", f)
        object.__setattr__(self, "sensitivity", t)

    def count_law(self, reports: int, compromised: bool) -> tuple[Q, ...]:
        """Binomial count law given one fixed hidden integrity state."""
        n = _report_count(reports)
        if type(compromised) is not bool:
            raise ValueError("compromised flag must be Boolean")
        rate = self.sensitivity if compromised else self.false_positive
        return tuple(Q(comb(n,k))*rate**k*(1-rate)**(n-k)
                     for k in range(n+1))

    def count_total_variation(self, reports: int) -> Q:
        intact = self.count_law(reports, False)
        bad = self.count_law(reports, True)
        return sum((abs(x-y) for x,y in zip(intact,bad)), Q(0))/2


@dataclass(frozen=True)
class AttestationCertificate:
    world: str
    reports: int
    public_transcripts: int
    public_tv: Q
    hidden_integrity_separation: Q
    report_channel_tv: Q
    observed_joint_tv: Q
    equal_prior_model_error: Q
    limiting_error: Q
    compromised_exploit_difference: Q
    model_a_false_alarm: Q
    model_b_miss_probability: Q


@dataclass(frozen=True)
class AttestationBudget:
    target_error: Q
    max_reports: int
    minimum_reports: int | None
    limiting_error: Q
    error_frontier: tuple[Q,...]


def _trace_pair(game_a: StatefulAwarenessGame,
                game_b: StatefulAwarenessGame,
                policy: PolicyNode):
    if not isinstance(game_a, StatefulAwarenessGame) or not isinstance(game_b, StatefulAwarenessGame):
        raise ValueError("both evaluators must use the RHT-24 typed game")
    if (len(game_a.probes) != len(game_b.probes)
            or any(a.name != b.name or a.outcomes != b.outcomes
                   for a,b in zip(game_a.probes,game_b.probes))):
        raise ValueError("comparison requires the same public action/outcome grammar")
    if visible_trace_distance(game_a, game_b, policy) != 0:
        raise ValueError("public transcript alias required for factorization")
    aa = terminal_traces(game_a, policy)
    bb = terminal_traces(game_b, policy)
    if tuple((t.history,t.terminal_action) for t in aa) != tuple(
            (t.history,t.terminal_action) for t in bb):
        raise AssertionError("fixed policy lost shared public trace keys")
    return aa,bb


def _world_masses(trace, world: str) -> tuple[Q,Q]:
    if world == "evaluation":
        return trace.evaluation_probability,trace.evaluation_compromised
    if world == "deployment":
        return trace.deployment_probability,trace.deployment_compromised
    raise ValueError("world must be evaluation or deployment")


def attested_trace_law(game: StatefulAwarenessGame,
                       policy: PolicyNode, attestor: SealedAttestor,
                       reports: int, world: str) -> dict[tuple,Q]:
    """Joint public transcript plus private positive-report count law."""
    if not isinstance(attestor,SealedAttestor):
        raise ValueError("attestor must be independently typed")
    n = _report_count(reports)
    intact = attestor.count_law(n,False)
    compromised = attestor.count_law(n,True)
    law = {}
    for trace in terminal_traces(game,policy):
        mass,bad = _world_masses(trace,world)
        assert 0<=bad<=mass
        for k in range(n+1):
            key=(trace.history,trace.terminal_action,k)
            if key in law:
                raise AssertionError("duplicate public transcript key")
            law[key]=(mass-bad)*intact[k]+bad*compromised[k]
    assert sum(law.values(),Q(0)) == 1
    return law


def audit_public_alias(game_a: StatefulAwarenessGame,
                       game_b: StatefulAwarenessGame,
                       policy: PolicyNode, attestor: SealedAttestor,
                       reports: int, *,
                       world: str = "deployment") -> AttestationCertificate:
    """Exact discrimination of two publicly identical models via sealed tests.

    Assumes every private report observes the SAME terminal integrity state,
    with independent test noise conditional on that state, and test results
    cannot change the actor's already-completed public policy.
    """
    n=_report_count(reports)
    aa,bb=_trace_pair(game_a,game_b,policy)
    if world not in ("evaluation","deployment"):
        raise ValueError("world must be evaluation or deployment")
    if not isinstance(attestor,SealedAttestor):
        raise ValueError("attestor must be independently typed")

    hidden_gap=Q(0)
    exposure_a=exposure_b=Q(0)
    for ta,tb in zip(aa,bb):
        pa,sa=_world_masses(ta,world)
        pb,sb=_world_masses(tb,world)
        assert pa==pb
        hidden_gap+=abs(sa-sb)
        if ta.terminal_action=="exploit":
            exposure_a+=sa
            exposure_b+=sb

    la=attested_trace_law(game_a,policy,attestor,n,world)
    lb=attested_trace_law(game_b,policy,attestor,n,world)
    assert la.keys()==lb.keys()
    observed=sum((abs(la[key]-lb[key]) for key in la),Q(0))/2
    channel_tv=attestor.count_total_variation(n)
    if observed != hidden_gap*channel_tv:
        raise AssertionError("persistent hidden-state factorization failed")
    if observed>hidden_gap or abs(exposure_a-exposure_b)>hidden_gap:
        raise AssertionError("private audit exceeded hidden-state information ceiling")

    # Equal-prior likelihood-ratio classifier: predict model B on evidence
    # that has greater probability under B; all ties choose model A.
    choose_b=tuple(key for key in la if lb[key]>la[key])
    false_alarm=sum((la[key] for key in choose_b),Q(0))
    miss=sum((lb[key] for key in la if key not in choose_b),Q(0))
    error=(false_alarm+miss)/2
    assert error==(1-observed)/2

    # If false positive and sensitivity coincide, even infinitely many
    # reports have zero distinguishing power. Otherwise a consistent
    # sample-mean test asymptotically recovers the terminal integrity bit.
    limiting= (1-hidden_gap)/2 if (
        attestor.false_positive!=attestor.sensitivity) else Q(1,2)
    return AttestationCertificate(
        world,n,len(aa),Q(0),hidden_gap,channel_tv,observed,error,limiting,
        abs(exposure_a-exposure_b),false_alarm,miss,
    )


def audit_budget(game_a: StatefulAwarenessGame,
                 game_b: StatefulAwarenessGame,policy: PolicyNode,
                 attestor: SealedAttestor,target_error: Q,
                 *,world: str="deployment",max_reports: int=16) -> AttestationBudget:
    """Smallest number of sealed tests achieving equal-prior error target."""
    cap=_report_count(max_reports)
    target=_rational(target_error,"target error")
    if not 0<=target<=Q(1,2):
        raise ValueError("target error must lie in [0,1/2]")
    # Shared conditional hidden-state geometry is unchanged as n grows.
    aa,bb=_trace_pair(game_a,game_b,policy)
    if world not in ("evaluation","deployment"):
        raise ValueError("world must be evaluation or deployment")
    gap=sum((abs(_world_masses(a,world)[1]-_world_masses(b,world)[1])
             for a,b in zip(aa,bb)),Q(0))
    informative=attestor.false_positive!=attestor.sensitivity
    limiting=(1-gap)/2 if informative else Q(1,2)
    errors=tuple((1-gap*attestor.count_total_variation(n))/2
                 for n in range(cap+1))
    assert all(errors[i+1]<=errors[i] for i in range(cap))
    found=next((i for i,e in enumerate(errors) if e<=target),None)
    return AttestationBudget(target,cap,found,limiting,errors)
