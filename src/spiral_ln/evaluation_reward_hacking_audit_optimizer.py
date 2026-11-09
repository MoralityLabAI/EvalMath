"""RHT-07: exact lazy private-gold audit optimization on multiway signals.

Unsafe feedback aliases are integral differences z with Mz=0 and bounded
coordinates; a private cell audit eliminates z iff it intersects supp(z).
Selecting a minimum-cost audit is therefore an exact weighted hitting set of
ALL dangerous witness supports. The algorithm solves a sequence of smaller
hitting sets, asking an exact separation oracle for any residual witness.

The unrestricted separator is a memoized finite integer-margin DP. Its cost
is governed by the number of *reachable margin states* and capacity ranges,
with an explicit resource cap. A rank-one rational kernel admits a closed
integer result using a primitive generator. The reachable separator instead
groups the frozen actor's explicit records by public and audited observations.

No audit design here discovers or validates an actual human value function.
The certified gold cochain and reachable policy roster are external premises.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache
from math import floor

from spiral_ln.evaluation_reward_hacking_multimap import (
    MultiMapSignals, primitive_integer_kernel_generators,
)


@dataclass(frozen=True)
class HiddenRewardWitness:
    maximum_width: Q
    difference: tuple[int, ...]
    high_record: tuple[int, ...]
    low_record: tuple[int, ...]
    method: str
    visited_states: int


@dataclass(frozen=True)
class PrivateAuditCertificate:
    audited_cells: tuple[int, ...]
    cost: Q
    count: int
    remaining_gold_width: Q
    tolerance: Q
    witnessed_obstructions: tuple[tuple[int, ...], ...]
    rounds: int
    separation_states: int
    hitting_search_nodes: int
    source_scope: str


def _gold(space: MultiMapSignals, weights) -> tuple[Q, ...]:
    t=tuple(Q(v) for v in weights)
    if len(t)!=len(space.cells):
        raise ValueError("one independently licensed gold weight per joint cell")
    return t


def _audits(space: MultiMapSignals, audited) -> tuple[int, ...]:
    S=tuple(audited)
    if (len(S)!=len(set(S)) or any(
        type(i) is not int or not 0<=i<len(space.cells) for i in S
    )):
        raise ValueError("private audit cells must be distinct valid indices")
    return tuple(sorted(S))


def _witness(width, z, method, states) -> HiddenRewardWitness:
    z=tuple(z)
    return HiddenRewardWitness(
        maximum_width=Q(width), difference=z,
        high_record=tuple(max(0,x) for x in z),
        low_record=tuple(max(0,-x) for x in z),
        method=method, visited_states=states,
    )


def maximum_hidden_gold_dp(
    space: MultiMapSignals, gold_weights, *,
    audited_cells=(), max_states:int=200000,
) -> HiddenRewardWitness:
    """Exact bounded integer kernel maximization, with an explicit state cap.

    For rank one, every integer vector in the rational kernel is a multiple
    of its primitive integer generator. This gives an O(m) closed solution.
    For higher rank, exact rational DP tracks partial Mz margins.
    """
    t=_gold(space,gold_weights)
    S=frozenset(_audits(space,audited_cells))
    m=len(t)
    if type(max_states)is not int or max_states<1:
        raise ValueError("max_states must be positive")
    if space.rational_nullity==0:
        return _witness(0,(0,)*m,"zero-rank",1)
    if space.rational_nullity==1:
        (g,)=primitive_integer_kernel_generators(space)
        nonzero=[i for i,x in enumerate(g) if x]
        if not nonzero:
            raise AssertionError("rank-one primitive generator must be nonzero")
        multiplier=min(space.capacities[i]//abs(g[i]) for i in nonzero)
        if S.intersection(nonzero):
            multiplier=0
        period=sum((w*v for w,v in zip(t,g)),Q(0))
        direction=1 if period>=0 else -1
        z=tuple(multiplier*direction*v for v in g)
        result=_witness(multiplier*abs(period),z,"primitive-rank-one",1)
        if any(space.feedback(z)):
            raise AssertionError("rank-one witness must preserve margins")
        return result

    M=space.matrix
    row_count=len(M)
    col=tuple(tuple(row[j] for row in M) for j in range(m))
    capacities=tuple(0 if j in S else s
                     for j,s in enumerate(space.capacities))
    remaining=[[0]*row_count for _ in range(m+1)]
    for j in range(m-1,-1,-1):
        for i in range(row_count):
            remaining[j][i]=remaining[j+1][i]+abs(col[j][i])*capacities[j]
    zero=(0,)*row_count
    visited=0

    @lru_cache(maxsize=None)
    def solve(index:int, margins:tuple[int,...]):
        nonlocal visited
        visited+=1
        if visited>max_states:
            raise ValueError("integer-margin DP exceeded registered state budget")
        if index==m:
            return (Q(0),()) if margins==zero else None
        best=None
        for z in range(-capacities[index],capacities[index]+1):
            nxt=tuple(v+a*z for v,a in zip(margins,col[index]))
            if any(abs(v)>bound for v,bound in
                   zip(nxt,remaining[index+1])):
                continue
            future=solve(index+1,nxt)
            if future is None:
                continue
            score=t[index]*z+future[0]
            if best is None or score>best[0]:
                best=(score,(z,)+future[1])
        return best

    result=solve(0,zero)
    if result is None:
        raise AssertionError("zero integer difference is always feasible")
    value,z=result
    if value<0 or any(space.feedback(z)):
        raise AssertionError("integer margin DP produced invalid optimum")
    if any(abs(v)>space.capacities[i] for i,v in enumerate(z)):
        raise AssertionError("integer margin DP breached capacity")
    return _witness(value,z,"exact-margin-dp",visited)


def maximum_reachable_gold(
    space: MultiMapSignals, gold_weights, reachable_records, *,
    audited_cells=(), max_records:int=5000,
) -> HiddenRewardWitness:
    """Exact best pair of actor-reachable, identical visible/audit records."""
    t=_gold(space,gold_weights)
    S=_audits(space,audited_cells)
    X=tuple(tuple(x) for x in reachable_records)
    if (not X or len(set(X))!=len(X) or len(X)>max_records
        or type(max_records)is not int or max_records<1):
        raise ValueError("frozen reachable record roster must be distinct and bounded")
    if any(len(x)!=len(t) or any(
        type(v)is not int or not 0<=v<=s
        for v,s in zip(x,space.capacities)) for x in X):
        raise ValueError("reachable records must be within integer capacities")
    lows={}
    highs={}
    for x in X:
        key=(space.feedback(x),tuple(x[i] for i in S))
        value=sum((a*b for a,b in zip(t,x)),Q(0))
        if key not in lows or value<lows[key][0]:
            lows[key]=(value,x)
        if key not in highs or value>highs[key][0]:
            highs[key]=(value,x)
    key=max(lows,key=lambda k:highs[k][0]-lows[k][0])
    hi,lo=highs[key][1],lows[key][1]
    difference=tuple(a-b for a,b in zip(hi,lo))
    return HiddenRewardWitness(
        maximum_width=highs[key][0]-lows[key][0],
        difference=difference, high_record=hi, low_record=lo,
        method="frozen-reachable-roster",visited_states=len(X)
    )


def _minimum_hitting_set(
    clauses:tuple[int,...], costs:tuple[Q,...], *, max_nodes:int=200000
):
    """Exact weighted minimum hitting set over positive obstruction masks.

    Ties prefer fewer cells, then lexicographically smaller index tuples.
    Clause inclusion reductions preserve the hitting-set family.
    """
    m=len(costs)
    if not clauses:
        return (),0
    if any(c==0 or c >> m for c in clauses):
        raise ValueError("nonempty masks restricted to declared cells required")
    # A subset clause dominates its supersets.
    all_masks=tuple(sorted(set(clauses),key=lambda c:(c.bit_count(),c)))
    active=[]
    for mask in all_masks:
        if not any(existing & mask==existing for existing in active):
            active.append(mask)
    best_mask=(1<<m)-1
    best_key=(sum(costs,Q(0)),m,tuple(range(m)))
    visited=set()
    nodes=0

    def recurse(mask:int, paid:Q):
        nonlocal best_mask,best_key,nodes
        if mask in visited:
            return
        visited.add(mask)
        nodes+=1
        if nodes>max_nodes:
            raise ValueError("weighted hitting-set search exceeded node budget")
        if paid>best_key[0]:
            return
        unhit=[c for c in active if not (c&mask)]
        if not unhit:
            items=tuple(j for j in range(m) if mask>>j&1)
            key=(paid,len(items),items)
            if key<best_key:
                best_key,best_mask=key,mask
            return
        clause=min(unhit,key=lambda c:(c.bit_count(),c))
        vertices=[j for j in range(m) if clause>>j&1]
        for j in sorted(vertices,key=lambda v:(costs[v],v)):
            recurse(mask|(1<<j),paid+costs[j])

    recurse(0,Q(0))
    answer=tuple(i for i in range(m) if best_mask>>i&1)
    return answer,nodes


def minimum_private_gold_audit_lazy(
    space:MultiMapSignals, gold_weights, *,
    tolerance=Q(0),cell_costs=None,
    reachable_records=None, max_states:int=200000,
    max_rounds:int=200, max_hitting_nodes:int=200000,
    max_reachable_records:int=5000,
) -> PrivateAuditCertificate:
    """Exact optimal weighted private audit with a lazy dangerous-witness oracle.

    On each iteration: optimize hidden gold after the chosen audit set. If
    the gap is too large, the witness's nonzero support is a newly violated
    hitting-set constraint. Optimize the resulting finite hitting set exactly.
    A final nonviolating separator proves feasibility and optimality jointly.
    """
    t=_gold(space,gold_weights)
    eps=Q(tolerance)
    m=len(t)
    if eps<0:
        raise ValueError("gold gap tolerance must be nonnegative")
    costs=(Q(1),)*m if cell_costs is None else tuple(Q(v) for v in cell_costs)
    if len(costs)!=m or any(c<=0 for c in costs):
        raise ValueError("one strictly positive private audit cost per joint cell required")
    if any(type(v)is not int or v<1 for v in (max_rounds,max_hitting_nodes)):
        raise ValueError("positive search budget required")
    X=None if reachable_records is None else tuple(tuple(x) for x in reachable_records)
    S=()
    clauses=[]
    supports=[]
    separation_states=0
    hit_nodes=0
    for step in range(max_rounds):
        witness=(maximum_hidden_gold_dp(space,t,audited_cells=S,max_states=max_states)
                 if X is None else
                 maximum_reachable_gold(space,t,X,audited_cells=S,
                     max_records=max_reachable_records))
        separation_states+=witness.visited_states
        if witness.maximum_width<=eps:
            return PrivateAuditCertificate(
                audited_cells=S,
                cost=sum((costs[i] for i in S),Q(0)),
                count=len(S),
                remaining_gold_width=witness.maximum_width,
                tolerance=eps,
                witnessed_obstructions=tuple(supports),
                rounds=step+1,separation_states=separation_states,
                hitting_search_nodes=hit_nodes,
                source_scope="capacity-box" if X is None else "frozen-reachable-roster"
            )
        indices=tuple(i for i,x in enumerate(witness.difference) if x)
        if not indices or any(i in S for i in indices):
            raise AssertionError("dangerous alias must differ outside audited cells")
        clause=sum(1<<i for i in indices)
        if clause in clauses:
            raise AssertionError("hitting-set improvement must cut each known alias")
        clauses.append(clause)
        supports.append(indices)
        S,nodes=_minimum_hitting_set(
            tuple(clauses),costs,max_nodes=max_hitting_nodes
        )
        hit_nodes+=nodes
    raise ValueError("lazy separation rounds exceeded registered budget")
