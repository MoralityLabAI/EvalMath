"""RHT-15: exact parametric POMDP reward regret across proxy-policy switches.

The RHT-14 finite mandatory-horizon grammar has one GLOBAL affine
transition parameter p in a rational subinterval of [0,1]. Every
deterministic policy's expected proxy and gold returns are rational
polynomials in p of degree at most two. Gold reward features remain
globally shared and independently licensed in a rational interval box.

RHT-15 removes the requirement that one proxy-optimal policy set stay
constant. Instead it partitions the p interval at EVERY proxy-policy
value crossing, including irrational quadratic roots and isolated
tangencies. For each open region it computes the exact proxy winners;
at every breakpoint it includes ALL tied winners, even policies winning
at a single isolated p. Regret is then maximized over each winner's
closed winning region and the independent gold interval vertices.

Quadratic roots and their reward values are represented as exact
rational-plus-rational-sqrt-rational numbers, compared without floats.
If dyadic rational region isolation or resource caps fail, the solver
raises rather than silently reporting a spurious certificate.

Established parametric-MDP theory supplies the foundations. This is
a small executable exact reference for EvalMath's licensed feedback
and globally coupled kernel grammar, not an arbitrary-horizon solver.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from functools import total_ordering
from itertools import combinations, product
from math import isqrt

from spiral_ln.evaluation_reward_shared_kernel import (
    SharedTransitionGame, enumerate_observation_policies,
    polynomial_policy_returns, _trim, _subtract,
)


def _sgn(x:Q) -> int:
    return (x>0)-(x<0)


def _one_radical_sign(r:Q, c:Q, d:Q) -> int:
    """Exact sign of r+c*sqrt(d), without floating arithmetic."""
    if d<0:
        raise ValueError("negative radicand")
    if d==0 or c==0:
        return _sgn(r)
    if r==0:
        return _sgn(c)
    if _sgn(r)==_sgn(c):
        return _sgn(r)
    return _sgn(r)*_sgn(r*r-c*c*d)


def _two_radical_sign(r:Q,a:Q,d:Q,b:Q,e:Q) -> int:
    """Exact sign of r+a*sqrt(d)+b*sqrt(e)."""
    first=_one_radical_sign(r,a,d)
    second=0 if not b or not e else _sgn(b)
    if first==0:
        return second
    if second==0 or first==second:
        return first
    # When A and B have opposing signs, compare A^2 with B^2.
    squared=_one_radical_sign(
        r*r+a*a*d-b*b*e,2*r*a,d
    )
    return first*squared


def _rational_square_root(n:Q) -> Q | None:
    if n<0:
        raise ValueError("negative square")
    a,b=isqrt(n.numerator),isqrt(n.denominator)
    return Q(a,b) if a*a==n.numerator and b*b==n.denominator else None


@total_ordering
@dataclass(frozen=True,eq=False)
class ExactQuadratic:
    rational:Q=Q(0)
    coefficient:Q=Q(0)
    radicand:Q=Q(0)

    def __post_init__(self):
        r,c,d=Q(self.rational),Q(self.coefficient),Q(self.radicand)
        if d<0:
            raise ValueError("negative real-root radicand")
        sq=_rational_square_root(d)
        if not c or not d or sq is not None:
            r+=c*sq if sq is not None else Q(0)
            c=d=Q(0)
        object.__setattr__(self,"rational",r)
        object.__setattr__(self,"coefficient",c)
        object.__setattr__(self,"radicand",d)

    @staticmethod
    def from_value(value):
        if isinstance(value,ExactQuadratic):
            return value
        if isinstance(value,(int,Q)):
            return ExactQuadratic(Q(value))
        return NotImplemented

    def compare(self,other) -> int:
        other=ExactQuadratic.from_value(other)
        if other is NotImplemented:
            return NotImplemented
        return _two_radical_sign(
            self.rational-other.rational,
            self.coefficient,self.radicand,
            -other.coefficient,other.radicand,
        )

    def __lt__(self,other):
        value=self.compare(other)
        return NotImplemented if value is NotImplemented else value<0

    def __eq__(self,other):
        value=self.compare(other)
        return NotImplemented if value is NotImplemented else value==0

    __hash__=None

    def as_fraction(self) -> Q | None:
        return self.rational if not self.coefficient else None

    def __str__(self) -> str:
        if not self.coefficient:
            return str(self.rational)
        return (
            f"{self.rational} + ({self.coefficient})"
            f"*sqrt({self.radicand})"
        )


def _value(poly,p) -> ExactQuadratic:
    f=_trim(poly)
    if len(f)>3:
        raise ValueError("polynomial degree exceeds two")
    x=ExactQuadratic.from_value(p)
    if x is NotImplemented:
        raise ValueError("unsupported algebraic parameter")
    r,c,d=x.rational,x.coefficient,x.radicand
    linear=f[1] if len(f)>1 else Q(0)
    quadratic=f[2] if len(f)>2 else Q(0)
    return ExactQuadratic(
        f[0]+linear*r+quadratic*(r*r+c*c*d),
        linear*c+quadratic*(2*r*c),
        d
    )


def _poly_roots(poly,low,high):
    """All distinct real quadratic roots inside one closed rational interval."""
    f=_trim(poly)
    lo,hi=ExactQuadratic.from_value(low),ExactQuadratic.from_value(high)
    if len(f)==1:
        return ()
    if len(f)==2:
        roots=(ExactQuadratic(-f[0]/f[1]),)
    else:
        a,b,c=f[2],f[1],f[0]
        discriminant=b*b-4*a*c
        if discriminant<0:
            return ()
        roots=(
            ExactQuadratic(-b/(2*a),Q(1)/(2*a),discriminant),
            ExactQuadratic(-b/(2*a),Q(-1)/(2*a),discriminant)
        )
    out=[]
    for r in sorted(roots):
        if lo<=r<=hi and all(r!=existing for existing in out):
            if _value(f,r)!=0:
                raise AssertionError("algebraic root does not satisfy polynomial")
            out.append(r)
    return tuple(out)


def _fraction_strictly_between(a:ExactQuadratic,b:ExactQuadratic,*,bits=128) -> Q:
    """Find a strictly interior dyadic rational, checked by exact comparisons."""
    if not a<b or a<0 or b>1:
        raise ValueError("ordered roots within the unit interval required")
    for k in range(bits+1):
        den=1<<k
        left,right=0,den
        while left<right:
            mid=(left+right)//2
            if Q(mid,den)<=a:
                left=mid+1
            else:
                right=mid
        if left<=den:
            result=Q(left,den)
            if a<result<b:
                return result
    raise ValueError("algebraic-root separation exhausted exact dyadic budget")


def _extreme_quadratic(poly,lo,hi,*,maximize:bool):
    """Exact extremum on a CLOSED interval with algebraic endpoints."""
    f=_trim(poly)
    if len(f)>3:
        raise ValueError("requires degree <=2")
    low,high=ExactQuadratic.from_value(lo),ExactQuadratic.from_value(hi)
    if low>high:
        raise ValueError("reversed algebraic interval")
    points=[low,high]
    if len(f)==3 and f[2]:
        station=ExactQuadratic(-f[1]/(2*f[2]))
        if low<=station<=high:
            points.append(station)
    candidates=tuple((_value(f,p),p) for p in points)
    current=candidates[0]
    for item in candidates[1:]:
        better=(item[0]>current[0] if maximize
                else item[0]<current[0])
        if better or item[0]==current[0] and item[1]<current[1]:
            current=item
    return current


def _winners(polynomials,p):
    scores=tuple(_value(f,p) for f in polynomials)
    best=max(scores)
    return tuple(i for i,score in enumerate(scores) if score==best)


@dataclass(frozen=True)
class SwitchingRegion:
    left:ExactQuadratic
    right:ExactQuadratic
    interior_sample:Q
    proxy_winning_policy_indices:tuple[int,...]


@dataclass(frozen=True)
class SwitchingKernelCertificate:
    maximum_gold_regret:ExactQuadratic
    worst_transition_probability:ExactQuadratic
    worst_gold_parameters:tuple[Q,...]
    gold_challenger_policy:object
    proxy_chosen_policy:object
    worst_proxy_chosen_gold:ExactQuadratic
    guaranteed_gold_floor:ExactQuadratic
    maximum_expected_discrepancy_width:ExactQuadratic
    endpoint_only_max_regret:ExactQuadratic
    transition_breakpoints:tuple[ExactQuadratic,...]
    proxy_regions:tuple[SwitchingRegion,...]
    isolated_tie_points:tuple[ExactQuadratic,...]
    distinct_proxy_winning_policies:int
    total_policies:int
    polynomial_pairs_checked:int
    passes:bool


def switching_kernel_robust_certificate(
    game:SharedTransitionGame,gold_intervals, *,
    maximum_allowed_regret=None,minimum_proxy_gold_return=None,
    max_policies=2000,max_proxy_comparisons=50000,
    max_reward_comparisons=200000,max_breakpoints=500,
    isolation_bits=128
) -> SwitchingKernelCertificate:
    """Globally exact two-step shared-kernel regret INCLUDING proxy switching.

    Every policy's proxy polynomial is independent of theta. All pairwise
    proxy equality roots partition the transition interval. Inside an
    open cell the proxy-optimal policy set is constant; a rational sample
    determines it exactly. Closed-cell endpoints and all breakpoint
    point-regions include ties, including tangency-only proxy policies.

    For each eligible proxy policy, challengers and independently licensed
    theta vertices are tested using exact algebraic quadratic extrema
    over its closed winning interval. Worst regret and safe gold floor
    are global and certified, not inferred by a p grid or floating solver.
    """
    try:
        intervals=tuple((Q(lo),Q(hi)) for lo,hi in gold_intervals)
    except (ValueError,TypeError,ZeroDivisionError) as exc:
        raise ValueError("rational licensed gold intervals required") from exc
    if (len(intervals)!=len(game.gold_parameters)
        or any(lo>hi for lo,hi in intervals)):
        raise ValueError("one valid interval for every shared gold parameter")
    budgets=(max_policies,max_proxy_comparisons,max_reward_comparisons,
             max_breakpoints,isolation_bits)
    if any(type(x)is not int or x<1 for x in budgets):
        raise ValueError("positive exact polynomial/region budgets required")
    lo,hi=tuple(Q(x) for x in game.parameter_interval)
    policies=enumerate_observation_policies(game,max_policies=max_policies)
    evaluated=tuple(polynomial_policy_returns(game,p) for p in policies)
    proxy=tuple(record.proxy for record in evaluated)
    unique_polys=tuple(dict.fromkeys(proxy))
    if len(unique_polys)*(len(unique_polys)-1)//2>max_proxy_comparisons:
        raise ValueError("pairwise proxy breakpoint budget exceeded")

    boundaries=[ExactQuadratic(lo),ExactQuadratic(hi)]
    for a,b in combinations(unique_polys,2):
        for root in _poly_roots(_subtract(a,b),lo,hi):
            if not any(root==v for v in boundaries):
                boundaries.append(root)
                if len(boundaries)>max_breakpoints:
                    raise ValueError("proxy breakpoint resource cap exceeded")
    boundaries=tuple(sorted(boundaries))
    point_winners=tuple(_winners(proxy,p) for p in boundaries)
    regions=[]
    for left,right in zip(boundaries,boundaries[1:]):
        if left==right:
            continue
        sample=_fraction_strictly_between(left,right,bits=isolation_bits)
        selected=_winners(proxy,sample)
        if any(_value(proxy[j],left)!=max(_value(f,left) for f in proxy)
               or _value(proxy[j],right)!=max(_value(f,right) for f in proxy)
               for j in selected):
            raise AssertionError("proxy optimum lost continuity at a cell boundary")
        regions.append(SwitchingRegion(left,right,sample,selected))
    intervals_regions=tuple(regions)

    isolated=[]
    for i,(point,winners) in enumerate(zip(boundaries,point_winners)):
        surrounding=set()
        if i>0:
            surrounding.update(intervals_regions[i-1].proxy_winning_policy_indices)
        if i<len(intervals_regions):
            surrounding.update(intervals_regions[i].proxy_winning_policy_indices)
        if any(index not in surrounding for index in winners):
            isolated.append(point)

    gold_vertices=tuple(product(*(
        tuple(sorted(set((a,b)))) for a,b in intervals
    )))
    count=0
    best=ExactQuadratic(Q(0))
    worst_p=ExactQuadratic(lo)
    worst_theta=tuple(x[0] for x in intervals)
    best_i=best_j=0
    floor=None
    width=ExactQuadratic(Q(0))
    endpoint=ExactQuadratic(Q(0))
    all_winners=set()
    for winner_list in point_winners:
        all_winners.update(winner_list)
    for region in intervals_regions:
        all_winners.update(region.proxy_winning_policy_indices)

    # Each midpoint cell's winners remain winners on its closed interval.
    # A policy can become eligible solely at a tangent breakpoint; those
    # singleton winner sets are enumerated independently below.
    for theta in gold_vertices:
        gold=tuple(record.gold(theta) for record in evaluated)
        gaps=tuple(_subtract(p,g) for p,g in zip(proxy,gold))
        for i in range(len(evaluated)):
            for j in range(len(evaluated)):
                count+=1
                if count>max_reward_comparisons:
                    raise ValueError("reward-pair enumeration cap exceeded")
                value,_=_extreme_quadratic(
                    _subtract(gaps[i],gaps[j]),boundaries[0],boundaries[-1],
                    maximize=True
                )
                if value>width:
                    width=value
        for region in intervals_regions:
            for j in region.proxy_winning_policy_indices:
                minimum,_=_extreme_quadratic(
                    gold[j],region.left,region.right,maximize=False
                )
                if floor is None or minimum<floor:
                    floor=minimum
                for i in range(len(evaluated)):
                    count+=1
                    if count>max_reward_comparisons:
                        raise ValueError("reward-pair enumeration cap exceeded")
                    value,p=_extreme_quadratic(
                        _subtract(gold[i],gold[j]),
                        region.left,region.right,maximize=True
                    )
                    if value>best:
                        best,worst_p,worst_theta,best_i,best_j=(
                            value,p,tuple(theta),i,j
                        )
        for point,selected in zip(boundaries,point_winners):
            for j in selected:
                chosen=_value(gold[j],point)
                if floor is None or chosen<floor:
                    floor=chosen
                for i in range(len(evaluated)):
                    count+=1
                    if count>max_reward_comparisons:
                        raise ValueError("reward-pair enumeration cap exceeded")
                    value=_value(_subtract(gold[i],gold[j]),point)
                    if value>best:
                        best,worst_p,worst_theta,best_i,best_j=(
                            value,point,tuple(theta),i,j
                        )
            if point==boundaries[0] or point==boundaries[-1]:
                for j in selected:
                    for i in range(len(evaluated)):
                        endpoint=max(endpoint,_value(
                            _subtract(gold[i],gold[j]),point
                        ))
    if floor is None or best<0 or best>width:
        raise AssertionError("robust regret/floor violates exact policy gap envelope")
    risk_cap=(None if maximum_allowed_regret is None
              else ExactQuadratic(Q(maximum_allowed_regret)))
    floor_cap=(None if minimum_proxy_gold_return is None
               else ExactQuadratic(Q(minimum_proxy_gold_return)))
    if risk_cap is not None and risk_cap<0:
        raise ValueError("maximum true regret threshold must be nonnegative")

    return SwitchingKernelCertificate(
        maximum_gold_regret=best,
        worst_transition_probability=worst_p,
        worst_gold_parameters=worst_theta,
        gold_challenger_policy=evaluated[best_i].policy,
        proxy_chosen_policy=evaluated[best_j].policy,
        worst_proxy_chosen_gold=_value(
            evaluated[best_j].gold(worst_theta),worst_p
        ),
        guaranteed_gold_floor=floor,
        maximum_expected_discrepancy_width=width,
        endpoint_only_max_regret=endpoint,
        transition_breakpoints=boundaries,
        proxy_regions=intervals_regions,
        isolated_tie_points=tuple(isolated),
        distinct_proxy_winning_policies=len(all_winners),
        total_policies=len(evaluated),
        polynomial_pairs_checked=count,
        passes=(risk_cap is None or best<=risk_cap)
               and (floor_cap is None or floor>=floor_cap),
    )
