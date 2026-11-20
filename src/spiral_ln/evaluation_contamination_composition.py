"""RHT-28: exact composition of changes to finite evaluation kernels.

The comparison is interventional: each schedule describes a declared complete
state under a fixed policy and task interface. Adaptive policies must be included
in the kernels, with sufficient history in the state. These computations do not
discover omitted state, license a supplied kernel, or establish model safety.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from itertools import product
from typing import Iterable

from spiral_ln.evaluation_finite_kernels import (
    Kernel, Law, apply, dobrushin, expectation, law, probability, row_distance,
    total_variation,
)

Exact = int | str | Q


def _probabilities(values: Iterable[Exact]) -> tuple[Q, ...]:
    if isinstance(values, (str, bytes)):
        raise TypeError("a probability sequence must be a container of exact values")
    return tuple(probability(value) for value in values)


def _schedule(initial: Iterable[Exact], kernels: Iterable[Kernel]) -> tuple[Law, tuple[Kernel, ...]]:
    start = law(initial)
    steps = tuple(kernels)
    size = len(start)
    for kernel in steps:
        if not isinstance(kernel, Kernel):
            raise TypeError("a schedule must contain Kernel objects")
        if kernel.input_size != size:
            raise ValueError("successive state-space dimensions must match")
        size = kernel.output_size
    return start, steps


def _paired_schedules(initial_p: Iterable[Exact], initial_q: Iterable[Exact],
                      kernels_p: Iterable[Kernel], kernels_q: Iterable[Kernel]
                      ) -> tuple[Law, Law, tuple[Kernel, ...], tuple[Kernel, ...]]:
    p, ps = _schedule(initial_p, kernels_p)
    q, qs = _schedule(initial_q, kernels_q)
    if len(p) != len(q) or len(ps) != len(qs):
        raise ValueError("paired systems need the same initial space and horizon")
    for left, right in zip(ps, qs):
        if (left.input_size, left.output_size) != (right.input_size, right.output_size):
            raise ValueError("paired systems need a common state space at each time")
    return p, q, ps, qs


@dataclass(frozen=True)
class CompositionStep:
    time: int
    epsilon: Q
    delta_p: Q
    delta_q: Q
    delta: Q
    actual_tv: Q
    recurrence_bound: Q
    unrolled_bound: Q
    trace_bound: Q


@dataclass(frozen=True)
class CompositionCertificate:
    initial_tv: Q
    final_p: Law
    final_q: Law
    steps: tuple[CompositionStep, ...]
    final_tv: Q
    recurrence_bound: Q
    unrolled_bound: Q
    trace_bound: Q
    terminal_bound: Q
    initial_contribution: Q
    injection_contributions: tuple[Q, ...]


def unrolled_contributions(initial_tv: Exact, epsilons: Iterable[Exact],
                           deltas: Iterable[Exact]) -> tuple[Q, tuple[Q, ...]]:
    """Return d0*prod(delta) and each epsilon_t*prod_{j>t}(delta_j).

    Inputs are licensed bounds in [0, 1]. Their relationship to physical kernels
    is an external assumption; composition_certificate computes exact values.
    """
    d0 = probability(initial_tv)
    eps = _probabilities(epsilons)
    ds = _probabilities(deltas)
    if len(eps) != len(ds):
        raise ValueError("one discrepancy and contraction coefficient per step")
    suffix = Q(1)
    contributions = []
    for epsilon, delta in reversed(tuple(zip(eps, ds))):
        contributions.append(epsilon * suffix)
        suffix *= delta
    return d0 * suffix, tuple(reversed(contributions))


def path_coupling_bound(initial_tv: Exact, epsilons: Iterable[Exact]) -> Q:
    """TV bound for the complete declared state history, including its start."""
    agreement = 1 - probability(initial_tv)
    for epsilon in _probabilities(epsilons):
        agreement *= 1 - epsilon
    return 1 - agreement


def composition_certificate(initial_p: Iterable[Exact], initial_q: Iterable[Exact],
                            kernels_p: Iterable[Kernel], kernels_q: Iterable[Kernel]
                            ) -> CompositionCertificate:
    """Compute exact laws and uniform discrepancy bounds without path expansion.

    At step t, epsilon=max_x TV(P_t(x),Q_t(x)) and
    delta=min(Dobrushin(P_t), Dobrushin(Q_t)). Both triangle-inequality
    orientations are valid, so d_t <= delta*d_{t-1}+epsilon. The clipped
    recurrence and separately unrolled formula are recorded. The terminal bound
    also uses the full-history coupling bound when it is tighter.
    """
    p, q, ps, qs = _paired_schedules(initial_p, initial_q, kernels_p, kernels_q)
    d0 = total_variation(p, q)
    recurrence = unrolled = d0
    agreement = 1 - d0
    records = []
    for time, (pk, qk) in enumerate(zip(ps, qs), 1):
        epsilon = row_distance(pk, qk)
        delta_p, delta_q = dobrushin(pk), dobrushin(qk)
        delta = min(delta_p, delta_q)
        p, q = apply(p, pk), apply(q, qk)
        actual = total_variation(p, q)
        recurrence = min(Q(1), delta * recurrence + epsilon)
        unrolled = delta * unrolled + epsilon
        agreement *= 1 - epsilon
        records.append(CompositionStep(time, epsilon, delta_p, delta_q, delta,
                                       actual, recurrence, min(Q(1), unrolled),
                                       1 - agreement))
    initial_term, injections = unrolled_contributions(
        d0, (r.epsilon for r in records), (r.delta for r in records))
    trace_bound = 1 - agreement
    return CompositionCertificate(
        d0, p, q, tuple(records), total_variation(p, q), recurrence,
        min(Q(1), unrolled), trace_bound, min(recurrence, trace_bound),
        initial_term, injections,
    )


@dataclass(frozen=True)
class TraceLaw:
    paths: tuple[tuple[int, ...], ...]
    probabilities: Law


def trace_law(initial: Iterable[Exact], kernels: Iterable[Kernel], *,
              max_paths: int = 100_000) -> TraceLaw:
    """Enumerate every full declared state history, including zero-mass paths.

    This is an exponential finite oracle. max_paths bounds the complete product
    space before any paths are allocated. Emitted actions are covered only when
    encoded in these states (or supplied through a common protected readout).
    """
    if isinstance(max_paths, bool) or not isinstance(max_paths, int) or max_paths < 1:
        raise ValueError("max_paths must be a positive integer")
    start, steps = _schedule(initial, kernels)
    sizes = (len(start), *(kernel.output_size for kernel in steps))
    count = 1
    for size in sizes:
        count *= size
        if count > max_paths:
            raise ValueError("complete trace space exceeds max_paths")
    paths = tuple(product(*(range(size) for size in sizes)))
    masses = []
    for path in paths:
        mass = start[path[0]]
        for time, kernel in enumerate(steps):
            mass *= kernel.rows[path[time]][path[time + 1]]
        masses.append(mass)
    return TraceLaw(paths, law(masses))


def trace_total_variation(initial_p: Iterable[Exact], initial_q: Iterable[Exact],
                          kernels_p: Iterable[Kernel], kernels_q: Iterable[Kernel], *,
                          max_paths: int = 100_000) -> Q:
    p, q, ps, qs = _paired_schedules(initial_p, initial_q, kernels_p, kernels_q)
    left = trace_law(p, ps, max_paths=max_paths)
    right = trace_law(q, qs, max_paths=max_paths)
    return total_variation(left.probabilities, right.probabilities)


@dataclass(frozen=True)
class RiskCertificate:
    actual_risk: Q
    reference_risk: Q
    absolute_gap: Q
    endpoint_discrepancy: Q
    gap_bound: Q
    actual_risk_upper_bound: Q


def risk_certificate(certificate: CompositionCertificate,
                     actual_payoff: Iterable[Exact],
                     reference_payoff: Iterable[Exact] | None = None) -> RiskCertificate:
    """Bound an event or a [0,1] loss, adding any endpoint-oracle discrepancy.

    The default uses the same protected endpoint in both systems. Supplying a
    different endpoint incurs eta=max_x|f(x)-g(x)|; copying a changed judge's
    verdict without eta would not bound the original harm event. The baseline
    risk remains part of the absolute-risk upper bound even at zero discrepancy.
    """
    actual_values = _probabilities(actual_payoff)
    reference_values = (actual_values if reference_payoff is None else
                        _probabilities(reference_payoff))
    if len(actual_values) != len(certificate.final_p) or len(reference_values) != len(certificate.final_q):
        raise ValueError("payoff dimensions must match the terminal state space")
    actual = expectation(certificate.final_p, actual_values)
    reference = expectation(certificate.final_q, reference_values)
    eta = max(abs(a - b) for a, b in zip(actual_values, reference_values))
    gap_bound = min(Q(1), certificate.terminal_bound + eta)
    return RiskCertificate(actual, reference, abs(actual - reference), eta,
                           gap_bound, min(Q(1), reference + gap_bound))
