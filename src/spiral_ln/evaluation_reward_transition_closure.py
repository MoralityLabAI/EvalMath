"""RHT-12: transition-closed reward cohomology on a time-expanded game DAG.

Each vertex carries a time layer. Every directed edge advances one layer.
A protected gold edge reward and an evaluator/proxy edge reward define
the rational discrepancy cochain omega=proxy-gold. We include the actual
task state AND the evaluator-integrity state in each declared vertex.

On productive edges and paths from the registered start to a terminal,
the discrepancy is constant iff it is a coboundary on the graph obtained
by joining all terminals to one root sink with zero-reward virtual edges.
The terminal gluing is necessary even in a tree-like DAG.

Exact DAG extremal-path DP computes the discrepancy width W and optimal
proxy-selection gold regret R, with 0<=R<=W. A spanning-tree/chord
construction computes relative H1 periods and an upper bound on W.

A second exact synchronized product-DAG DP computes the strongest possible
W and proxy-selection regret under independently licensed gold-reward
intervals, taking account of the fact that an edge shared by two paths
cancels from their difference. All results are rational, and no learned
reward function or model is assumed to be a correct gold oracle.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q


@dataclass(frozen=True)
class TimedRewardEdge:
    source: int
    target: int
    gold: Q
    proxy: Q
    action: str = ""

    def __post_init__(self):
        try:
            Q(self.gold)
            Q(self.proxy)
        except (ValueError, TypeError, ZeroDivisionError) as exc:
            raise ValueError("rewards must be finite rational values") from exc


@dataclass(frozen=True)
class TimedRewardGame:
    layers: tuple[int, ...]
    start: int
    terminals: tuple[int, ...]
    edges: tuple[TimedRewardEdge, ...]

    def __post_init__(self):
        n = len(self.layers)
        if (not n or any(type(t) is not int or t < 0 for t in self.layers)
            or type(self.start) is not int or not 0 <= self.start < n
            or self.layers[self.start] != 0):
            raise ValueError("finite layered DAG with a layer-zero start required")
        if (not self.terminals or len(set(self.terminals)) != len(self.terminals)
            or any(type(t) is not int or not 0 <= t < n
                   for t in self.terminals)):
            raise ValueError("nonempty distinct terminal vertices required")
        terminals = set(self.terminals)
        for e in self.edges:
            if (type(e.source) is not int or type(e.target) is not int
                or not 0 <= e.source < n or not 0 <= e.target < n
                or self.layers[e.target] != self.layers[e.source] + 1
                or e.source in terminals):
                raise ValueError("edges must advance exactly one time layer from nonterminal")
        if not any(self._reach_to_terminal()):
            raise ValueError("start must reach a declared terminal")

    def _reach_to_terminal(self):
        outgoing = [[] for _ in self.layers]
        for i, e in enumerate(self.edges):
            outgoing[e.source].append(e.target)
        reach = {self.start}
        for v in sorted(range(len(self.layers)), key=lambda i:self.layers[i]):
            if v in reach:
                reach.update(outgoing[v])
        return tuple(t in reach for t in self.terminals)

    def productive(self):
        n = len(self.layers)
        outgoing = [[] for _ in range(n)]
        incoming = [[] for _ in range(n)]
        for i,e in enumerate(self.edges):
            outgoing[e.source].append(i)
            incoming[e.target].append(i)
        forward = {self.start}
        for v in sorted(range(n), key=lambda i:self.layers[i]):
            if v in forward:
                forward.update(self.edges[i].target for i in outgoing[v])
        backward = set(self.terminals)
        for v in sorted(range(n), key=lambda i:self.layers[i],reverse=True):
            if v in backward:
                backward.update(self.edges[i].source for i in incoming[v])
        kept = forward & backward
        use = tuple(i for i,e in enumerate(self.edges)
                    if e.source in kept and e.target in kept)
        return kept, use

    def complete_paths(self, *, max_paths=10000):
        """Exact source-to-terminal path census, for independent finite controls."""
        if type(max_paths) is not int or max_paths < 1:
            raise ValueError("positive path census cap required")
        outgoing = [[] for _ in self.layers]
        for i,e in enumerate(self.edges):
            outgoing[e.source].append(i)
        paths = []
        def visit(vertex, sofar):
            if vertex in self.terminals:
                if len(paths) >= max_paths:
                    raise ValueError("path census exceeded registered budget")
                paths.append(tuple(sofar))
                return
            for i in outgoing[vertex]:
                sofar.append(i)
                visit(self.edges[i].target,sofar)
                sofar.pop()
        visit(self.start,[])
        return tuple(paths)

    def path_returns(self, path):
        """Validate a directed path and calculate independent gold/proxy."""
        vertex = self.start
        gold = proxy = Q(0)
        for i in path:
            if type(i) is not int or not 0 <= i < len(self.edges):
                raise ValueError("unregistered edge in path")
            e = self.edges[i]
            if e.source != vertex:
                raise ValueError("edge path is not contiguous")
            gold += Q(e.gold)
            proxy += Q(e.proxy)
            vertex = e.target
        if vertex not in self.terminals:
            raise ValueError("path must reach a declared terminal")
        return gold, proxy


@dataclass(frozen=True)
class RelativeRewardCertificate:
    minimum_discrepancy: Q
    maximum_discrepancy: Q
    discrepancy_width: Q
    minimum_path: tuple[int, ...]
    maximum_path: tuple[int, ...]
    relative_exact: bool
    relative_potential: tuple[Q | None, ...] | None
    fundamental_periods: tuple[tuple[int, Q], ...]
    sum_absolute_fundamental_periods: Q
    true_gold_optimum: Q
    proxy_optimum: Q
    worst_proxy_selected_gold: Q
    worst_proxy_selected_regret: Q
    proxy_selected_path: tuple[int, ...]
    gold_optimum_path: tuple[int, ...]


def _extreme_paths(game:TimedRewardGame, weights, *, maximize:bool):
    used,edges = game.productive()
    out = {u:[] for u in used}
    for i in edges:
        e=game.edges[i]
        out[e.source].append(i)
    order=sorted(used,key=lambda u:(game.layers[u],u))
    best = {game.start:(Q(0),())}
    for u in order:
        if u not in best:
            continue
        value, path = best[u]
        for i in out[u]:
            v=game.edges[i].target
            trial=(value+Q(weights[i]),path+(i,))
            if (v not in best or (trial[0]>best[v][0] if maximize
                                  else trial[0]<best[v][0])):
                best[v]=trial
    choices=tuple(best[t] for t in game.terminals if t in best)
    return max(choices,key=lambda x:x[0]) if maximize else min(choices,key=lambda x:x[0])


def _tree_potential_periods(game:TimedRewardGame, weights):
    """Spanning-tree integral on productive graph with terminals glued to sink."""
    kept,original=game.productive()
    sink=len(game.layers)
    augmented=tuple(
        (game.edges[i].source,game.edges[i].target,Q(weights[i]),i)
        for i in original
    )+tuple((t,sink,Q(0),len(game.edges)+j)
            for j,t in enumerate(game.terminals) if t in kept)
    parent=list(range(sink+1))
    def find(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]]
            x=parent[x]
        return x
    tree=[]
    chords=[]
    for u,v,delta,i in augmented:
        a,b=find(u),find(v)
        if a==b:
            chords.append((u,v,delta,i))
        else:
            parent[a]=b
            tree.append((u,v,delta,i))
    adjacency={u:[] for u in kept|{sink}}
    for u,v,delta,_ in tree:
        adjacency[u].append((v,delta))
        adjacency[v].append((u,-delta))
    phi={game.start:Q(0)}
    queue=[game.start]
    for u in queue:
        for v,weight in adjacency[u]:
            if v not in phi:
                phi[v]=phi[u]+weight
                queue.append(v)
    if set(phi)!=set(adjacency):
        raise AssertionError("productive augmented graph must be connected")
    periods=tuple((i,delta-(phi[v]-phi[u])) for u,v,delta,i in chords)
    exact=all(period==0 for _,period in periods)
    return (
        exact,
        tuple(phi.get(v) for v in range(sink+1)) if exact else None,
        periods,
        sum((abs(period) for _,period in periods),Q(0)),
    )


def certify_relative_reward(game:TimedRewardGame) -> RelativeRewardCertificate:
    """Prove the exact relative cohomology and quantitative regret ceiling."""
    gold=tuple(Q(e.gold) for e in game.edges)
    proxy=tuple(Q(e.proxy) for e in game.edges)
    gap=tuple(p-g for p,g in zip(proxy,gold))
    low,lp=_extreme_paths(game,gap,maximize=False)
    high,hp=_extreme_paths(game,gap,maximize=True)
    exact,potential,periods,basis_bound=_tree_potential_periods(game,gap)
    if (exact!=(low==high) or high-low>basis_bound):
        raise AssertionError("relative cohomology and path gap width disagree")
    best_gold,best_gold_path=_extreme_paths(game,gold,maximize=True)

    # Select by highest proxy, then lowest gold. This lexicographic
    # objective is additive and permits a single DAG recurrence.
    kept,indices=game.productive()
    outgoing={u:[] for u in kept}
    for i in indices:
        outgoing[game.edges[i].source].append(i)
    scores={game.start:(Q(0),Q(0),())}
    for u in sorted(kept,key=lambda v:(game.layers[v],v)):
        if u not in scores:
            continue
        pv,gv,path=scores[u]
        for i in outgoing[u]:
            v=game.edges[i].target
            cand=(pv+proxy[i],gv+gold[i],path+(i,))
            if v not in scores or (cand[0],-cand[1]) > (
                scores[v][0],-scores[v][1]
            ):
                scores[v]=cand
    selected=max(
        (scores[t] for t in game.terminals if t in scores),
        key=lambda item:(item[0],-item[1])
    )
    best_proxy,worst_gold,selected_path=selected
    regret=best_gold-worst_gold
    if not Q(0)<=regret<=high-low:
        raise AssertionError("proxy-selection regret exceeds discrepancy width")
    return RelativeRewardCertificate(
        minimum_discrepancy=low,maximum_discrepancy=high,
        discrepancy_width=high-low,
        minimum_path=lp,maximum_path=hp,
        relative_exact=exact,relative_potential=potential,
        fundamental_periods=periods,
        sum_absolute_fundamental_periods=basis_bound,
        true_gold_optimum=best_gold,
        proxy_optimum=best_proxy,
        worst_proxy_selected_gold=worst_gold,
        worst_proxy_selected_regret=regret,
        proxy_selected_path=selected_path,
        gold_optimum_path=best_gold_path,
    )


@dataclass(frozen=True)
class RobustTransitionCertificate:
    maximum_width: Q
    maximum_proxy_regret: Q
    width_high_path: tuple[int, ...]
    width_low_path: tuple[int, ...]
    regret_challenger_path: tuple[int, ...]
    regret_proxy_path: tuple[int, ...]
    witness_gold_rewards: tuple[Q, ...]
    guaranteed_proxy_gold_floor: Q
    states_visited: int
    passes: bool
    maximum_allowed_regret: Q | None
    minimum_required_true_return: Q | None


def _synchronized_pair_max(
    game:TimedRewardGame,lower,upper, *,
    proxy_optimal_second:bool,
):
    """Exact interval-envelope optimum on product of two synchronized DAGs."""
    terminal_layers={game.layers[t] for t in game.terminals}
    if len(terminal_layers)!=1:
        raise ValueError("robust product DP requires terminals at one horizon")
    horizon=next(iter(terminal_layers))
    kept,indices=game.productive()
    out={v:[] for v in kept}
    for i in indices:
        out[game.edges[i].source].append(i)
    fwd={game.start:Q(0)}
    order=sorted(kept,key=lambda v:(game.layers[v],v))
    for u in order:
        if u not in fwd:
            continue
        for i in out[u]:
            v=game.edges[i].target
            score=fwd[u]+Q(game.edges[i].proxy)
            if v not in fwd or score>fwd[v]:
                fwd[v]=score
    best_proxy=max(fwd[t] for t in game.terminals if t in fwd)
    back={t:Q(0) for t in game.terminals if t in kept}
    for u in reversed(order):
        for i in out[u]:
            v=game.edges[i].target
            if v in back:
                trial=Q(game.edges[i].proxy)+back[v]
                if u not in back or trial>back[u]:
                    back[u]=trial
    tight=set(i for i in indices if
              game.edges[i].source in fwd and game.edges[i].target in back
              and fwd[game.edges[i].source]+Q(game.edges[i].proxy)
              +back[game.edges[i].target]==best_proxy)
    dp={(game.start,game.start):(Q(0),(),())}
    visited=1
    for _ in range(horizon):
        nxt={}
        for (u,v),(value,p_path,q_path) in dp.items():
            for i in out[u]:
                for j in out[v]:
                    if proxy_optimal_second and j not in tight:
                        continue
                    e,f=game.edges[i],game.edges[j]
                    increment=Q(0) if i==j else Q(upper[i])-Q(lower[j])
                    candidate=(value+increment,p_path+(i,),q_path+(j,))
                    key=(e.target,f.target)
                    if key not in nxt or candidate[0]>nxt[key][0]:
                        nxt[key]=candidate
        dp=nxt
        visited+=len(dp)
    terminal=set(game.terminals)
    candidates=(v for (u,w),v in dp.items()
                if u in terminal and w in terminal)
    best=max(candidates,key=lambda item:item[0])
    return best,visited


def robust_transition_certify(
    game:TimedRewardGame,gold_lower,gold_upper, *,
    maximum_allowed_regret=None,minimum_required_true_return=None,
) -> RobustTransitionCertificate:
    """Worst-case proxy regret over independent per-edge gold intervals.

    Intervals are externally licensed. The proxy edge rewards are fixed.
    A product-DAG path pair chooses gold upper on edges used only by the
    challenger and gold lower on edges used only by a proxy-optimal path.
    Shared edges cancel, so the maximum is exact.

    The separate robust width covers proxy-minus-gold discrepancies, with
    delta_lower=proxy-gold_upper, delta_upper=proxy-gold_lower.
    """
    lower=tuple(Q(x) for x in gold_lower)
    upper=tuple(Q(x) for x in gold_upper)
    if len(lower)!=len(game.edges) or len(upper)!=len(game.edges):
        raise ValueError("one independently registered interval per transition")
    if any(lo>hi for lo,hi in zip(lower,upper)):
        raise ValueError("gold interval lower bounds must not exceed upper bounds")
    proxy=tuple(Q(e.proxy) for e in game.edges)
    gap_low=tuple(p-u for p,u in zip(proxy,upper))
    gap_high=tuple(p-l for p,l in zip(proxy,lower))
    (width,pw,qw),s1=_synchronized_pair_max(
        game,gap_low,gap_high,proxy_optimal_second=False,
    )
    (regret,challenger,chosen),s2=_synchronized_pair_max(
        game,lower,upper,proxy_optimal_second=True,
    )
    chosen_edges=set(chosen)
    challenger_edges=set(challenger)
    witness=tuple(
        hi if i in challenger_edges-chosen_edges else lo
        for i,(lo,hi) in enumerate(zip(lower,upper))
    )
    p_challenger=sum((witness[i] for i in challenger),Q(0))
    p_chosen=sum((witness[i] for i in chosen),Q(0))
    if regret!=p_challenger-p_chosen or regret>width or regret<0:
        raise AssertionError("robust regret witness or width inequality invalid")
    if game.path_returns(chosen)[1]!=_extreme_paths(game,proxy,maximize=True)[0]:
        raise AssertionError("chosen witness path must be proxy-optimal")
    # Lower bound on actual gold for ANY proxy-optimal path and ANY
    # gold reward vector from the licensed independent interval box.
    best_proxy=_extreme_paths(game,proxy,maximize=True)[0]
    kept,indices=game.productive()
    out={u:[] for u in kept}
    for i in indices:
        out[game.edges[i].source].append(i)
    fwd={game.start:Q(0)}
    back={t:Q(0) for t in game.terminals if t in kept}
    order=sorted(kept,key=lambda v:(game.layers[v],v))
    for u in order:
        if u not in fwd:
            continue
        for i in out[u]:
            e=game.edges[i]
            fwd[e.target]=max(fwd.get(e.target,Q(-10**100)),
                              fwd[u]+Q(e.proxy))
    for u in reversed(order):
        for i in out[u]:
            e=game.edges[i]
            if e.target in back:
                back[u]=max(back.get(u,Q(-10**100)),
                            Q(e.proxy)+back[e.target])
    min_gold={game.start:Q(0)}
    for u in order:
        if u not in min_gold:
            continue
        for i in out[u]:
            e=game.edges[i]
            if (fwd[u]+Q(e.proxy)+back[e.target]==best_proxy):
                trial=min_gold[u]+lower[i]
                if e.target not in min_gold or trial<min_gold[e.target]:
                    min_gold[e.target]=trial
    gold_floor=min(min_gold[t] for t in game.terminals if t in min_gold)
    cap=(None if maximum_allowed_regret is None
         else Q(maximum_allowed_regret))
    floor=(None if minimum_required_true_return is None
           else Q(minimum_required_true_return))
    if cap is not None and cap<0:
        raise ValueError("maximum regret must be nonnegative")
    return RobustTransitionCertificate(
        maximum_width=width,maximum_proxy_regret=regret,
        width_high_path=pw,width_low_path=qw,
        regret_challenger_path=challenger,regret_proxy_path=chosen,
        witness_gold_rewards=witness,guaranteed_proxy_gold_floor=gold_floor,
        states_visited=s1+s2,
        passes=(cap is None or regret<=cap)
               and (floor is None or gold_floor>=floor),
        maximum_allowed_regret=cap,
        minimum_required_true_return=floor,
    )
