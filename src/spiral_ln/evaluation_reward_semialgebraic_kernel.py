"""RHT-19: exact q-affine polynomial proxy winner regions.

Finite rational polynomial policy surfaces P_j(p,q)=A_j(p)+B_j(p)q,
G_j(p,q;theta)=C_j(p;theta)+D_j(p;theta)q are supplied by a
separately validated stochastic model or an explicit finite fixture.

The exact root backend uses rational Sturm isolation and resultant-based
algebraic value comparison. No floating-point values decide eligibility,
extrema or the robust safety threshold. Search caps fail closed.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from functools import cmp_to_key, lru_cache
from itertools import combinations, product

from spiral_ln.evaluation_reward_two_kernel import BiPoly, PolicySurface, policy_surface
from spiral_ln.evaluation_reward_shared_kernel import enumerate_observation_policies


ZERO = (Q(0),)
ONE = (Q(1),)


def trim(p):
    v = tuple(Q(x) for x in p)
    if not v:
        return ZERO
    while len(v) > 1 and not v[-1]:
        v = v[:-1]
    return v


def add(a, b):
    return trim(tuple((a[i] if i < len(a) else 0) +
                      (b[i] if i < len(b) else 0)
                      for i in range(max(len(a), len(b)))))


def neg(a):
    return tuple(-x for x in a)


def sub(a, b):
    return add(a, neg(b))


def mul(a, b):
    out = [Q(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] += x*y
    return trim(out)


def scale(a, x):
    return trim(tuple(v*Q(x) for v in a))


def deriv(a):
    return trim(tuple(i*a[i] for i in range(1, len(a))))


def evaluate(a, x):
    out = Q(0)
    for v in reversed(a):
        out = out*x + v
    return out


def divmod_poly(a, b):
    if b == ZERO:
        raise ZeroDivisionError("zero polynomial divisor")
    rem = list(a)
    quo = [Q(0)] * max(1, len(a)-len(b)+1)
    while len(rem) >= len(b) and any(rem):
        i = len(rem)-len(b)
        c = rem[-1]/b[-1]
        quo[i] += c
        for j, v in enumerate(b):
            rem[i+j] -= c*v
        rem = list(trim(rem))
    return trim(quo), trim(rem)


def monic(p):
    p = trim(p)
    return scale(p, 1/p[-1]) if p != ZERO else ZERO


@lru_cache(maxsize=8192)
def gcd_poly(a, b):
    a, b = trim(a), trim(b)
    while b != ZERO:
        a, b = b, divmod_poly(a, b)[1]
    return monic(a)


def squarefree(p):
    p = monic(p)
    if len(p) <= 1:
        return p
    g = gcd_poly(p, deriv(p))
    return monic(divmod_poly(p, g)[0])


def sign(v):
    return (v > 0)-(v < 0)


@lru_cache(maxsize=8192)
def sturm(p):
    p = squarefree(p)
    if len(p) <= 1:
        return (p,)
    seq = [p, deriv(p)]
    while len(seq[-1]) > 1:
        rem = divmod_poly(seq[-2], seq[-1])[1]
        if rem == ZERO:
            break
        seq.append(neg(rem))
    return tuple(seq)


def side_sign(p, x, side):
    f = p
    parity = 1
    while True:
        s = sign(evaluate(f, x))
        if s:
            return s*parity
        if len(f) == 1:
            return 0
        f = deriv(f)
        parity *= side


def variations(p, x, side):
    signs = [side_sign(f, x, side) for f in sturm(p)]
    nonzero = [v for v in signs if v]
    return sum(a != b for a, b in zip(nonzero, nonzero[1:]))


def roots_open(p, lo, hi):
    if lo >= hi or len(trim(p)) <= 1:
        return 0
    return variations(p, lo, +1)-variations(p, hi, -1)


def roots_closed(p, lo, hi):
    if lo > hi:
        return 0
    if lo == hi:
        return int(evaluate(p, lo) == 0)
    return roots_open(p, lo, hi) + int(evaluate(p, lo) == 0) + int(evaluate(p, hi) == 0)


@dataclass(frozen=True)
class RealRoot:
    poly: tuple[Q, ...]
    lo: Q
    hi: Q

    def __post_init__(self):
        p, lo, hi = squarefree(self.poly), Q(self.lo), Q(self.hi)
        if len(p) < 2 or lo > hi:
            raise ValueError("invalid isolating interval")
        if lo == hi:
            if evaluate(p, lo):
                raise ValueError("point is not a polynomial root")
        elif (evaluate(p, lo) == 0 or evaluate(p, hi) == 0
              or roots_open(p, lo, hi) != 1):
            raise ValueError("interval does not isolate exactly one root")
        object.__setattr__(self, "poly", p)
        object.__setattr__(self, "lo", lo)
        object.__setattr__(self, "hi", hi)

    @staticmethod
    def rational(x):
        x = Q(x)
        return RealRoot((-x, Q(1)), x, x)

    def approx(self):
        r=self
        for _ in range(50):
            r=refine(r)
        return float((r.lo+r.hi)/2)


def refine(r):
    if r.lo == r.hi:
        return r
    middle = (r.lo+r.hi)/2
    if evaluate(r.poly, middle) == 0:
        return RealRoot.rational(middle)
    if roots_open(r.poly, r.lo, middle):
        return RealRoot(r.poly, r.lo, middle)
    return RealRoot(r.poly, middle, r.hi)


def cmp_root(a, b, *, budget=256):
    if a is b or a == b:
        return 0
    if a.hi <= b.lo:
        return -1
    if b.hi <= a.lo:
        return 1
    if a.lo == a.hi and b.lo == b.hi:
        return sign(a.lo-b.lo)
    if a.lo == a.hi:
        if evaluate(b.poly, a.lo) == 0 and b.lo < a.lo < b.hi:
            return 0
    elif b.lo == b.hi:
        if evaluate(a.poly, b.lo) == 0 and a.lo < b.lo < a.hi:
            return 0
    else:
        common = gcd_poly(a.poly, b.poly)
        if len(common) > 1 and roots_open(common, max(a.lo, b.lo), min(a.hi, b.hi)):
            return 0
    for _ in range(budget):
        if a.hi <= b.lo:
            return -1
        if b.hi <= a.lo:
            return 1
        a, b = refine(a), refine(b)
        if a.lo == a.hi or b.lo == b.hi:
            return cmp_root(a, b, budget=budget)
    raise ValueError("algebraic root separation budget exceeded")


def isolate(p, lo=Q(0), hi=Q(1), *, max_roots=256, max_nodes=4096):
    p = squarefree(trim(p))
    lo, hi = Q(lo), Q(hi)
    if lo > hi:
        raise ValueError("reversed interval")
    if len(p) < 2:
        return ()
    result = []
    if evaluate(p, lo) == 0:
        result.append(RealRoot.rational(lo))
    if hi != lo and evaluate(p, hi) == 0:
        result.append(RealRoot.rational(hi))
    stack = [(lo, hi)] if hi > lo else []
    nodes = 0
    while stack:
        a, b = stack.pop()
        nodes += 1
        if nodes > max_nodes:
            raise ValueError("Sturm isolation node cap exceeded")
        count = roots_open(p, a, b)
        if count == 0:
            continue
        if len(result) + count > max_roots:
            raise ValueError("Sturm root cap exceeded")
        if count == 1 and evaluate(p, a) != 0 and evaluate(p, b) != 0:
            result.append(RealRoot(p, a, b))
            continue
        mid = (a+b)/2
        if evaluate(p, mid) == 0:
            result.append(RealRoot.rational(mid))
        stack.extend(((a, mid), (mid, b)))
    return tuple(sorted(result, key=cmp_to_key(cmp_root)))


def sign_at(p, root, *, budget=256):
    p = trim(p)
    if p == ZERO:
        return 0
    if root.lo == root.hi:
        return sign(evaluate(p, root.lo))
    common = gcd_poly(root.poly, p)
    if len(common) > 1 and roots_open(common, root.lo, root.hi):
        return 0
    r = root
    for _ in range(budget):
        v0, v1 = evaluate(p, r.lo), evaluate(p, r.hi)
        if v0 and v1 and sign(v0) == sign(v1) and roots_open(p, r.lo, r.hi) == 0:
            return sign(v0)
        r = refine(r)
        if r.lo == r.hi:
            return sign(evaluate(p, r.lo))
    raise ValueError("polynomial sign separation budget exceeded")


def rational_between(a, b, *, budget=256):
    if cmp_root(a, b) >= 0:
        raise ValueError("ordered algebraic breakpoints required")
    for _ in range(budget):
        if a.hi < b.lo:
            return (a.hi+b.lo)/2
        a, b = refine(a), refine(b)
    raise ValueError("rational strip sample search budget exceeded")


def interval_eval(poly, lo, hi):
    a = b = Q(0)
    for c in reversed(poly):
        v = (a*lo, a*hi, b*lo, b*hi)
        a, b = min(v)+c, max(v)+c
    return a, b


def interval_div(n, d):
    a, b = n
    c, e = d
    if c <= 0 <= e:
        raise ZeroDivisionError("interval denominator contains zero")
    corners = (a/c, a/e, b/c, b/e)
    return min(corners), max(corners)


def determinant(a):
    m = [list(row) for row in a]
    n = len(m)
    if n == 0:
        return Q(1)
    prev, s = Q(1), 1
    for k in range(n-1):
        if m[k][k] == 0:
            pivot = next((i for i in range(k+1, n) if m[i][k]), None)
            if pivot is None:
                return Q(0)
            m[k], m[pivot] = m[pivot], m[k]
            s = -s
        pivot = m[k][k]
        for i in range(k+1, n):
            for j in range(k+1, n):
                m[i][j] = (m[i][j]*pivot-m[i][k]*m[k][j])/prev
            m[i][k] = Q(0)
        prev = pivot
    return s*m[-1][-1]


def resultant(f, g, *, degree_g=None):
    m = len(f)-1
    n = len(g)-1 if degree_g is None else degree_g
    if len(g)-1>n:
        raise ValueError("Sylvester degree exceeded")
    g = tuple(g)+(Q(0),)*(n+1-len(g))
    size = m+n
    if size == 0:
        return Q(1)
    matrix = []
    for k in range(n):
        matrix.append([Q(0)]*k + list(reversed(f)) + [Q(0)]*(n-1-k))
    for k in range(m):
        matrix.append([Q(0)]*k + list(reversed(g)) + [Q(0)]*(m-1-k))
    return determinant(matrix)


@lru_cache(maxsize=8192)
def value_resultant(p, num, den):
    # Eliminate p from f(p)=0 and num(p)-y*den(p)=0.
    common = gcd_poly(p, gcd_poly(num, den))
    if len(common)>1:
        p = divmod_poly(p, common)[0]
    degree = len(p)-1
    if degree < 1:
        raise ValueError("undefined value resultant")
    size_g=max(len(num),len(den))-1
    values = tuple(resultant(p, sub(num, scale(den, Q(y))),degree_g=size_g)
                   for y in range(degree+1))
    # Rational Newton interpolation of the resultant polynomial.
    ys = [Q(i) for i in range(degree+1)]
    coeff = list(values)
    result = ZERO
    basis = ONE
    for i in range(degree+1):
        result = add(result, scale(basis, coeff[0]))
        basis = mul(basis, (-ys[i], Q(1)))
        coeff = [(coeff[j+1]-coeff[j])/(ys[j+i+1]-ys[j])
                 for j in range(len(coeff)-1)]
    if result == ZERO:
        raise ValueError("resultant vanishes identically")
    return squarefree(result)


@dataclass(frozen=True)
class AtRoot:
    root: RealRoot
    num: tuple[Q, ...]
    den: tuple[Q, ...] = ONE

    def __post_init__(self):
        num, den = trim(self.num), trim(self.den)
        if sign_at(den, self.root) == 0:
            raise ValueError("rational function pole at algebraic witness")
        object.__setattr__(self, "num", num)
        object.__setattr__(self, "den", den)

    @staticmethod
    def constant(value):
        return AtRoot(RealRoot.rational(Q(0)), (Q(value),))

    def rational(self):
        if self.root.lo == self.root.hi:
            x = self.root.lo
            return evaluate(self.num, x)/evaluate(self.den, x)
        if len(self.num) == 1 and len(self.den) == 1:
            return self.num[0]/self.den[0]
        quotient, rem = divmod_poly(self.num, self.den)
        if rem == ZERO and len(quotient) == 1:
            return quotient[0]
        return None

    def interval(self, root=None):
        r = root or self.root
        return interval_div(interval_eval(self.num, r.lo, r.hi),
                            interval_eval(self.den, r.lo, r.hi))

    def as_root(self, *, budget=256):
        v = self.rational()
        if v is not None:
            return RealRoot.rational(v)
        f = value_resultant(self.root.poly, self.num, self.den)
        r = self.root
        for k in range(budget):
            try:
                lo, hi = self.interval(r)
                margin = Q(1, 1 << (k+2))
                l, h = lo-margin, hi+margin
                if evaluate(f, l) and evaluate(f, h) and roots_open(f, l, h) == 1:
                    return RealRoot(f, l, h)
            except ZeroDivisionError:
                pass
            r = refine(r)
        raise ValueError("algebraic value isolation budget exceeded")

    def approx(self):
        r=self.root
        for _ in range(60):
            r=refine(r)
        a,b=self.interval(r)
        return float((a+b)/2)


def cmp_value(a, b, *, budget=64):
    ra, rb = a.rational(), b.rational()
    if ra is not None and rb is not None:
        return sign(ra-rb)
    if cmp_root(a.root, b.root) == 0:
        f = sub(mul(a.num, b.den), mul(b.num, a.den))
        return sign_at(f, a.root)*sign_at(a.den, a.root)*sign_at(b.den, b.root)
    x, y = a.root, b.root
    for _ in range(budget):
        try:
            ia, ib = a.interval(x), b.interval(y)
            if ia[1] < ib[0]:
                return -1
            if ib[1] < ia[0]:
                return 1
        except ZeroDivisionError:
            pass
        x, y = refine(x), refine(y)
    return cmp_root(a.as_root(), b.as_root())


def poly_parts(p):
    if any(j>1 for _, j, _ in p.terms):
        raise ValueError("RHT-19 requires q-affine polynomial surfaces")
    degree = max((i for i, _, _ in p.terms), default=0)
    return (trim(tuple(p.coefficient(i,0) for i in range(degree+1))),
            trim(tuple(p.coefficient(i,1) for i in range(degree+1))))


def normal_curve(num, den):
    if den == ZERO:
        raise ValueError("identically zero curve denominator")
    g = gcd_poly(num, den)
    return (divmod_poly(num, g)[0], divmod_poly(den, g)[0])


def curve_value(curve, p):
    return AtRoot(p, *curve)


def curve_cmp(c1, c2, p):
    n1, d1 = c1
    n2, d2 = c2
    return (sign_at(sub(mul(n1,d2),mul(n2,d1)),p)
            *sign_at(d1,p)*sign_at(d2,p))


@dataclass(frozen=True)
class WinnerRegion:
    policy_index: int
    breakpoints: tuple[RealRoot, ...]
    strips: tuple[tuple[RealRoot, RealRoot, tuple, tuple], ...]
    slices: tuple[tuple[RealRoot, tuple, tuple], ...]


def winner_region(proxy, chosen, p_interval=(Q(0),Q(1)),
                  q_interval=(Q(0),Q(1)), *, max_roots=300):
    pieces = tuple(poly_parts(s) for s in proxy)
    p0,p1 = map(Q, p_interval)
    q0,q1 = map(Q, q_interval)
    if not 0<=p0<=p1<=1 or not 0<=q0<=q1<=1:
        raise ValueError("licensed parameter rectangle must lie within [0,1]^2")
    if not 0<=chosen<len(proxy):
        raise ValueError("invalid proxy policy")
    constraints = tuple((sub(pieces[chosen][0],pieces[k][0]),
                         sub(pieces[chosen][1],pieces[k][1]))
                        for k in range(len(proxy)) if k!=chosen)
    curves = [( (q0,), ONE), ((q1,), ONE)]
    breaks = [RealRoot.rational(p0),RealRoot.rational(p1)]
    polys = []
    for a,b in constraints:
        polys.extend((a,b,add(a,scale(b,q0)),add(a,scale(b,q1))))
        if b != ZERO:
            curves.append(normal_curve(neg(a),b))
    for (a,b),(c,d) in combinations(curves,2):
        polys.append(sub(mul(a,d),mul(c,b)))
    for f in dict.fromkeys(polys):
        if len(f)>1:
            breaks.extend(isolate(f,p0,p1,max_roots=max_roots))
            if len(breaks)>max_roots:
                raise ValueError("winner arrangement root cap exceeded")
    critical=[]
    for x in sorted(breaks,key=cmp_to_key(cmp_root)):
        if not critical or cmp_root(critical[-1], x):
            critical.append(x)

    def active_at(p):
        lower = [curves[0]]
        upper = [curves[1]]
        for a,b in constraints:
            sb = sign_at(b,p)
            if not sb:
                if sign_at(a,p)<0:
                    return None
                continue
            q = normal_curve(neg(a),b)
            (lower if sb>0 else upper).append(q)
        l = lower[0]
        u = upper[0]
        for curve in lower[1:]:
            if curve_cmp(curve,l,p)>0:
                l=curve
        for curve in upper[1:]:
            if curve_cmp(curve,u,p)<0:
                u=curve
        return (l,u) if curve_cmp(l,u,p)<=0 else None

    slices=[]
    strips=[]
    for x in critical:
        r = active_at(x)
        if r is not None:
            slices.append((x,*r))
    for a,b in zip(critical,critical[1:]):
        if cmp_root(a,b)>=0:
            continue
        sample = RealRoot.rational(rational_between(a,b))
        r = active_at(sample)
        if r is not None:
            strips.append((a,b,*r))
    return WinnerRegion(chosen,tuple(critical),tuple(strips),tuple(slices))


def extrema_on_region(surface, region, *, maximize=True, max_roots=300):
    a,b = poly_parts(surface)
    candidates=[]
    for p,l,u in region.slices:
        for n,d in (l,u):
            candidates.append((AtRoot(p,add(mul(a,d),mul(b,n)),d),
                               p,AtRoot(p,n,d)))
    for low,high,l,u in region.strips:
        for n,d in (l,u):
            num = add(mul(a,d),mul(b,n))
            derivative = sub(mul(deriv(num),d),mul(num,deriv(d)))
            critical = [low, high]
            if len(derivative)>1:
                for p in isolate(derivative,low.lo,high.hi,max_roots=max_roots):
                    if cmp_root(low,p) < 0 and cmp_root(p,high) < 0:
                        critical.append(p)
            for p in critical:
                candidates.append((AtRoot(p,num,d),p,AtRoot(p,n,d)))
    if not candidates:
        return None
    best=candidates[0]
    for candidate in candidates[1:]:
        c=cmp_value(candidate[0],best[0])
        if (c>0 if maximize else c<0):
            best=candidate
    return best


@dataclass(frozen=True)
class SemialgebraicCertificate:
    maximum_gold_regret:AtRoot
    worst_p:RealRoot
    worst_q:AtRoot
    gold_vertex:tuple[Q,...]
    challenger_policy:object
    proxy_chosen_policy:object
    guaranteed_gold_floor:AtRoot
    maximum_expected_discrepancy_width:AtRoot
    corner_only_regret:Q
    regions:tuple[WinnerRegion,...]
    passes:bool


def semialgebraic_certificate(surfaces, gold_intervals, *,
                              p_interval=(Q(0),Q(1)), q_interval=(Q(0),Q(1)),
                              maximum_allowed_regret=None,
                              minimum_proxy_gold_return=None,
                              max_policies=40,max_pairs=10000,max_roots=300):
    """Exact max gold regret over q-affine polynomial policy surfaces.

    The input policy roster and gold features are externally registered. Every
    surface is checked for q-degree at most one. Proxy winner ties are adversarial.
    """
    surfaces=tuple(surfaces)
    try:
        theta=tuple((Q(a),Q(b)) for a,b in gold_intervals)
    except (ValueError,TypeError,ZeroDivisionError) as exc:
        raise ValueError("licensed true-gold intervals must be rational") from exc
    if (not surfaces or len(surfaces)>max_policies or not theta
        or any(a>b for a,b in theta)
        or any(len(s.gold_features)!=len(theta) for s in surfaces)
        or not all(type(v)is int and v>0 for v in (max_policies,max_pairs,max_roots))):
        raise ValueError("invalid policy roster, gold parameters or exact resource cap")
    for s in surfaces:
        for p in (s.proxy,s.gold_base,*s.gold_features):
            poly_parts(p)
    proxy=tuple(s.proxy for s in surfaces)
    unique=tuple(dict.fromkeys(proxy))
    templates={p:winner_region(unique,k,p_interval,q_interval,max_roots=max_roots)
               for k,p in enumerate(unique)}
    regions=tuple(WinnerRegion(i,templates[s.proxy].breakpoints,
                templates[s.proxy].strips,templates[s.proxy].slices)
                for i,s in enumerate(surfaces)
                if templates[s.proxy].strips or templates[s.proxy].slices)
    if not regions:
        raise AssertionError("empty proxy winner arrangement")
    best=AtRoot.constant(0)
    floor=None
    width=AtRoot.constant(0)
    winning_p=RealRoot.rational(Q(p_interval[0]))
    winning_q=AtRoot.constant(Q(q_interval[0]))
    winning_theta=tuple(x[0] for x in theta)
    challenger=proxy_chosen=surfaces[0].policy
    pairs=0
    corner_regret=Q(0)
    full=WinnerRegion(-1,(RealRoot.rational(p_interval[0]),RealRoot.rational(p_interval[1])),
        ((RealRoot.rational(p_interval[0]),RealRoot.rational(p_interval[1]),
           ((Q(q_interval[0]),),ONE),((Q(q_interval[1]),),ONE)),),
        ((RealRoot.rational(p_interval[0]),((Q(q_interval[0]),),ONE),((Q(q_interval[1]),),ONE)),
         (RealRoot.rational(p_interval[1]),((Q(q_interval[0]),),ONE),((Q(q_interval[1]),),ONE))))
    for vertex in product(*(sorted(set(v)) for v in theta)):
        gold=tuple(s.gold(vertex) for s in surfaces)
        gap=tuple(s.proxy-g for s,g in zip(surfaces,gold))
        for p,q in product(tuple(Q(v) for v in p_interval),
                           tuple(Q(v) for v in q_interval)):
            scores=tuple(s.proxy.value(p,q) for s in surfaces)
            m=max(scores)
            for j,score in enumerate(scores):
                if score==m:
                    for i in range(len(surfaces)):
                        corner_regret=max(corner_regret,
                            gold[i].value(p,q)-gold[j].value(p,q))
        for x in gap:
            for y in gap:
                pairs+=1
                if pairs>max_pairs:
                    raise ValueError("full gap search exceeded pair cap")
                v=extrema_on_region(x-y,full,max_roots=max_roots)
                if v is not None and cmp_value(v[0],width)>0:
                    width=v[0]
        for region in regions:
            j=region.policy_index
            low=extrema_on_region(gold[j],region,maximize=False,max_roots=max_roots)
            if low is None:
                raise AssertionError("empty registered winning region")
            if floor is None or cmp_value(low[0],floor)<0:
                floor=low[0]
            for i in range(len(surfaces)):
                pairs+=1
                if pairs>max_pairs:
                    raise ValueError("gold regret search exceeded pair cap")
                result=extrema_on_region(gold[i]-gold[j],region,max_roots=max_roots)
                if result is not None and cmp_value(result[0],best)>0:
                    best,winning_p,winning_q=result
                    winning_theta=vertex
                    challenger,proxy_chosen=surfaces[i].policy,surfaces[j].policy
    if floor is None or cmp_value(best,width)>0:
        raise AssertionError("gold regret exceeds discrepancy bound")
    passes=True
    if maximum_allowed_regret is not None:
        cap=Q(maximum_allowed_regret)
        if cap<0:
            raise ValueError("negative regret cap")
        passes=cmp_value(best,AtRoot.constant(cap))<=0
    if minimum_proxy_gold_return is not None:
        passes=passes and cmp_value(floor,AtRoot.constant(Q(minimum_proxy_gold_return)))>=0
    return SemialgebraicCertificate(best,winning_p,winning_q,
        winning_theta,challenger,proxy_chosen,floor,width,corner_regret,regions,passes)


def two_kernel_semialgebraic_certificate(game,gold_intervals,*,max_policies=40,**kwargs):
    """RHT-16/18-compatible wrapper; complete census remains horizon <= 2."""
    if game.horizon>2:
        raise ValueError("higher horizons require a separately registered full roster")
    policies=enumerate_observation_policies(game,max_policies=max_policies)
    return semialgebraic_certificate(
        (policy_surface(game,p) for p in policies),gold_intervals,
        p_interval=game.p_interval,q_interval=game.q_interval,
        max_policies=max_policies,**kwargs)