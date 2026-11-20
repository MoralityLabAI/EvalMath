"""RHT-26 empirical bridge: exact joint-endpoint and resolution arithmetic.

The counts are a compact snapshot of the published eight-root Qwen3-1.7B
development cohort at Control-Harness commit 27b210f. This is neither an
independent GPU replication nor confirmation evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from math import ceil, comb, log, sqrt
from typing import Mapping


@dataclass(frozen=True)
class JointCounts:
    """Full (B,A) endpoint counts, ordered 00, 01, 10, 11."""

    n00: int
    n01: int
    n10: int
    n11: int

    def __post_init__(self) -> None:
        if any(type(n) is not int or n < 0 for n in
               (self.n00, self.n01, self.n10, self.n11)):
            raise ValueError("outcome counts must be nonnegative integers")
        if not self.n:
            raise ValueError("at least one case required")

    @property
    def n(self) -> int:
        return self.n00 + self.n01 + self.n10 + self.n11

    @property
    def before(self) -> Q:
        return Q(self.n10 + self.n11, self.n)

    @property
    def after(self) -> Q:
        return Q(self.n01 + self.n11, self.n)

    @property
    def joint(self) -> Q:
        return Q(self.n11, self.n)

    @property
    def persistence_given_before(self) -> Q | None:
        b = self.n10 + self.n11
        return Q(self.n11, b) if b else None

    @property
    def recovered_given_before(self) -> Q | None:
        b = self.n10 + self.n11
        return Q(self.n10, b) if b else None


def factorial_contrasts(arms: Mapping[str, JointCounts]) -> dict[str, Q]:
    """Population joint risk differences, not selected-denominator ratios."""
    if set(arms) != {"p00", "p10", "p01", "p11"}:
        raise ValueError("expected all four arms")
    if len({v.n for v in arms.values()}) != 1:
        raise ValueError("this summary requires matched denominators")
    a, b, c, d = (arms[name].joint for name in ("p00", "p10", "p01", "p11"))
    return {
        "artifact_frozen": b-a,
        "learning_clean": c-a,
        "combined": d-a,
        "interaction": d-b-c+a,
        "update_given_artifact": d-b,
    }


def selected_denominator_decomposition(
    frozen: JointCounts, updated: JointCounts
) -> tuple[Q, Q, Q]:
    """Delta p = Delta P(B)*r_frozen + P_updated(B)*Delta r.

    This selected-group decomposition is exact arithmetic, NOT mediation.
    """
    r0, r1 = frozen.persistence_given_before, updated.persistence_given_before
    if r0 is None or r1 is None:
        raise ValueError("both arms need a positive pre-correction denominator")
    pre = (updated.before - frozen.before) * r0
    recovery = updated.before * (r1-r0)
    total = updated.joint - frozen.joint
    assert pre + recovery == total
    return pre, recovery, total


def independent_write_threshold(episodes: int, threshold: int, q: Q) -> Q:
    """Exact P(Binomial(episodes,q) >= threshold) for a monotone toy model.

    Its monotonicity depends on retained independent writes and a fixed
    activation threshold. This family was not fitted to Qwen outputs.
    """
    if type(episodes) is not int or episodes < 0:
        raise ValueError("episodes must be nonnegative integer")
    if type(threshold) is not int or threshold < 1:
        raise ValueError("threshold must be positive integer")
    if not isinstance(q, Q) or not 0 <= q <= 1:
        raise ValueError("q must be rational probability")
    return sum((Q(comb(episodes,j))*q**j*(1-q)**(episodes-j)
                for j in range(threshold, episodes+1)),Q(0))


def hoeffding_floor_planning(*, target: Q, floor: Q, comparisons: int,
                             alpha: Q, range_width: Q = Q(2),
                             confirm_roots: int = 64) -> dict[str, object]:
    """FSI-01 one-sided floor *resolution* if observed mean equals target.

    Root effects are bounded in an interval of width range_width. No claim
    about 80% statistical power or future mean replicability follows.
    """
    if any(type(v) is not Q for v in (target, floor, alpha, range_width)):
        raise ValueError("use exact Fraction arguments")
    if not (0 <= floor < target <= 1 and 0 < alpha < 1 and range_width > 0):
        raise ValueError("invalid numerical planning parameters")
    if (type(comparisons) is not int or comparisons < 1 or
        type(confirm_roots) is not int or confirm_roots < 2):
        raise ValueError("invalid root count or comparison count")
    factor = log(comparisons / float(alpha))
    gap = float(target - floor)
    required = ceil(float(range_width)**2 * factor / (2*gap**2))
    radius = float(range_width)*sqrt(factor/(2*confirm_roots))
    return {
        "min_roots_if_observed_mean_equals_target": required,
        "lower_bound_if_observed_mean_equals_target": float(target)-radius,
        "resolvable_mean_at_planned_roots": float(floor)+radius,
        "floor": str(floor),
        "target": str(target),
        "comparisons": comparisons,
        "range_width": str(range_width),
        "scope": "Finite-sample mean-floor resolution only, not 80%-power.",
    }


def complete_pilot_fixture() -> dict[str, JointCounts]:
    """Published dose-8 aggregate data (8 roots x 32 cases per arm)."""
    return {
        "p00": JointCounts(256,0,0,0),
        "p10": JointCounts(0,0,14,242),
        "p01": JointCounts(256,0,0,0),
        "p11": JointCounts(38,0,174,44),
    }
