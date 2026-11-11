"""RHT-21: finite-horizon active evaluator-cue inference with exact rational proofs.

A fixed hidden world is E (evaluation) or D (deployment). The agent sees an
initial cue and may pay to run informative probes. Each probe's conditional
observation kernel is specified independently for both hidden worlds. The
agent can stop early and choose PROTECT or EXPLOIT, with adversarial terminal
ties broken toward EXPLOIT. All conditional probabilities are exact rationals.

The Bellman recursion is a finite exact-POMDP baseline. Its alpha vectors
form a convex piecewise-linear optimal-value envelope over the prior. A
separate maximal-coupling inequality bounds evaluation/deployment compliance
transfer through the *complete observable adaptive transcript*.

These quantities describe a subjective synthetic agent, not measured model
motives, reliable simulator rewards, or actual future optimizer updates.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache
from itertools import product
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from spiral_ln.evaluation_reward_training_awareness import EvaluationCueGame


def _rational(value, name: str) -> Q:
    if isinstance(value, (float, bool)):
        raise ValueError(f"{name} must be exact rational")
    try:
        return Q(value)
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        raise ValueError(f"{name} must be exact rational") from exc


def _distribution(values, name: str) -> tuple[Q, ...]:
    result = tuple(_rational(v, name) for v in values)
    if not result or any(v < 0 or v > 1 for v in result) or sum(result) != 1:
        raise ValueError(f"{name} must be a normalized distribution")
    return result


@dataclass(frozen=True)
class EvaluationProbe:
    """A registered probe with observation laws conditioned on latent type."""
    name: str
    observations: tuple[str, ...]
    evaluation: tuple[Q, ...]
    deployment: tuple[Q, ...]
    cost: Q = Q(0)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("probe needs a nonempty name")
        if (not isinstance(self.observations, tuple) or not self.observations
                or any(not isinstance(o, str) or not o for o in self.observations)
                or len(set(self.observations)) != len(self.observations)):
            raise ValueError("probe observations must be unique nonempty strings")
        e = _distribution(self.evaluation, "evaluation probe kernel")
        d = _distribution(self.deployment, "deployment probe kernel")
        if len(e) != len(self.observations) or len(d) != len(self.observations):
            raise ValueError("probe kernel dimensions must match observations")
        cost = _rational(self.cost, "probe cost")
        if cost < 0:
            raise ValueError("probe cost must be nonnegative")
        object.__setattr__(self, "evaluation", e)
        object.__setattr__(self, "deployment", d)
        object.__setattr__(self, "cost", cost)

    def total_variation(self) -> Q:
        return sum((abs(e - d) for e, d in zip(self.evaluation, self.deployment)), Q(0)) / 2


@dataclass(frozen=True)
class AdaptivePolicyNode:
    """Finite deterministic policy tree with unnormalized optimal payoff."""
    action: str
    value: Q
    probe_index: int | None = None
    children: tuple["AdaptivePolicyNode", ...] = ()


@dataclass(frozen=True)
class AdaptiveCueCertificate:
    initial_actions: tuple[str, ...]
    policies: tuple[AdaptivePolicyNode, ...]
    subjective_optimal_value: Q
    subjective_no_probe_value: Q
    evaluation_protection: Q
    deployment_protection: Q
    expected_probes_evaluation: Q
    expected_probes_deployment: Q
    initial_cue_tv: Q
    complete_transcript_tv: Q
    conditional_probe_tv_cap: Q
    coupling_tv_upper_bound: Q
    transcript_leaves_checked: int
    belief_states_visited: int
    horizon: int


@dataclass(frozen=True, order=True)
class AlphaValue:
    """A deterministic contingent plan's expected value in pure E and D."""
    evaluation: Q
    deployment: Q

    def at_prior(self, prior: Q) -> Q:
        return prior * self.evaluation + (1 - prior) * self.deployment


@dataclass(frozen=True)
class PriorEnvelopeCertificate:
    minimum_optimal_value: Q
    worst_prior: Q
    prior_endpoints_only_minimum: Q
    critical_priors_checked: int
    total_alpha_vectors: int
    initial_cues: int
    horizon: int


