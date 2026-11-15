"""BPD-01: exact finite observability and curriculum probe selection.

The rows describe hypothetical deterministic mechanism outcomes, not measured
neural components. Unrouted rows have zero information. A missing outcome is
not interpreted as a negative. All optimization costs are positive integers.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations
from collections import defaultdict, Counter
from typing import Iterable


@dataclass(frozen=True)
class Probe:
    name: str
    outcomes: tuple[int, ...]
    cost: int = 1
    routed: bool = True


def validate(probes: Iterable[Probe]) -> tuple[tuple[Probe, ...], int]:
    rows = tuple(probes)
    if not rows or not all(isinstance(e, Probe) for e in rows):
        raise ValueError("nonempty sequence of Probe records required")
    n = len(rows[0].outcomes)
    if n < 2 or len({p.name for p in rows}) != len(rows):
        raise ValueError("at least two hypotheses and unique probe names required")
    for p in rows:
        if (not isinstance(p.name, str) or not p.name or type(p.cost) is not int
                or p.cost <= 0 or type(p.routed) is not bool
                or len(p.outcomes) != n or any(type(x) is not int or x < 0
                                              for x in p.outcomes)):
            raise ValueError("invalid probe shape, cost, routing or categorical outcome")
    return rows, n


def pairs(n: int) -> tuple[tuple[int, int], ...]:
    return tuple(combinations(range(n), 2))


def masks(probes: Iterable[Probe]) -> tuple[tuple[int, ...], tuple[tuple[int, int], ...]]:
    rows, n = validate(probes)
    ps = pairs(n)
    return (tuple(sum(1 << k for k, (i, j) in enumerate(ps)
                      if p.routed and p.outcomes[i] != p.outcomes[j])
                  for p in rows), ps)


def quotient(probes: Iterable[Probe]) -> tuple[tuple[int, ...], ...]:
    """Observational equivalence classes of candidate mechanisms."""
    rows, n = validate(probes)
    classes: dict[tuple[int, ...], list[int]] = defaultdict(list)
    for i in range(n):
        classes[tuple(p.outcomes[i] for p in rows if p.routed)].append(i)
    return tuple(sorted((tuple(v) for v in classes.values()), key=lambda x: x[0]))


def coverage(probes: Iterable[Probe]) -> dict:
    rows, n = validate(probes)
    ms, ps = masks(rows)
    cover = 0
    for m in ms:
        cover |= m
    return {
        "hypotheses": n,
        "probes": len(rows),
        "routed_probes": sum(p.routed for p in rows),
        "total_pairs": len(ps),
        "separated_pairs": cover.bit_count(),
        "unresolved_pairs": [list(p) for k, p in enumerate(ps) if not (cover >> k & 1)],
        "equivalence_classes": [list(c) for c in quotient(rows)],
    }


def minimum_batch(probes: Iterable[Probe]) -> tuple[int, tuple[str, ...]] | None:
    """Exact minimum-cost NONADAPTIVE set of probes separating every pair."""
    rows, n = validate(probes)
    ms, ps = masks(rows)
    full = (1 << len(ps)) - 1
    if full & ~_union(ms):
        return None

    @lru_cache(None)
    def solve(missing: int) -> tuple[int, tuple[int, ...]] | None:
        if missing == 0:
            return (0, ())
        pivot = missing & -missing
        best = None
        for j, m in enumerate(ms):
            if not m & pivot:
                continue
            sub = solve(missing & ~m)
            if sub is None:
                continue
            candidate = (rows[j].cost + sub[0], tuple(sorted((j,) + sub[1])))
            if best is None or candidate < best:
                best = candidate
        return best

    answer = solve(full)
    return (answer[0], tuple(rows[i].name for i in answer[1])) if answer else None


def _union(values: Iterable[int]) -> int:
    r = 0
    for x in values:
        r |= x
    return r


def exhaustive_batch(probes: Iterable[Probe]) -> tuple[int, tuple[str, ...]] | None:
    """Independent exhaustive subsets, intentionally not using minimum_batch's DP."""
    rows, n = validate(probes)
    if len(rows) > 20:
        raise ValueError("exhaustive oracle supports <=20 probes")
    ps = pairs(n)
    answer = None
    for r in range(len(rows) + 1):
        for ids in combinations(range(len(rows)), r):
            signatures = {tuple(rows[j].outcomes[i] for j in ids if rows[j].routed)
                          for i in range(n)}
            if len(signatures) == n:
                candidate = (sum(rows[j].cost for j in ids), ids)
                if answer is None or candidate < answer:
                    answer = candidate
    return (answer[0], tuple(rows[i].name for i in answer[1])) if answer else None


