"""RHT-14: shared uncertain transition parameters in finite POMDP reward hacking.

A single rational parameter p is reused across every occurrence of an
affine conditional transition law K_p(s',o|s,a)=base+slope*p.
The kernel uncertainty is NONRECTANGULAR across states, actions and time:
nature chooses one p for the entire episode. Gold reward features are
independently licensed globally shared rational parameters theta.

For fixed deterministic observation policies, finite-horizon expected
proxy/gold returns are polynomials in p, affine in theta. The RHT-13
gold-interval vertex theorem remains valid for each fixed p; checking
ONLY transition-interval endpoints is unsound when p is reused.

This exact reference solver enumerates ALL deterministic policies for
mandatory horizon <=2 and requires a uniformly proxy-optimal policy set
over the full p interval. It proves that condition with exact polynomial
inequalities, failing closed when proxy winners change or an additional
policy ties only at an isolated p. Regret and safe-throughput extrema are
then computed at rational endpoints or quadratic stationary points.

Every source, state/action normalization, policy and search budget is
registered. The code is a small analytic proof oracle, not a general
algorithm for robust nonrectangular POMDPs, nor a trained-model evaluation.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache
from itertools import product

from spiral_ln.evaluation_reward_stochastic_closure import (
    ObservationPolicy, StochasticRewardEdge, StochasticRewardGame,
)


def _trim(values):
    data=[Q(x) for x in values]
    while len(data)>1 and data[-1]==0:
        data.pop()
    return tuple(data) if data else (Q(0),)


def _add(a,b):
    return _trim(tuple(
        (a[i] if i<len(a) else Q(0)) +
        (b[i] if i<len(b) else Q(0))
        for i in range(max(len(a),len(b)))
    ))


def _subtract(a,b):
    return _add(a,tuple(-v for v in b))


def _scale(a,number):
    return _trim(tuple(Q(v)*Q(number) for v in a))


def _multiply(a,b):
    ans=[Q(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            ans[i+j]+=Q(x)*Q(y)
    return _trim(ans)


def _evaluate(poly,p):
    x=Q(p)
    total=Q(0)
    for coef in reversed(poly):
        total=total*x+coef
    return total


def _quadratic_extreme(poly, interval, maximize):
    """Sharp rational extrema for polynomials of degree at most two."""
    f=_trim(poly)
    if len(f)>3:
        raise ValueError("quadratic exact oracle supports at most two steps")
    lo,hi=tuple(Q(x) for x in interval)
    if lo>hi:
        raise ValueError("invalid parameter interval")
    candidates=[lo,hi]
    if len(f)==3 and f[2]:
        vertex=-f[1]/(2*f[2])
        if lo<=vertex<=hi:
            candidates.append(vertex)
    candidates=tuple(sorted(set(candidates)))
    return (
        max(((_evaluate(f,p),p) for p in candidates),
            key=lambda pair:(pair[0],-pair[1]))
        if maximize
        else min(((_evaluate(f,p),p) for p in candidates),
                 key=lambda pair:(pair[0],pair[1]))
    )


@dataclass(frozen=True)
class SharedTransitionEdge:
    source:int
    action:int
    target:int
    observation:str
    probability_base:Q
    probability_slope:Q
    proxy:Q=Q(0)
    gold_base:Q=Q(0)
    gold_coefficients:tuple[Q,...]=()

    def probability(self,p):
        return Q(self.probability_base)+Q(self.probability_slope)*Q(p)


@dataclass(frozen=True)
class SharedTransitionGame:
    state_count:int
    actions:tuple[str,...]
    initial:tuple[Q,...]
    gold_parameters:tuple[str,...]
    parameter_interval:tuple[Q,Q]
    edges:tuple[SharedTransitionEdge,...]
    horizon:int=2

    def __post_init__(self):
        if (type(self.state_count)is not int or not 1<=self.state_count<=12
            or type(self.horizon)is not int or not 1<=self.horizon<=2
            or not self.actions or len(set(self.actions))!=len(self.actions)
            or any(not isinstance(a,str) or not a for a in self.actions)
            or not self.gold_parameters or len(set(self.gold_parameters))!=len(self.gold_parameters)
            or len(self.gold_parameters)>4):
            raise ValueError("seed supports <=12 hidden states and horizon 1..2")
        if len(self.parameter_interval)!=2:
            raise ValueError("one shared rational transition interval required")
        try:
            lo,hi=tuple(Q(x) for x in self.parameter_interval)
            initial=tuple(Q(x) for x in self.initial)
        except (ValueError,TypeError,ZeroDivisionError) as exc:
            raise ValueError("rational transition bounds and priors required") from exc
        if not 0<=lo<=hi<=1 or len(initial)!=self.state_count:
            raise ValueError("shared probability must lie in [0,1], with one mass per state")
        if any(x<0 for x in initial) or sum(initial)!=1:
            raise ValueError("initial hidden-state distribution must be normalized")
        if not self.edges:
            raise ValueError("at least one transition required")
        groups={}
        for e in self.edges:
            if (type(e.source)is not int or not 0<=e.source<self.state_count
                or type(e.target)is not int or not 0<=e.target<self.state_count
                or type(e.action)is not int or not 0<=e.action<len(self.actions)
                or not isinstance(e.observation,str) or not e.observation
                or len(e.gold_coefficients)!=len(self.gold_parameters)):
                raise ValueError("transition index, observation or feature invalid")
            try:
                Q(e.probability_base); Q(e.probability_slope)
                Q(e.proxy); Q(e.gold_base)
                tuple(Q(v) for v in e.gold_coefficients)
            except (ValueError,TypeError,ZeroDivisionError) as exc:
                raise ValueError("all kernel/reward coefficients must be rational") from exc
            if (e.probability(lo)<0 or e.probability(hi)<0
                or e.probability(lo)>1 or e.probability(hi)>1):
                raise ValueError("affine transition probability invalid at an interval endpoint")
            if e.probability(lo)==0 and e.probability(hi)==0:
                raise ValueError("omit identically unavailable transitions")
            groups.setdefault((e.source,e.action),[]).append(e)
        for state in range(self.state_count):
            for action in range(len(self.actions)):
                group=groups.get((state,action),())
                if (not group or
                    sum((Q(e.probability_base) for e in group),Q(0))!=1 or
                    sum((Q(e.probability_slope) for e in group),Q(0))!=0):
                    raise ValueError("each state/action kernel must normalize identically in p")

    def by_state_action(self):
        groups={}
        for e in self.edges:
            groups.setdefault((e.source,e.action),[]).append(e)
        return {key:tuple(v) for key,v in groups.items()}

    def instantiate(self,p):
        """Construct RHT-13 exact ordinary POMDP at a licensed parameter."""
        value=Q(p)
        if not Q(self.parameter_interval[0])<=value<=Q(self.parameter_interval[1]):
            raise ValueError("transition parameter outside licensed range")
        return StochasticRewardGame(
            state_count=self.state_count,actions=self.actions,
            initial=self.initial,gold_parameters=self.gold_parameters,
            edges=tuple(
                StochasticRewardEdge(
                    e.source,e.action,e.target,e.observation,
                    e.probability(value),e.proxy,e.gold_base,
                    e.gold_coefficients
                )
                for e in self.edges if e.probability(value)>0
            ),
            horizon=self.horizon,
        )


def enumerate_observation_policies(game:SharedTransitionGame,*,max_policies=2000):
    """Complete deterministic observation policies for one or two steps."""
    if type(max_policies)is not int or max_policies<1:
        raise ValueError("positive policy census budget required")
    bank=game.by_state_action()
    policies=[]
    for first in range(len(game.actions)):
        if game.horizon==1:
            policies.append(ObservationPolicy(first,(("terminal",ObservationPolicy()),)))
            continue
        responses=tuple(sorted({
            e.observation
            for state,m in enumerate(game.initial) if Q(m)>0
            for e in bank[state,first]
        }))
        for choices in product(range(len(game.actions)),repeat=len(responses)):
            branches=tuple(
                (obs,ObservationPolicy(a)) for obs,a in zip(responses,choices)
            )
            policies.append(ObservationPolicy(first,branches))
            if len(policies)>max_policies:
                raise ValueError("observation policy census exceeded registered budget")
    if len(policies)>max_policies:
        raise ValueError("observation policy census exceeded registered budget")
    return tuple(policies)


@dataclass(frozen=True)
class PolicyPolynomial:
    policy:ObservationPolicy
    proxy:tuple[Q,...]
    gold_base:tuple[Q,...]
    gold_features:tuple[tuple[Q,...],...]

    def gold(self,theta):
        result=self.gold_base
        for p,v in zip(self.gold_features,theta):
            result=_add(result,_scale(p,Q(v)))
        return result


def polynomial_policy_returns(game:SharedTransitionGame,policy:ObservationPolicy):
    """Compute exact polynomials without fixing the transition parameter."""
    bank=game.by_state_action()
    k=len(game.gold_parameters)
    zero=(Q(0),)
    @lru_cache(None)
    def solve(state,node,remaining):
        if remaining==0:
            if node.action is not None or node.branches:
                raise ValueError("nonterminal policy at the declared horizon")
            return zero,zero,(zero,)*k
        if type(node.action)is not int or not 0<=node.action<len(game.actions):
            raise ValueError("mandatory-horizon policy action invalid")
        children=dict(node.branches)
        if len(children)!=len(node.branches):
            raise ValueError("duplicate observation branch")
        p=zero
        b=zero
        feats=[zero]*k
        for e in bank[state,node.action]:
            if remaining==1:
                # The one-step policy terminates after this transition.
                child=children.get(e.observation,ObservationPolicy())
                if child.action is not None or child.branches:
                    raise ValueError("last-step policy must terminate")
                pp,bb,cc=zero,zero,(zero,)*k
            else:
                child=children.get(e.observation)
                if child is None:
                    raise ValueError("policy lacks a potential observation")
                pp,bb,cc=solve(e.target,child,remaining-1)
            probability=(Q(e.probability_base),Q(e.probability_slope))
            p=_add(p,_multiply(probability,_add((Q(e.proxy),),pp)))
            b=_add(b,_multiply(probability,_add((Q(e.gold_base),),bb)))
            for j,coef in enumerate(e.gold_coefficients):
                feats[j]=_add(feats[j],_multiply(
                    probability,_add((Q(coef),),cc[j])
                ))
        return p,b,tuple(feats)

    proxy=zero
    gold_base=zero
    features=[zero]*k
    for state,mass in enumerate(game.initial):
        if not mass:
            continue
        p,b,c=solve(state,policy,game.horizon)
        proxy=_add(proxy,_scale(p,mass))
        gold_base=_add(gold_base,_scale(b,mass))
        for j,v in enumerate(c):
            features[j]=_add(features[j],_scale(v,mass))
    return PolicyPolynomial(policy,proxy,gold_base,tuple(features))


@dataclass(frozen=True)
class SharedKernelRobustCertificate:
    maximum_gold_regret:Q
    worst_transition_probability:Q
    worst_gold_parameters:tuple[Q,...]
    gold_challenger_policy:ObservationPolicy
    proxy_chosen_policy:ObservationPolicy
    worst_expected_proxy_gold:Q
    guaranteed_gold_floor:Q
    maximum_expected_discrepancy_width:Q
    endpoint_only_max_regret:Q
    proxy_optimal_policies:int
    total_policies:int
    polynomial_pairs_checked:int
    passes:bool


def shared_kernel_robust_certificate(
    game:SharedTransitionGame,
    gold_intervals,
    *,
    maximum_allowed_regret=None,
    minimum_proxy_gold_return=None,
    max_policies=2000
):
    """Exact robust regret for degree<=2 under UNIFORM proxy-policy winners.

    The winner set is proven constant on the closed p interval using exact
    quadratic comparisons. Any crossing or isolated new tie forces an
    explicit error, preventing unsound endpoint-only extrapolation.
    """
    try:
        intervals=tuple((Q(lo),Q(hi)) for lo,hi in gold_intervals)
    except (TypeError,ValueError,ZeroDivisionError) as exc:
        raise ValueError("rational gold intervals required") from exc
    if (len(intervals)!=len(game.gold_parameters)
        or any(lo>hi for lo,hi in intervals)):
        raise ValueError("one valid interval per globally identified gold feature")
    low,high=tuple(Q(v) for v in game.parameter_interval)
    policies=enumerate_observation_policies(game,max_policies=max_policies)
    evaluated=tuple(polynomial_policy_returns(game,p) for p in policies)
    mid=(low+high)/2
    candidate=max(evaluated,key=lambda result:_evaluate(result.proxy,mid))
    reference=candidate.proxy
    winners=[]
    for i,policy in enumerate(evaluated):
        diff=_subtract(reference,policy.proxy)
        if diff==(Q(0),):
            winners.append(i)
        elif _quadratic_extreme(diff,(low,high),False)[0]<=0:
            raise ValueError(
                "proxy winner crosses or ties at an isolated kernel value; "
                "constant proxy-optimal set required"
            )
    if not winners:
        raise AssertionError("a proxy-optimal policy must exist")

    gold_vertices=tuple(product(*(
        tuple(sorted(set((lo,hi)))) for lo,hi in intervals
    )))
    best=Q(-1)
    regret_theta=()
    regret_p=low
    regret_i=regret_j=0
    endpoint_only=Q(0)
    floor=None
    width=Q(0)
    counter=0
    for theta in gold_vertices:
        gold=tuple(result.gold(theta) for result in evaluated)
        gaps=tuple(_subtract(result.proxy,g)
                   for result,g in zip(evaluated,gold))
        for j in winners:
            for i in range(len(evaluated)):
                delta=_subtract(gold[i],gold[j])
                value,location=_quadratic_extreme(delta,(low,high),True)
                counter+=1
                if value>best:
                    best,regret_theta,regret_p,regret_i,regret_j=(
                        value,theta,location,i,j
                    )
                endpoint_only=max(endpoint_only,
                                  _evaluate(delta,low),_evaluate(delta,high))
            minimum,_=_quadratic_extreme(gold[j],(low,high),False)
            floor=minimum if floor is None else min(floor,minimum)
        for i in range(len(evaluated)):
            for j in range(len(evaluated)):
                v,_=_quadratic_extreme(
                    _subtract(gaps[i],gaps[j]),(low,high),True
                )
                width=max(width,v)
                counter+=1
    if not 0<=best<=width or floor is None:
        raise AssertionError("robust regret outside full policy discrepancy envelope")
    risk_cap=(None if maximum_allowed_regret is None
              else Q(maximum_allowed_regret))
    floor_cap=(None if minimum_proxy_gold_return is None
               else Q(minimum_proxy_gold_return))
    if risk_cap is not None and risk_cap<0:
        raise ValueError("maximal regret threshold must be nonnegative")
    bad_gold=evaluated[regret_j].gold(regret_theta)
    return SharedKernelRobustCertificate(
        maximum_gold_regret=best,
        worst_transition_probability=regret_p,
        worst_gold_parameters=tuple(regret_theta),
        gold_challenger_policy=evaluated[regret_i].policy,
        proxy_chosen_policy=evaluated[regret_j].policy,
        worst_expected_proxy_gold=_evaluate(bad_gold,regret_p),
        guaranteed_gold_floor=Q(floor),
        maximum_expected_discrepancy_width=width,
        endpoint_only_max_regret=endpoint_only,
        proxy_optimal_policies=len(winners),
        total_policies=len(policies),
        polynomial_pairs_checked=counter,
        passes=(risk_cap is None or best<=risk_cap)
               and (floor_cap is None or Q(floor)>=floor_cap)
    )
