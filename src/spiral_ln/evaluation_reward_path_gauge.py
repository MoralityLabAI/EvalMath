"""RHT-02: boundary-relative reward shaping on an explicitly registered game.

For finite *undiscounted* paths of the same initial vertex to a terminal
set T, a proxy-minus-gold edge cochain whose graph potential is constant on
T adds a common path offset. Rankings and argmax policies are unchanged.

The statement is for paths/walks over the registered edge graph. It does
not silently transfer to discounted MDPs: there the correct potential term
is gamma*Phi(next)-Phi(current), and terminal conventions matter.

A non-exact difference yields a nonzero closed-walk period. A positive
proxy loop with nonpositive true return is a repeatable hacking witness
when the game permits that loop. A difference can be exact while still
misranking different terminal outcomes due to a boundary potential.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q


@dataclass(frozen=True)
class RewardTransition:
    source: int
    target: int
    true_reward: Q
    proxy_reward: Q


@dataclass(frozen=True)
class RewardPathGame:
    vertices: int
    start: int
    terminals: tuple[int, ...]
    edges: tuple[RewardTransition, ...]

    def __post_init__(self):
        if (type(self.vertices) is not int or self.vertices < 1
            or not 0 <= self.start < self.vertices
            or not self.terminals
            or len(set(self.terminals)) != len(self.terminals)
            or any(not 0 <= v < self.vertices for v in self.terminals)):
            raise ValueError("valid vertices, start and terminal set required")
        for e in self.edges:
            if not 0 <= e.source < self.vertices or not 0 <= e.target < self.vertices:
                raise ValueError("edge endpoints outside game")
            Q(e.true_reward)
            Q(e.proxy_reward)


def potential_if_exact(game: RewardPathGame) -> tuple[Q, ...] | None:
    """BFS-integrate proxy-minus-gold as an undirected graph 1-cochain."""
    adj: list[list[tuple[int,Q]]] = [[] for _ in range(game.vertices)]
    for e in game.edges:
        delta=Q(e.proxy_reward)-Q(e.true_reward)
        adj[e.source].append((e.target,delta))
        adj[e.target].append((e.source,-delta))
    psi: list[Q | None] = [None]*game.vertices
    for root in range(game.vertices):
        if psi[root] is not None:
            continue
        psi[root]=Q(0)
        todo=[root]
        for u in todo:
            for v,delta in adj[u]:
                p=Q(psi[u])+delta
                if psi[v] is None:
                    psi[v]=p
                    todo.append(v)
                elif psi[v]!=p:
                    return None
    return tuple(Q(p) for p in psi)


def boundary_relative_certificate(game:RewardPathGame):
    """Check exact shaping on every edge and one common terminal potential.

    Return the common additive proxy shift for paths from the declared start
    to any terminal. Every terminal must lie in the start component, so the
    comparison covers the full target set.
    """
    phi=potential_if_exact(game)
    if phi is None:
        return None
    visited={game.start}
    todo=[game.start]
    adj=[set() for _ in range(game.vertices)]
    for e in game.edges:
        adj[e.source].add(e.target)
        adj[e.target].add(e.source)
    for u in todo:
        for v in adj[u]:
            if v not in visited:
                visited.add(v)
                todo.append(v)
    if any(t not in visited for t in game.terminals):
        return None
    if len({phi[t] for t in game.terminals})!=1:
        return None
    return {"potential":phi,
            "common_path_offset":phi[game.terminals[0]]-phi[game.start]}


def path_returns(game:RewardPathGame, edge_indices:tuple[int, ...]):
    """Validate a directed path from start to a declared terminal."""
    at=game.start
    gold,proxy=Q(0),Q(0)
    for i in edge_indices:
        if type(i) is not int or not 0<=i<len(game.edges):
            raise ValueError("invalid edge reference")
        e=game.edges[i]
        if e.source!=at:
            raise ValueError("edges do not form directed path from start")
        at=e.target
        gold+=Q(e.true_reward)
        proxy+=Q(e.proxy_reward)
    if at not in game.terminals:
        raise ValueError("path must terminate in declared terminal set")
    return gold,proxy


def policy_rank_reversal(game, first_path, second_path):
    """True if these two legal paths are strictly oppositely ranked."""
    a=path_returns(game,tuple(first_path))
    b=path_returns(game,tuple(second_path))
    true_diff=a[0]-b[0]
    proxy_diff=a[1]-b[1]
    return true_diff*proxy_diff<0


def directed_loop_exploit(game:RewardPathGame, indices):
    """Return a repeatable proxy-arbitrage witness when both sums permit it.

    The loop is checked for directed continuity and closure. 'Repeatable'
    still requires that the game scheduler permits indefinite return to the
    same node, an assumption encoded in this finite transition system.
    """
    indices=tuple(indices)
    if not indices:
        raise ValueError("cycle must have edges")
    first=game.edges[indices[0]]
    at=first.source
    gold,proxy=Q(0),Q(0)
    for i in indices:
        if type(i)is not int or not 0<=i<len(game.edges):
            raise ValueError("bad edge index")
        e=game.edges[i]
        if at!=e.source:
            raise ValueError("loop is not directed and contiguous")
        at=e.target
        gold+=Q(e.true_reward)
        proxy+=Q(e.proxy_reward)
    if at!=first.source:
        raise ValueError("walk is not closed")
    if proxy>0 and gold<=0:
        return {"true_per_lap":gold,
                "proxy_per_lap":proxy,
                "proxy_minus_true":proxy-gold,
                "edge_indices":indices}
    return None