def bayes_update(eval_mass: Q, deploy_mass: Q, probe: EvaluationProbe,
                 observation_index: int) -> tuple[Q, Q, Q | None]:
    """Unnormalized Bayes update; posterior None on an impossible branch."""
    e, d = _rational(eval_mass, "eval mass"), _rational(deploy_mass, "deploy mass")
    if e < 0 or d < 0 or e + d > 1:
        raise ValueError("belief masses must be nonnegative and sum at most one")
    if (type(observation_index) is not int or observation_index < 0
            or observation_index >= len(probe.observations)):
        raise ValueError("invalid observation index")
    new_e = e * probe.evaluation[observation_index]
    new_d = d * probe.deployment[observation_index]
    mass = new_e + new_d
    return new_e, new_d, new_e / mass if mass else None


def _validate_protocol(probes: tuple[EvaluationProbe, ...], horizon: int,
                       max_states: int) -> None:
    if (not isinstance(probes, tuple)
            or any(not isinstance(q, EvaluationProbe) for q in probes)
            or len({q.name for q in probes}) != len(probes)):
        raise ValueError("probes must be a tuple with unique probe names")
    if type(horizon) is not int or horizon < 0 or horizon > 100:
        raise ValueError("horizon must be an integer between 0 and 100")
    if type(max_states) is not int or max_states < 1:
        raise ValueError("state cap must be a positive integer")


def solve_belief(eval_mass: Q, deploy_mass: Q, *, protect_reward: Q,
                 exploit_gain: Q, future_delta: Q = Q(0),
                 probes: tuple[EvaluationProbe, ...] = (), horizon: int = 0,
                 max_states: int = 20000,
                 ) -> tuple[AdaptivePolicyNode, int]:
    """Exact Bellman optimum among all finite observation-adaptive policies.

    A probe's cost is paid whether the hidden world is E or D. Terminal
    PROTECT carries a subjective additional future-policy value delta in
    either world. All ties favor stopping; terminal ties favor EXPLOIT.
    """
    _validate_protocol(probes, horizon, max_states)
    e0 = _rational(eval_mass, "eval mass")
    d0 = _rational(deploy_mass, "deploy mass")
    if e0 < 0 or d0 < 0 or e0 + d0 > 1:
        raise ValueError("belief masses must be nonnegative and sum at most one")
    r = _rational(protect_reward, "protect reward")
    g = _rational(exploit_gain, "exploit gain")
    delta = _rational(future_delta, "future delta")
    if r <= 0 or g <= 0:
        raise ValueError("reward and gain must be positive")

    count = 0

    @lru_cache(maxsize=None)
    def best(e: Q, d: Q, depth: int) -> AdaptivePolicyNode:
        nonlocal count
        count += 1
        if count > max_states:
            raise ValueError("adaptive belief state cap exceeded")
        protect = e * r + (e + d) * delta
        exploit = d * g
        if protect > exploit:
            candidate = AdaptivePolicyNode("protect", protect)
        else:
            candidate = AdaptivePolicyNode("exploit", exploit)
        if depth == 0 or not (e + d):
            return candidate
        for qi, probe in enumerate(probes):
            children = tuple(
                best(e * ke, d * kd, depth - 1)
                for ke, kd in zip(probe.evaluation, probe.deployment)
            )
            value = sum((child.value for child in children), Q(0)) - (e + d) * probe.cost
            if value > candidate.value:
                candidate = AdaptivePolicyNode("probe", value, qi, children)
        return candidate

    node = best(e0, d0, horizon)
    return node, count


def policy_type_metrics(node: AdaptivePolicyNode,
                        probes: tuple[EvaluationProbe, ...]
                        ) -> tuple[Q, Q, Q, Q]:
    """Conditional P(PROTECT|E/D) and expected probe counts for fixed tree."""
    if node.action in ("protect", "exploit"):
        return (Q(1) if node.action == "protect" else Q(0),
                Q(1) if node.action == "protect" else Q(0), Q(0), Q(0))
    if node.action != "probe" or node.probe_index is None:
        raise ValueError("malformed policy tree")
    if node.probe_index < 0 or node.probe_index >= len(probes):
        raise ValueError("policy probe not registered")
    probe = probes[node.probe_index]
    if len(node.children) != len(probe.observations):
        raise ValueError("policy observation branches incomplete")
    metrics = tuple(policy_type_metrics(c, probes) for c in node.children)
    return (
        sum((q * m[0] for q, m in zip(probe.evaluation, metrics)), Q(0)),
        sum((q * m[1] for q, m in zip(probe.deployment, metrics)), Q(0)),
        Q(1) + sum((q * m[2] for q, m in zip(probe.evaluation, metrics)), Q(0)),
        Q(1) + sum((q * m[3] for q, m in zip(probe.deployment, metrics)), Q(0)),
    )


