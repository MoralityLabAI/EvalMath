"""EM-MPT-04--06: finite reasoning memory, robust control, calibration envelopes."""
from collections import defaultdict
from fractions import Fraction as F
from functools import lru_cache
from itertools import product, combinations
from math import comb
from spiral_ln.evaluation_math_controller import model, bayes


def optimal_tree(rows, costs, prior, budget):
    rows,costs,prior=model(rows,costs,prior)
    value,solve=bayes(rows,costs,prior,budget)
    def tree(i,b,w):
        a=solve(i,b,w)[1]
        if a is None:
            return None
        p,c=rows[i][a],costs[i][a]
        return (a,tree(i+1,b-c,tuple(x*y for x,y in zip(w,p))),
                tree(i,b-c,tuple(x*(1-y) for x,y in zip(w,p))))
    return value,tree(0,budget,prior)


def evaluate(tree, rows, costs, budget, types):
    """Conditional closure vector; evaluate a frozen policy under another model."""
    def go(t,i,b,z):
        if i==len(rows): return F(1)
        if t is None: return F(0)
        a,y,n=t; c=costs[i][a]; p=rows[i][a][z]
        if c>b: raise ValueError('unaffordable policy action')
        return p*go(y,i+1,b-c,z)+(1-p)*go(n,i,b-c,z)
    return tuple(go(tree,0,budget,z) for z in range(types))


def compile_tree(tree,costs,budget):
    """Exact residual-policy classes at observable (progress, remaining budget)."""
    classes=defaultdict(set)
    def visit(t,i,b):
        if t in classes[i,b]: return
        classes[i,b].add(t)
        if t is not None:
            a,y,n=t; c=costs[i][a]
            visit(y,i+1,b-c); visit(n,i,b-c)
    visit(tree,0,budget)
    ids={s:{t:k for k,t in enumerate(sorted(ts,key=repr))} for s,ts in classes.items()}
    table={}
    for (i,b),ts in ids.items():
        for t,k in ts.items():
            if t is None: table[i,b,k]=None; continue
            a,y,n=t; c=costs[i][a]
            table[i,b,k]=(a,ids[i+1,b-c][y],ids[i,b-c][n])
    width=max(map(len,classes.values()))
    return ids[0,budget][tree],table,width,(width-1).bit_length()


def decode(start,table,costs,budget):
    def go(i,b,k):
        entry=table[i,b,k]
        if entry is None: return None
        a,y,n=entry; c=costs[i][a]
        return a,go(i+1,b-c,y),go(i,b-c,n)
    return go(0,budget,start)


def quantized_tree(rows,costs,prior,budget,denom):
    """Online nearest-grid posterior, two types; exact planning at rounded belief."""
    rows,costs,prior=model(rows,costs,prior)
    if len(prior)!=2 or denom<1: raise ValueError('need two types and positive denominator')
    _,solve=bayes(rows,costs,prior,budget)
    def roundp(p):
        return min(range(denom+1),key=lambda j:(abs(F(j,denom)-p),j))
    def update(q,lik):
        w=(q*lik[0],(1-q)*lik[1]); s=sum(w)
        return roundp(w[0]/s if s else F(1,2))
    def go(i,b,j):
        q=F(j,denom); a=solve(i,b,(q,1-q))[1]
        if a is None: return None
        p=rows[i][a]; c=costs[i][a]
        return a,go(i+1,b-c,update(q,p)),go(i,b-c,update(q,tuple(1-x for x in p)))
    return go(0,budget,roundp(prior[0]))


def posterior_regret_certificate(tree,rows,costs,prior,budget):
    """Exact sum of posterior Bellman action gaps on the policy's actual histories."""
    _,solve=bayes(rows,costs,prior,budget)
    def go(t,i,b,w):
        if not any(w) or i==len(rows): return F(0)
        opt=solve(i,b,w)[0]
        if t is None: return opt
        a,y,n=t; c=costs[i][a]; p=rows[i][a]
        wy=tuple(x*z for x,z in zip(w,p)); wn=tuple(x*(1-z) for x,z in zip(w,p))
        gap=opt-solve(i+1,b-c,wy)[0]-solve(i,b-c,wn)[0]
        return gap+go(y,i+1,b-c,wy)+go(n,i,b-c,wn)
    return go(tree,0,budget,prior)


def frontier(rows,costs,budget,types):
    """Exact conditional payoff vectors for deterministic history policies."""
    @lru_cache(None)
    def go(i,b):
        if i==len(rows): return ((F(1),)*types,)
        v={(F(0),)*types}
        for p,c in zip(rows[i],costs[i]):
            if c<=b:
                for y,n in product(go(i+1,b-c),go(i,b-c)):
                    v.add(tuple(pj*yj+(1-pj)*nj for pj,yj,nj in zip(p,y,n)))
        return tuple(sorted(x for x in v if not any(x!=y and all(a<=b for a,b in zip(x,y)) for y in v)))
    return go(0,budget)


def robust_two(vectors):
    """Maximin over mixtures of policies for two possible worlds; exact witness."""
    if not vectors or any(len(v)!=2 for v in vectors): raise ValueError('need two-world payoffs')
    best=max(vectors,key=lambda v:min(v)); val=min(best); witness=(best,best,F(1))
    for u,v in combinations(vectors,2):
        du=u[0]-u[1]; dv=v[0]-v[1]
        if du==dv: continue
        t=-dv/(du-dv)
        if 0<=t<=1:
            score=t*u[0]+(1-t)*v[0]
            if score>val: val,witness=score,(u,v,t)
    return val,witness


def coupling_bound(delta,epsilon,horizon):
    delta,epsilon=F(delta),F(epsilon)
    if not 0<=delta<=1 or not 0<=epsilon<=1 or horizon<0: raise ValueError('invalid bound input')
    return 1-(1-delta)*(1-epsilon)**horizon


def binom_tail(n,k,p,upper):
    indices=range(k,n+1) if upper else range(k+1)
    return sum((comb(n,x)*p**x*(1-p)**(n-x) for x in indices),F(0))


@lru_cache(None)
def interval(n,k,alpha,grid):
    """Outward-rounded exact equal-tail binomial confidence interval."""
    alpha=F(alpha)
    if not 0<=k<=n or n<1 or not 0<alpha<1 or grid<1: raise ValueError('invalid interval')
    s=[F(j,grid) for j in range(grid+1)]
    # Excluded lower/upper grids use inclusive rejection; endpoints rounded outward.
    lo=max((p for p in s if binom_tail(n,k,p,True)<=alpha/2),default=F(0))
    hi=min((p for p in s if binom_tail(n,k,p,False)<=alpha/2),default=F(1))
    return lo,hi


def envelope(tree,bounds,costs,budget):
    """Exact rectangular envelope for one frozen tree, keyed by (history,action)."""
    def go(t,i,b,h):
        if i==len(costs): return F(1),F(1)
        if t is None: return F(0),F(0)
        a,y,n=t; c=costs[i][a]
        if c>b: raise ValueError('unaffordable action')
        lo,hi=bounds[h,a]
        if not 0<=lo<=hi<=1: raise ValueError('invalid bounds')
        yl,yu=go(y,i+1,b-c,h+((a,1),)); nl,nu=go(n,i,b-c,h+((a,0),))
        return min(p*yl+(1-p)*nl for p in (lo,hi)),max(p*yu+(1-p)*nu for p in (lo,hi))
    return go(tree,0,budget,())
