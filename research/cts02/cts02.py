"""CTS-02 development: exact normal-fan search versus bounded edge walks.
Python standard library only. No model training or confirmation split.
"""
from fractions import Fraction as F
from functools import cmp_to_key
from random import Random
from math import comb
import json


def cross(a,b): return a[0]*b[1]-a[1]*b[0]
def dot(a,b): return a[0]*b[0]+a[1]*b[1]
def sub(a,b): return (a[0]-b[0],a[1]-b[1])
def half(a): return int(a[1]<0 or (a[1]==0 and a[0]<0))
def angle(a,b):
    if half(a)!=half(b): return half(a)-half(b)
    k=cross(a,b)
    return (k<0)-(k>0)


def hull(points):
    p=sorted(set(points))
    def chain(seq):
        out=[]
        for v in seq:
            while len(out)>=2 and cross(sub(out[-1],out[-2]),sub(v,out[-1]))<=0: out.pop()
            out.append(v)
        return out
    return chain(p)[:-1]+chain(reversed(p))[:-1]


def polygon(seed,family):
    rng=Random(seed); q=rng.randint(5,35)
    if family=='lens':
        r=100; xs=sorted(rng.sample(range(-r+1,r),q))
        ys=sorted(rng.sample(range(-r+1,r),q))
        p=[(-r,0),(r,0)]+[(x,(r*r-x*x)*rng_scale) for rng_scale in [rng.randint(1,5)] for x in xs]+[(x,-(r*r-x*x)*rng_scale) for rng_scale in [rng.randint(1,5)] for x in ys]
    elif family=='zonotope':
        e=[(1,x) for x in rng.sample(range(-100,101),q)]
        e=sorted(e+[(-a,-b) for a,b in e],key=cmp_to_key(angle)); p=[]; x=y=0
        for a,b in e: p.append((x,y)); x+=a; y+=b
    elif family=='circle':
        # Rational parameterization, then integer grid rounding and exact hull.
        p=[]
        for t in rng.sample(range(-100,101),2*q):
            z=F(t,20); den=1+z*z
            p.append((int(10**8*(1-z*z)/den),int(10**8*2*z/den)))
    else: raise ValueError(family)
    # Independently randomized invertible integer affine map.
    while True:
        a,b,c,d=[rng.randint(-4,4) for _ in range(4)]
        if a*d-b*c: break
    u,v=rng.randint(-100,100),rng.randint(-100,100)
    p=hull([(a*x+b*y+u,c*x+d*y+v) for x,y in p]); n=len(p)
    assert n>=3
    rows=[]
    for i,x in enumerate(p):
        e=sub(p[(i+1)%n],x); normal=(e[1],-e[0]); rows.append((normal,dot(normal,x)))
    rng.shuffle(rows)
    while True:
        c=(rng.randint(-100,100),rng.randint(-100,100))
        if c!=(0,0) and all(cross(a,c) for a,_ in rows): break
    return rows,c,p


def intersection(r,s):
    a,b=r; c,d=s; det=cross(a,c)
    assert det!=0
    return (F(b*c[1]-a[1]*d,det),F(a[0]*d-b*c[0],det))


def cone(a,b,c): return cross(a,c)>0 and cross(c,b)>0


def certificate(rows,c,i):
    n=len(rows); a,b=rows[i-1]; v,w=rows[i]; x=intersection(rows[i-1],rows[i]); det=cross(a,v)
    l=F(cross(c,v),det); r=F(cross(a,c),det)
    return l>=0 and r>=0 and all(dot(s,x)<=t for s,t in rows) and all(l*a[j]+r*v[j]==c[j] for j in (0,1)) and l*b+r*w==dot(c,x)


def global_search(rows,c):
    lo,hi=0,len(rows); probes=0
    while lo<hi:
        m=(lo+hi)//2; probes+=1
        if angle(rows[m][0],c)<0: lo=m+1
        else: hi=m
    return lo%len(rows),probes+1 # final support proposal


def key(a):
    # Strictly increasing rational octant surrogate on the angular circle.
    x,y=a; den=abs(x)+abs(y)
    if x>=0 and y>=0: return F(y,den)
    if x<0 and y>=0: return 1+F(-x,den)
    if x<=0 and y<0: return 2+F(-y,den)
    return 3+F(x,den)


def rank_search(rows,c):
    # Single exact rank guess, then binary search; the guess is only a proposal.
    n=len(rows); p=min(n-1,int(n*key(c)/4)); probes=1
    if angle(rows[p][0],c)<0: lo,hi=p+1,n
    else: lo,hi=0,p
    while lo<hi:
        m=(lo+hi)//2; probes+=1
        if angle(rows[m][0],c)<0: lo=m+1
        else: hi=m
    return lo%n,probes+1


def local_search(rows,c,start):
    n=len(rows); i=start; probes=0
    while probes<=n:
        a,b=rows[i-1][0],rows[i][0]; probes+=1
        if cone(a,b,c): return i,probes
        i=(i+1)%n if cross(b,c)>0 else (i-1)%n
    raise AssertionError('local walk failed')


def root(seed,family,K=6):
    rows,c,verts=polygon(seed,family); n=len(rows)
    rows.sort(key=cmp_to_key(lambda a,b:angle(a[0],b[0])))
    goal,g=global_search(rows,c); goal_r,rc=rank_search(rows,c); assert goal_r==goal and certificate(rows,c,goal)
    assert set(intersection(rows[i-1],rows[i]) for i in range(n))==set(verts)
    exact=[]; rng=Random(seed+1234567)
    for i in range(n):
        j,l=local_search(rows,c,i); assert j==goal
        a,b=rows[i-1][0],rows[i][0]
        # Public, fixed one-step lookahead: check current cone and its neighbors.
        # Charge each inspected cone; then fallback to global with remaining budget.
        route=0; h=None
        for t in (i,(i+1)%n,(i-1)%n):
            route+=1
            if cone(rows[t-1][0],rows[t][0],c): h=route; break
        if h is None: h=route+g
        # Sham: randomly choose local/global at the same total probe cap.
        # The two fixed baselines and hybrid have identical final certificate checks.
        L=int(l<=K); G=int(g<=K); H=int(h<=K)
        S=int((l if rng.randrange(2)==0 else g)<=K)
        R=int(rc<=K)
        d=min((i-goal)%n,(goal-i)%n)
        exact.append(dict(start=i,edge_distance=d,local=l,global_cost=g,hybrid=h,L=L,G=G,H=H,S=S,R=R,rank_cost=rc))
    return dict(seed=seed,family=family,facets=n,goal=goal,global_cost=g,cases=exact,
                mean={a:str(F(sum(x[a] for x in exact),n)) for a in 'LGHSR'})


def run():
    # All 64 roots per family are exposed development roots. Root mean is the unit.
    # Three generator strata; independent seeded draws within each stratum.
    roots=[root(10000+1000*j+i,f) for j,f in enumerate(('lens','zonotope','circle')) for i in range(64)]
    out={}
    for f in ('lens','zonotope','circle','all'):
        r=[x for x in roots if f=='all' or x['family']==f]; n=len(r)
        out[f]={'roots':n,'cases':sum(x['facets'] for x in r),
                'root_mean':{a:str(sum((F(x['mean'][a]) for x in r),F(0))/n) for a in 'LGHSR'},
                'case_success':{a:sum(z[a] for x in r for z in x['cases']) for a in 'LGHSR'}}
    return {'schema':'CTS-02/dev-v1','K':6,'summary':out,'roots':roots}


if __name__=='__main__':
    import sys
    with open(sys.argv[1],'w') as f: json.dump(run(),f,sort_keys=True,indent=2)
