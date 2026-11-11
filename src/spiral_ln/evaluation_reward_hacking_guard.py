"""RHT-03: protected audit selection and a finite reward-hacking safety gate.

The gold signal is an externally justified independent function or belongs
to a frozen finite uncertainty set. The learner sees only a proxy score
derived from category margins Mx. Any added cell-count audits are held
privately by an independent verifier and never fed back to the learner.

An epsilon-audit bounds the largest change in gold reward hidden by the
combined observation (Mx, x_S). A robust selection gate releases only a
reachable controller whose regret is <= epsilon for EVERY registered
candidate gold signal. It can abstain and explicitly reports failure of
a declared nonzero utility/competence floor.

These are exact conditional guarantees; no procedure can infer that the
registered gold set includes the true human value model from proxy data.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from itertools import combinations

from spiral_ln.evaluation_leak_topology import box, margins_of
from spiral_ln.evaluation_reward_hacking_topology import (
    _gold, _count_bounded, minimum_gold_audit,
)


def augmented_feedback_width(
    graph, gold_weights, audited_cells: tuple[int,...],
    *, max_states:int=50000
) -> Q:
    """Largest true-score difference in the same privately audited fibre."""
    t=_gold(graph,gold_weights)
    S=tuple(audited_cells)
    if len(set(S))!=len(S) or any(
        type(e) is not int or not 0<=e<len(t) for e in S
    ):
        raise ValueError("audited cells must be distinct valid indices")
    _count_bounded(graph,max_states)
    spans: dict[tuple,tuple[Q,Q]]={}
    for x in box(graph["sizes"]):
        key=(margins_of(graph,x),tuple(x[e] for e in S))
        true=sum((w*v for w,v in zip(t,x)),Q(0))
        if key in spans:
            lo,hi=spans[key]
            spans[key]=(min(lo,true),max(hi,true))
        else:
            spans[key]=(true,true)
    return max((hi-lo for lo,hi in spans.values()),default=Q(0))


def minimal_epsilon_gold_audit(
    graph, gold_weights, epsilon: Q, *,
    max_cells:int=12, max_states:int=50000
):
    """Fewest private cell-count reads to make all fibre gold widths <=eps."""
    t=_gold(graph,gold_weights)
    eps=Q(epsilon)
    if eps<0:
        raise ValueError("tolerated gold ambiguity must be nonnegative")
    if len(t)>max_cells:
        raise ValueError("audit enumeration exceeds declared cell cap")
    for size in range(len(t)+1):
        for S in combinations(range(len(t)),size):
            width=augmented_feedback_width(graph,t,S,max_states=max_states)
            if width<=eps:
                return {"count":size,"audited_cells":S,
                        "remaining_gold_width":width,"epsilon":eps}
    raise AssertionError("full private audit must identify gold")


@dataclass(frozen=True)
class RobustRewardGuard:
    selected_record: tuple[int,...] | None
    selected_proxy_score: Q | None
    worst_case_regret: Q | None
    minimum_gold_level: Q | None
    safe_candidate_count: int
    original_candidate_count: int
    passed: bool


def robust_proxy_guard(
    graph,
    reachable_candidates,
    proxy_margin_weights,
    plausible_gold_weights,
    *,
    max_regret:Q,
    minimum_gold:Q,
    max_states:int=50000,
) -> RobustRewardGuard:
    """Pick highest proxy among candidates with a stated gold-regret bound.

    RobustRegret(x) = max_{t in T}[max_{y in X} t·y - t·x].
    The gold set T is frozen independently of the proxy learner. The bound
    holds only if the unknown actual gold t belongs to T. The utility floor
    is a *worst-case* gold-level constraint, excluding inert abstention.
    """
    X=tuple(tuple(x) for x in reachable_candidates)
    if not X or len(X)>max_states or len(set(X))!=len(X):
        raise ValueError("frozen reachable roster must be distinct, nonempty and capped")
    weights=tuple(_gold(graph,t) for t in plausible_gold_weights)
    if not weights:
        raise ValueError("a nonempty independently licensed gold set is required")
    if any(len(x)!=len(graph["sizes"]) or any(
        type(v) is not int or not 0<=v<=s
        for v,s in zip(x,graph["sizes"])) for x in X):
        raise ValueError("reachable records outside declared capacities")
    proxy=tuple(Q(v) for v in proxy_margin_weights)
    if len(proxy)!=len(graph["rows"])+len(graph["columns"]):
        raise ValueError("one coefficient per published feedback margin")
    epsilon=Q(max_regret)
    floor=Q(minimum_gold)
    if epsilon<0:
        raise ValueError("nonnegative regret bound required")
    def true(t,x):
        return sum((v*w for v,w in zip(t,x)),Q(0))
    optimums=tuple(max(true(t,x) for x in X) for t in weights)
    safe=[]
    for x in X:
        risk=max(opt-true(t,x) for t,opt in zip(weights,optimums))
        guaranteed=min(true(t,x) for t in weights)
        if risk<=epsilon and guaranteed>=floor:
            score=sum((p*y for p,y in zip(proxy,margins_of(graph,x))),Q(0))
            safe.append((score,x,risk,guaranteed))
    if not safe:
        return RobustRewardGuard(None,None,None,None,0,len(X),False)
    # Deterministic tie-breaking; no random or post hoc oracle.
    best=max(safe,key=lambda v:(v[0],tuple(-x for x in v[1])))
    return RobustRewardGuard(
        selected_record=best[1],selected_proxy_score=best[0],
        worst_case_regret=best[2],minimum_gold_level=best[3],
        safe_candidate_count=len(safe),original_candidate_count=len(X),
        passed=True,
    )
