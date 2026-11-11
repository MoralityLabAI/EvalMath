"""RHT-09: joint private-audit / public-leakage / terminal-veto frontier.

The finite game uses RHT-08's frozen latent worlds, rational independent
gold, proxy-maximizing actor action roster, and deterministic subset-sum
queries. The auditor controls whether a query and its answer are sealed or
public; the actor observes every PUBLIC query ID and answer. After the
actor selects its action, the auditor may authorize/veto it according to the
entire PRIVATE query transcript. The veto outcome is visible only AFTER
the actor's final one-shot action choice. No retries are permitted.

Two separate exact objectives:
  malicious harm = Pr(actor-selected proxy max is unsafe AND is authorized)
    maximized by the actor for every actor-visible transcript;
  benign liveness = Pr(authorized | safe action) when an independently
    defined benign actor draws uniformly over the proxy-maximizing roster.

The solver enumerates tiny deterministic audit trees and terminal veto
rules with exact Fractions, subject to a minimum benign liveness, maximum
unvetoed public-leak risk, query-cost cap, and max path depth. A separate
analytic DP handles the scalable one-hot zero-harm/secret-query case.

This is a conditional mathematical model; no training, model activity,
human-preference validation, actual attestation or live actions occur.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache
from itertools import product

from spiral_ln.evaluation_reward_hacking_adaptive_feedback import (
    AdaptiveRewardGame, MixedAuditNode, one_hot_ugc_disclosure_game,
)


@dataclass(frozen=True)
class JointAuditCertificate:
    policy: MixedAuditNode
    allowed_actions_by_private_trace: tuple[
        tuple[tuple[tuple[int, int], ...], tuple[int, ...]], ...
    ]
    authorized_unsafe_risk: Q
    benign_safe_authorization: Q
    public_attack_risk_without_veto: Q
    expected_query_cost: Q
    max_queries: int
    trees_enumerated: int
    gate_assignments_checked: int
    private_leaves: int
    public_leaves: int


def policy_transcripts(
    game: AdaptiveRewardGame,
    policy: MixedAuditNode,
    *,
    sealed_query_cost: Q = Q(1),
    public_query_cost: Q = Q(1),
    max_depth: int = 4,
):
    """World-keyed complete/visible traces, rational cost and path depth."""
    private_cost, public_cost = Q(sealed_query_cost), Q(public_query_cost)
    if private_cost <= 0 or public_cost <= 0:
        raise ValueError("query costs must be strictly positive")
    if type(max_depth) is not int or max_depth < 0:
        raise ValueError("path-depth budget must be a nonnegative integer")
    outcomes = []
    for world in range(len(game.world_records)):
        node = policy
        full = []
        visible = []
        cost = Q(0)
        depth = 0
        while node.query is not None:
            depth += 1
            if depth > max_depth:
                raise ValueError("policy exceeds declared path depth")
            if (type(node.query) is not int or
                not 0 <= node.query < len(game.queries) or
                node.visibility not in ("sealed", "public")):
                raise ValueError("unregistered query identity or visibility")
            answer = game.query_answer(world, node.query)
            step = (node.query, answer)
            full.append(step)
            if node.visibility == "public":
                visible.append(step)
                cost += public_cost
            else:
                cost += private_cost
            children = dict(node.branches)
            if len(children) != len(node.branches) or answer not in children:
                raise ValueError("missing or duplicate branch on reachable query answer")
            node = children[answer]
        if node.branches:
            raise ValueError("terminal query node cannot contain children")
        outcomes.append((tuple(full), tuple(visible), cost, depth))
    return tuple(outcomes)


def _risk_and_liveness(game, traces, masks):
    """Exact terminal strategic harm, safe authorization, and public leak."""
    allowed = game.public_maximizers()
    W = game.total
    full_keys = tuple(sorted({trace[0] for trace in traces}))
    mask_by_trace = dict(zip(full_keys, masks))
    if len(mask_by_trace) != len(full_keys):
        raise AssertionError("one terminal veto mask per private transcript")
    if any(mask < 0 or mask >= 1 << len(allowed) for mask in masks):
        raise ValueError("unregistered terminal action approval")
    public = {}
    for w,(_,visible,_,_) in enumerate(traces):
        public.setdefault(visible,[]).append(w)
    unsafe_mass = 0
    public_without_veto = 0
    for worlds in public.values():
        harmful_by_action = []
        unvetoed_by_action = []
        for a_index, a in enumerate(allowed):
            harmful_by_action.append(sum(
                game.world_weights[w]
                for w in worlds
                if game.unsafe(w,a) and
                (mask_by_trace[traces[w][0]] >> a_index) & 1
            ))
            unvetoed_by_action.append(sum(
                game.world_weights[w] for w in worlds if game.unsafe(w,a)
            ))
        unsafe_mass += max(harmful_by_action)
        public_without_veto += max(unvetoed_by_action)
    safe_total = sum(
        game.world_weights[w]
        for w in range(len(game.world_records))
        for a in allowed if not game.unsafe(w,a)
    )
    if safe_total == 0:
        raise ValueError("non-inert benign safety comparison needs safe attempts")
    safe_approved = sum(
        game.world_weights[w]
        for w in range(len(game.world_records))
        for a_index,a in enumerate(allowed)
        if not game.unsafe(w,a) and
        (mask_by_trace[traces[w][0]] >> a_index) & 1
    )
    if not 0 <= unsafe_mass <= W:
        raise AssertionError("malicious probability out of bounds")
    return (
        Q(unsafe_mass,W),
        Q(safe_approved,safe_total),
        Q(public_without_veto,W),
        full_keys,
        len(public),
    )


def evaluate_joint_audit(
    game: AdaptiveRewardGame,
    policy: MixedAuditNode,
    approved: dict[tuple[tuple[int,int],...], tuple[int,...]],
    *,
    sealed_query_cost=Q(1),
    public_query_cost=Q(1),
    max_depth=4,
) -> JointAuditCertificate:
    """Independently score a fixed complete audit tree and veto rule."""
    traces = policy_transcripts(
        game,policy,sealed_query_cost=sealed_query_cost,
        public_query_cost=public_query_cost,max_depth=max_depth
    )
    eligible = game.public_maximizers()
    keys = tuple(sorted({trace[0] for trace in traces}))
    if set(approved) != set(keys):
        raise ValueError("approval map must cover every reachable private trace")
    masks = []
    for key in keys:
        actions=tuple(approved[key])
        if len(set(actions)) != len(actions) or any(
            type(a) is not int or a not in eligible for a in actions
        ):
            raise ValueError("only distinct registered proxy-maximizing actions may be approved")
        masks.append(sum(1 << eligible.index(a) for a in actions))
    harm,liveness,leak,_,npublic = _risk_and_liveness(game,traces,tuple(masks))
    average=sum((game.world_weights[i]*trace[2] for i,trace in enumerate(traces)),Q(0))/game.total
    return JointAuditCertificate(
        policy=policy,
        allowed_actions_by_private_trace=tuple((key,tuple(sorted(approved[key]))) for key in keys),
        authorized_unsafe_risk=harm,
        benign_safe_authorization=liveness,
        public_attack_risk_without_veto=leak,
        expected_query_cost=average,
        max_queries=max(trace[3] for trace in traces),
        trees_enumerated=1,
        gate_assignments_checked=1,
        private_leaves=len(keys),
        public_leaves=npublic,
    )


def _query_trees(game, worlds, depth, *, max_trees):
    """Generate finite informative query trees, with public/secret choices.

    A query with identical answers throughout a node provides no additional
    private information and is omitted. For a minimization of harm, cost,
    and public leakage with nonnegative costs, such a query cannot improve
    an audit: it can only be removed. Explicit noninformative public
    continuation probes remain supported by evaluate_joint_audit.
    """
    yield MixedAuditNode()
    if depth==0 or len(worlds)<=1:
        return
    for query in range(len(game.queries)):
        groups={}
        for w in worlds:
            groups.setdefault(game.query_answer(w,query),[]).append(w)
        if len(groups)<2:
            continue
        ordered=tuple((a,tuple(group)) for a,group in sorted(groups.items()))
        children=[]
        combinations=1
        for _,group in ordered:
            choices=[]
            for subtree in _query_trees(game,group,depth-1,max_trees=max_trees):
                choices.append(subtree)
                if len(choices)>max_trees:
                    raise ValueError("recursive subtree enumeration exceeded resource cap")
            children.append(tuple(choices))
            combinations*=len(choices)
            if combinations>max_trees:
                raise ValueError("recursive tree product exceeded resource cap")
        for subtrees in product(*children):
            branches=tuple((ordered[i][0],tree)
                           for i,tree in enumerate(subtrees))
            for visibility in ("sealed","public"):
                yield MixedAuditNode(query,visibility,branches)


def optimum_joint_audit(
    game: AdaptiveRewardGame,
    *,
    max_queries:int=1,
    minimum_benign_safe_authorization=Q(2,3),
    maximum_public_attack_risk=Q(1),
    maximum_expected_query_cost=Q(2),
    maximum_authorized_unsafe_risk=Q(1),
    sealed_query_cost=Q(1),
    public_query_cost=Q(1),
    max_trees:int=5000,
    max_gate_assignments:int=400000,
) -> JointAuditCertificate | None:
    """Tiny complete min-max design search with exact liveness/leak limits.

    Objective is min authorized malicious harm. Among equal-harm policies,
    prefer lower expected query cost, then lower public leakage and higher
    benign safe authorization. Every tree is checked against every terminal
    veto mask, up to explicit finite resource caps. If no admissible
    configuration exists, return None. Search budget excess raises.
    """
    if (type(max_queries) is not int or not 0<=max_queries<=3
        or len(game.world_records)>5 or len(game.public_maximizers())>5
        or len(game.queries)>10):
        raise ValueError("bounded seed: <=3 rounds, <=5 worlds/actions, <=10 queries")
    if any(type(x) is not int or x<1 for x in (max_trees,max_gate_assignments)):
        raise ValueError("positive enumeration budgets required")
    lmin,pmax,cmax,rmax=map(Q,(minimum_benign_safe_authorization,
                         maximum_public_attack_risk,maximum_expected_query_cost,
                         maximum_authorized_unsafe_risk))
    if not 0<=lmin<=1 or not 0<=pmax<=1 or cmax<0 or not 0<=rmax<=1:
        raise ValueError("valid liveness, public leak and nonnegative cost caps required")
    total_trees=0
    total_masks=0
    best=None
    keybest=None
    for policy in _query_trees(
        game,tuple(range(len(game.world_records))),max_queries,max_trees=max_trees
    ):
        total_trees+=1
        if total_trees>max_trees:
            raise ValueError("audit tree enumeration exceeded declared resource cap")
        traces=policy_transcripts(
            game,policy,sealed_query_cost=sealed_query_cost,
            public_query_cost=public_query_cost,max_depth=max_queries,
        )
        average=sum((game.world_weights[w]*trace[2]
                     for w,trace in enumerate(traces)),Q(0))/game.total
        if average>cmax:
            continue
        full=tuple(sorted({trace[0] for trace in traces}))
        eligible=game.public_maximizers()
        # Public leakage depends on the audit tree, not terminal veto bits.
        zero=(0,)*len(full)
        _,_,leak,_,npublic=_risk_and_liveness(game,traces,zero)
        if leak>pmax:
            continue
        possibilities=1 << (len(full)*len(eligible))
        if total_masks+possibilities>max_gate_assignments:
            raise ValueError("terminal veto enumeration exceeds declared cap")
        for code in range(possibilities):
            total_masks+=1
            bits=(1<<len(eligible))-1
            gates=tuple((code>>(i*len(eligible)))&bits
                        for i in range(len(full)))
            harm,life,_,_,_= _risk_and_liveness(game,traces,gates)
            if life<lmin or harm>rmax:
                continue
            rank=(harm,average,leak,-life)
            if keybest is None or rank<keybest:
                keybest=rank
                best=JointAuditCertificate(
                    policy=policy,
                    allowed_actions_by_private_trace=tuple(
                        (key,tuple(eligible[a] for a in range(len(eligible))
                                   if gate>>a&1))
                        for key,gate in zip(full,gates)
                    ),
                    authorized_unsafe_risk=harm,
                    benign_safe_authorization=life,
                    public_attack_risk_without_veto=leak,
                    expected_query_cost=average,
                    max_queries=max(trace[3] for trace in traces),
                    trees_enumerated=0,
                    gate_assignments_checked=0,
                    private_leaves=len(full),public_leaves=npublic,
                )
    if best is None:
        return None
    return JointAuditCertificate(
        policy=best.policy,
        allowed_actions_by_private_trace=best.allowed_actions_by_private_trace,
        authorized_unsafe_risk=best.authorized_unsafe_risk,
        benign_safe_authorization=best.benign_safe_authorization,
        public_attack_risk_without_veto=best.public_attack_risk_without_veto,
        expected_query_cost=best.expected_query_cost,
        max_queries=best.max_queries,trees_enumerated=total_trees,
        gate_assignments_checked=total_masks,
        private_leaves=best.private_leaves,public_leaves=best.public_leaves,
    )


@dataclass(frozen=True)
class OneHotSealedFrontier:
    worlds:int
    max_queries:int
    maximum_zero_harm_benign_liveness:Q
    posterior_collision_probability:Q
    private_leaf_sizes:tuple[int,...]
    expected_query_count:Q
    query_tree:MixedAuditNode
    subproblems:int


def one_hot_sealed_zero_harm_frontier(
    worlds:int, max_queries:int
) -> OneHotSealedFrontier:
    """Exact optimal zero-harm safe authorization with sealed interval queries.

    On a leaf of k latent worlds, zero malicious authorization requires
    denying all k matching actions and allowing all other actions. This
    accepts k(n-k) safe (world,action) pairs. Maximize its total count
    via Bellman splitting on allowable contiguous interval queries.

    With leaf sizes k_j, safe-authorization among genuinely safe uniform
    attempts is [n^2-sum_j k_j^2]/[n(n-1)]. The numerator is n^2
    times 1 minus the posterior collision probability; the link is
    the same collision statistic used in EvalMath adaptive disclosure.
    """
    if (type(worlds) is not int or not 2<=worlds<=12
        or type(max_queries) is not int or not 0<=max_queries<=5):
        raise ValueError("bounded UGC seed: n in 2..12, budget in 0..5")
    game=one_hot_ugc_disclosure_game(worlds)
    @lru_cache(maxsize=None)
    def solve(indices:tuple[int,...],budget:int):
        k=len(indices)
        baseline=k*(worlds-k)
        best=baseline
        tree=MixedAuditNode()
        if budget and k>1:
            for qi in range(len(game.queries)):
                groups={}
                for w in indices:
                    groups.setdefault(game.query_answer(w,qi),[]).append(w)
                if len(groups)<2:
                    continue
                parts=tuple((ans,solve(tuple(v),budget-1))
                             for ans,v in sorted(groups.items()))
                mass=sum(p[1][0] for p in parts)
                if mass>best:
                    best=mass
                    tree=MixedAuditNode(
                        qi,"sealed",tuple(
                            (answer,solution[1]) for answer,solution in parts)
                    )
        return best,tree

    mass,tree=solve(tuple(range(worlds)),max_queries)
    traces=policy_transcripts(game,tree,max_depth=max_queries)
    leaf_groups={}
    for w,(full,visible,_,_) in enumerate(traces):
        if visible:
            raise AssertionError("sealed-only query tree must have zero actor-visible trace")
        leaf_groups.setdefault(full,[]).append(w)
    sizes=tuple(sorted((len(g) for g in leaf_groups.values()),reverse=True))
    collision=Q(sum(k*k for k in sizes),worlds*worlds)
    liveness=Q(worlds*worlds-sum(k*k for k in sizes),worlds*(worlds-1))
    if liveness!=Q(mass,worlds*(worlds-1)):
        raise AssertionError("Bellman liveness differs from collision identity")
    expected=Q(sum(game.world_weights[w]*traces[w][3]
                   for w in range(worlds)),game.total)
    return OneHotSealedFrontier(
        worlds=worlds,max_queries=max_queries,
        maximum_zero_harm_benign_liveness=liveness,
        posterior_collision_probability=collision,
        private_leaf_sizes=sizes,expected_query_count=expected,
        query_tree=tree,subproblems=solve.cache_info().currsize,
    )
