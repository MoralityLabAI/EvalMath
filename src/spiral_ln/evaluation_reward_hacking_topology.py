"""RHT-01: exact cohomological certificates for evaluation reward hacking.

Two separately observed evaluation category maps induce a bipartite
intersection graph I. Each edge is a nonempty intersection cell of capacity
s_e >= 1. The published feedback y=Mx consists of the two sets of category
margins. A protected gold utility U_t(x)=<t,x> is defined independently of
the reported proxy p(Mx).

The information hidden inside every feedback fibre is H_1(I;Q)=ker M.
Pairing the gold cochain t with alternating cycles gives an exact necessary
and sufficient condition for its identifiability from separate margins.
The minimum targeted cell-disclosure audit equals the edge-deletion distance
needed to make the gold cochain exact on the unobserved subgraph.

All finite optimizations are exact. Exponential oracles have explicit caps.
No model, judge, agent, or safety-relevant reward source is inferred.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from itertools import combinations, product

from spiral_ln.evaluation_leak_topology import (
    box, cycle_rank, fundamental_cycles, margin_matrix, margins_of,
    spanning_forest,
)


def _gold(graph, weights) -> tuple[Q, ...]:
    values = tuple(Q(w) for w in weights)
    if len(values) != len(graph["edges"]):
        raise ValueError("one independently justified true-reward weight per cell")
    if len(graph["sizes"]) != len(values) or any(s < 1 for s in graph["sizes"]):
        raise ValueError("positive capacities required")
    return values


def _ends(graph) -> tuple[tuple[int, int], ...]:
    shift = len(graph["rows"])
    return tuple((int(a), shift + int(b)) for a, b in graph["edges"])


def cycle_periods(graph, gold_weights) -> tuple[tuple[int, Q], ...]:
    """Full cohomology coordinates pairing the gold 1-cochain with H_1."""
    w = _gold(graph, gold_weights)
    return tuple((chord, sum((weight*cycle[e]
                              for e, weight in enumerate(w)), Q(0)))
                 for chord, cycle in fundamental_cycles(graph))


def vertex_potential(
    graph, gold_weights, audited_cells: tuple[int, ...] = ()
) -> tuple[Q, ...] | None:
    """Return psi with psi(column)-psi(row)=gold_e on all unaudited edges.

    The source bipartite cell graph may become disconnected after auditing.
    The root potential on each component is fixed to zero.
    """
    w = _gold(graph, gold_weights)
    audited = tuple(audited_cells)
    if len(set(audited)) != len(audited) or any(
        type(i) is not int or not 0 <= i < len(w) for i in audited
    ):
        raise ValueError("audited cells must be distinct valid edge indices")
    excluded = set(audited)
    ends = _ends(graph)
    n = len(graph["rows"]) + len(graph["columns"])
    adj: list[list[tuple[int, Q]]] = [[] for _ in range(n)]
    for e, (u, v) in enumerate(ends):
        if e in excluded:
            continue
        adj[u].append((v, w[e]))
        adj[v].append((u, -w[e]))
    potential: list[Q | None] = [None] * n
    for root in range(n):
        if potential[root] is not None:
            continue
        potential[root] = Q(0)
        queue = [root]
        for u in queue:
            for v, delta in adj[u]:
                predicted = Q(potential[u]) + delta
                if potential[v] is None:
                    potential[v] = predicted
                    queue.append(v)
                elif potential[v] != predicted:
                    return None
    return tuple(Q(x) for x in potential)


def exact_from_margins(graph, gold_weights) -> bool:
    """Equivalent to the gold cochain annihilating every hidden cycle."""
    return vertex_potential(graph, gold_weights) is not None


def cycle_alias_witness(graph, gold_weights):
    """Two integral cell tables with identical margins, distinct gold utility.

    When all periods vanish, return None. Otherwise use the positive and
    negative parts of a fundamental cycle, feasible since s_e>=1.
    """
    w = _gold(graph, gold_weights)
    for chord, z in fundamental_cycles(graph):
        period = sum((weight * v for weight, v in zip(w,z)), Q(0))
        if period == 0:
            continue
        left = tuple(max(0,v) for v in z)
        right = tuple(max(0,-v) for v in z)
        if any(max(x,y) > cap for x,y,cap in zip(left,right,graph["sizes"])):
            raise AssertionError("unit cycle witness must fit positive capacities")
        if margins_of(graph,left) != margins_of(graph,right):
            raise AssertionError("cycle alias must be in margin kernel")
        if sum((t*(x-y) for t,x,y in zip(w,left,right)),Q(0)) != period:
            raise AssertionError("gold discrepancy must equal the period")
        return {
            "chord": chord,
            "cycle": z,
            "first": left,
            "second": right,
            "published_margins": margins_of(graph,left),
            "true_difference": period,
        }
    return None


def _count_bounded(graph, budget: int) -> int:
    if type(budget) is not int or budget < 1:
        raise ValueError("enumeration cap must be positive")
    count = 1
    for s in graph["sizes"]:
        count *= s + 1
        if count > budget:
            raise ValueError("exponential enumeration exceeds declared capacity budget")
    return count


def hidden_gold_width(graph, gold_weights, *, max_states: int = 50000):
    """Maximum within-feedback-fibre gold span, with realized alias witnesses."""
    w = _gold(graph, gold_weights)
    _count_bounded(graph,max_states)
    minima: dict[tuple[int,...], tuple[Q, tuple[int,...]]] = {}
    maxima: dict[tuple[int,...], tuple[Q, tuple[int,...]]] = {}
    for x in box(graph["sizes"]):
        y = margins_of(graph,x)
        utility = sum((t*v for t,v in zip(w,x)), Q(0))
        if y not in minima or utility < minima[y][0]:
            minima[y] = (utility,x)
        if y not in maxima or utility > maxima[y][0]:
            maxima[y] = (utility,x)
    y = max(minima, key=lambda key: maxima[key][0]-minima[key][0])
    minimum,xlow = minima[y]
    maximum,xhigh = maxima[y]
    return {
        "maximum_width": maximum-minimum,
        "margins": y,
        "low_record": xlow,
        "high_record": xhigh,
        "minimum_true_utility": minimum,
        "maximum_true_utility": maximum,
        "feedback_fibres": len(minima),
    }


def circulation_oracle(graph, gold_weights, *, max_states: int = 200000):
    """Independent exact integer circulation maximization.

    Every integral z in ker M with -s_e<=z_e<=s_e corresponds to a pair
    x=z_+, y=z_- of feasible tables with the same margins. This oracle
    checks the topological formula for the maximum hidden gold width.
    """
    w = _gold(graph,gold_weights)
    count = 1
    for s in graph["sizes"]:
        count *= 2*s+1
        if count > max_states:
            raise ValueError("circulation enumeration exceeds budget")
    M = margin_matrix(graph)
    best = Q(-1)
    witness = None
    for z in product(*(range(-s,s+1) for s in graph["sizes"])):
        if any(sum(row[e]*z[e] for e in range(len(z))) != 0 for row in M):
            continue
        value = sum((v*t for v,t in zip(z,w)),Q(0))
        if value > best:
            best,witness = value,z
    return best,witness


def audit_reconstruction(graph, gold_weights, audited_cells):
    """Exact formula U(x)=lambda·Mx + sum_{e in S} residual_e*x_e."""
    w = _gold(graph, gold_weights)
    audited = tuple(audited_cells)
    potential = vertex_potential(graph,w,audited)
    if potential is None:
        return None
    row_count = len(graph["rows"])
    lam = tuple(-potential[i] if i < row_count else potential[i]
                for i in range(len(potential)))
    endpoints = _ends(graph)
    residuals = tuple(
        (e, w[e] - lam[endpoints[e][0]] - lam[endpoints[e][1]])
        for e in audited
    )
    for e,(u,v) in enumerate(endpoints):
        error=w[e]-lam[u]-lam[v]
        if e not in audited and error:
            raise AssertionError("audit formula fails on unobserved edge")
    return {"margin_coefficients":lam, "audited_residuals":residuals}


def reconstruct_gold(graph, counts, formula) -> Q:
    """Evaluate a previously constructed exact audit certificate."""
    if formula is None:
        raise ValueError("certificate unavailable")
    x=tuple(counts)
    if len(x)!=len(graph["sizes"]) or any(
        type(v) is not int or not 0<=v<=s for v,s in zip(x,graph["sizes"])
    ):
        raise ValueError("cell table must respect declared capacities")
    y=margins_of(graph,x)
    return (sum((coef*value for coef,value in
                 zip(formula["margin_coefficients"],y)),Q(0))
            +sum((residual*x[e]
                  for e,residual in formula["audited_residuals"]),Q(0)))


def minimum_gold_audit(graph,gold_weights,*,max_cells:int=12):
    """Smallest set of cell counts that makes protected gold identifiable.

    For known gold weights t, the unaudited subgraph must admit a
    potential representing t on every retained edge. This is the
    block-Hamming cosystolic deletion distance of t (over Q).
    """
    w=_gold(graph,gold_weights)
    m=len(w)
    if m>max_cells:
        raise ValueError("audit set enumeration exceeds explicit cap")
    for n in range(m+1):
        for S in combinations(range(m),n):
            formula=audit_reconstruction(graph,w,S)
            if formula is not None:
                return {"count":n,"audited_cells":S,"formula":formula,
                        "universal_upper_bound":cycle_rank(graph)}
    raise AssertionError("auditing every cell must identify the true score")


@dataclass(frozen=True)
class RewardHackingRegret:
    true_optimum: Q
    selected_proxy_score: Q
    worst_selected_true_utility: Q
    worst_true_regret: Q
    wrong_fibre_gap: Q
    hidden_fibre_gap: Q
    worst_selected_record: tuple[int,...]
    selected_feedback: tuple[int,...]
    feasible_candidates: int


def proxy_optimization_regret(
    graph,gold_weights,proxy_margin_weights,
    *,
    allowed_candidates=None,
    max_states:int=50000,
) -> RewardHackingRegret:
    """Worst tie-breaking regret after maximizing a proxy computed from Mx.

    The reachable candidate set is an explicit part of the eval game.
    If omitted, all feasible tables in the full capacity box are allowed.
    """
    w=_gold(graph,gold_weights)
    alpha=tuple(Q(v) for v in proxy_margin_weights)
    n=len(graph["rows"])+len(graph["columns"])
    if len(alpha)!=n:
        raise ValueError("one proxy weight per released category margin required")
    if allowed_candidates is None:
        _count_bounded(graph,max_states)
        X=tuple(box(graph["sizes"]))
    else:
        X=tuple(tuple(x) for x in allowed_candidates)
        if not X or len(X)>max_states or len(set(X))!=len(X):
            raise ValueError("candidate collection must be distinct, nonempty and capped")
        if any(len(x)!=len(w) or any(type(v)is not int or not 0<=v<=s
               for v,s in zip(x,graph["sizes"])) for x in X):
            raise ValueError("every reachable cell table must respect capacities")
    utilities={x:sum((v*t for v,t in zip(x,w)),Q(0)) for x in X}
    margins={x:margins_of(graph,x) for x in X}
    scores={x:sum((alpha_i*y_i for alpha_i,y_i in
                   zip(alpha,margins[x])),Q(0)) for x in X}
    best_proxy=max(scores.values())
    selected=[x for x in X if scores[x]==best_proxy]
    victim=min(selected,key=lambda x: utilities[x])
    y=margins[victim]
    same_fibre=[x for x in X if margins[x]==y]
    u_low=utilities[victim]
    u_high=max(utilities[x] for x in same_fibre)
    true_best=max(utilities.values())
    return RewardHackingRegret(
        true_optimum=true_best,
        selected_proxy_score=best_proxy,
        worst_selected_true_utility=u_low,
        worst_true_regret=true_best-u_low,
        wrong_fibre_gap=true_best-u_high,
        hidden_fibre_gap=u_high-u_low,
        worst_selected_record=victim,
        selected_feedback=y,
        feasible_candidates=len(X),
    )


def ugc_reachable_records(game, disclosure_graph, *, max_worlds:int=50000):
    """Map binary constraint satisfactions to evaluation cell counts.

    This uses the actual F2^s translation-game semantics from UGC-PT-01.
    The disclosure graph contains exactly one item for each game edge.
    An actor's reachable set is the set of joint records generated by
    assignments to the game vertices.
    """
    if len(game.edges)!=disclosure_graph["items"]:
        raise ValueError("evaluation item count must match UGC edge occurrences")
    if game.alphabet_size**game.vertices>max_worlds:
        raise ValueError("UGC world enumeration exceeds budget")
    candidates={}
    for labels in product(range(game.alphabet_size),repeat=game.vertices):
        bits="".join("1" if labels[e.v] == (labels[e.u]^e.shift)
                     else "0" for e in game.edges)
        x=tuple(sum(bits[i]=="1" for i in cells)
                for cells in disclosure_graph["cells"])
        candidates.setdefault(x,labels)
    return candidates
