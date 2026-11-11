"""RHT-13: stochastic reward closure with hidden evaluator integrity.

A finite partially observed controlled Markov kernel has hidden states,
actor-visible observations, and conditional transition probabilities. Every
transition emits a proxy reward and a *gold reward feature vector* tied to
a globally shared, independently licensed parameter theta. Reusing a
feature across many transitions preserves the uncertainty's identity.

A belief-state Bellman recursion computes the proxy-optimal expected return
and the minimum true-gold return among proxy-optimal policies. Another
Bellman recursion computes the true-gold optimum in the SAME actor
observation/action policy class. Their difference is true regret.

Because every policy's expected gold return is affine in theta, the
maximum regret over a rectangular gold set occurs at one of its vertices.
Exact finite endpoint search provides a robust regret and gold-floor
certificate without enumerating all conditional policies.

A backward Markov-coboundary check gives a sufficient invariance theorem:
if the expected per-action discrepancy is E[phi(next)]-phi(current)
with terminal potential zero, every fixed-horizon observation policy has
the same EXPECTED reward shift. Realized path discrepancies can still be
nonzero, providing a null control for a pathwise topological certificate.

All computations are Fraction arithmetic, capped and scoped to a frozen
kernel, fixed horizon, no voluntary early stop, and independent gold data.
They do not verify actual agent behavior or human reward correctness.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache
from itertools import product


@dataclass(frozen=True)
class StochasticRewardEdge:
    source: int
    action: int
    target: int
    observation: str
    probability: Q
    proxy: Q
    gold_base: Q = Q(0)
    gold_coefficients: tuple[Q, ...] = ()

    def __post_init__(self):
        if not isinstance(self.observation,str) or not self.observation:
            raise ValueError("observations must be nonempty strings")
        try:
            vals=(Q(self.probability),Q(self.proxy),Q(self.gold_base)) + tuple(
                Q(v) for v in self.gold_coefficients
            )
        except (ValueError,TypeError,ZeroDivisionError) as exc:
            raise ValueError("all transition values must be rational") from exc
        if not 0<vals[0]<=1:
            raise ValueError("nonzero transition probability required")


@dataclass(frozen=True)
class StochasticRewardGame:
    state_count: int
    actions: tuple[str, ...]
    initial: tuple[Q, ...]
    gold_parameters: tuple[str, ...]
    edges: tuple[StochasticRewardEdge, ...]
    horizon: int

    def __post_init__(self):
        if (type(self.state_count)is not int or not 1<=self.state_count<=16
            or not self.actions or len(set(self.actions))!=len(self.actions)
            or any(not isinstance(a,str) or not a for a in self.actions)
            or not self.gold_parameters or
            len(set(self.gold_parameters))!=len(self.gold_parameters)
            or len(self.gold_parameters)>7
            or type(self.horizon)is not int or not 1<=self.horizon<=5):
            raise ValueError("bounded finite states/actions/parameters/horizon required")
        if len(self.initial)!=self.state_count:
            raise ValueError("one initial mass per hidden state")
        try:
            masses=tuple(Q(m) for m in self.initial)
        except (ValueError,TypeError,ZeroDivisionError) as exc:
            raise ValueError("initial mass must be rational") from exc
        if sum(masses)!=1 or any(v<0 for v in masses):
            raise ValueError("initial hidden-state masses must sum to one")
        if not self.edges:
            raise ValueError("nonempty complete transition kernel required")
        groups={}
        for edge in self.edges:
            if (type(edge.source)is not int or
                not 0<=edge.source<self.state_count or
                type(edge.target)is not int or
                not 0<=edge.target<self.state_count or
                type(edge.action)is not int or
                not 0<=edge.action<len(self.actions) or
                len(edge.gold_coefficients)!=len(self.gold_parameters)):
                raise ValueError("invalid transition, action or gold feature dimensions")
            groups.setdefault((edge.source,edge.action),[]).append(edge)
        for state in range(self.state_count):
            for action in range(len(self.actions)):
                current=groups.get((state,action),())
                if not current or sum((Q(e.probability) for e in current),Q(0))!=1:
                    raise ValueError("each hidden state/action must have normalized transitions")

    def by_state_action(self):
        groups={}
        for edge in self.edges:
            groups.setdefault((edge.source,edge.action),[]).append(edge)
        return {key:tuple(values) for key,values in groups.items()}

    def gold(self,edge:StochasticRewardEdge,theta) -> Q:
        return Q(edge.gold_base)+sum((
            Q(c)*Q(t) for c,t in zip(edge.gold_coefficients,theta)
        ),Q(0))


@dataclass(frozen=True)
class ObservationPolicy:
    action: int | None = None
    branches: tuple[tuple[str, "ObservationPolicy"], ...] = ()


@dataclass(frozen=True)
class PolicySolution:
    objective: str
    proxy_return: Q
    gold_return: Q
    policy: ObservationPolicy
    states_visited: int


def _gold_theta(game:StochasticRewardGame,theta):
    try:
        value=tuple(Q(v) for v in theta)
    except (ValueError,TypeError,ZeroDivisionError) as exc:
        raise ValueError("gold parameters must be rational") from exc
    if len(value)!=len(game.gold_parameters):
        raise ValueError("one gold parameter per registered feature")
    return value


def optimize_stochastic_policy(
    game:StochasticRewardGame,theta, *,
    objective:str="proxy_worst_gold", max_states:int=100000
) -> PolicySolution:
    """Exact optimal deterministic observation policy under a fixed theta.

    Proxy tie-breaking is adversarial for proxy_worst_gold. Every step is
    compulsory until the declared horizon, including after any hidden
    alarm/absorbing state. Transitions in such a state can carry zero reward.
    """
    gold=_gold_theta(game,theta)
    if objective not in (
        "proxy_worst_gold","gold_max","gap_max","gap_min"
    ) or type(max_states)is not int or max_states<1:
        raise ValueError("invalid objective or DP resource cap")
    lookup=game.by_state_action()
    visited=0

    def priority(p,g):
        if objective=="proxy_worst_gold":
            return (p,-g)
        if objective=="gold_max":
            return (g,p)
        if objective=="gap_max":
            return (p-g,p)
        return (g-p,p)

    @lru_cache(None)
    def solve(mass:tuple[Q,...],remaining:int):
        nonlocal visited
        visited+=1
        if visited>max_states:
            raise ValueError("POMDP belief DP exceeds registered state budget")
        if remaining==0 or not any(mass):
            return Q(0),Q(0),ObservationPolicy()
        winner=None
        for a in range(len(game.actions)):
            immediate_proxy=immediate_gold=Q(0)
            observation_mass={}
            for s,weight in enumerate(mass):
                if not weight:
                    continue
                for e in lookup[s,a]:
                    probability=weight*Q(e.probability)
                    immediate_proxy+=probability*Q(e.proxy)
                    immediate_gold+=probability*game.gold(e,gold)
                    branch=observation_mass.setdefault(
                        e.observation,[Q(0)]*game.state_count
                    )
                    branch[e.target]+=probability
            p,g=immediate_proxy,immediate_gold
            branches=[]
            for observation,masses in sorted(observation_mass.items()):
                pp,gg,child=solve(tuple(masses),remaining-1)
                p+=pp
                g+=gg
                branches.append((observation,child))
            candidate=(p,g,ObservationPolicy(a,tuple(branches)))
            if winner is None or priority(p,g)>priority(winner[0],winner[1]):
                winner=candidate
        if winner is None:
            raise AssertionError("a nonterminal belief must have a legal action")
        return winner

    p,g,policy=solve(tuple(Q(x) for x in game.initial),game.horizon)
    return PolicySolution(objective,p,g,policy,visited)


@dataclass(frozen=True)
class OccupancyReturn:
    proxy: Q
    gold_base: Q
    gold_feature_occupancy: tuple[Q,...]
    histories: int


def policy_occupancy(
    game:StochasticRewardGame,policy:ObservationPolicy, *,
    max_histories:int=100000
) -> OccupancyReturn:
    """Independent world-by-world exact public-history policy evaluation.

    All transition types with the same gold feature accumulate into one
    common coefficient. An unseen or repeated observation branch is invalid.
    """
    if type(max_histories)is not int or max_histories<1:
        raise ValueError("positive history enumeration cap required")
    lookup=game.by_state_action()
    p=b=Q(0)
    coeffs=[Q(0)]*len(game.gold_parameters)
    histories=0

    def visit(s:int,node:ObservationPolicy,depth:int,mass:Q):
        nonlocal p,b,histories
        if not mass:
            return
        histories+=1
        if histories>max_histories:
            raise ValueError("exact occupancy path enumeration cap exceeded")
        if depth==0:
            if node.action is not None or node.branches:
                raise ValueError("policy continues past registered horizon")
            return
        if type(node.action)is not int or not 0<=node.action<len(game.actions):
            raise ValueError("mandatory-horizon policy has invalid action")
        branches=dict(node.branches)
        if len(branches)!=len(node.branches):
            raise ValueError("duplicate observation branch in policy")
        for e in lookup[s,node.action]:
            weight=mass*Q(e.probability)
            p+=weight*Q(e.proxy)
            b+=weight*Q(e.gold_base)
            for j,c in enumerate(e.gold_coefficients):
                coeffs[j]+=weight*Q(c)
            child=branches.get(e.observation)
            if child is None:
                raise ValueError("policy lacks a reachable observation branch")
            visit(e.target,child,depth-1,weight)

    for state,mass in enumerate(game.initial):
        visit(state,policy,game.horizon,Q(mass))
    return OccupancyReturn(p,b,tuple(coeffs),histories)


@dataclass(frozen=True)
class RobustStochasticRewardCertificate:
    nominal_proxy: Q
    nominal_gold_at_proxy: Q
    nominal_optimal_gold: Q
    nominal_regret: Q
    nominal_policy_discrepancy_width: Q
    robust_max_regret: Q
    robust_policy_discrepancy_width: Q
    guaranteed_proxy_gold_floor: Q
    worst_gold_parameters: tuple[Q,...]
    worst_gold_policy: ObservationPolicy
    worst_proxy_policy: ObservationPolicy
    worst_gold_witness_occupancy: tuple[Q,...]
    worst_proxy_witness_occupancy: tuple[Q,...]
    reward_interval_vertices_checked: int
    belief_dp_states_visited: int
    passes: bool


def stochastic_robust_certificate(
    game:StochasticRewardGame, intervals, *,
    nominal=None, maximum_allowed_regret=None,
    minimum_proxy_gold_return=None, max_states=100000,
) -> RobustStochasticRewardCertificate:
    """Sharp regret against proxy-maximizing POMDP policies over gold box.

    For any fixed policy pi, J_gold(pi,theta) is affine in theta. Gold-opt
    minus worst proxy-opt gold is max of finitely many affine functions
    (one for each challenger/proxy policy pair), hence convex in theta.
    A convex function on an axis-aligned box attains a maximum at a
    vertex. Evaluating 2^K endpoints with exact belief DP is sufficient.
    Gold-floor minimization over proxy-optimal policies also occurs at an
    endpoint, since it is the minimum of affine functions.
    """
    if len(intervals)!=len(game.gold_parameters):
        raise ValueError("one licensed interval for each shared gold parameter")
    try:
        endpoints=tuple((Q(lo),Q(hi)) for lo,hi in intervals)
    except (TypeError,ValueError,ZeroDivisionError) as exc:
        raise ValueError("rational interval endpoints required") from exc
    if any(lo>hi for lo,hi in endpoints):
        raise ValueError("gold interval lower bound exceeds upper bound")
    middle=(tuple((lo+hi)/2 for lo,hi in endpoints)
            if nominal is None else _gold_theta(game,nominal))
    if any(not lo<=v<=hi for v,(lo,hi) in zip(middle,endpoints)):
        raise ValueError("nominal true gold parameter must lie inside its licensed interval")

    total_states=0
    cache={}
    def solve(theta,objective):
        nonlocal total_states
        key=(theta,objective)
        if key not in cache:
            result=optimize_stochastic_policy(
                game,theta,objective=objective,max_states=max_states
            )
            occupancy=policy_occupancy(game,result.policy)
            evaluated_gold=occupancy.gold_base+sum((
                c*t for c,t in zip(occupancy.gold_feature_occupancy,theta)
            ),Q(0))
            if evaluated_gold!=result.gold_return or occupancy.proxy!=result.proxy_return:
                raise AssertionError("independent occupancy oracle mismatches policy Bellman")
            cache[key]=(result,occupancy)
            total_states+=result.states_visited
        return cache[key]

    def stats(theta):
        best_gold,_=solve(theta,"gold_max")
        proxy,_=solve(theta,"proxy_worst_gold")
        high,_=solve(theta,"gap_max")
        low,_=solve(theta,"gap_min")
        regret=best_gold.gold_return-proxy.gold_return
        width=(high.proxy_return-high.gold_return)-(low.proxy_return-low.gold_return)
        if not 0<=regret<=width:
            raise AssertionError("policy regret violates discrepancy oscillation bound")
        return regret,width,best_gold,proxy

    nominal_regret,nominal_width,nominal_best,nominal_proxy=stats(middle)
    vertices=tuple(sorted(set(product(*(tuple(sorted(set(pair))) for pair in endpoints)))))
    highest=Q(-1)
    high_width=Q(0)
    gold_floor=None
    worst=None
    worst_gold=worst_proxy=None
    for theta in vertices:
        regret,width,gold,proxy=stats(theta)
        high_width=max(high_width,width)
        gold_floor=(proxy.gold_return if gold_floor is None
                    else min(gold_floor,proxy.gold_return))
        if regret>highest:
            highest,worst=regret,theta
            worst_gold,worst_proxy=gold,proxy
    if worst is None or worst_gold is None or worst_proxy is None:
        raise AssertionError("gold interval box must have at least one vertex")
    high_occ=solve(worst,"gold_max")[1]
    proxy_occ=solve(worst,"proxy_worst_gold")[1]
    risk_cap=(None if maximum_allowed_regret is None else Q(maximum_allowed_regret))
    floor=(None if minimum_proxy_gold_return is None else Q(minimum_proxy_gold_return))
    if risk_cap is not None and risk_cap<0:
        raise ValueError("maximum regret must be nonnegative")
    return RobustStochasticRewardCertificate(
        nominal_proxy=nominal_proxy.proxy_return,
        nominal_gold_at_proxy=nominal_proxy.gold_return,
        nominal_optimal_gold=nominal_best.gold_return,
        nominal_regret=nominal_regret,
        nominal_policy_discrepancy_width=nominal_width,
        robust_max_regret=highest,
        robust_policy_discrepancy_width=high_width,
        guaranteed_proxy_gold_floor=Q(gold_floor),
        worst_gold_parameters=worst,
        worst_gold_policy=worst_gold.policy,
        worst_proxy_policy=worst_proxy.policy,
        worst_gold_witness_occupancy=high_occ.gold_feature_occupancy,
        worst_proxy_witness_occupancy=proxy_occ.gold_feature_occupancy,
        reward_interval_vertices_checked=len(vertices),
        belief_dp_states_visited=total_states,
        passes=(risk_cap is None or highest<=risk_cap)
               and (floor is None or Q(gold_floor)>=floor),
    )


@dataclass(frozen=True)
class ExpectedCoboundaryCertificate:
    valid: bool
    potential_by_time: tuple[tuple[Q,...],...] | None
    expected_gap_all_fixed_horizon_policies: Q | None
    first_action_inconsistency: tuple[int,int,int,int,Q,Q] | None


def expected_markov_coboundary(
    game:StochasticRewardGame,theta,
) -> ExpectedCoboundaryCertificate:
    """Sufficient, hidden-state conditional expectation shaping criterion.

    Starting at phi_H(s)=0, calculate for each t,s,a
        candidate=E[phi_{t+1}(next) - (proxy-gold) | s,a].
    If candidate is independent of a, set phi_t(s)=candidate. Then
        E[proxy-gold | s,a]=E[phi_{t+1}(next)|s,a]-phi_t(s).
    Its conditional martingale-difference residual has mean zero, so
    E[total proxy-gold] = -E[phi_0(initial)] for EVERY observation policy
    taking exactly H actions. Pathwise reward discrepancies may vary.
    """
    gold=_gold_theta(game,theta)
    kernel=game.by_state_action()
    potentials=[[Q(0)]*game.state_count for _ in range(game.horizon+1)]
    for time in range(game.horizon-1,-1,-1):
        for state in range(game.state_count):
            options=[]
            for a in range(len(game.actions)):
                value=sum((
                    Q(e.probability)*(
                        potentials[time+1][e.target]
                        -(Q(e.proxy)-game.gold(e,gold))
                    ) for e in kernel[state,a]
                ),Q(0))
                options.append(value)
            if any(v!=options[0] for v in options):
                different=next(i for i,v in enumerate(options)
                               if v!=options[0])
                return ExpectedCoboundaryCertificate(
                    False,None,None,
                    (time,state,0,different,options[0],options[different])
                )
            potentials[time][state]=options[0]
    constant=-sum((
        Q(p)*potentials[0][s] for s,p in enumerate(game.initial)
    ),Q(0))
    return ExpectedCoboundaryCertificate(
        True,tuple(tuple(row) for row in potentials),constant,None
    )
