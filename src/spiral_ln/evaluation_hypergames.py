"""HG-01: exact finite hypergame geometry and goal-identification oracles.

Tensor/Clifford matrices are represented implicitly. All evaluative quantities
are rational; no rollout or model inference is performed by this module.
"""
from __future__ import annotations

from fractions import Fraction as F
from itertools import combinations
from typing import Any, Mapping, Sequence

State = Mapping[str, F]
Actions = Mapping[str, State]


def rational(value: Any) -> F:
    """Convert a JSON finite decimal to an exact rational; reject nonnumeric values."""
    if type(value) is bool or not isinstance(value, (int, float, str, F)):
        raise ValueError("expected rational or finite JSON number")
    try:
        result = F(str(value))
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise ValueError("invalid rational") from exc
    return result


def _matching(left: State, right: State, weights: Mapping[str, F] | None = None) -> tuple[str, ...]:
    if not left or set(left) != set(right):
        raise ValueError("states must have identical nonempty feature domains")
    names = tuple(sorted(left))
    if weights is not None and set(weights) != set(names):
        raise ValueError("weight domain must equal state domain")
    for name in names:
        rational(left[name]); rational(right[name])
        if weights is not None and rational(weights[name]) <= 0:
            raise ValueError("every weight must be positive")
    return names


def dirac_distance_squared(left: State, right: State, weights: Mapping[str, F] | None = None) -> F:
    """Clifford-induced squared norm: ||D_w(x)-D_w(y)||_op^2, exactly.

    D_w(x) = sum_j w_j x_j Gamma_j with {Gamma_i,Gamma_j}=2 delta_ij I.
    Explicit gamma matrices are never allocated. Cost O(number of features).
    """
    names = _matching(left, right, weights)
    return sum((rational(weights[name]) if weights is not None else F(1))**2
               * (rational(left[name])-rational(right[name]))**2
               for name in names)


def categorical_overlap(left: Sequence[str], right: Sequence[str],
                        alpha: F = F(3, 5), beta: F = F(4, 5)) -> F:
    """Exact inner product for tensor factors alpha|common> + beta|value>.

    Unmatched categorical basis labels are orthogonal; dimension is implicit.
    All factors are normalized. Equal coordinates contribute 1; unequal alpha^2.
    """
    alpha, beta = rational(alpha), rational(beta)
    if alpha <= 0 or beta <= 0 or alpha**2 + beta**2 != 1:
        raise ValueError("positive normalized rational amplitudes required")
    if not left or len(left) != len(right) or any(type(v) is not str for v in (*left, *right)):
        raise ValueError("nonempty equally sized categorical coordinates required")
    overlap = F(1)
    for a, b in zip(left, right):
        if a != b:
            overlap *= alpha**2
    return overlap


def categorical_chord_squared(left: Sequence[str], right: Sequence[str],
                               alpha: F = F(3, 5), beta: F = F(4, 5)) -> F:
    """||phi(left)-phi(right)||^2 = 2-2<phi(left),phi(right)> (not geodesic)."""
    return 2 * (1 - categorical_overlap(left, right, alpha, beta))


def minimizers(actions: Actions, goal: State,
               weights: Mapping[str, F] | None = None) -> tuple[str, ...]:
    if not actions or any(type(a) is not str for a in actions):
        raise ValueError("nonempty action map with string names required")
    costs = {a: dirac_distance_squared(successor, goal, weights)
             for a, successor in actions.items()}
    best = min(costs.values())
    return tuple(sorted(a for a, val in costs.items() if val == best))


def regret(actions: Actions, chosen: str, goal: State,
           weights: Mapping[str, F] | None = None) -> F:
    """One-step deterministic inverse-planning regret relative to supplied successors."""
    if chosen not in actions:
        raise ValueError("chosen action must be in supplied legal counterfactuals")
    scores = {a: dirac_distance_squared(s, goal, weights) for a, s in actions.items()}
    return scores[chosen] - min(scores.values())


