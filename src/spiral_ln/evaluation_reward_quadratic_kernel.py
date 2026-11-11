"""RHT-18: exact parabolic proxy regions for two shared kernel parameters.

This finite reference extends RHT-17's multiaffine proxy/gold grammar to
verified proxy surfaces A0+A1*p+A2*p**2+B*q and gold surfaces
C0+C1*p+C2*p**2+(D0+D1*p)*q. These are the q-affine quadratic
subclass of the actual two-step stochastic policy polynomials.

Each proxy winner j is characterized by inequalities
    (A_j(p)-A_k(p))+(B_j-B_k)*q >= 0.
At fixed p, these give quadratic lower/upper q-boundary curves or
vertical sign constraints. Their intersections have degree at most two,
so all critical p values are rational or quadratic irrational.

On any open p-strip between critical values, the active q envelope
curves are fixed. Gold differences are affine in q; their extrema
occur on an envelope. Substituting quadratic q(p) gives a rational
CUBIC in p. Its stationary points solve a quadratic derivative and
their values are represented exactly by RHT-15's quadratic algebraic
numbers. Every critical vertical slice is checked independently to
preserve isolated/tangency proxy winners.

The result is an exact, capped and narrowly typed nonrectangular
two-parameter robust regret and protected gold-floor certificate.
Source gold and transition uncertainty must be licensed externally.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from itertools import combinations,product

from spiral_ln.evaluation_reward_two_kernel import (
    BiPoly,TwoKernelGame,policy_surface,
)
from spiral_ln.evaluation_reward_shared_kernel import enumerate_observation_policies,_trim
from spiral_ln.evaluation_reward_kernel_switching import (
    ExactQuadratic,_poly_roots,_fraction_strictly_between,
)
from spiral_ln.evaluation_reward_curved_kernel import (
    _add,_mul,_sub,
)


def _quadratic_value(coeffs,p) -> ExactQuadratic:
    p=ExactQuadratic.from_value(p)
    if p is NotImplemented:
        raise ValueError("parameter must be rational or quadratic algebraic")
    total=ExactQuadratic(Q(0))
    for coefficient in reversed(tuple(Q(x) for x in coeffs)):
        total=_add(coefficient,_mul(p,total))
    return total


def _cubic_value(coeffs,p) -> ExactQuadratic:
    if len(_trim(coeffs))>4:
        raise ValueError("cubic boundary oracle received higher-degree polynomial")
    return _quadratic_value_horner(coeffs,p)


def _quadratic_value_horner(coeffs,p):
    total=ExactQuadratic(Q(0))
    for coefficient in reversed(tuple(Q(x) for x in coeffs)):
        total=_add(coefficient,_mul(p,total))
    return total


def _poly_sub(a,b):
    return _trim(tuple(
        (Q(a[i]) if i<len(a) else Q(0))
        -(Q(b[i]) if i<len(b) else Q(0))
        for i in range(max(len(a),len(b)))
    ))


def _poly_add(a,b):
    return _trim(tuple(
        (Q(a[i]) if i<len(a) else Q(0))
        +(Q(b[i]) if i<len(b) else Q(0))
        for i in range(max(len(a),len(b)))
    ))


def _poly_scale(a,v):
    return _trim(tuple(Q(x)*Q(v) for x in a))


def _poly_multiply(a,b):
    result=[Q(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            result[i+j]+=Q(x)*Q(y)
    return _trim(result)


def _polynomial_roots(poly,lo,hi):
    """Exact rational/quadratic algebraic roots within an algebraic interval."""
    roots=_poly_roots(_trim(poly),Q(0),Q(1))
    return tuple(x for x in roots if lo<=x<=hi)


def _proxy_parts(poly:BiPoly):
    if any((i,j) not in ((0,0),(1,0),(2,0),(0,1))
           for i,j,c in poly.terms):
        raise ValueError("proxy must be q-affine with a quadratic p polynomial and constant q coefficient")
    return (
        _trim(tuple(poly.coefficient(i,0) for i in range(3))),
        poly.coefficient(0,1),
    )


def _gold_parts(poly:BiPoly):
    if any((i,j) not in ((0,0),(1,0),(2,0),(0,1),(1,1))
           for i,j,c in poly.terms):
        raise ValueError("gold must have p degree <=2 and q coefficient affine in p")
    return (
        _trim(tuple(poly.coefficient(i,0) for i in range(3))),
        _trim(tuple(poly.coefficient(i,1) for i in range(2))),
    )


def _substitute_gold(poly:BiPoly,curve):
    """Exact cubic gold polynomial on q=curve(p)."""
    a,b=_gold_parts(poly)
    result=_poly_add(a,_poly_multiply(b,curve))
    if len(result)>4:
        raise AssertionError("substituted q-affine quadratic gold must be cubic")
    return result


def _gold_value(poly,p,q):
    a,b=_gold_parts(poly)
    return _add(_quadratic_value(a,p),_mul(_quadratic_value(b,p),q))


def _cubic_extremum(poly,left,right,*,maximize):
    """Exact cubic extremum at endpoints and quadratic derivative roots."""
    f=_trim(poly)
    if len(f)>4 or not left<=right:
        raise ValueError("invalid cubic or interval")
    derivative=_trim(tuple(i*f[i] for i in range(1,len(f))))
    candidates=[left,right]
    if any(derivative):
        candidates.extend(_polynomial_roots(derivative,left,right))
    best=None
    for p in candidates:
        p=ExactQuadratic.from_value(p)
        value=_cubic_value(f,p)
        if (best is None or
            (value>best[0] if maximize else value<best[0])
            or (value==best[0] and p<best[1])):
            best=(value,p)
    return best


def _dedupe_points(points):
    values=[]
    for p in sorted(points):
        if not any(p==other for other in values):
            values.append(p)
    return tuple(values)


def _selected(curves,p,*,maximize):
    found=None
    for curve in curves:
        value=_quadratic_value(curve,p)
        if found is None or (value>found[0] if maximize
                             else value<found[0]):
            found=(value,curve)
    if found is None:
        raise AssertionError("every region needs box-boundary curves")
    return found


@dataclass(frozen=True)
class QuadraticProxyRegion:
    policy_index:int
    breakpoints:tuple[ExactQuadratic,...]
    feasible_strips:tuple[
        tuple[ExactQuadratic,ExactQuadratic,tuple[Q,...],tuple[Q,...]],...
    ]
    vertical_slices:tuple[
        tuple[ExactQuadratic,ExactQuadratic,ExactQuadratic],...
    ]


def quadratic_proxy_winner_region(
    game:TwoKernelGame,proxy_surfaces,policy_index, *,
    max_breakpoints=150
) -> QuadraticProxyRegion:
    """Exact closed q-quadratic winner region, including tie-only slices."""
    if type(max_breakpoints)is not int or max_breakpoints<2:
        raise ValueError("positive root arrangement cap required")
    if not 0<=policy_index<len(proxy_surfaces):
        raise ValueError("unregistered proxy policy")
    pieces=tuple(_proxy_parts(poly) for poly in proxy_surfaces)
    p0,p1=tuple(Q(v) for v in game.p_interval)
    q0,q1=tuple(Q(v) for v in game.q_interval)
    lower=[(Q(q0),)]
    upper=[(Q(q1),)]
    vertical=[]
    own_A,own_B=pieces[policy_index]
    for j,(other_A,other_B) in enumerate(pieces):
        if j==policy_index:
            continue
        diffA=_poly_sub(own_A,other_A)
        diffB=own_B-other_B
        if diffB>0:
            lower.append(_poly_scale(diffA,-Q(1)/diffB))
        elif diffB<0:
            upper.append(_poly_scale(diffA,-Q(1)/diffB))
        else:
            vertical.append(diffA)
    lower=tuple(dict.fromkeys(lower))
    upper=tuple(dict.fromkeys(upper))
    lo,hi=ExactQuadratic(p0),ExactQuadratic(p1)
    roots=[lo,hi]
    allcurves=tuple(dict.fromkeys(lower+upper))
    for first,second in combinations(allcurves,2):
        roots.extend(_polynomial_roots(_poly_sub(first,second),lo,hi))
    for constraint in vertical:
        roots.extend(_polynomial_roots(constraint,lo,hi))
    critical=_dedupe_points(roots)
    if len(critical)>max_breakpoints:
        raise ValueError("quadratic proxy root arrangement exceeded cap")
    slices=[]
    strips=[]
    def feasible(p):
        if any(_quadratic_value(c,p)<0 for c in vertical):
            return None
        low=_selected(lower,p,maximize=True)
        high=_selected(upper,p,maximize=False)
        return (low,high) if low[0]<=high[0] else None
    for p in critical:
        result=feasible(p)
        if result is not None:
            low,high=result
            slices.append((p,low[0],high[0]))
    for left,right in zip(critical,critical[1:]):
        if not left<right:
            continue
        sample=_fraction_strictly_between(left,right)
        result=feasible(sample)
        if result is not None:
            low,high=result
            strips.append((left,right,low[1],high[1]))
    return QuadraticProxyRegion(policy_index,critical,tuple(strips),tuple(slices))


def quadratic_region_extreme(poly:BiPoly,region:QuadraticProxyRegion,*,maximize):
    """Sharp exact q-affine gold extremum on a closed quadratic region."""
    _gold_parts(poly)
    best=None
    def register(value,p,q):
        nonlocal best
        point=(p,q)
        if (best is None or
            (value>best[0] if maximize else value<best[0])
            or (value==best[0] and point<best[1])):
            best=(value,point)
    for p,low,high in region.vertical_slices:
        for q in (low,high):
            register(_gold_value(poly,p,q),p,q)
    for left,right,curve_low,curve_high in region.feasible_strips:
        for curve in (curve_low,curve_high):
            substitute=_substitute_gold(poly,curve)
            value,p=_cubic_extremum(
                substitute,left,right,maximize=maximize
            )
            q=_quadratic_value(curve,p)
            register(value,p,q)
    return best


def _full_rectangle_region(game):
    p0,p1=tuple(Q(x) for x in game.p_interval)
    q0,q1=tuple(Q(x) for x in game.q_interval)
    left,right=ExactQuadratic(p0),ExactQuadratic(p1)
    strips=(() if left==right else
            ((left,right,(q0,),(q1,)),))
    return QuadraticProxyRegion(
        -1,(left,right) if left!=right else (left,),
        strips,((left,ExactQuadratic(q0),ExactQuadratic(q1)),
                (right,ExactQuadratic(q0),ExactQuadratic(q1)))
    )


@dataclass(frozen=True)
class QuadraticRegionCertificate:
    maximum_gold_regret:ExactQuadratic
    worst_transition_parameters:tuple[ExactQuadratic,ExactQuadratic]
    worst_gold_parameters:tuple[Q,...]
    challenger_policy:object
    proxy_chosen_policy:object
    guaranteed_gold_floor:ExactQuadratic
    worst_proxy_gold:ExactQuadratic
    maximum_expected_discrepancy_width:ExactQuadratic
    rectangle_corner_only_regret:Q
    winning_regions:tuple[QuadraticProxyRegion,...]
    policy_count:int
    reward_pair_checks:int
    passes:bool


def quadratic_kernel_robust_certificate(
    game:TwoKernelGame,gold_intervals, *,
    maximum_allowed_regret=None,minimum_proxy_gold_return=None,
    max_policies=100,max_reward_pairs=30000,max_breakpoints=150
) -> QuadraticRegionCertificate:
    """Exact robust two-parameter kernel regret for verified q-quadratic proxy."""
    try:
        intervals=tuple((Q(lo),Q(hi)) for lo,hi in gold_intervals)
    except (TypeError,ValueError,ZeroDivisionError) as exc:
        raise ValueError("true gold feature intervals must be rational") from exc
    if (len(intervals)!=len(game.gold_parameters)
        or any(lo>hi for lo,hi in intervals)):
        raise ValueError("one ordered licensed interval per shared gold parameter")
    if any(type(n)is not int or n<1 for n in
           (max_policies,max_reward_pairs,max_breakpoints)):
        raise ValueError("positive exact policy and region search budget required")
    policies=enumerate_observation_policies(game,max_policies=max_policies)
    surfaces=tuple(policy_surface(game,p) for p in policies)
    proxy=tuple(s.proxy for s in surfaces)
    for p in proxy:
        _proxy_parts(p)
    for s in surfaces:
        _gold_parts(s.gold_base)
        for feature in s.gold_features:
            _gold_parts(feature)
    # Reuse one geometry per distinct proxy polynomial.
    unique=tuple(dict.fromkeys(proxy))
    templates={}
    for index,p in enumerate(unique):
        templates[p]=quadratic_proxy_winner_region(
            game,unique,index,max_breakpoints=max_breakpoints
        )
    regions=tuple(QuadraticProxyRegion(
        i,templates[p].breakpoints,
        templates[p].feasible_strips,
        templates[p].vertical_slices,
    ) for i,p in enumerate(proxy) if (
        templates[p].feasible_strips or templates[p].vertical_slices
    ))
    if not regions:
        raise AssertionError("some proxy policy must win on the parameter rectangle")
    theta_vertices=tuple(product(*(
        tuple(sorted(set((lo,hi)))) for lo,hi in intervals
    )))
    corners=tuple(product(
        tuple(Q(x) for x in game.p_interval),
        tuple(Q(x) for x in game.q_interval),
    ))
    full=_full_rectangle_region(game)
    best=ExactQuadratic(Q(0))
    witness=(ExactQuadratic(corners[0][0]),ExactQuadratic(corners[0][1]))
    chosen_theta=theta_vertices[0]
    selection=(0,0)
    floor=None
    width=ExactQuadratic(Q(0))
    corner_risk=Q(0)
    checked=0
    for theta in theta_vertices:
        gold=tuple(s.gold(theta) for s in surfaces)
        gap=tuple(a-b for a,b in zip(proxy,gold))
        for i in range(len(surfaces)):
            for j in range(len(surfaces)):
                checked+=1
                if checked>max_reward_pairs:
                    raise ValueError("full policy gap comparison exceeded resource budget")
                value,_=quadratic_region_extreme(
                    gap[i]-gap[j],full,maximize=True
                )
                if value>width:
                    width=value
        for region in regions:
            j=region.policy_index
            low=quadratic_region_extreme(gold[j],region,maximize=False)
            if low is None:
                raise AssertionError("eligible proxy region must be nonempty")
            if floor is None or low[0]<floor:
                floor=low[0]
            for i in range(len(surfaces)):
                checked+=1
                if checked>max_reward_pairs:
                    raise ValueError("proxy regret pair comparison exceeded resource budget")
                value,point=quadratic_region_extreme(
                    gold[i]-gold[j],region,maximize=True
                )
                if value>best:
                    best,witness,chosen_theta,selection=value,point,theta,(i,j)
        for p,q in corners:
            scores=tuple(s.value(p,q) for s in proxy)
            winner=max(scores)
            winning=tuple(j for j,v in enumerate(scores) if v==winner)
            for j in winning:
                for i in range(len(surfaces)):
                    corner_risk=max(
                        corner_risk,gold[i].value(p,q)-gold[j].value(p,q)
                    )
    if floor is None or best<0 or best>width:
        raise AssertionError("exact gold regret is outside full policy gap envelope")
    cap=None if maximum_allowed_regret is None else ExactQuadratic(
        Q(maximum_allowed_regret)
    )
    minimum=None if minimum_proxy_gold_return is None else ExactQuadratic(
        Q(minimum_proxy_gold_return)
    )
    if cap is not None and cap<0:
        raise ValueError("maximum allowed gold regret must be nonnegative")
    return QuadraticRegionCertificate(
        maximum_gold_regret=best,
        worst_transition_parameters=witness,
        worst_gold_parameters=tuple(chosen_theta),
        challenger_policy=surfaces[selection[0]].policy,
        proxy_chosen_policy=surfaces[selection[1]].policy,
        guaranteed_gold_floor=floor,
        worst_proxy_gold=_gold_value(surfaces[selection[1]].gold(chosen_theta),*witness),
        maximum_expected_discrepancy_width=width,
        rectangle_corner_only_regret=corner_risk,
        winning_regions=regions,
        policy_count=len(surfaces),
        reward_pair_checks=checked,
        passes=(cap is None or best<=cap)
               and (minimum is None or floor>=minimum),
    )