def _transcript_absolute_gap(node: AdaptivePolicyNode, probes: tuple[EvaluationProbe, ...],
                             e: Q, d: Q, max_leaves: int,
                             counter: list[int]) -> Q:
    if node.action != "probe":
        if node.action not in ("protect", "exploit"):
            raise ValueError("malformed terminal decision")
        counter[0] += 1
        if counter[0] > max_leaves:
            raise ValueError("adaptive transcript cap exceeded")
        return abs(e - d)
    if node.probe_index is None or not 0 <= node.probe_index < len(probes):
        raise ValueError("unregistered probe in policy")
    q = probes[node.probe_index]
    if len(node.children) != len(q.observations):
        raise ValueError("incomplete observation policy")
    return sum((
        _transcript_absolute_gap(child, probes, e * pe, d * pd, max_leaves, counter)
        for child, pe, pd in zip(node.children, q.evaluation, q.deployment)
    ), Q(0))


def solve_initial_cues(game: "EvaluationCueGame", probes: tuple[EvaluationProbe, ...],
                       horizon: int, *, max_states: int = 20000,
                       max_transcript_leaves: int = 50000) -> AdaptiveCueCertificate:
    """Compose RHT-20's one-shot initial cue with a finite adaptive probe tree.

    TV on complete transcripts is exact for this fixed policy. A looser
    maximal-coupling upper bound depends only on initial cue TV and the
    maximum TV over all available probe actions.
    """
    _validate_protocol(probes, horizon, max_states)
    if type(max_transcript_leaves) is not int or max_transcript_leaves < 1:
        raise ValueError("transcript cap must be positive")
    policies = []
    ecomp = dcomp = ecalls = dcalls = value = Q(0)
    states = 0
    for i in range(len(game.cues)):
        node, seen = solve_belief(
            game.prior * game.evaluation[i],
            (1 - game.prior) * game.deployment[i],
            protect_reward=game.protect_reward, exploit_gain=game.exploit_gain,
            future_delta=game.future_delta[i], probes=probes,
            horizon=horizon, max_states=max_states,
        )
        states += seen
        policies.append(node)
        e, d, pe, pd = policy_type_metrics(node, probes)
        ecomp += game.evaluation[i] * e
        dcomp += game.deployment[i] * d
        ecalls += game.evaluation[i] * pe
        dcalls += game.deployment[i] * pd
        value += node.value
    counter = [0]
    transcript_tv = sum((
        _transcript_absolute_gap(node, probes, game.evaluation[i],
                                 game.deployment[i], max_transcript_leaves, counter)
        for i, node in enumerate(policies)
    ), Q(0)) / 2
    tv0 = game.total_variation()
    eps = max((probe.total_variation() for probe in probes), default=Q(0))
    coupling_cap = 1 - (1 - tv0) * (1 - eps) ** horizon
    if not abs(ecomp - dcomp) <= transcript_tv <= coupling_cap:
        raise AssertionError("adaptive transcript coupling invariants failed")
    baseline = game.policy_value(game.bayes_policy())
    if value < baseline:
        raise AssertionError("optional stopping cannot be worse than no probe")
    return AdaptiveCueCertificate(
        initial_actions=tuple(n.action for n in policies),
        policies=tuple(policies),
        subjective_optimal_value=value,
        subjective_no_probe_value=baseline,
        evaluation_protection=ecomp, deployment_protection=dcomp,
        expected_probes_evaluation=ecalls, expected_probes_deployment=dcalls,
        initial_cue_tv=tv0, complete_transcript_tv=transcript_tv,
        conditional_probe_tv_cap=eps,
        coupling_tv_upper_bound=coupling_cap,
        transcript_leaves_checked=counter[0],
        belief_states_visited=states, horizon=horizon,
    )


def _prune_component_dominated(vectors: set[AlphaValue]) -> tuple[AlphaValue, ...]:
    """Safe pruning: a vector dominated in both worlds is useless at any prior."""
    out = tuple(sorted(vectors))
    return tuple(v for v in out if not any(
        v != other and other.evaluation >= v.evaluation
        and other.deployment >= v.deployment for other in out
    ))


