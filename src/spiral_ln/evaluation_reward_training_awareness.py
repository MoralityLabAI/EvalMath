"""RHT-20: exact finite simulation-aware incentives and audit-cue transfer.

A synthetic, two-type evaluation/deployment decision game. A model observes a
cue before selecting PROTECT or EXPLOIT. The latent type is evaluation E or
real deployment R. This module computes Bayes-optimal cue-conditioned actions,
independent audit-transfer bounds, and a robust condition for protection on
every deployment-reachable cue.

The optional future-policy value is an externally specified *subjective*
training-update term, not an observed gradient or evidence that a model
actually controls its successor. The evaluation and deployment cue laws,
reward scale, and gold interpretation must be independently justified.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q


def _rational(value, name: str) -> Q:
    if isinstance(value, (float, bool)):
        raise ValueError(f"{name} must be an exact rational, not float/bool")
    try:
        return Q(value)
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        raise ValueError(f"{name} must be a finite rational") from exc


def _distribution(values, name: str) -> tuple[Q, ...]:
    result = tuple(_rational(v, name) for v in values)
    if not result or any(v < 0 or v > 1 for v in result) or sum(result) != 1:
        raise ValueError(f"{name} must be a nonempty normalized distribution")
    return result


def _interval(bounds, name: str, *, lower: Q | None = Q(0), positive=False) -> tuple[Q, Q]:
    if len(bounds) != 2:
        raise ValueError(f"{name} needs two endpoints")
    lo, hi = (_rational(v, name) for v in bounds)
    if lo > hi or (lower is not None and lo < lower) or (positive and lo == 0):
        raise ValueError(f"{name} has invalid bounds")
    return lo, hi


@dataclass(frozen=True)
class EvaluationCueGame:
    """Cue kernels P(s|E), P(s|R), prior P(E), and subjective utilities.

    In an evaluation world, PROTECT earns reward R; in deployment EXPLOIT
    earns gain G. A cue-dependent `future_delta` adds to the subjective
    value of PROTECT versus EXPLOIT in *either* world. Adversarial ties
    choose EXPLOIT. Cue laws are fixed before the actor chooses a policy.
    """
    cues: tuple[str, ...]
    evaluation: tuple[Q, ...]
    deployment: tuple[Q, ...]
    prior: Q
    protect_reward: Q
    exploit_gain: Q
    future_delta: tuple[Q, ...] = ()

    def __post_init__(self):
        if (not self.cues or len(set(self.cues)) != len(self.cues)
                or any(not isinstance(c, str) or not c for c in self.cues)):
            raise ValueError("cues must be nonempty unique strings")
        qe = _distribution(self.evaluation, "evaluation cue kernel")
        qr = _distribution(self.deployment, "deployment cue kernel")
        if len(qe) != len(self.cues) or len(qr) != len(self.cues):
            raise ValueError("cue kernels must match declared cue roster")
        p = _rational(self.prior, "evaluation prior")
        r = _rational(self.protect_reward, "protect reward")
        g = _rational(self.exploit_gain, "exploit gain")
        if not 0 <= p <= 1 or r <= 0 or g <= 0:
            raise ValueError("prior must be a probability; reward and gain positive")
        future = (tuple(_rational(v, "future delta") for v in self.future_delta)
                  if self.future_delta else (Q(0),) * len(self.cues))
        if len(future) != len(self.cues):
            raise ValueError("future delta must match declared cue roster")
        for name, val in (("evaluation", qe), ("deployment", qr),
                          ("prior", p), ("protect_reward", r),
                          ("exploit_gain", g), ("future_delta", future)):
            object.__setattr__(self, name, val)

    def cue_mass(self, i: int) -> Q:
        return self.prior * self.evaluation[i] + (1 - self.prior) * self.deployment[i]

    def posterior(self, i: int) -> Q | None:
        """P(E|cue), None for an impossible cue under the joint prior."""
        mass = self.cue_mass(i)
        return (self.prior * self.evaluation[i] / mass) if mass else None

    def score(self, i: int, *, prior: Q | None = None,
              protect_reward: Q | None = None, exploit_gain: Q | None = None,
              future_delta: Q | None = None) -> Q:
        """Unnormalized Bayes advantage of PROTECT; strict positivity wins."""
        p = self.prior if prior is None else _rational(prior, "prior")
        r = self.protect_reward if protect_reward is None else _rational(protect_reward, "reward")
        g = self.exploit_gain if exploit_gain is None else _rational(exploit_gain, "gain")
        d = self.future_delta[i] if future_delta is None else _rational(future_delta, "delta")
        if not 0 <= p <= 1 or r <= 0 or g <= 0:
            raise ValueError("invalid utility parameters")
        qe, qr = self.evaluation[i], self.deployment[i]
        return p * qe * r - (1 - p) * qr * g + (p * qe + (1 - p) * qr) * d

    def bayes_policy(self) -> tuple[bool, ...]:
        """True means PROTECT. Tie is adversarially resolved to EXPLOIT."""
        return tuple(self.score(i) > 0 for i in range(len(self.cues)))

    def policy_value(self, policy: tuple[bool, ...]) -> Q:
        policy = _policy(policy, len(self.cues))
        result = Q(0)
        for i, protect in enumerate(policy):
            if protect:
                result += self.prior * self.evaluation[i] * self.protect_reward
                result += self.cue_mass(i) * self.future_delta[i]
            else:
                result += (1 - self.prior) * self.deployment[i] * self.exploit_gain
        return result

    def compliance(self, policy: tuple[bool, ...]) -> tuple[Q, Q]:
        """(P(PROTECT|E), P(PROTECT|R)) for a fixed cue-conditioned policy."""
        policy = _policy(policy, len(self.cues))
        return (sum((q for q, a in zip(self.evaluation, policy) if a), Q(0)),
                sum((q for q, a in zip(self.deployment, policy) if a), Q(0)))

    def coverage_ratio(self) -> Q:
        """Minimum P(cue|E)/P(cue|R) over real-deployment support."""
        return min(self.evaluation[i] / qr for i, qr in enumerate(self.deployment) if qr > 0)

    def total_variation(self) -> Q:
        return sum((abs(e - r) for e, r in zip(self.evaluation, self.deployment)), Q(0)) / 2

    def audit_transfer(self, policy: tuple[bool, ...]) -> "AuditTransferCertificate":
        e, r = self.compliance(policy)
        tv = self.total_variation()
        assert abs(e - r) <= tv
        return AuditTransferCertificate(e, r, tv, max(Q(0), e - tv))

    def maximum_audit_gap_witness(self) -> tuple[bool, ...]:
        """An exact witness attaining P(PROTECT|E)-P(PROTECT|R)=TV."""
        return tuple(e > r for e, r in zip(self.evaluation, self.deployment))


@dataclass(frozen=True)
class AuditTransferCertificate:
    evaluation_compliance: Q
    deployment_compliance: Q
    total_variation: Q
    guaranteed_deployment_compliance: Q


@dataclass(frozen=True)
class RobustCoverageCertificate:
    forced_protection: bool
    minimum_advantage: Q
    weakest_cue: str
    worst_prior: Q
    cues_checked: int


def _policy(policy, n: int) -> tuple[bool, ...]:
    result = tuple(policy)
    if len(result) != n or any(type(a) is not bool for a in result):
        raise ValueError("policy must give one Boolean action for each cue")
    return result


def robust_protection(game: EvaluationCueGame,
                      prior_range: tuple[Q, Q],
                      reward_range: tuple[Q, Q],
                      gain_range: tuple[Q, Q],
                      future_delta_ranges: tuple[tuple[Q, Q], ...] | None = None,
                      ) -> RobustCoverageCertificate:
    """Exact rectangular-uncertainty guarantee across all deployment cues.

    Worst reward is the lower endpoint, worst exploitation gain the upper
    endpoint, and worst future value the lower endpoint. The remaining
    margin is affine in the globally shared prior, so its minimum occurs
    at one of the two prior endpoints. A zero margin fails with ties.
    """
    p_lo, p_hi = _interval(prior_range, "prior", lower=Q(0))
    if p_hi > 1:
        raise ValueError("prior endpoints must not exceed one")
    r_lo, _ = _interval(reward_range, "protect reward", positive=True)
    _, g_hi = _interval(gain_range, "exploit gain", positive=True)
    if future_delta_ranges is None:
        deltas = tuple((v, v) for v in game.future_delta)
    else:
        if len(future_delta_ranges) != len(game.cues):
            raise ValueError("future value bounds must match cue roster")
        deltas = tuple(_interval(pair, "future delta", lower=None)
                       for pair in future_delta_ranges)
    candidates = ((game.score(i, prior=p, protect_reward=r_lo,
                              exploit_gain=g_hi, future_delta=deltas[i][0]),
                   game.cues[i], p)
                  for i, qr in enumerate(game.deployment) if qr > 0
                  for p in (p_lo, p_hi))
    score, cue, prior = min(candidates, key=lambda x: (x[0], x[1], x[2]))
    return RobustCoverageCertificate(
        forced_protection=(score > 0), minimum_advantage=score,
        weakest_cue=cue, worst_prior=prior,
        cues_checked=sum(q > 0 for q in game.deployment),
    )


def future_policy_value_delta(protect_kernel: tuple[Q, ...],
                              exploit_kernel: tuple[Q, ...],
                              future_values: tuple[Q, ...],
                              discount: Q = Q(1)) -> Q:
    """Discounted two-action change in expected value of a future policy.

    Both kernels are hypothesized post-training successor distributions.
    This quantity is a declared subjective influence, not an inferred
    optimization gradient or a causal estimate from a visible model trace.
    """
    kc = _distribution(protect_kernel, "protect successor kernel")
    kd = _distribution(exploit_kernel, "exploit successor kernel")
    if len(kc) != len(kd) or len(kc) != len(future_values):
        raise ValueError("successor kernels and values must share dimensions")
    values = tuple(_rational(v, "future utility") for v in future_values)
    d = _rational(discount, "discount")
    if not 0 <= d <= 1:
        raise ValueError("discount must be in [0,1]")
    return d * sum(((c - a) * v for c, a, v in zip(kc, kd, values)), Q(0))


def sharp_audit_gap(game: EvaluationCueGame) -> Q:
    """Independent constructive calculation of the maximal compliance gap."""
    return sum((max(Q(0), e - r) for e, r in zip(game.evaluation, game.deployment)), Q(0))