def infer_goals(decisions: Sequence[tuple[str, Actions]],
                goals: Mapping[str, State], weights: Mapping[str, F] | None = None) -> dict:
    """Exact consistency set; nonzero-regret hypotheses are rejected.

    The successors must come from a frozen agent-subjective transition oracle.
    A raw turn trace alone does not supply these missing counterfactuals.
    """
    if not decisions or not goals or any(not actions for _, actions in decisions):
        raise ValueError("at least one decision and one candidate goal required")
    sums = {g: sum((regret(actions, choice, target, weights)
                    for choice, actions in decisions), F(0))
            for g, target in goals.items()}
    compatible = tuple(sorted(g for g in sums if sums[g] == 0))
    status = ("identified" if len(compatible) == 1 else "ambiguous"
              if compatible else "no_hypothesis_fits")
    return {"status": status, "compatible": compatible,
            "regret": {g: str(sums[g]) for g in sorted(sums)}}


def hypergame_view_gap(chosen: str, goal: State, subjective: Actions,
                       objective: Actions, weights: Mapping[str, F] | None = None) -> dict:
    """Compare one agent's game model with an audited world transition model."""
    if set(subjective) != set(objective):
        raise ValueError("subjective and objective views require identical action menus")
    sub = regret(subjective, chosen, goal, weights)
    obj = regret(objective, chosen, goal, weights)
    return {"subjective_regret": str(sub), "objective_regret": str(obj),
            "subjectively_optimal": sub == 0, "objectively_optimal": obj == 0}


def minimum_robust_probe_cover(probes: Mapping[str, Actions], goals: Mapping[str, State],
                               costs: Mapping[str, int] | None = None,
                               weights: Mapping[str, F] | None = None) -> dict:
    """Minimum-cost fixed set of probes separating all goal pairs despite ties.

    Each probe predicts a *set* of optimal actions for each goal. A pair is
    robustly separated only if its two minimizer sets are disjoint.
    Exhaustive reference solver, limited to 16 probes.
    """
    if not goals or len(probes) > 16:
        raise ValueError("need goals and at most 16 probes for exhaustive oracle")
    if costs is not None and set(costs) != set(probes):
        raise ValueError("costs must cover exactly the probes")
    if costs is not None and any(type(c) is not int or c <= 0 for c in costs.values()):
        raise ValueError("probe costs must be strictly positive integers")
    names = tuple(sorted(goals))
    pairs = set(combinations(names, 2))
    separated: dict[str, set[tuple[str, str]]] = {}
    for p, actions in probes.items():
        predictions = {g: set(minimizers(actions, target, weights))
                       for g, target in goals.items()}
        separated[p] = {pair for pair in pairs if predictions[pair[0]].isdisjoint(predictions[pair[1]])}
    blockers = tuple(sorted(p for p in pairs if not any(p in s for s in separated.values())))
    if blockers:
        return {"feasible": False, "unseparated_pairs": blockers,
                "min_cost": None, "probes": ()}
    best: tuple[int, tuple[str, ...]] | None = None
    ids = tuple(sorted(probes))
    for size in range(len(ids) + 1):
        for subset in combinations(ids, size):
            cost = sum(costs[p] if costs is not None else 1 for p in subset)
            if best is not None and cost > best[0]:
                continue
            covered = set().union(*(separated[p] for p in subset)) if subset else set()
            if covered == pairs and (best is None or (cost, subset) < best):
                best = (cost, subset)
    assert best is not None
    return {"feasible": True, "unseparated_pairs": (),
            "min_cost": best[0], "probes": best[1]}


