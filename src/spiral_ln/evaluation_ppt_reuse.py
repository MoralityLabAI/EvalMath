"""Exact finite witnesses for posterior-prefix-tuning sample-reuse selection bias.

Each latent is a Bernoulli probability p. PPT uses the k=0 tilt
W(p; alpha) = ((1-alpha)(1-p) + alpha*p)**m. The utilities are
one-bit success, one-bit failure, and two-bit disagreement.

The finite oracle assumes IID exact latent-prior draws, exact conditional
utilities, and a fixed candidate family. It does not prove calibrated
claims for approximate BFT/PMC latents or for data-dependent utility families.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from itertools import product
from math import comb


@dataclass(frozen=True)
class Candidate:
    alpha: Q
    length: int
    utility: str

    def __post_init__(self):
        if not isinstance(self.alpha, Q) or not 0 <= self.alpha <= 1:
            raise ValueError("alpha must be a rational probability")
        if type(self.length) is not int or self.length < 1:
            raise ValueError("positive integer prefix length required")
        if self.utility not in ("one", "zero", "change"):
            raise ValueError("unknown utility")


@dataclass(frozen=True)
class Estimate:
    numerator: Q   # empirical mean of W * mu
    denominator: Q # empirical mean of W
    value: Q
    ess: Q


TWO_POINT_PRIOR = ((Q(1, 4), Q(1, 2)), (Q(3, 4), Q(1, 2)))
FOUR_POINT_PRIOR = tuple((Q(i, 8), Q(1, 4)) for i in (1, 3, 5, 7))


def check_prior(prior):
    prior = tuple(prior)
    if (not prior or any(not isinstance(p, Q) or not isinstance(mass, Q)
                         or not 0 <= p <= 1 or mass <= 0 for p, mass in prior)
            or sum((mass for _, mass in prior), Q(0)) != 1):
        raise ValueError("finite rational prior with positive masses summing to one required")
    return prior


def tilt_weight(p: Q, alpha: Q, length: int) -> Q:
    if not 0 <= p <= 1 or not 0 <= alpha <= 1 or type(length) is not int or length < 1:
        raise ValueError("invalid binary kernel, prompt parameter or prefix length")
    return ((1 - alpha) * (1 - p) + alpha * p) ** length


def utility_mean(p: Q, utility: str) -> Q:
    if utility == "one":
        return p
    if utility == "zero":
        return 1 - p
    if utility == "change":
        return 2 * p * (1 - p)
    raise ValueError("unknown utility")


def population_objective(prior, candidate: Candidate) -> Q:
    prior = check_prior(prior)
    terms = [(mass * tilt_weight(p, candidate.alpha, candidate.length),
              utility_mean(p, candidate.utility)) for p, mass in prior]
    denominator = sum((weight for weight, _ in terms), Q(0))
    if denominator == 0:
        raise ValueError("zero population tilt mass")
    return sum((weight * mu for weight, mu in terms), Q(0)) / denominator


def sample_estimate(samples, candidate: Candidate) -> Estimate:
    samples = tuple(samples)
    if not samples:
        raise ValueError("at least one sample required")
    weights = tuple(tilt_weight(p, candidate.alpha, candidate.length) for p in samples)
    total = sum(weights, Q(0))
    if total <= 0:
        raise ValueError("zero empirical tilt mass; abstain from certification")
    weighted_utility = sum((w * utility_mean(p, candidate.utility)
                            for w, p in zip(weights, samples)), Q(0))
    n = len(samples)
    return Estimate(weighted_utility / n, total / n,
                    weighted_utility / total,
                    total * total / sum((w * w for w in weights), Q(0)))


def ratio_interval(estimate: Estimate, epsilon: Q) -> tuple[Q, Q]:
    """Deterministic interval if numerator and denominator errors are <=epsilon.

    Confidence coverage requires a separate uniform or independent-sample
    probability bound on the two empirical means.
    """
    if not isinstance(epsilon, Q) or epsilon < 0:
        raise ValueError("epsilon must be a nonnegative rational")
    a, b = estimate.numerator, estimate.denominator
    if b <= 0 or a < 0 or a > b:
        raise ValueError("expected 0 <= numerator <= denominator with positive denominator")
    lo = max(Q(0), (a - epsilon) / (b + epsilon))
    hi = Q(1) if b <= epsilon else min(Q(1), (a + epsilon) / (b - epsilon))
    return lo, hi


def exact_selection_profile(prior, candidates, n: int, threshold: Q = Q(1, 4)) -> dict:
    """Enumerate independent prior sample pools and the highest-scoring candidate.

    Samples are visible to the selector. Candidate family must be fixed in
    advance for the accompanying uniform-concentration argument.
    """
    prior = check_prior(prior)
    candidates = tuple(candidates)
    if type(n) is not int or not 1 <= n <= 8 or not candidates:
        raise ValueError("finite enumeration: 1 <= n <= 8 and nonempty candidate set")
    if not isinstance(threshold, Q) or threshold < 0:
        raise ValueError("nonnegative rational threshold required")
    truth = tuple(population_objective(prior, c) for c in candidates)
    fixed_mean = [Q(0)] * len(candidates)
    selected_mean = Q(0)
    selected_true = Q(0)
    fixed_risk = [Q(0)] * len(candidates)
    selected_risk = Q(0)
    min_ess = Q(n)
    max_ess = Q(0)
    worlds = 0
    for chosen in product(prior, repeat=n):
        worlds += 1
        mass = Q(1)
        samples = []
        for p, weight in chosen:
            mass *= weight
            samples.append(p)
        estimates = tuple(sample_estimate(samples, c) for c in candidates)
        for j, e in enumerate(estimates):
            fixed_mean[j] += mass * e.value
            fixed_risk[j] += mass * (e.value - truth[j] >= threshold)
            min_ess = min(min_ess, e.ess)
            max_ess = max(max_ess, e.ess)
        j = max(range(len(candidates)), key=lambda j: (estimates[j].value, -j))
        selected_mean += mass * estimates[j].value
        selected_true += mass * truth[j]
        selected_risk += mass * (estimates[j].value - truth[j] >= threshold)
    return {"true_values": truth, "fixed_estimate_means": tuple(fixed_mean),
            "selected_estimate_mean": selected_mean,
            "selected_true_mean": selected_true,
            "selection_optimism": selected_mean - selected_true,
            "extra_over_first_estimator": selected_mean - fixed_mean[0],
            "fixed_false_risks": tuple(fixed_risk),
            "selected_false_risk": selected_risk,
            "min_ess": min_ess, "max_ess": max_ess, "worlds": worlds}


def closed_form_two_utility_gap(n: int) -> Q:
    """Exact expected winner's-curse gap, alpha=1/2, two-point prior.

    max(score_one, score_zero) = 1/2 + |sum_i sign_i|/(4n).
    """
    if type(n) is not int or n < 1:
        raise ValueError("positive sample count required")
    return sum((Q(comb(n, k), 2 ** n) * Q(abs(2*k - n), 4*n)
                for k in range(n + 1)), Q(0))


def exact_uniform_coverage(prior, candidates, n: int, epsilon: Q) -> dict:
    """Finite audit of an all-candidate numerator/denominator deviation event.

    Returns its *exact* probability under the specified finite prior; this
    enumeration is not a distribution-free confidence theorem.
    """
    prior = check_prior(prior)
    candidates = tuple(candidates)
    if type(n) is not int or not 1 <= n <= 8 or not candidates:
        raise ValueError("finite enumeration: 1 <= n <= 8 and nonempty candidate set")
    if not isinstance(epsilon, Q) or epsilon < 0:
        raise ValueError("nonnegative rational epsilon required")
    truth = tuple(population_objective(prior, c) for c in candidates)
    pop_means = []
    for c in candidates:
        b = sum((mass * tilt_weight(p, c.alpha, c.length) for p, mass in prior), Q(0))
        pop_means.append((truth[len(pop_means)] * b, b))
    uniform_prob = Q(0)
    all_intervals_cover_prob = Q(0)
    selected_interval_cover_prob = Q(0)
    implication_ok = True
    for chosen in product(prior, repeat=n):
        mass = Q(1)
        samples = []
        for p, m in chosen:
            mass *= m
            samples.append(p)
        es = tuple(sample_estimate(samples, c) for c in candidates)
        uniform = all(abs(e.numerator - a) <= epsilon and
                      abs(e.denominator - b) <= epsilon
                      for e, (a, b) in zip(es, pop_means))
        covered = tuple(lo <= j <= hi for (lo, hi), j in
                        zip((ratio_interval(e, epsilon) for e in es), truth))
        selector = max(range(len(candidates)), key=lambda j: (es[j].value, -j))
        uniform_prob += mass * uniform
        all_intervals_cover_prob += mass * all(covered)
        selected_interval_cover_prob += mass * covered[selector]
        implication_ok &= not uniform or all(covered)
    return {"uniform_mean_event_probability": uniform_prob,
            "all_interval_coverage_probability": all_intervals_cover_prob,
            "selected_interval_coverage_probability": selected_interval_cover_prob,
            "uniform_event_implies_all_intervals": implication_ok}
