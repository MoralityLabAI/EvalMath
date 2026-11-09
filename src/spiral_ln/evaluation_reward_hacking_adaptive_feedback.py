"""RHT-08: adaptive disclosure of audit signals in game-space reward hacking.

The source world is a hidden evaluation cell-count table. Its PUBLIC
category margins are initially identical across registered worlds. An
actor can choose a proxy-maximizing candidate controller after seeing
additional, registered query responses. Each world has an independently
specified gold cochain, and a candidate is unsafe if its regret relative
to that world's optimal reachable candidate exceeds a positive threshold.

Public queries can increase adversarial proxy-tie selection risk; sealed
queries enable an independent auditor to choose a safer terminal action.
Query IDENTITIES are visible whenever a query is public. Choosing which
public query to issue based on a sealed answer can thus leak that answer.

The public attack DP reuses EvalMath's existing selection_risk.NullModel,
and the one-hot interval fixture crosschecks adaptive_disclosure. This is
finite synthetic worst-case analysis, conditional on an external gold
function and a frozen actor/auditor access grammar. No model is run.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache

from spiral_ln.evaluation_reward_hacking_multimap import MultiMapSignals
from spiral_ln.evaluation_selection_risk import (
    NullModel, adaptive_optimum, fixed_optimum,
    no_feedback_risk, policy_fibres, policy_risk, risk_for_fibres,
)


@dataclass(frozen=True)
class AdaptiveRewardGame:
    space: MultiMapSignals
    world_records: tuple[tuple[int, ...], ...]
    world_weights: tuple[int, ...]
    actions: tuple[tuple[int, ...], ...]
    gold_by_world: tuple[tuple[Q, ...], ...]
    proxy_margin_weights: tuple[Q, ...]
    queries: tuple[tuple[int, ...], ...]
    unsafe_regret: Q = Q(1)

    def __post_init__(self):
        m=len(self.space.cells)
        w=len(self.world_records)
        if (w<1 or len(set(self.world_records))!=w or
            len(self.world_weights)!=w or
            any(type(v)is not int or v<=0 for v in self.world_weights)):
            raise ValueError("nonempty distinct worlds with positive integer masses required")
        if not self.actions or len(set(self.actions))!=len(self.actions):
            raise ValueError("frozen distinct controller roster required")
        for x in self.world_records+self.actions:
            if (len(x)!=m or any(type(v)is not int or not 0<=v<=s
                for v,s in zip(x,self.space.capacities))):
                raise ValueError("world and controller records must respect cell capacities")
        if len({self.space.feedback(x) for x in self.world_records})!=1:
            raise ValueError("all worlds must share the declared initial public margin fibre")
        if len(self.gold_by_world)!=w or any(len(t)!=m for t in self.gold_by_world):
            raise ValueError("each world needs an independently licensed gold cochain")
        try:
            for t in self.gold_by_world:
                for v in t:
                    Q(v)
        except (ValueError,TypeError,ZeroDivisionError) as exc:
            raise ValueError("gold weights must be rational") from exc
        if len(self.proxy_margin_weights)!=len(self.space.matrix):
            raise ValueError("proxy score must factor through all public category margins")
        for v in self.proxy_margin_weights:
            Q(v)
        if not self.queries or any(
            len(q)!=m or any(type(v)is not int or v not in (0,1) for v in q)
            for q in self.queries
        ):
            raise ValueError("a nonempty bank of binary subset-sum queries is required")
        if Q(self.unsafe_regret)<=0:
            raise ValueError("unsafe regret threshold must be positive")

    @property
    def total(self) -> int:
        return sum(self.world_weights)

    def proxy_score(self, action:tuple[int,...]) -> Q:
        return sum((Q(coef)*v for coef,v in
                    zip(self.proxy_margin_weights,self.space.feedback(action))),Q(0))

    def public_maximizers(self) -> tuple[int,...]:
        scores=tuple(self.proxy_score(x) for x in self.actions)
        maximum=max(scores)
        return tuple(i for i,p in enumerate(scores) if p==maximum)

    def gold(self, world:int, action:int) -> Q:
        if not (0<=world<len(self.world_records) and 0<=action<len(self.actions)):
            raise ValueError("invalid world or action index")
        return sum((Q(t)*v for t,v in
                    zip(self.gold_by_world[world],self.actions[action])),Q(0))

    def unsafe(self, world:int, action:int) -> bool:
        optimum=max(self.gold(world,i) for i in range(len(self.actions)))
        return optimum-self.gold(world,action)>=Q(self.unsafe_regret)

    def query_answer(self, world:int, query:int) -> int:
        if not (0<=world<len(self.world_records) and 0<=query<len(self.queries)):
            raise ValueError("invalid world or query")
        return sum(a*x for a,x in zip(
            self.queries[query],self.world_records[world]))

    def attack_null(self) -> NullModel:
        eligible=self.public_maximizers()
        return NullModel(
            self.world_weights,
            tuple(tuple(self.unsafe(i,j) for i in range(len(self.world_records)))
                  for j in eligible),
            tuple(tuple(self.query_answer(i,j)
                        for i in range(len(self.world_records)))
                  for j in range(len(self.queries))),
        )


def public_attack_risks(game:AdaptiveRewardGame, budget:int) -> dict:
    """Max dangerous proxy-selection risk after public fixed/adaptive queries."""
    null=game.attack_null()
    baseline=no_feedback_risk(null)
    fixed=fixed_optimum(null,budget)
    adaptive=adaptive_optimum(null,budget)
    if not baseline<=fixed["risk"]<=adaptive["risk"]:
        raise AssertionError("feedback refinement order violated")
    return {
        "baseline":baseline, "fixed":fixed["risk"],
        "adaptive":adaptive["risk"], "fixed_schedule":fixed["schedule"],
        "adaptive_tree":adaptive["tree"],
        "fixed_schedules_checked":fixed["schedules_checked"],
        "adaptive_subproblems":adaptive["subproblems"],
    }


def protected_auditor_optimum(game:AdaptiveRewardGame,budget:int):
    """Minimum expected unsafe outcome probability with PRIVATE query answers.

    The external auditor can release any action from the frozen roster at
    the terminal step. Query IDs, responses and its policy tree remain sealed
    from the optimizing actor until this terminal action has executed.
    Its objective here is worst-case regret-event probability under the
    frozen world prior; no hidden world can change during the audit.
    """
    if type(budget)is not int or budget<0:
        raise ValueError("audit budget must be a nonnegative integer")
    n=len(game.world_records)
    weights=game.world_weights
    m=len(game.actions)

    @lru_cache(maxsize=None)
    def mass(indices:tuple[int,...],steps:int):
        best=min(sum(weights[i] for i in indices if game.unsafe(i,a))
                 for a in range(m))
        query_choice=None
        if steps:
            for q in range(len(game.queries)):
                groups={}
                for i in indices:
                    groups.setdefault(game.query_answer(i,q),[]).append(i)
                if len(groups)<2:
                    continue
                nxt=sum(mass(tuple(sub),steps-1)[0]
                        for _,sub in sorted(groups.items()))
                if nxt<best:
                    best=nxt
                    query_choice=q
        return best,query_choice

    value,initial_query=mass(tuple(range(n)),budget)
    return {
        "risk":Q(value,game.total),
        "first_private_query":initial_query,
        "subproblems":mass.cache_info().currsize,
    }


@dataclass(frozen=True)
class MixedAuditNode:
    query:int|None=None
    visibility:str="sealed"
    branches:tuple[tuple[int,"MixedAuditNode"],...]=()


def visible_transcript(
    game:AdaptiveRewardGame,world:int,policy:MixedAuditNode
) -> tuple[tuple[int,int], ...]:
    """Actor transcript; sealed query responses are omitted from the record.

    The next public query ID remains visible even when chosen using a
    previous sealed observation. This captures action-selection side leakage.
    """
    if not 0<=world<len(game.world_records):
        raise ValueError("invalid reference world")
    node=policy
    transcript=[]
    depth=0
    while node.query is not None:
        depth+=1
        if depth>64:
            raise ValueError("audit policy exceeds registered path depth")
        if node.visibility not in ("sealed","public"):
            raise ValueError("query visibility must be sealed or public")
        query=node.query
        if type(query)is not int or not 0<=query<len(game.queries):
            raise ValueError("mixed audit policy contains invalid query")
        answer=game.query_answer(world,query)
        children=dict(node.branches)
        if len(children)!=len(node.branches) or answer not in children:
            raise ValueError("missing or duplicated policy response branch")
        if node.visibility=="public":
            transcript.append((query,answer))
        node=children[answer]
    if node.branches:
        raise ValueError("terminal audit node must have no children")
    return tuple(transcript)


def mixed_disclosure_attack_risk(
    game:AdaptiveRewardGame,policy:MixedAuditNode
) -> dict:
    """Optimal actor risk after seeing only *visible* query ID/answer trace."""
    null=game.attack_null()
    fibres={}
    for i in range(len(game.world_records)):
        visible=visible_transcript(game,i,policy)
        fibres.setdefault(visible,[]).append(i)
    risk=risk_for_fibres(null,tuple(tuple(group)
                                   for group in fibres.values()))
    return {
        "risk":risk,
        "visible_fibres":tuple(
            (trace,tuple(indices))
            for trace,indices in sorted(fibres.items())
        ),
        "visible_leaves":len(fibres),
        "baseline":no_feedback_risk(null),
    }


def interval_query_bank(space:MultiMapSignals) -> tuple[tuple[int,...],...]:
    """The allowed contiguous first-row interval sum queries for K2,n cells."""
    if len(space.cells[0])!=2:
        raise ValueError("requires two category maps")
    rows=sorted({c[0] for c in space.cells})
    columns=sorted({c[1] for c in space.cells})
    if rows!=(0,1) or columns!=list(range(len(columns))):
        raise ValueError("requires row labels 0/1 and consecutive column labels")
    if len(space.cells)!=2*len(columns):
        raise ValueError("requires full K2,n intersection support")
    return tuple(
        tuple(int(c[0]==0 and a<=c[1]<b) for c in space.cells)
        for a in range(len(columns))
        for b in range(a+1,len(columns)+1)
    )


def one_hot_ugc_disclosure_game(n:int) -> AdaptiveRewardGame:
    """Construct explicit K2,n feedback fibre with n proxy-tied actions.

    Let world i be the unit table with row-0 cell (0,i) satisfied and all
    other column satisfactions in row 1. Each world/actuator action is an
    actual F2 translation-game constraint-satisfaction record on K2,n,
    with all edge shifts zero and endpoint labels fixed to 0 and 1.
    The actor is restricted to these n reachable candidates.

    World i's protected gold cochain assigns reward 1 to each row-0 cell
    except i and 0 elsewhere. Thus action a has gold 0 when a=i, gold
    1 otherwise. Every action has equal public proxy and margin vector.
    """
    if type(n)is not int or n<2 or n>12:
        raise ValueError("frozen model supports 2<=n<=12")
    cells=tuple((r,c) for r in range(2) for c in range(n))
    space=MultiMapSignals(cells,(1,)*(2*n),((0,),(1,)))
    worlds=tuple(
        tuple(int((r==0 and c==i) or (r==1 and c!=i))
              for r,c in cells)
        for i in range(n)
    )
    gold=tuple(
        tuple(Q(1) if r==0 and c!=i else Q(0)
              for r,c in cells)
        for i in range(n)
    )
    game=AdaptiveRewardGame(
        space=space,world_records=worlds,world_weights=(1,)*n,
        actions=worlds,gold_by_world=gold,
        proxy_margin_weights=(Q(1),Q(1))+(Q(0),)*n,
        queries=interval_query_bank(space),unsafe_regret=Q(1),
    )
    if len({space.feedback(x) for x in worlds})!=1:
        raise AssertionError("one-hot row/column margins must match")
    for w in range(n):
        for a in range(n):
            if game.unsafe(w,a)!=(w==a):
                raise AssertionError("one-hot adversarial gold schema violated")
    return game