def adaptive_worst_cost(probes: Iterable[Probe]) -> int | None:
    """Optimal worst-case tree depth in cost units, identifying ALL hypotheses."""
    rows, n = validate(probes)

    @lru_cache(None)
    def solve(worlds: tuple[int, ...]) -> int | None:
        if len(worlds) <= 1:
            return 0
        best = None
        for probe in rows:
            if not probe.routed:
                continue
            branch: dict[int, list[int]] = defaultdict(list)
            for world in worlds:
                branch[probe.outcomes[world]].append(world)
            if len(branch) < 2:
                continue
            children = [solve(tuple(v)) for v in branch.values()]
            if any(x is None for x in children):
                continue
            cost = probe.cost + max(children)
            if best is None or cost < best:
                best = cost
        return best

    return solve(tuple(range(n)))


def fibre_floor(samples: Iterable[dict], features: tuple[str, ...]) -> dict:
    """Exact minimum 0-1 errors for ANY deterministic predictor of `features`.

    Rows sharing an identical feature tuple must receive one prediction. Labels
    are 0/1; optional weight is a positive integer. Keys are explicit, so the
    caller must include task, intervention, component and observed state IDs.
    """
    rows = tuple(samples)
    if not rows or not features or len(set(features)) != len(features):
        raise ValueError("nonempty samples and unique feature keys required")
    fibres: dict[tuple, Counter] = defaultdict(Counter)
    for row in rows:
        if (row.get("label") not in (0, 1) or type(row.get("label")) is not int
                or type(row.get("weight", 1)) is not int or row.get("weight", 1) <= 0):
            raise ValueError("binary labels and positive integer weights required")
        if any(key not in row or not isinstance(row[key], (str, int))
               or isinstance(row[key], bool) for key in features):
            raise ValueError("missing or invalid feature")
        fibres[tuple(row[key] for key in features)][row["label"]] += row.get("weight", 1)
    disagreements = [(key, min(counts[0], counts[1]))
                     for key, counts in fibres.items() if counts[0] and counts[1]]
    return {
        "minimum_errors": sum(v for _, v in disagreements),
        "total_weight": sum(sum(c.values()) for c in fibres.values()),
        "fibres": len(fibres),
        "conflicting_fibres": len(disagreements),
        "first_conflict": list(sorted(disagreements, key=lambda x: repr(x[0]))[0][0])
                          if disagreements else None,
    }


def clock_visibility_floors(samples: Iterable[dict]) -> dict:
    """Fit bounds, not actual probe accuracy or causal importance estimates."""
    rows = tuple(samples)
    base = ("case", "component", "intervention")
    return {
        "state_only": fibre_floor(rows, base + ("state",)),
        "state_clock": fibre_floor(rows, base + ("state", "pass")),
        "visible_only": fibre_floor(rows, base + ("visible",)),
    }


def refill_witness(passes: int = 4, source_bit: int = 1) -> dict:
    """Synthetic repeated refresh: early single-pass erasure is rebuilt."""
    if type(passes) is not int or passes < 2 or source_bit not in (0, 1):
        raise ValueError("requires >=2 passes and a bit-valued source")
    baseline = (source_bit,) * passes
    single_final = []
    single_trajectories = []
    for cut in range(passes):
        path = list(baseline)
        path[cut] = 0
        single_trajectories.append(path)
        single_final.append(path[-1])
    persistent = (0,) * passes
    return {
        "baseline": list(baseline),
        "single_cut_final": single_final,
        "single_cut_trajectories": single_trajectories,
        "persistent_cut_final": persistent[-1],
        "terminal_blind_early_cuts": sum(final == source_bit for final in single_final[:-1]),
    }
