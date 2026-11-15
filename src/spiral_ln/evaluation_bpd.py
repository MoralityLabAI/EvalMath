"""BPD-01: exact finite observability, minimum test collection, optimal decision tree,
feature-fibre floors, explicit refill dynamics, and FC-12 three-state cell ledger.

The rows describe hypothetical deterministic mechanism outcomes, not measured
neural components. Unrouted rows have zero information. A missing outcome is
not interpreted as a negative. When realized observations match no candidate in
`H`, `identify_hypothesis` returns `"no hypothesis fits"` (truth outside `H`).
All optimization costs are positive integers.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations
from typing import Iterable, Mapping, Sequence

NO_HYPOTHESIS_FITS = "no hypothesis fits"
FC12_GOALS = 51
FC12_FAMILIES = ("exact", "rw", "rcases", "induction")
FC12_TOTAL_CELLS = FC12_GOALS * len(FC12_FAMILIES)  # 204


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


def identify_hypothesis(
    probes: Iterable[Probe],
    observed: Mapping[str, int | None] | Sequence[int | None],
) -> int | tuple[int, ...] | str:
    """Match realized outcomes against `H`, returning `'no hypothesis fits'` when truth is outside `H`.

    Unrouted probes (`routed=False`) and missing observations (`None`) impose no
    constraint. Returns:
      - `int`: unique surviving hypothesis index `h in 0..n-1` when `|survivors| == 1`,
      - `tuple[int, ...]`: surviving equivalence slice when `|survivors| > 1`,
      - `'no hypothesis fits'`: when no `h in H` matches every routed observed outcome.
    """
    rows, n = validate(probes)
    if isinstance(observed, Mapping):
        unknown = set(observed.keys()) - {p.name for p in rows}
        if unknown:
            raise ValueError(f"unknown probe names in observed: {sorted(unknown)}")
        obs_by_idx = [observed.get(p.name) for p in rows]
    elif isinstance(observed, Sequence) and not isinstance(observed, (str, bytes)):
        if len(observed) != len(rows):
            raise ValueError("observed sequence length must match probes length")
        obs_by_idx = list(observed)
    else:
        raise ValueError("observed must be a mapping or sequence of categorical ints / None")

    for val in obs_by_idx:
        if val is not None and (type(val) is not int or val < 0):
            raise ValueError("observed outcomes must be non-negative ints or None")

    survivors = []
    for h_idx in range(n):
        if all(
            obs_by_idx[p_idx] is None or not p.routed or p.outcomes[h_idx] == obs_by_idx[p_idx]
            for p_idx, p in enumerate(rows)
        ):
            survivors.append(h_idx)

    if not survivors:
        return NO_HYPOTHESIS_FITS
    if len(survivors) == 1:
        return survivors[0]
    return tuple(survivors)


def minimum_test_collection(probes: Iterable[Probe]) -> tuple[int, tuple[str, ...]] | None:
    """T1: Exact minimum-cost nonadaptive test collection separating every pair in `H`."""
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


# Backwards-compatible alias
minimum_batch = minimum_test_collection


def _union(values: Iterable[int]) -> int:
    r = 0
    for x in values:
        r |= x
    return r


def exhaustive_batch(probes: Iterable[Probe]) -> tuple[int, tuple[str, ...]] | None:
    """Independent exhaustive subsets, intentionally not using minimum_test_collection's DP."""
    rows, n = validate(probes)
    if len(rows) > 20:
        raise ValueError("exhaustive oracle supports <=20 probes")
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


def optimal_decision_tree_cost(probes: Iterable[Probe]) -> int | None:
    """T2: Optimal worst-case adaptive decision tree depth in cost units identifying all `H`."""
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


# Backwards-compatible alias
adaptive_worst_cost = optimal_decision_tree_cost


def fibre_floor(samples: Iterable[dict], features: tuple[str, ...]) -> dict:
    """T3: Exact minimum 0-1 errors for ANY deterministic predictor of discrete `features`.

    Rows sharing an identical feature tuple must receive one prediction. With raw
    continuous states, distinct trajectories occupy singleton fibres so the unbinned
    floor is zero and the state-matching tolerance decides the empirical result;
    an exact clock gap at a repeated state on a fixed-horizon loop measures
    remaining pass budget.
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


def refill_step(state: int, source_bit: int, cut: bool = False) -> int:
    """Explicit T4 state transition `s_{t+1} = 0` if `cut` else `refresh(s_t, x)` with `refresh(s, x) = s | x`."""
    if state not in (0, 1) or source_bit not in (0, 1) or type(cut) is not bool:
        raise ValueError("state and source_bit must be bits in {0, 1} and cut must be bool")
    refreshed = state | source_bit
    return 0 if cut else refreshed


def _rollout_refill(passes: int, source_bit: int, cut_mask: Sequence[bool], initial_state: int = 0) -> list[int]:
    state = initial_state
    trajectory: list[int] = []
    for t in range(passes):
        state = refill_step(state, source_bit, cut=cut_mask[t])
        trajectory.append(state)
    return trajectory


def refill_witness(passes: int = 4, source_bit: int = 1) -> dict:
    """T4: Explicit recurrent refill dynamics where early single-pass erasure is rebuilt on step `t + 1`."""
    if type(passes) is not int or passes < 2 or source_bit not in (0, 1):
        raise ValueError("requires >=2 passes and a bit-valued source")
    no_cuts = [False] * passes
    baseline = _rollout_refill(passes, source_bit, no_cuts, initial_state=0)
    single_final = []
    single_trajectories = []
    for cut_idx in range(passes):
        mask = [t == cut_idx for t in range(passes)]
        path = _rollout_refill(passes, source_bit, mask, initial_state=0)
        single_trajectories.append(path)
        single_final.append(path[-1])
    persistent_traj = _rollout_refill(passes, source_bit, [True] * passes, initial_state=0)
    return {
        "update_rule": "s_0 = 0; s_{t+1} = 0 if cut_t else (s_t | source_bit)",
        "baseline": baseline,
        "single_cut_final": single_final,
        "single_cut_trajectories": single_trajectories,
        "persistent_cut_trajectory": persistent_traj,
        "persistent_cut_final": persistent_traj[-1],
        "terminal_blind_early_cuts": sum(final == source_bit for final in single_final[:-1]),
    }


def fc12_cell_ledger(
    *,
    positives: int = 39,
    negatives: int = 0,
    untested: int = 165,
    goals: int = FC12_GOALS,
    families: int = len(FC12_FAMILIES),
) -> dict:
    """Explicit three-state (`positive`, `negative`, `untested`) accounting for FC-12 (`51 x 4 = 204`).

    In the unprobed FC-12 incidence graph, `39` verified positives plus `165` untested
    cells already sum to all `204` cells (`negatives == 0`). Separating hypotheses requires
    compiling non-winning candidates and recording kernel-rejected attempts as explicit
    `negative` cells rather than conflating `untested` with `negative`.
    """
    for val in (positives, negatives, untested, goals, families):
        if type(val) is not int or val < 0:
            raise ValueError("FC-12 ledger counts must be non-negative integers")
    if goals <= 0 or families <= 0:
        raise ValueError("goals and families must be positive integers")
    total = goals * families
    if positives + negatives + untested != total:
        raise ValueError(
            f"positive ({positives}) + negative ({negatives}) + untested ({untested}) != {total}"
        )
    return {
        "goals": goals,
        "families": families,
        "total_cells": total,
        "positive_cells": positives,
        "negative_cells": negatives,
        "untested_cells": untested,
        "has_recorded_negatives": negatives > 0,
        "probed_fraction": (positives + negatives) / total,
    }