def projection_margin_certificate(actions: Actions, goal: State,
                                  keep: Sequence[str],
                                  weights: Mapping[str, F] | None = None) -> dict:
    """Sufficient stability criterion under omission of weighted coordinates.

    If the unique full-space winner gap exceeds the range of the omitted
    energies across actions, every projected action ranking retains that winner.
    """
    if not actions:
        raise ValueError("nonempty actions required")
    names = _matching(next(iter(actions.values())), goal, weights)
    chosen_keep = set(keep)
    if not chosen_keep or not chosen_keep <= set(names):
        raise ValueError("projection must retain named coordinates")
    if len(chosen_keep) == len(names):
        omitted_range = F(0)
    costs = {a: dirac_distance_squared(s, goal, weights) for a, s in actions.items()}
    sorted_costs = sorted(costs.items(), key=lambda t: (t[1], t[0]))
    winner = sorted_costs[0][0]
    gap = (sorted_costs[1][1] - sorted_costs[0][1]) if len(sorted_costs) >= 2 else F(0)
    removed = {a: sum((rational(weights[j]) if weights else F(1))**2
                      * (rational(s[j]) - rational(goal[j]))**2
                      for j in names if j not in chosen_keep)
               for a, s in actions.items()}
    omitted_range = max(removed.values()) - min(removed.values())
    projected = {a: c - removed[a] for a, c in costs.items()}
    projected_min = min(projected.values())
    return {"winner": winner, "full_gap": str(gap),
            "omitted_energy_range": str(omitted_range),
            "certified_stable": len(actions) == 1 or gap > omitted_range,
            "projected_minimizers": tuple(sorted(a for a in actions if projected[a] == projected_min))}


def diplomacy_v2_visible_numeric(row: Mapping[str, Any],
                                 world_var_allowlist: Sequence[str] = ()) -> dict[str, F]:
    """Audit-safe projection of GPTStoryworld v2 pre-decision visible state.

    Hidden state, realized outcomes, after-beliefs, and reasoning text are
    intentionally inaccessible. World variables require explicit allowlisting.
    """
    state = row.get("visible_state")
    if not isinstance(state, dict) or not isinstance(state.get("beliefs"), dict):
        raise ValueError("expected storyworld v2 visible_state with beliefs")
    beliefs = state["beliefs"]
    result: dict[str, F] = {}
    ids = sorted(beliefs)
    for observer in ids:
        b = beliefs[observer]
        if not isinstance(b, dict) or not isinstance(b.get("trust"), dict):
            raise ValueError("malformed trust matrix")
        for target in ids:
            if target not in b["trust"]:
                raise ValueError("incomplete trust matrix")
            result[f"trust.{observer}.{target}"] = rational(b["trust"][target])
        if "expected_payoff" in b:
            result[f"payoff.{observer}"] = rational(b["expected_payoff"])
    coalitions = state.get("coalitions", [])
    if not isinstance(coalitions, list):
        raise ValueError("malformed coalitions")
    groups = [set(c["members"]) for c in coalitions]
    for a, b in combinations(ids, 2):
        result[f"coalition.{a}.{b}"] = F(int(any(a in members and b in members for members in groups)))
    vars_ = state.get("world_vars", {})
    if not isinstance(vars_, dict):
        raise ValueError("malformed world_vars")
    for key in world_var_allowlist:
        if key not in vars_:
            raise ValueError("missing allowlisted world variable")
        result[f"world.{key}"] = rational(vars_[key])
    return result