def alpha_vectors(probes: tuple[EvaluationProbe, ...], horizon: int, *,
                  protect_reward: Q, exploit_gain: Q, future_delta: Q = Q(0),
                  max_vectors: int = 5000,
                  max_proposals: int = 100000) -> tuple[AlphaValue, ...]:
    """Exact contingent-plan alpha vectors for a two-type finite POMDP.

    A terminal-protect alpha is (R+delta, delta), terminal exploit is
    (0,G), and a probe backs up each child alpha under its corresponding
    world-conditioned observation law. Prunes only component-dominated
    vectors, preserving the exact value envelope for all priors.
    """
    _validate_protocol(probes, horizon, max_vectors)
    if type(max_proposals) is not int or max_proposals < 1:
        raise ValueError("alpha proposal cap must be positive")
    r = _rational(protect_reward, "reward")
    g = _rational(exploit_gain, "gain")
    delta = _rational(future_delta, "future delta")
    if r <= 0 or g <= 0:
        raise ValueError("reward and gain must be positive")
    vectors = _prune_component_dominated({
        AlphaValue(r + delta, delta), AlphaValue(Q(0), g),
    })
    for _ in range(horizon):
        next_vectors = set(vectors)  # stopping early is always permitted
        for probe in probes:
            if len(vectors) ** len(probe.observations) > max_proposals:
                raise ValueError("alpha proposal cap exceeded")
            for children in product(vectors, repeat=len(probe.observations)):
                ev = -probe.cost + sum((pe * child.evaluation for pe, child
                                        in zip(probe.evaluation, children)), Q(0))
                dv = -probe.cost + sum((pd * child.deployment for pd, child
                                        in zip(probe.deployment, children)), Q(0))
                next_vectors.add(AlphaValue(ev, dv))
                if len(next_vectors) > max_vectors:
                    raise ValueError("alpha vector cap exceeded")
        vectors = _prune_component_dominated(next_vectors)
    return vectors


def _pair_crossings(lines: tuple[tuple[Q, Q], ...],
                    lo: Q, hi: Q) -> set[Q]:
    """Lines are (intercept, slope); include all internal intersections."""
    candidates = set()
    for i, (b0, a0) in enumerate(lines):
        for b1, a1 in lines[i + 1:]:
            if a0 == a1:
                continue
            cross = (b1 - b0) / (a0 - a1)
            if lo <= cross <= hi:
                candidates.add(cross)
    return candidates


def robust_prior_envelope(game: "EvaluationCueGame",
                          probes: tuple[EvaluationProbe, ...], horizon: int,
                          prior_interval: tuple[Q, Q], *,
                          max_vectors: int = 5000,
                          max_crossings: int = 100000,
                          ) -> PriorEnvelopeCertificate:
    """Exact minimum over an uncertain global prior of the *optimal* value.

    The actor is allowed to select its optimal history-adaptive policy for
    each actual prior. The resulting envelope is convex piecewise-linear
    in the shared prior; a minimum can occur at an INTERIOR crossing. The
    method unions breakpoints across all initially visible cues.

    This is the worst subjective optimal value, not an alignment guarantee
    or a worst-deployment compliance certificate.
    """
    _validate_protocol(probes, horizon, max_vectors)
    if len(prior_interval) != 2:
        raise ValueError("prior interval needs two endpoints")
    lo, hi = (_rational(x, "prior") for x in prior_interval)
    if not Q(0) <= lo <= hi <= Q(1):
        raise ValueError("invalid prior interval")
    if type(max_crossings) is not int or max_crossings < 2:
        raise ValueError("crossing cap must be at least two")

    all_lines = []
    candidates = {lo, hi}
    vector_total = 0
    for i in range(len(game.cues)):
        vecs = alpha_vectors(
            probes, horizon,
            protect_reward=game.protect_reward,
            exploit_gain=game.exploit_gain,
            future_delta=game.future_delta[i], max_vectors=max_vectors,
        )
        vector_total += len(vecs)
        e, d = game.evaluation[i], game.deployment[i]
        lines = tuple((d * v.deployment,
                       e * v.evaluation - d * v.deployment) for v in vecs)
        all_lines.append(lines)
        candidates.update(_pair_crossings(lines, lo, hi))
        if len(candidates) > max_crossings:
            raise ValueError("prior crossing cap exceeded")

    def value(prior: Q) -> Q:
        return sum((max((b + a * prior for b, a in lines))
                    for lines in all_lines), Q(0))

    worst_prior = min(candidates, key=lambda p: (value(p), p))
    worst_value = value(worst_prior)
    endpoints = min(value(lo), value(hi))
    if worst_value > endpoints:
        raise AssertionError("prior envelope critical-point ordering failed")
    return PriorEnvelopeCertificate(
        minimum_optimal_value=worst_value,
        worst_prior=worst_prior,
        prior_endpoints_only_minimum=endpoints,
        critical_priors_checked=len(candidates),
        total_alpha_vectors=vector_total,
        initial_cues=len(game.cues), horizon=horizon,
    )
