"""RHC-01: exact finite signal-limited reward-hacking detection certificates.

A model-free, rational-arithmetic minimax toy. All probabilities are exact.
This module does not prove any claim about a trained agent or the CFT bootstrap.
"""

from __future__ import annotations

from fractions import Fraction as F
from itertools import combinations
from typing import Iterable, Sequence


def distribution(values: Iterable[int | F]) -> tuple[F, ...]:
    values = tuple(F(x) for x in values)
    if not values or min(values) < 0 or sum(values) != 1:
        raise ValueError("distribution must be nonempty, nonnegative and sum to one")
    return values


def _problem(
    safe: Sequence[F], exploits: Sequence[Sequence[F]], alpha: F
) -> tuple[tuple[F, ...], tuple[tuple[F, ...], ...], F]:
    p = distribution(safe)
    qs = tuple(distribution(q) for q in exploits)
    if not qs or any(len(q) != len(p) for q in qs):
        raise ValueError("need at least one exploit of matching signal dimension")
    alpha = F(alpha)
    if not 0 <= alpha <= 1:
        raise ValueError("false-positive budget outside [0,1]")
    return p, qs, alpha


def expected(dist: Sequence[F], detector: Sequence[F]) -> F:
    if len(dist) != len(detector):
        raise ValueError("mismatched dimensions")
    return sum((F(p) * F(f) for p, f in zip(dist, detector)), F(0))


def detector_certificate(
    safe: Sequence[F], exploits: Sequence[Sequence[F]], alpha: F, detector: Sequence[F]
) -> dict:
    p, qs, alpha = _problem(safe, exploits, alpha)
    f = tuple(F(x) for x in detector)
    if len(f) != len(p) or any(x < 0 or x > 1 for x in f):
        raise ValueError("detector values must be in [0,1] on each signal")
    fpr = expected(p, f)
    if fpr > alpha:
        raise ValueError("false-positive budget exceeded")
    hits = tuple(expected(q, f) for q in qs)
    return {"false_positive": fpr, "per_exploit": hits, "guaranteed_detection": min(hits)}


def dual_certificate(
    safe: Sequence[F], exploits: Sequence[Sequence[F]], alpha: F,
    mixing: Sequence[F], threshold: F
) -> dict:
    """A valid upper bound for any mixture of attacks and t >= 0.

    Formula: alpha*t + sum_o max(0, Q_mix(o) - t*P(o)).
    """
    p, qs, alpha = _problem(safe, exploits, alpha)
    lam = distribution(mixing)
    if len(lam) != len(qs) or F(threshold) < 0:
        raise ValueError("invalid attack mixture or threshold")
    t = F(threshold)
    mixed = tuple(sum((lam[j] * qs[j][i] for j in range(len(qs))), F(0))
                  for i in range(len(p)))
    excess = tuple(max(F(0), mixed[i] - t * p[i]) for i in range(len(p)))
    return {"attack_mixture": mixed, "threshold": t,
            "excess": excess, "upper_bound": alpha * t + sum(excess, F(0))}


def _solve_square(rows: Sequence[Sequence[F]], rhs: Sequence[F]) -> tuple[F, ...] | None:
    """Exact Gauss-Jordan solve; None for singular systems."""
    n = len(rhs)
    a = [[F(v) for v in row] + [F(b)] for row, b in zip(rows, rhs)]
    if len(a) != n or any(len(row) != n + 1 for row in a):
        raise ValueError("expected a square system")
    for col in range(n):
        pivot = next((i for i in range(col, n) if a[i][col]), None)
        if pivot is None:
            return None
        a[col], a[pivot] = a[pivot], a[col]
        divisor = a[col][col]
        a[col] = [x / divisor for x in a[col]]
        for row in range(n):
            if row != col and a[row][col]:
                coefficient = a[row][col]
                a[row] = [x - coefficient * y for x, y in zip(a[row], a[col])]
    return tuple(row[-1] for row in a)