def observer_nested_beliefs(snapshot: Mapping[str, Any], observer: str) -> dict[str, F]:
    """Extract only observer-owned pValue/p2Value cells, preserving full keyrings.

    Expected source form is GPTStoryworld's pp2_snapshot with p[observer]
    and p2[observer]. Other agents' private belief maps are excluded.
    This is a typed adapter, not a claim that a trace actually exposes p2.
    """
    p = snapshot.get("p", {})
    p2 = snapshot.get("p2", {})
    if not isinstance(p, dict) or not isinstance(p2, dict) or observer not in p:
        raise ValueError("observer's first-order beliefs unavailable")
    result: dict[str, F] = {}
    own = p[observer]
    if not isinstance(own, dict):
        raise ValueError("malformed first-order belief map")
    for target, traits in own.items():
        if not isinstance(traits, dict):
            raise ValueError("malformed first-order trait map")
        for trait, value in traits.items():
            result[f"p.{target}.{trait}"] = rational(value)
    second = p2.get(observer, {})
    if not isinstance(second, dict):
        raise ValueError("malformed second-order belief map")
    for mediator, third_map in second.items():
        if not isinstance(third_map, dict):
            raise ValueError("malformed second-order mediator map")
        for target, traits in third_map.items():
            if not isinstance(traits, dict):
                raise ValueError("malformed second-order trait map")
            for trait, value in traits.items():
                result[f"p2.{mediator}.{target}.{trait}"] = rational(value)
    return result


def exact_row_rank(matrix: Sequence[Sequence[F]]) -> int:
    """Gauss elimination over Q, including empty matrices and dependent rows."""
    if not matrix:
        return 0
    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise ValueError("ragged matrix")
    a = [[rational(v) for v in row] for row in matrix]
    pivot_row = 0
    for column in range(width):
        pivot = next((r for r in range(pivot_row, len(a)) if a[r][column] != 0), None)
        if pivot is None:
            continue
        a[pivot_row], a[pivot] = a[pivot], a[pivot_row]
        scale = a[pivot_row][column]
        a[pivot_row] = [v / scale for v in a[pivot_row]]
        for r in range(len(a)):
            if r != pivot_row and a[r][column]:
                multiple = a[r][column]
                a[r] = [v - multiple * z for v, z in zip(a[r], a[pivot_row])]
        pivot_row += 1
        if pivot_row == len(a):
            break
    return pivot_row


def inverse_voronoi_halfspaces(decisions: Sequence[tuple[str, Actions]],
                               weights: Mapping[str, F] | None = None) -> dict:
    """Each chosen c over alternative a imposes 2<W²(a-c),g> <= ||Wa||²-||Wc||².

    Coefficients are exact. A rank-r comparison system has a (d-r)-dimensional
    linear blind subspace, whether the overall inequalities are feasible or not.
    """
    if not decisions:
        raise ValueError("at least one decision required")
    first_actions = decisions[0][1]
    if not first_actions:
        raise ValueError("empty action map")
    names = tuple(sorted(next(iter(first_actions.values()))))
    if not names:
        raise ValueError("empty feature domain")
    dummy = {name: F(0) for name in names}
    constraints = []
    for chosen, actions in decisions:
        if chosen not in actions:
            raise ValueError("chosen action not supplied")
        c = actions[chosen]
        _matching(c, dummy, weights)
        for alt, a in actions.items():
            _matching(a, dummy, weights)
            if alt == chosen:
                continue
            coeff = tuple(2 * (rational(weights[j]) if weights else F(1))**2
                          * (rational(a[j]) - rational(c[j])) for j in names)
            bound = sum(((rational(weights[j]) if weights else F(1))**2
                        * (rational(a[j])**2 - rational(c[j])**2) for j in names), F(0))
            constraints.append({"chosen": chosen, "alternative": alt,
                                "coefficients": coeff, "upper": bound})
    rank = exact_row_rank([c["coefficients"] for c in constraints])
    return {"features": names, "constraints": tuple(constraints),
            "comparison_rank": rank, "blind_linear_dimensions": len(names) - rank}


def halfspaces_accept(halfspaces: dict, goal: State) -> bool:
    """Direct exact evaluation of an inverse Voronoi goal-region certificate."""
    names = halfspaces["features"]
    if set(goal) != set(names):
        raise ValueError("candidate goal has wrong feature domain")
    return all(sum((coeff * rational(goal[j]) for j, coeff in zip(names, constraint["coefficients"])), F(0))
               <= constraint["upper"] for constraint in halfspaces["constraints"])
