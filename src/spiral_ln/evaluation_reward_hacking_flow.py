"""RHT-05: exact maximum-cost circulation solver for hidden reward width.

For two separately disclosed category maps, the feedback kernel is the
cycle space of their bipartite intersection graph I. Gold-score variation
within an evaluation feedback fibre has the exact dual characterization

  W(t,I,s) = max {t·z: D z=0, -s_e<=z_e<=s_e, z_e integer}.

This module solves the bounded circulation by building two opposing arcs of
capacity s_e for each category cell e, with costs -t_e and +t_e, then
canceling negative residual cycles with exact rational arithmetic.

Negative-cycle cancellation is finite and exact for the declared integral
capacity problem. This particular implementation is not claimed strongly
polynomial; its optional augmentation cap prevents unbounded work in
research runners. The min-cost circulation problem itself has classical
polynomial-time algorithms. No gold reward is inferred from proxy signals.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q

from spiral_ln.evaluation_reward_hacking_topology import _gold
from spiral_ln.evaluation_leak_topology import margins_of


@dataclass
class _Arc:
    target: int
    reverse: int
    capacity: int
    cost: Q


@dataclass(frozen=True)
class FlowRewardCertificate:
    maximum_hidden_width: Q
    integer_circulation: tuple[int, ...]
    high_record: tuple[int, ...]
    low_record: tuple[int, ...]
    cancelled_negative_cycles: int
    audited_cells: tuple[int, ...]


def maximum_hidden_width_flow(
    graph,
    gold_weights,
    *,
    audited_cells: tuple[int, ...] = (),
    max_augmentations: int = 100000,
) -> FlowRewardCertificate:
    """Exact maximum within-privileged-feedback gold ambiguity via circulation.

    If audited_cells=S, the auditor also privately sees x_e for each e in S;
    a hidden difference must have z_e=0 on every audited edge. The graph
    has positive integer cell capacities as in evaluation_leak_topology.
    """
    w = _gold(graph, gold_weights)
    sizes = tuple(graph["sizes"])
    S = tuple(audited_cells)
    if (len(set(S)) != len(S) or any(type(i) is not int or
            not 0 <= i < len(w) for i in S)):
        raise ValueError("audited cells must be distinct valid edge indices")
    if type(max_augmentations) is not int or max_augmentations < 1:
        raise ValueError("positive augmentation budget required")
    excluded = set(S)
    nrows = len(graph["rows"])
    nverts = nrows + len(graph["columns"])
    residual: list[list[_Arc]] = [[] for _ in range(nverts)]

    def add_arc(u: int, v: int, capacity: int, cost: Q) -> tuple[int,int]:
        fwd = len(residual[u])
        rev = len(residual[v])
        if u == v:
            raise ValueError("cell intersection graph must be bipartite")
        residual[u].append(_Arc(v, rev, capacity, cost))
        residual[v].append(_Arc(u, fwd, 0, -cost))
        return u,fwd

    original: list[tuple[tuple[int,int] | None,
                         tuple[int,int] | None]] = []
    for e, (row,col) in enumerate(graph["edges"]):
        if e in excluded:
            original.append((None,None))
            continue
        u,v=int(row),nrows+int(col)
        plus=add_arc(u,v,sizes[e],-w[e])
        minus=add_arc(v,u,sizes[e],w[e])
        original.append((plus,minus))

    def find_negative_cycle() -> tuple[tuple[int,int], ...] | None:
        dist=[Q(0)]*nverts
        pred: list[tuple[int,int] | None]=[None]*nverts
        changed=None
        for _ in range(nverts):
            changed=None
            for u in range(nverts):
                for i,arc in enumerate(residual[u]):
                    if arc.capacity > 0 and dist[u]+arc.cost < dist[arc.target]:
                        dist[arc.target]=dist[u]+arc.cost
                        pred[arc.target]=(u,i)
                        changed=arc.target
            if changed is None:
                return None
        if changed is None:
            return None
        vertex=changed
        for _ in range(nverts):
            if pred[vertex] is None:
                raise AssertionError("negative-cycle predecessor unexpectedly absent")
            vertex=pred[vertex][0]
        start=vertex
        cycle=[]
        while True:
            prior=pred[vertex]
            if prior is None:
                raise AssertionError("incomplete negative cycle")
            cycle.append(prior)
            vertex=prior[0]
            if vertex==start:
                break
            if len(cycle)>nverts:
                raise AssertionError("cycle extractor exceeded vertex count")
        if sum((residual[u][i].cost for u,i in cycle),Q(0)) >= 0:
            raise AssertionError("recovered residual cycle must have negative cost")
        return tuple(cycle)

    augmentations=0
    while True:
        cycle=find_negative_cycle()
        if cycle is None:
            break
        if augmentations >= max_augmentations:
            raise ValueError("negative-cycle augmentation budget exceeded")
        units=min(residual[u][i].capacity for u,i in cycle)
        if units < 1:
            raise AssertionError("negative cycle must have positive capacity")
        for u,i in cycle:
            arc=residual[u][i]
            arc.capacity-=units
            residual[arc.target][arc.reverse].capacity+=units
        augmentations+=1

    z=[]
    for e,(plus,minus) in enumerate(original):
        if e in excluded:
            z.append(0)
            continue
        if plus is None or minus is None:
            raise AssertionError("missing original arc")
        u,i=plus
        v,j=minus
        net=(sizes[e]-residual[u][i].capacity
             -(sizes[e]-residual[v][j].capacity))
        if not -sizes[e] <= net <= sizes[e]:
            raise AssertionError("reconstructed circulation exceeds edge capacity")
        z.append(net)
    z=tuple(z)
    if any(value != 0 for value in margins_of(graph,z)):
        raise AssertionError("flow conservation failed in original cell coordinates")
    width=sum((weight*value for weight,value in zip(w,z)),Q(0))
    if width < 0:
        raise AssertionError("zero flow is feasible and must beat negative width")
    hi=tuple(max(value,0) for value in z)
    lo=tuple(max(-value,0) for value in z)
    if any(hi[i]!=lo[i] for i in S):
        raise AssertionError("private audit cells must have no hidden variation")
    if margins_of(graph,hi)!=margins_of(graph,lo):
        raise AssertionError("flow witness must preserve published margins")
    return FlowRewardCertificate(
        maximum_hidden_width=width,
        integer_circulation=z,
        high_record=hi,
        low_record=lo,
        cancelled_negative_cycles=augmentations,
        audited_cells=S,
    )
