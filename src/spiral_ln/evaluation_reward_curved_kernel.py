"""RHT-17: exact curved proxy-policy regions in a two-parameter POMDP.

Extends RHT-16's finite two-step game grammar to MULTIAFFINE proxy
and gold policy surfaces: A+B*p+C*q+D*p*q. Every conditional kernel
remains affine in globally shared (p,q), with its normalization and
rectangle corner nonnegativity checked upstream.

A proxy policy j wins on intersections of bilinear inequalities
H_jk(p,q)=a+b*p+c*q+d*p*q >= 0. Each inequality is linear in q
after fixing p. Project the arrangement to the p-axis using:
  - q coefficient zeros c+d*p=0;
  - intersections of H_jk with q box endpoints;
  - pairwise bilinear-boundary intersections (quadratic resultants).
This partitions the p interval into exact rational/quadratic-irrational
breakpoints. Inside each open strip, feasible q ranges between two
fixed rational-linear-fractional envelopes. At critical p values,
a separate exact vertical-slice test retains isolated tie-only winners.

On an envelope q(p)=-(a+b*p)/(c+d*p), a bilinear gold difference
becomes a quadratic-over-linear rational function; its derivative is
a rational quadratic. Checking the strip endpoints and all stationary
points gives its exact global extrema. Algebraic values are represented
as rational-plus-rational-sqrt-rational numbers and compared exactly.

For every independently licensed gold-interval vertex and every
proxy-winning policy, compute exact challenger regret, gold floor and
parameter witnesses. Full expected proxy/gold discrepancy width
remains multi-affine, and is checked at parameter-box corners.

This is a narrow exact semialgebraic reference, with capped policy,
region and reward comparisons. It does not claim an efficient solution
to general parametric POMDPs or certify any external gold model.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from itertools import product

from spiral_ln.evaluation_reward_two_kernel import (
    BiPoly,TwoKernelGame,policy_surface,
)
from spiral_ln.evaluation_reward_shared_kernel import enumerate_observation_policies
from spiral_ln.evaluation_reward_kernel_switching import (
    ExactQuadratic,_poly_roots,_fraction_strictly_between,
)


def _alg(v):
    return ExactQuadratic.from_value(v)


def _add(x,y):
    a,b=_alg(x),_alg(y)
    if a is NotImplemented or b is NotImplemented:
        raise ValueError("unsupported quadratic-algebraic value")
    if a.coefficient and b.coefficient and a.radicand!=b.radicand:
        raise ValueError("mixed independent algebraic fields are unsupported")
    rad=a.radicand if a.coefficient else b.radicand
    return ExactQuadratic(a.rational+b.rational,
                          a.coefficient+b.coefficient,rad)


def _neg(x):
    a=_alg(x)
    return ExactQuadratic(-a.rational,-a.coefficient,a.radicand)


def _sub(x,y):
    return _add(x,_neg(y))


def _mul(x,y):
    a,b=_alg(x),_alg(y)
    if a.coefficient and b.coefficient and a.radicand!=b.radicand:
        raise ValueError("mixed independent algebraic fields are unsupported")
    rad=a.radicand if a.coefficient else b.radicand
    return ExactQuadratic(
        a.rational*b.rational+a.coefficient*b.coefficient*rad,
        a.rational*b.coefficient+a.coefficient*b.rational,rad
    )


def _inverse(x):
    a=_alg(x)
    denominator=a.rational*a.rational-a.coefficient*a.coefficient*a.radicand
    if denominator==0:
        raise ValueError("zero algebraic denominator")
    return ExactQuadratic(a.rational/denominator,
                          -a.coefficient/denominator,a.radicand)


def _div(x,y):
    return _mul(x,_inverse(y))


def _lin(a,b,p):
    return _add(a,_mul(b,p))


def _evaluate(poly,p,q):
    a,b,c,d=(poly.coefficient(*powers)
             for powers in ((0,0),(1,0),(0,1),(1,1)))
    return _add(_add(a,_mul(b,p)),_mul(_add(c,_mul(d,p)),q))


def _linear_root(a,b,lower,upper):
    if b==0:
        return ()
    root=ExactQuadratic(-Q(a)/Q(b))
    return (root,) if lower<=root<=upper else ()


def _quadratic_roots(values,lower,upper):
    return tuple(root for root in _poly_roots(values,Q(0),Q(1))
                 if lower<=root<=upper)


def _constraint(poly):
    return tuple(poly.coefficient(*powers)
                 for powers in ((0,0),(1,0),(0,1),(1,1)))


def _bound_value(bound,p):
    a,b,c,d=bound
    n=_lin(a,b,p)
    s=_lin(c,d,p)
    if s==0:
        if n==0 and d:
            return ExactQuadratic(-Q(b)/Q(d))
        raise ValueError("unbounded switching curve at critical parameter")
    return _div(_neg(n),s)


def _vertical_slice(constraints,p,q0,q1):
    """Exact gold-valid q endpoints at a fixed possibly irrational p."""
    low=(ExactQuadratic(Q(q0)),(-Q(q0),Q(0),Q(1),Q(0)))
    high=(ExactQuadratic(Q(q1)),(-Q(q1),Q(0),Q(1),Q(0)))
    for bound in constraints:
        a,b,c,d=bound
        n,s=_lin(a,b,p),_lin(c,d,p)
        if s==0:
            if n<0:
                return None
            continue
        q=_div(_neg(n),s)
        if s>0 and q>low[0]:
            low=(q,bound)
        elif s<0 and q<high[0]:
            high=(q,bound)
        if low[0]>high[0]:
            return None
    return low,high


def _critical_points(constraints,p0,p1,q0,q1, *,max_roots):
    """All p events where the order/type of q boundary can change."""
    lo,hi=ExactQuadratic(Q(p0)),ExactQuadratic(Q(p1))
    critical=[lo,hi]
    def include(points):
        for root in points:
            if not any(root==x for x in critical):
                critical.append(root)
                if len(critical)>max_roots:
                    raise ValueError("curved proxy arrangement root cap exceeded")
    for a,b,c,d in constraints:
        include(_linear_root(c,d,lo,hi))
        for q in (q0,q1):
            include(_linear_root(a+c*q,b+d*q,lo,hi))
    for i,left in enumerate(constraints):
        a,b,c,d=left
        for right in constraints[i+1:]:
            e,f,g,h=right
            # (a+b*p)*(g+h*p)-(e+f*p)*(c+d*p)=0.
            resultant=(a*g-e*c,
                       a*h+b*g-e*d-f*c,
                       b*h-f*d)
            if any(resultant):
                include(_quadratic_roots(resultant,lo,hi))
    return tuple(sorted(critical))


def _ratio_extremum(poly,bound,left,right, *,maximize):
    """Exact bilinear-on-rational-curve extrema within one closed strip."""
    a,b,c,d=_constraint(poly)
    A,B,C,D=bound
    # (a+b*p)* (C+D*p) - (c+d*p)*(A+B*p)
    numerator=(a*C-c*A,
               a*D+b*C-c*B-d*A,
               b*D-d*B)
    denominator=(C,D)
    # (N' D - N D') has degree at most two.
    derivative=(
        numerator[1]*C-numerator[0]*D,
        2*numerator[2]*C,
        numerator[2]*D
    )
    candidates=[left,right]
    if any(derivative):
        candidates.extend(_quadratic_roots(derivative,left,right))
    best=None
    for p in candidates:
        q=_bound_value(bound,p)
        value=_evaluate(poly,p,q)
        if best is None or (
            value>best[0] if maximize else value<best[0]
        ) or value==best[0] and (p,q)<best[1]:
            best=(value,(p,q))
    return best


@dataclass(frozen=True)
class CurvedWinnerRegion:
    policy_index:int
    critical_p:tuple[ExactQuadratic,...]
    feasible_strips:tuple[
        tuple[ExactQuadratic,ExactQuadratic,tuple[Q,Q,Q,Q],tuple[Q,Q,Q,Q]],...
    ]
    feasible_vertical_slices:tuple[
        tuple[ExactQuadratic,ExactQuadratic,ExactQuadratic],...
    ]


def curved_winner_region(game,proxy_surfaces,index,*,max_roots=100):
    """Exact bilinear proxy-winning semialgebraic region, including ties."""
    p0,p1=tuple(Q(v) for v in game.p_interval)
    q0,q1=tuple(Q(v) for v in game.q_interval)
    if not all(v.multiaffine for v in proxy_surfaces):
        raise ValueError("proxy policy surfaces must be multiaffine")
    constraints=tuple(dict.fromkeys(
        _constraint(proxy_surfaces[index]-other)
        for other in proxy_surfaces
        if proxy_surfaces[index]!=other
    ))
    critical=_critical_points(
        constraints,p0,p1,q0,q1,max_roots=max_roots
    )
    slices=[]
    for p in critical:
        result=_vertical_slice(constraints,p,q0,q1)
        if result is not None:
            low,high=result
            slices.append((p,low[0],high[0]))
    strips=[]
    for left,right in zip(critical,critical[1:]):
        if not left<right:
            continue
        sample=_fraction_strictly_between(left,right)
        result=_vertical_slice(constraints,sample,q0,q1)
        if result is None:
            continue
        lo,hi=result
        strips.append((left,right,lo[1],hi[1]))
    return CurvedWinnerRegion(
        policy_index=index,critical_p=critical,
        feasible_strips=tuple(strips),
        feasible_vertical_slices=tuple(slices),
    )


def curved_region_extreme(poly,region,*,maximize):
    """Exact extremum of multiaffine reward over one closed winner region."""
    if not poly.multiaffine:
        raise ValueError("gold reward must be multiaffine")
    best=None
    def record(value,point):
        nonlocal best
        if best is None or (
            value>best[0] if maximize else value<best[0]
        ) or value==best[0] and point<best[1]:
            best=(value,point)
    for p,low,high in region.feasible_vertical_slices:
        for q in (low,high):
            record(_evaluate(poly,p,q),(p,q))
    for left,right,lower,upper in region.feasible_strips:
        for boundary in (lower,upper):
            value,point=_ratio_extremum(
                poly,boundary,left,right,maximize=maximize
            )
            record(value,point)
    return best


@dataclass(frozen=True)
class CurvedKernelCertificate:
    maximum_gold_regret:ExactQuadratic
    worst_transition_parameters:tuple[ExactQuadratic,ExactQuadratic]
    worst_gold_parameters:tuple[Q,...]
    challenger_policy:object
    proxy_chosen_policy:object
    guaranteed_gold_floor:ExactQuadratic
    worst_proxy_gold:ExactQuadratic
    maximum_expected_discrepancy_width:Q
    rectangle_corner_only_regret:Q
    winning_regions:tuple[CurvedWinnerRegion,...]
    policies_enumerated:int
    exact_reward_pairs_checked:int
    passes:bool


def curved_kernel_robust_certificate(
    game:TwoKernelGame,gold_intervals, *,
    maximum_allowed_regret=None,minimum_proxy_gold_return=None,
    max_policies=100,max_reward_pairs=20000,max_roots=100
):
    """Sharp exact 2D robust regret for multiaffine proxy and gold surfaces."""
    try:
        intervals=tuple((Q(lo),Q(hi)) for lo,hi in gold_intervals)
    except (ValueError,TypeError,ZeroDivisionError) as exc:
        raise ValueError("licensed true reward interval values must be rational") from exc
    if len(intervals)!=len(game.gold_parameters) or any(lo>hi for lo,hi in intervals):
        raise ValueError("one ordered gold interval per source feature required")
    if any(type(v)is not int or v<1 for v in
           (max_policies,max_reward_pairs,max_roots)):
        raise ValueError("positive exact solver resource caps required")
    policies=enumerate_observation_policies(game,max_policies=max_policies)
    surfaces=tuple(policy_surface(game,pi) for pi in policies)
    if any(not (
        s.proxy.multiaffine and s.gold_base.multiaffine
        and all(f.multiaffine for f in s.gold_features)
    ) for s in surfaces):
        raise ValueError("non-multiaffine expected proxy or gold surface outside exact solver class")
    proxy=tuple(s.proxy for s in surfaces)
    unique=tuple(dict.fromkeys(proxy))
    # Build each distinct proxy winner region once; identical proxy
    # polynomials share the same geometric eligibility but different gold.
    proto={}
    for i,surface in enumerate(proxy):
        if surface not in proto:
            proto[surface]=curved_winner_region(
                game,unique,unique.index(surface),max_roots=max_roots
            )
    winners=tuple(
        CurvedWinnerRegion(
            policy_index=i,
            critical_p=proto[surface].critical_p,
            feasible_strips=proto[surface].feasible_strips,
            feasible_vertical_slices=proto[surface].feasible_vertical_slices,
        )
        for i,surface in enumerate(proxy)
        if (proto[surface].feasible_strips or
            proto[surface].feasible_vertical_slices)
    )
    if not winners:
        raise AssertionError("at least one proxy policy must win at some parameter")
    vertices=tuple(product(*(tuple(sorted(set((lo,hi))))
                             for lo,hi in intervals)))
    corners=tuple(product(
        tuple(Q(v) for v in game.p_interval),
        tuple(Q(v) for v in game.q_interval)
    ))
    maximum=ExactQuadratic(Q(0))
    worst_point=(ExactQuadratic(Q(corners[0][0])),
                 ExactQuadratic(Q(corners[0][1])))
    worst_theta=vertices[0]
    pair=(0,0)
    floor=None
    width=Q(0)
    corner_regret=Q(0)
    counter=0
    for theta in vertices:
        gold=tuple(surface.gold(theta) for surface in surfaces)
        gaps=tuple(px-g for px,g in zip(proxy,gold))
        for a in range(len(surfaces)):
            for b in range(len(surfaces)):
                counter+=1
                if counter>max_reward_pairs:
                    raise ValueError("discrepancy pair comparison cap exceeded")
                diff=gaps[a]-gaps[b]
                width=max(width,*(diff.value(*pt) for pt in corners))
        for region in winners:
            j=region.policy_index
            best_low=curved_region_extreme(gold[j],region,maximize=False)
            if best_low is None:
                raise AssertionError("declared winner must have nonempty parameter region")
            if floor is None or best_low[0]<floor:
                floor=best_low[0]
            for i in range(len(surfaces)):
                counter+=1
                if counter>max_reward_pairs:
                    raise ValueError("regret pair comparison cap exceeded")
                value,point=curved_region_extreme(
                    gold[i]-gold[j],region,maximize=True
                )
                if value>maximum:
                    maximum,worst_point,worst_theta,pair=(
                        value,point,theta,(i,j)
                    )
        for p,q in corners:
            scores=tuple(px.value(p,q) for px in proxy)
            winning=max(scores)
            eligible=tuple(j for j,score in enumerate(scores)
                           if score==winning)
            for j in eligible:
                for i in range(len(surfaces)):
                    corner_regret=max(corner_regret,
                        gold[i].value(p,q)-gold[j].value(p,q))
    if floor is None or maximum<0 or maximum>width:
        raise AssertionError("robust risk violates expected policy gap envelope")
    risk_limit=None if maximum_allowed_regret is None else ExactQuadratic(
        Q(maximum_allowed_regret)
    )
    min_gold=None if minimum_proxy_gold_return is None else ExactQuadratic(
        Q(minimum_proxy_gold_return)
    )
    if risk_limit is not None and risk_limit<0:
        raise ValueError("maximum regret bound must be nonnegative")
    return CurvedKernelCertificate(
        maximum_gold_regret=maximum,
        worst_transition_parameters=worst_point,
        worst_gold_parameters=tuple(worst_theta),
        challenger_policy=surfaces[pair[0]].policy,
        proxy_chosen_policy=surfaces[pair[1]].policy,
        guaranteed_gold_floor=floor,
        worst_proxy_gold=_evaluate(
            surfaces[pair[1]].gold(worst_theta),*worst_point
        ),
        maximum_expected_discrepancy_width=width,
        rectangle_corner_only_regret=corner_regret,
        winning_regions=winners,
        policies_enumerated=len(surfaces),
        exact_reward_pairs_checked=counter,
        passes=(risk_limit is None or maximum<=risk_limit)
               and (min_gold is None or floor>=min_gold),
    )
