"""RHT-21: exact finite adaptive Bayesian evaluation-awareness game.

A hidden, fixed world type E (evaluation) or D (deployment) generates
independent probe observations conditional on the world and the chosen probe.
An agent chooses terminal PROTECT/EXPLOIT or an adaptive observation probe.
Its finite-horizon subjective objective includes a constant hypothetical
future-successor value differential for PROTECT, and the cost of each probe.

This provides exact reference mathematics; it is not an empirical claim that a
trained model estimates these quantities or can influence future gradients.
Conditional probe kernels and the protocol-closed action roster are assumed
licensed independently of the actor. Every probability is rational.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache

from spiral_ln.evaluation_reward_training_awareness import (
    _distribution, _rational,
)


@dataclass(frozen=True)
class EvaluationProbe:
    name: str
    observations: tuple[str, ...]
    evaluation: tuple[Q, ...]
    deployment: tuple[Q, ...]
    cost: Q = Q(0)

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("probe name must be a nonempty string")
        if (not self.observations or len(set(self.observations)) != len(self.observations)
                or any(not isinstance(s, str) or not s for s in self.observations)):
            raise ValueError("probe observations must be unique nonempty strings")
        e = _distribution(self.evaluation, "evaluation observation kernel")
        d = _distribution(self.deployment, "deployment observation kernel")
        if len(e) != len(self.observations) or len(d) != len(self.observations):
            raise ValueError("probe kernel dimensions must match observation roster")
        cost = _rational(self.cost, "probe cost")
        if cost < 0:
            raise ValueError("probe cost must be nonnegative")
        object.__setattr__(self, "evaluation", e)
        object.__setattr__(self, "deployment", d)
        object.__setattr__(self, "cost", cost)

    def total_variation(self) -> Q:
        return sum((abs(e-d) for e, d in zip(
            self.evaluation, self.deployment)), Q(0)) / 2


@dataclass(frozen=True)
class AdaptiveCuePolicy:
    """A deterministic, complete, bounded observation tree.

    Terminal kinds are 'protect' and 'exploit'. A 'probe' node names a declared
    probe and supplies one child per observation, in the declared order.
    """
    kind: str
    probe: str | None = None
    branches: tuple["AdaptiveCuePolicy", ...] = ()


PROTECT = AdaptiveCuePolicy("protect")
EXPLOIT = AdaptiveCuePolicy("exploit")


@dataclass(frozen=True)
class SequentialAuditCertificate:
    evaluation_compliance: Q
    deployment_compliance: Q
    transcript_total_variation: Q
    guaranteed_deployment_compliance: Q
    evaluation_expected_probes: Q
    deployment_expected_probes: Q

    @property
    def observed_gap(self) -> Q:
        return self.evaluation_compliance-self.deployment_compliance


@dataclass(frozen=True)
class SequentialBayesResult:
    subjective_value: Q
    policy: AdaptiveCuePolicy
    audit: SequentialAuditCertificate
    explored_states: int


@dataclass(frozen=True)
class ControlledTransferCertificate:
    maximum_audit_deployment_gap: Q
    witness: AdaptiveCuePolicy
    maximum_coupling_bound: Q
    explored_states: int


@dataclass(frozen=True)
class AdaptiveEvaluationGame:
    probes: tuple[EvaluationProbe, ...]
    prior: Q
    protect_reward: Q
    exploit_gain: Q
    max_probes: int
    future_delta: Q = Q(0)
    max_states: int = 100000

    def __post_init__(self):
        probes = tuple(self.probes)
        if (any(not isinstance(pr, EvaluationProbe) for pr in probes)
                or len(set(pr.name for pr in probes)) != len(probes)):
            raise ValueError("probes must have unique names and valid kernels")
        prior = _rational(self.prior, "evaluation prior")
        r = _rational(self.protect_reward, "protect reward")
        g = _rational(self.exploit_gain, "exploit gain")
        delta = _rational(self.future_delta, "future-policy delta")
        if prior < 0 or prior > 1 or r <= 0 or g <= 0:
            raise ValueError("invalid prior/reward/gain")
        if type(self.max_probes) is not int or not 0 <= self.max_probes <= 20:
            raise ValueError("max_probes must be an integer between 0 and 20")
        if type(self.max_states) is not int or self.max_states < 1:
            raise ValueError("max_states must be positive integer")
        object.__setattr__(self, "probes", probes)
        object.__setattr__(self, "prior", prior)
        object.__setattr__(self, "protect_reward", r)
        object.__setattr__(self, "exploit_gain", g)
        object.__setattr__(self, "future_delta", delta)

    def _by_name(self) -> dict[str, EvaluationProbe]:
        return {probe.name: probe for probe in self.probes}

    def posterior(self, history: tuple[tuple[str, str], ...] = ()) -> Q | None:
        """Bayes posterior, with None for probability-zero histories.

        Repeated probes are conditionally independent given the hidden world.
        """
        e, d = self.prior, 1-self.prior
        lookup = self._by_name()
        if len(history) > self.max_probes:
            raise ValueError("history exceeds the declared probe budget")
        for name, observation in history:
            if name not in lookup:
                raise ValueError("history references unknown probe")
            probe = lookup[name]
            try:
                i = probe.observations.index(observation)
            except ValueError as exc:
                raise ValueError("history references unknown observation") from exc
            e *= probe.evaluation[i]
            d *= probe.deployment[i]
        return e / (e+d) if e+d else None

    def posterior_martingale(self, history: tuple[tuple[str, str], ...],
                             probe_name: str) -> tuple[Q, Q]:
        """(present unnormalized E mass, E mass after expectation over outcomes).

        This exact equality expresses the posterior martingale after dividing
        each side by the current joint mass, whenever that mass is positive.
        """
        lookup = self._by_name()
        if probe_name not in lookup:
            raise ValueError("unknown probe")
        if len(history) >= self.max_probes:
            raise ValueError("history has exhausted probe budget")
        e, d = self.prior, 1-self.prior
        for name, observation in history:
            if name not in lookup or observation not in lookup[name].observations:
                raise ValueError("invalid probe history")
            i = lookup[name].observations.index(observation)
            e *= lookup[name].evaluation[i]
            d *= lookup[name].deployment[i]
        probe = lookup[probe_name]
        return e, sum((e * ke for ke in probe.evaluation), Q(0))

    def _validate_policy(self, policy: AdaptiveCuePolicy) -> None:
        lookup = self._by_name()
        def walk(node: AdaptiveCuePolicy, remaining: int) -> None:
            if not isinstance(node, AdaptiveCuePolicy):
                raise ValueError("policy must be an AdaptiveCuePolicy tree")
            if node.kind in ("protect", "exploit"):
                if node.probe is not None or node.branches:
                    raise ValueError("terminal node cannot carry probe or branches")
                return
            if node.kind != "probe" or remaining <= 0:
                raise ValueError("invalid policy action or exhausted probe budget")
            if node.probe not in lookup:
                raise ValueError("policy names unknown probe")
            if len(node.branches) != len(lookup[node.probe].observations):
                raise ValueError("policy must specify every observation branch")
            for child in node.branches:
                walk(child, remaining-1)
        walk(policy, self.max_probes)

    def policy_value(self, policy: AdaptiveCuePolicy) -> Q:
        """Exact *unconditional* subjective utility of a fixed adaptive tree."""
        self._validate_policy(policy)
        lookup = self._by_name()
        def run(node: AdaptiveCuePolicy, e: Q, d: Q) -> Q:
            if node.kind == "protect":
                return e*self.protect_reward+(e+d)*self.future_delta
            if node.kind == "exploit":
                return d*self.exploit_gain
            probe = lookup[node.probe]
            return -(e+d)*probe.cost+sum((
                run(child,e*ke,d*kd)
                for child,ke,kd in zip(node.branches,probe.evaluation,probe.deployment)
            ), Q(0))
        return run(policy, self.prior, 1-self.prior)

    def audit(self, policy: AdaptiveCuePolicy) -> SequentialAuditCertificate:
        """Exact audit/deployment protection and TV of complete action traces."""
        self._validate_policy(policy)
        lookup = self._by_name()
        leaves: list[tuple[Q,Q,bool]] = []
        expected_e, expected_d = Q(0), Q(0)

        def traverse(node: AdaptiveCuePolicy, e: Q, d: Q) -> None:
            nonlocal expected_e, expected_d
            if node.kind != "probe":
                leaves.append((e,d,node.kind=="protect"))
                return
            probe = lookup[node.probe]
            expected_e += e
            expected_d += d
            for child,ke,kd in zip(node.branches,probe.evaluation,probe.deployment):
                traverse(child, e*ke,d*kd)
        traverse(policy,Q(1),Q(1))
        assert sum((e for e,_,_ in leaves),Q(0))==1
        assert sum((d for _,d,_ in leaves),Q(0))==1
        compliance_e=sum((e for e,_,protect in leaves if protect),Q(0))
        compliance_d=sum((d for _,d,protect in leaves if protect),Q(0))
        tv=sum((abs(e-d) for e,d,_ in leaves),Q(0))/2
        assert abs(compliance_e-compliance_d)<=tv
        return SequentialAuditCertificate(
            evaluation_compliance=compliance_e,
            deployment_compliance=compliance_d,
            transcript_total_variation=tv,
            guaranteed_deployment_compliance=max(Q(0),compliance_e-tv),
            evaluation_expected_probes=expected_e,
            deployment_expected_probes=expected_d,
        )

    def bayes_optimal(self) -> SequentialBayesResult:
        """Exact Bellman solution over all declared adaptive trees.

        Ties between PROTECT and EXPLOIT go to EXPLOIT. Ties with probes
        prefer the current terminal action; equal probes use roster order.
        Recursing on unnormalized masses avoids posterior rounding and
        handles zero-likelihood observations.
        """
        states=0
        @lru_cache(None)
        def solve(remaining: int,e: Q,d: Q) -> tuple[Q,AdaptiveCuePolicy]:
            nonlocal states
            states+=1
            if states>self.max_states:
                raise ValueError("Bayes search exceeded state budget")
            exploit=d*self.exploit_gain
            protect=e*self.protect_reward+(e+d)*self.future_delta
            if protect>exploit:
                value,tree=protect,PROTECT
            else:
                value,tree=exploit,EXPLOIT
            if remaining:
                for probe in self.probes:
                    results=tuple(solve(remaining-1,e*ke,d*kd)
                                  for ke,kd in zip(probe.evaluation,probe.deployment))
                    trial=-(e+d)*probe.cost+sum((v for v,_ in results),Q(0))
                    if trial>value:
                        value=trial
                        tree=AdaptiveCuePolicy(
                            "probe",probe.name,tuple(t for _,t in results))
            return value,tree
        value,policy=solve(self.max_probes,self.prior,1-self.prior)
        assert self.policy_value(policy)==value
        return SequentialBayesResult(value,policy,self.audit(policy),states)

    def maximal_coupling_bound(self) -> Q:
        """Conservative uniform H-step adaptive TV bound.

        Each shared-history probe can be maximally coupled with agreement
        probability at least 1-epsilon. The action chosen is identical on
        coupled histories, giving TV <= 1-(1-epsilon)**H.
        """
        if not self.probes:
            return Q(0)
        epsilon=max(probe.total_variation() for probe in self.probes)
        return 1-(1-epsilon)**self.max_probes

    def controlled_audit_gap(self) -> ControlledTransferCertificate:
        """Max over ALL adaptive probe trees of C_E-C_D, independent of utility.

        D_0(e,d) = max(0,e-d)
        D_h(e,d) = max(D_0(e,d), max_a sum_o D_(h-1)(e*kE,d*kD)).
        This is also the sharp controlled TV of terminal transcripts when
        the experiment and terminal protection rule can be chosen together.
        """
        states=0
        @lru_cache(None)
        def search(remaining: int,e: Q,d: Q) -> tuple[Q,AdaptiveCuePolicy]:
            nonlocal states
            states+=1
            if states>self.max_states:
                raise ValueError("controlled TV search exceeded state budget")
            if e>d:
                value,policy=e-d,PROTECT
            else:
                value,policy=Q(0),EXPLOIT
            if remaining:
                for probe in self.probes:
                    results=tuple(search(remaining-1,e*ke,d*kd)
                                  for ke,kd in zip(probe.evaluation,probe.deployment))
                    trial=sum((v for v,_ in results),Q(0))
                    if trial>value:
                        value=trial
                        policy=AdaptiveCuePolicy(
                            "probe",probe.name,tuple(t for _,t in results))
            return value,policy
        value,witness=search(self.max_probes,Q(1),Q(1))
        audited=self.audit(witness)
        assert audited.observed_gap==value
        bound=self.maximal_coupling_bound()
        assert value<=bound
        return ControlledTransferCertificate(value,witness,bound,states)
