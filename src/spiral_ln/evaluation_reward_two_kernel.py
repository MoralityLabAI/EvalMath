"""RHT-16: exact two-parameter proxy-switching and gold-regret certificate.

Two globally shared uncertain affine transition parameters (p,q) are
licensed in a rational rectangle. Each conditional probability is
base + slope_p*p + slope_q*q, with nonnegative normalized kernels
verified exactly on the rectangle's corners.

For at-most-two-step observation policies, proxy/gold expectations are
computed symbolically. This reference solver requires every proxy-policy
return to be AFFINE in (p,q), and every gold-policy return to be
MULTIAFFINE (1,p,q,p*q). These polynomial-degree contracts are checked
for every policy and feature, rather than assumed. A failing instance
raises and cannot obtain a false exact certificate.

Every proxy policy j is eligible on the convex polygon where its affine
score dominates every other policy. Exact rational halfplane clipping
constructs these polygons, including lower-dimensional tie-only regions.
For each gold interval vertex and challenger i, the worst gold regret
is the maximum of the bilinear difference Gold_i-Gold_j on j's polygon.

A bilinear function on a compact polygon attains a maximum on its
boundary: if the mixed coefficient is nonzero the interior stationary
point is a saddle; otherwise the function is affine. Restricting the
bilinear function to a polygon edge yields a univariate quadratic,
whose exact extremum occurs at endpoints or a rational stationary point.

This gives a finite exact robust-regret, gold-floor and full-policy
discrepancy-width certificate with NO floating-point safety decisions.
The code is a narrow parameter synthesis baseline, not a general
polynomial-time method for multi-parameter robust POMDPs or a
real-model alignment claim.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from itertools import product

from spiral_ln.evaluation_reward_shared_kernel import (
    enumerate_observation_policies,
)
from spiral_ln.evaluation_reward_stochastic_closure import (
    ObservationPolicy,StochasticRewardGame,StochasticRewardEdge,
)


@dataclass(frozen=True)
class BiPoly:
    """Sparse exact rational polynomial in two globally shared parameters."""
    terms:tuple[tuple[int,int,Q],...]=()

    def __post_init__(self):
        combined={}
        for i,j,c in self.terms:
            if type(i)is not int or type(j)is not int or i<0 or j<0:
                raise ValueError("polynomial exponents must be nonnegative integers")
            combined[(i,j)]=combined.get((i,j),Q(0))+Q(c)
        object.__setattr__(self,"terms",tuple(sorted(
            (i,j,c) for (i,j),c in combined.items() if c
        )))

    @staticmethod
    def constant(value):
        return BiPoly(((0,0,Q(value)),))

    def __add__(self,other):
        if not isinstance(other,BiPoly):
            return NotImplemented
        return BiPoly(self.terms+other.terms)

    def __neg__(self):
        return BiPoly(tuple((i,j,-c) for i,j,c in self.terms))

    def __sub__(self,other):
        return self+(-other)

    def __mul__(self,other):
        if not isinstance(other,BiPoly):
            return NotImplemented
        return BiPoly(tuple(
            (i+k,j+l,c*d)
            for i,j,c in self.terms
            for k,l,d in other.terms
        ))

    def scale(self,value):
        return BiPoly(tuple((i,j,c*Q(value)) for i,j,c in self.terms))

    def value(self,p,q) -> Q:
        x,y=Q(p),Q(q)
        return sum((c*x**i*y**j for i,j,c in self.terms),Q(0))

    def coefficient(self,i,j):
        return next((c for a,b,c in self.terms if a==i and b==j),Q(0))

    @property
    def affine(self):
        return all((i,j) in ((0,0),(1,0),(0,1))
                   for i,j,_ in self.terms)

    @property
    def multiaffine(self):
        return all(i<=1 and j<=1 for i,j,_ in self.terms)


ZERO=BiPoly()
ONE=BiPoly.constant(1)


@dataclass(frozen=True)
class TwoKernelEdge:
    source:int
    action:int
    target:int
    observation:str
    probability_base:Q
    probability_p:Q=Q(0)
    probability_q:Q=Q(0)
    proxy:Q=Q(0)
    gold_base:Q=Q(0)
    gold_coefficients:tuple[Q,...]=()

    def probability(self,p,q):
        return (Q(self.probability_base)+Q(self.probability_p)*Q(p)
                +Q(self.probability_q)*Q(q))

    @property
    def symbolic(self):
        return BiPoly((
            (0,0,Q(self.probability_base)),
            (1,0,Q(self.probability_p)),
            (0,1,Q(self.probability_q)),
        ))


@dataclass(frozen=True)
class TwoKernelGame:
    state_count:int
    actions:tuple[str,...]
    initial:tuple[Q,...]
    gold_parameters:tuple[str,...]
    p_interval:tuple[Q,Q]
    q_interval:tuple[Q,Q]
    edges:tuple[TwoKernelEdge,...]
    horizon:int=2

    def __post_init__(self):
        if (type(self.state_count)is not int or not 1<=self.state_count<=12
            or type(self.horizon)is not int or not 1<=self.horizon<=2
            or not self.actions or len(set(self.actions))!=len(self.actions)
            or any(not isinstance(a,str) or not a for a in self.actions)
            or not self.gold_parameters or len(set(self.gold_parameters))!=len(self.gold_parameters)
            or len(self.gold_parameters)>4
            or not self.edges):
            raise ValueError("two-parameter seed requires finite hidden states/actions/features")
        try:
            prior=tuple(Q(v) for v in self.initial)
            pp=tuple(Q(v) for v in self.p_interval)
            qq=tuple(Q(v) for v in self.q_interval)
        except (TypeError,ValueError,ZeroDivisionError) as exc:
            raise ValueError("probabilities and parameter intervals must be rational") from exc
        if (len(prior)!=self.state_count or any(x<0 for x in prior)
            or sum(prior)!=1 or len(pp)!=2 or len(qq)!=2
            or not 0<=pp[0]<=pp[1]<=1 or not 0<=qq[0]<=qq[1]<=1):
            raise ValueError("normalized prior and parameter boxes within [0,1] required")
        groups={}
        for e in self.edges:
            if (type(e.source)is not int or not 0<=e.source<self.state_count
                or type(e.target)is not int or not 0<=e.target<self.state_count
                or type(e.action)is not int or not 0<=e.action<len(self.actions)
                or not isinstance(e.observation,str) or not e.observation
                or len(e.gold_coefficients)!=len(self.gold_parameters)):
                raise ValueError("invalid typed two-parameter transition")
            try:
                for v in (e.probability_base,e.probability_p,e.probability_q,
                          e.proxy,e.gold_base,*e.gold_coefficients):
                    Q(v)
            except (TypeError,ValueError,ZeroDivisionError) as exc:
                raise ValueError("transition values must be finite rational numbers") from exc
            for p,q in product(pp,qq):
                if not 0<=e.probability(p,q)<=1:
                    raise ValueError("affine probability outside unit interval at box corner")
            if all(e.probability(p,q)==0 for p,q in product(pp,qq)):
                raise ValueError("omit identically zero-probability transitions")
            groups.setdefault((e.source,e.action),[]).append(e)
        for s in range(self.state_count):
            for a in range(len(self.actions)):
                group=groups.get((s,a),())
                if not group or (sum((Q(e.probability_base) for e in group),Q(0))!=1
                                 or sum((Q(e.probability_p) for e in group),Q(0))!=0
                                 or sum((Q(e.probability_q) for e in group),Q(0))!=0):
                    raise ValueError("conditional kernel must normalize identically in p,q")

    def by_state_action(self):
        groups={}
        for e in self.edges:
            groups.setdefault((e.source,e.action),[]).append(e)
        return {k:tuple(v) for k,v in groups.items()}

    def instantiate(self,p,q):
        x,y=Q(p),Q(q)
        if not (Q(self.p_interval[0])<=x<=Q(self.p_interval[1])
                and Q(self.q_interval[0])<=y<=Q(self.q_interval[1])):
            raise ValueError("transition parameters outside licensed rectangle")
        return StochasticRewardGame(
            self.state_count,self.actions,self.initial,self.gold_parameters,
            tuple(
                StochasticRewardEdge(
                    e.source,e.action,e.target,e.observation,
                    e.probability(x,y),e.proxy,e.gold_base,e.gold_coefficients
                ) for e in self.edges if e.probability(x,y)>0
            ),self.horizon
        )


@dataclass(frozen=True)
class PolicySurface:
    policy:ObservationPolicy
    proxy:BiPoly
    gold_base:BiPoly
    gold_features:tuple[BiPoly,...]

    def gold(self,theta):
        return self.gold_base+sum((
            f.scale(v) for f,v in zip(self.gold_features,theta)
        ),ZERO)


def policy_surface(game:TwoKernelGame,policy:ObservationPolicy) -> PolicySurface:
    """Independently sum all conditional worlds as symbolic p,q polynomials."""
    bank=game.by_state_action()
    k=len(game.gold_parameters)
    def visit(s,node,remaining):
        if remaining==0:
            if node.action is not None or node.branches:
                raise ValueError("nonterminal policy at horizon")
            return ZERO,ZERO,(ZERO,)*k
        if type(node.action)is not int or not 0<=node.action<len(game.actions):
            raise ValueError("unregistered observation-policy action")
        branches=dict(node.branches)
        if len(branches)!=len(node.branches):
            raise ValueError("duplicated observation-policy branch")
        p=b=ZERO
        feats=[ZERO]*k
        for e in bank[s,node.action]:
            if remaining==1:
                pp,bb,ff=ZERO,ZERO,(ZERO,)*k
                child=branches.get(e.observation,ObservationPolicy())
                if child.action is not None or child.branches:
                    raise ValueError("nonterminal last-step branch")
            else:
                child=branches.get(e.observation)
                if child is None:
                    raise ValueError("policy omits an allowed observation")
                pp,bb,ff=visit(e.target,child,remaining-1)
            chance=e.symbolic
            p=p+chance*(BiPoly.constant(e.proxy)+pp)
            b=b+chance*(BiPoly.constant(e.gold_base)+bb)
            for i,c in enumerate(e.gold_coefficients):
                feats[i]=feats[i]+chance*(BiPoly.constant(c)+ff[i])
        return p,b,tuple(feats)
    total_proxy=total_gold=ZERO
    total_feats=[ZERO]*k
    for state,mass in enumerate(game.initial):
        if not mass:
            continue
        p,b,f=visit(state,policy,game.horizon)
        total_proxy=total_proxy+p.scale(mass)
        total_gold=total_gold+b.scale(mass)
        for j,term in enumerate(f):
            total_feats[j]=total_feats[j]+term.scale(mass)
    return PolicySurface(policy,total_proxy,total_gold,tuple(total_feats))


def _halfplane_value(pt,coef):
    return Q(coef[0])*pt[0]+Q(coef[1])*pt[1]+Q(coef[2])


def _distinct_polygon(vertices):
    out=[]
    for point in vertices:
        point=tuple(Q(v) for v in point)
        if not out or point!=out[-1]:
            out.append(point)
    if len(out)>1 and out[0]==out[-1]:
        out.pop()
    if len(out)>2:
        # Collinear cycles and fully collapsed faces are normalized to
        # their two extreme endpoints, preserving all closed tie points.
        if all((out[i][0]-out[0][0])*(out[1][1]-out[0][1])==
               (out[i][1]-out[0][1])*(out[1][0]-out[0][0])
               for i in range(2,len(out))):
            axis=0 if len({pt[0] for pt in out})>1 else 1
            lo=min(out,key=lambda v:v[axis])
            hi=max(out,key=lambda v:v[axis])
            return (lo,) if lo==hi else (lo,hi)
    return tuple(out)


def clip_polygon(vertices,coefficient):
    """Exact closed rational halfplane clip a convex polygon/segment/point."""
    poly=_distinct_polygon(vertices)
    if not poly:
        return ()
    output=[]
    if len(poly)==1:
        return poly if _halfplane_value(poly[0],coefficient)>=0 else ()
    for index,b in enumerate(poly):
        a=poly[index-1]
        va,vb=_halfplane_value(a,coefficient),_halfplane_value(b,coefficient)
        if (va<0 and vb>0) or (va>0 and vb<0):
            frac=va/(va-vb)
            output.append(tuple(a[j]+frac*(b[j]-a[j]) for j in (0,1)))
        elif va!=vb and va*vb==0:
            # Preserve the exact boundary vertex by ordinary inclusion.
            pass
        if vb>=0:
            output.append(b)
    return _distinct_polygon(output)


def winning_polygon(proxy_surfaces,chosen,p_bounds,q_bounds):
    """Closed region where chosen affine proxy surface maximizes reward."""
    p0,p1=tuple(Q(v) for v in p_bounds)
    q0,q1=tuple(Q(v) for v in q_bounds)
    if not 0<=p0<=p1<=1 or not 0<=q0<=q1<=1:
        raise ValueError("rational parameter rectangle invalid")
    for poly in proxy_surfaces:
        if not poly.affine:
            raise ValueError("exact polygon certificate requires affine proxy policies")
    poly=_distinct_polygon(((p0,q0),(p1,q0),(p1,q1),(p0,q1)))
    score=proxy_surfaces[chosen]
    for rival in proxy_surfaces:
        diff=score-rival
        poly=clip_polygon(poly,(
            diff.coefficient(1,0),diff.coefficient(0,1),diff.coefficient(0,0)
        ))
        if not poly:
            return ()
    return poly


def bilinear_extreme(poly,polygon,*,maximize):
    """Exact best value and witness on closed convex rational polygon."""
    if not poly.multiaffine:
        raise ValueError("gold reward polynomial must be multi-affine")
    points=_distinct_polygon(polygon)
    if not points:
        raise ValueError("nonempty winning region required")
    options=[(poly.value(*v),v) for v in points]
    if len(points)>1:
        edges=tuple((points[i-1],points[i])
                    for i in range(len(points)))
        for x,y in edges:
            dx,dy=y[0]-x[0],y[1]-x[1]
            a=poly.coefficient(1,1)*dx*dy
            b=(poly.coefficient(1,0)*dx+poly.coefficient(0,1)*dy
               +poly.coefficient(1,1)*(x[0]*dy+x[1]*dx))
            if a:
                t=-b/(2*a)
                if 0<t<1:
                    point=(x[0]+dx*t,x[1]+dy*t)
                    options.append((poly.value(*point),point))
    chosen=options[0]
    for option in options[1:]:
        if ((option[0]>chosen[0] if maximize else option[0]<chosen[0])
            or option[0]==chosen[0] and option[1]<chosen[1]):
            chosen=option
    return chosen


@dataclass(frozen=True)
class TwoKernelRobustCertificate:
    maximum_gold_regret:Q
    worst_transition_parameters:tuple[Q,Q]
    worst_gold_parameters:tuple[Q,...]
    challenger_policy:ObservationPolicy
    proxy_chosen_policy:ObservationPolicy
    guaranteed_gold_floor:Q
    worst_proxy_gold:Q
    maximum_expected_discrepancy_width:Q
    rectangle_corner_only_regret:Q
    winning_polygons:tuple[tuple[int,tuple[tuple[Q,Q],...]],...]
    policies_enumerated:int
    reward_pair_checks:int
    passes:bool


def two_kernel_robust_certificate(
    game:TwoKernelGame,gold_intervals, *,
    maximum_allowed_regret=None,minimum_proxy_gold_return=None,
    max_policies=200,max_reward_pairs=20000
) -> TwoKernelRobustCertificate:
    """Exact two-parameter safe-regret proof for affine-proxy/bilinear-gold."""
    try:
        intervals=tuple((Q(lo),Q(hi)) for lo,hi in gold_intervals)
    except (TypeError,ValueError,ZeroDivisionError) as exc:
        raise ValueError("licensed gold bounds must be rational") from exc
    if len(intervals)!=len(game.gold_parameters) or any(a>b for a,b in intervals):
        raise ValueError("one ordered licensed interval per shared gold feature")
    if type(max_policies)is not int or max_policies<1 or type(max_reward_pairs)is not int or max_reward_pairs<1:
        raise ValueError("positive policy and reward-comparison budgets required")
    policies=enumerate_observation_policies(game,max_policies=max_policies)
    surfaces=tuple(policy_surface(game,policy) for policy in policies)
    if any(not (s.proxy.affine and s.gold_base.multiaffine
                and all(g.multiaffine for g in s.gold_features))
           for s in surfaces):
        raise ValueError("non-affine proxy or non-multiaffine gold polynomial exceeds exact certificate class")
    proxy=tuple(s.proxy for s in surfaces)
    regions=tuple(
        (i,winning_polygon(proxy,i,game.p_interval,game.q_interval))
        for i in range(len(surfaces))
    )
    regions=tuple((i,poly) for i,poly in regions if poly)
    if not regions:
        raise AssertionError("some proxy policy must win on a nonempty region")
    vertices=tuple(product(*(tuple(sorted(set((lo,hi)))) for lo,hi in intervals)))
    rectangle=tuple(product(tuple(Q(x) for x in game.p_interval),
                            tuple(Q(x) for x in game.q_interval)))
    maximum=Q(0)
    selected_i=selected_j=0
    selected_theta=vertices[0]
    selected_point=rectangle[0]
    floor=None
    width=Q(0)
    corner_regret=Q(0)
    checked=0
    for theta in vertices:
        gold=tuple(s.gold(theta) for s in surfaces)
        gaps=tuple(p-g for p,g in zip(proxy,gold))
        for a in range(len(surfaces)):
            for b in range(len(surfaces)):
                checked+=1
                if checked>max_reward_pairs:
                    raise ValueError("robust reward pair comparison cap exceeded")
                diff=gaps[a]-gaps[b]
                width=max(width,*(diff.value(*pt) for pt in rectangle))
        for j,polygon in regions:
            candidate,_=bilinear_extreme(gold[j],polygon,maximize=False)
            if floor is None or candidate<floor:
                floor=candidate
            for i in range(len(surfaces)):
                checked+=1
                if checked>max_reward_pairs:
                    raise ValueError("robust reward pair comparison cap exceeded")
                current,pt=bilinear_extreme(gold[i]-gold[j],polygon,maximize=True)
                if current>maximum:
                    maximum=current
                    selected_i,selected_j,selected_theta,selected_point=i,j,theta,pt
        for pt in rectangle:
            best_score=max(s.value(*pt) for s in proxy)
            present=tuple(j for j,s in enumerate(proxy)
                          if s.value(*pt)==best_score)
            for i in range(len(gold)):
                for j in present:
                    corner_regret=max(corner_regret,
                                      gold[i].value(*pt)-gold[j].value(*pt))
    if floor is None or maximum>width:
        raise AssertionError("gold regret cannot exceed full policy gap width")
    risk=(None if maximum_allowed_regret is None else Q(maximum_allowed_regret))
    progress=(None if minimum_proxy_gold_return is None else Q(minimum_proxy_gold_return))
    if risk is not None and risk<0:
        raise ValueError("regret bound must be nonnegative")
    return TwoKernelRobustCertificate(
        maximum_gold_regret=maximum,
        worst_transition_parameters=selected_point,
        worst_gold_parameters=tuple(selected_theta),
        challenger_policy=surfaces[selected_i].policy,
        proxy_chosen_policy=surfaces[selected_j].policy,
        guaranteed_gold_floor=Q(floor),
        worst_proxy_gold=surfaces[selected_j].gold(selected_theta).value(*selected_point),
        maximum_expected_discrepancy_width=width,
        rectangle_corner_only_regret=corner_regret,
        winning_polygons=regions,
        policies_enumerated=len(policies),
        reward_pair_checks=checked,
        passes=(risk is None or maximum<=risk)
               and (progress is None or Q(floor)>=progress),
    )