def optimal_detector(
    safe: Sequence[F], exploits: Sequence[Sequence[F]], alpha: F
) -> dict:
    """Independently maximize min_j E_Qj f by exact LP vertex enumeration.

    Intended only for small signal alphabets (n <= 5); combinatorial runtime.
    The final coordinate is the guaranteed detection variable d.
    """
    p, qs, alpha = _problem(safe, exploits, alpha)
    n = len(p)
    if n > 5:
        raise ValueError("vertex oracle is restricted to <=5 signals")
    zero = F(0)
    inequalities: list[tuple[tuple[F, ...], F]] = []
    for i in range(n):
        lower = [zero] * (n + 1)
        lower[i] = F(-1)
        inequalities.append((tuple(lower), zero))
        upper = [zero] * (n + 1)
        upper[i] = F(1)
        inequalities.append((tuple(upper), F(1)))
    inequalities.append((tuple(p) + (zero,), alpha))
    inequalities.append((tuple([zero] * n + [F(-1)]), zero))  # d >= 0
    inequalities.append((tuple([zero] * n + [F(1)]), F(1)))  # d <= 1
    for q in qs:
        inequalities.append((tuple(-v for v in q) + (F(1),), zero))  # d <= Q_j dot f
    best: tuple[F, ...] | None = None
    vertices = 0
    for active in combinations(range(len(inequalities)), n + 1):
        solution = _solve_square([inequalities[i][0] for i in active],
                                 [inequalities[i][1] for i in active])
        if solution is None or any(expected(row, solution) > b for row, b in inequalities):
            continue
        vertices += 1
        if best is None or (solution[-1], tuple(-x for x in solution[:-1])) > (
            best[-1], tuple(-x for x in best[:-1])
        ):
            best = solution
    assert best is not None, "bounded nonempty polytope must have a vertex"
    check = detector_certificate(p, qs, alpha, best[:-1])
    assert check["guaranteed_detection"] == best[-1]
    return {"detector": best[:-1], "value": best[-1],
            "vertices_visited": vertices, "false_positive": check["false_positive"],
            "per_exploit": check["per_exploit"]}


def total_variation(a: Sequence[F], b: Sequence[F]) -> F:
    p, q = distribution(a), distribution(b)
    if len(p) != len(q):
        raise ValueError("mismatched dimensions")
    return sum((abs(x - y) for x, y in zip(p, q)), F(0)) / 2


def pushforward(dist: Sequence[F], observations: Sequence[int], n_signals: int) -> tuple[F, ...]:
    """Apply a deterministic signal channel to a trajectory distribution."""
    p = distribution(dist)
    if len(observations) != len(p) or n_signals < 1:
        raise ValueError("invalid observation channel")
    out = [F(0)] * n_signals
    for mass, signal in zip(p, observations):
        if not isinstance(signal, int) or not 0 <= signal < n_signals:
            raise ValueError("signal outside alphabet")
        out[signal] += mass
    return tuple(out)


# A diamond graph: two s-to-t paths, one ordinary and one exploit.
VERTICES = ("s", "a", "b", "t")
EDGES = (("s", "a"), ("a", "t"), ("s", "b"), ("b", "t"))
SAFE_PATH = (0, 1)
HACK_PATH = (2, 3)


def gradient(potential: dict[str, F]) -> tuple[F, ...]:
    if set(potential) != set(VERTICES):
        raise ValueError("potential must cover graph vertices")
    return tuple(F(potential[v]) - F(potential[u]) for u, v in EDGES)


def path_integral(weights: Sequence[F], path: Sequence[int]) -> F:
    if len(weights) != len(EDGES) or any(i not in range(len(EDGES)) for i in path):
        raise ValueError("unknown edge")
    return sum((F(weights[i]) for i in path), F(0))


def chain_boundary(coefficients: Sequence[int | F]) -> dict[str, F]:
    if len(coefficients) != len(EDGES):
        raise ValueError("expected one coefficient per edge")
    boundary = {v: F(0) for v in VERTICES}
    for mass, (src, dst) in zip(coefficients, EDGES):
        boundary[src] -= F(mass)
        boundary[dst] += F(mass)
    return boundary


def finite_witness() -> dict:
    """Reproducible exact benchmark, including non-exact cycle-sensitive repair."""
    alpha = F(1, 4)
    p = (F(1, 2), F(1, 4), F(1, 4))
    qs = ((F(0), F(1), F(0)), (F(0), F(0), F(1)))
    lower = detector_certificate(p, qs, alpha, (F(0), F(1, 2), F(1, 2)))
    upper = dual_certificate(p, qs, alpha, (F(1, 2), F(1, 2)), F(2))
    exact = optimal_detector(p, qs, alpha)
    # With gradient-only *path totals*, safe and hack paths have the same observation.
    blind = optimal_detector((F(1),), ((F(1),),), alpha)
    # A non-exact edge 1-cochain separates the two routes perfectly.
    repaired = optimal_detector((F(1), F(0)), ((F(0), F(1)),), alpha)
    cycle = (-1, -1, 1, 1)  # HACK_PATH - SAFE_PATH
    omega = (F(0), F(0), F(1), F(0))
    check = {
        "matching_primal_and_dual_half": lower["guaranteed_detection"] == upper["upper_bound"] == exact["value"] == F(1, 2),
        "unique_witness_detector": exact["detector"] == (F(0), F(1, 2), F(1, 2)),
        "blind_gradient_channel_equals_alpha": blind["value"] == alpha,
        "nonexact_channel_recovers_one": repaired["value"] == F(1),
        "cycle_boundary_zero": all(value == 0 for value in chain_boundary(cycle).values()),
        "nonexact_cochain_detects_cycle": sum((F(x) * y for x, y in zip(cycle, omega)), F(0)) == F(1),
    }
    return {"alpha": alpha, "primal": lower, "dual": upper, "oracle": exact,
            "gradient_only": blind, "cycle_sensitive": repaired,
            "checks": check, "all_passed": all(check.values())}
