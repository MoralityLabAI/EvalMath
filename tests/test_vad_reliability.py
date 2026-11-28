"""Independent rational checks of censored feedback and stopping; optional neural receipt audit."""
from fractions import Fraction as F
from itertools import product
from math import isclose
from pathlib import Path
import hashlib
import json
import sys
from random import Random

root=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(root if root.is_dir() else Path(__file__).resolve().parent))
import verify_vad_reliability as v
import verify_vad_stopping as parent


def ftuple(xs): return tuple(F(str(x)) for x in xs)


def test_planner_against_exact_parent():
    for i in range(v.GRID+1):
        r=F(i,v.GRID); w=ftuple(v.BASE); qs=tuple(map(ftuple,v.CHANNELS))
        ww=tuple((1-r)*x for x in w)+tuple(r*x for x in w)
        exact=parent.bellman(ww,qs[0]+qs[1],times=v.TIMES*2)
        acts,val=v.plan((tuple(float((1-r)*x) for x in w),tuple(float(r*x) for x in w)),v.CHANNELS)
        assert isclose(val,float(exact(0,0)[0]),abs_tol=1e-9)
        result=parent.evaluate(ww,qs[0]+qs[1],lambda n,k:acts[n,k],times=v.TIMES*2)
        assert result['net']==exact(0,0)[0]


def test_censored_likelihood_and_filter():
    # Path multiplicity depends on the stopping policy, not the latent mode.
    for i in (0,5,10,15,20):
        acts=v.policy(i)
        for prior,channel in ((v.BASE,v.CHANNELS[0]),(v.BASE,v.CHANNELS[1]),(v.HIGH_NULL,v.WEAK)):
            w,q=ftuple(prior),ftuple(channel); state={(0,0):1}; mass=F(0)
            for n in range(v.H+1):
                nxt={}
                for (_,k),count in state.items():
                    if n==v.H or not acts[n,k]:
                        mass+=count*sum(x*p**k*(1-p)**(n-k) for t,x,p in zip(v.TIMES,w,q) if t>n)
                        continue
                    mass+=count*sum(x*p**k*(1-p)**(n-k) for t,x,p in zip(v.TIMES,w,q) if t==n+1)
                    for b in (0,1): nxt[n+1,k+b]=nxt.get((n+1,k+b),0)+count
                state=nxt
            assert mass==1
    rng=Random(2026)
    # Brute sum over all 2^5 latent paths, including transition likelihoods.
    for seed in range(16):
        stream=v.family_stream(seed,'markov',5); records=[v.execute(world,cap=rng.choice((2,4,8)))[0] for world in stream]
        p=.5
        for j,rec in enumerate(records):
            post,_=v.update(p,rec); p=v.transition(post)
            z=[F(0),F(0)]
            for path in product((0,1),repeat=j+1):
                m=F(1,2)
                for ix,mode in enumerate(path):
                    if ix: m*=F(19,20) if mode==path[ix-1] else F(1,20)
                    n,k,hit=records[ix]; f=n-int(hit)
                    m*=sum(w*q**k*(1-q)**(f-k) for t,w,q in zip(v.TIMES,ftuple(v.BASE),ftuple(v.CHANNELS[mode])) if (t==n if hit else t>n))
                z[path[-1]]+=m
            assert isclose(post,float(z[1]/sum(z)),abs_tol=1e-12)


def test_unseen_suffix_and_simplex():
    for scenario in v.SCENARIOS:
        s=v.family_stream(83400,scenario,20)
        for method in v.METHODS:
            a=v.simulate(s,method); b=v.simulate(s[:8],method)
            assert a[:8]==b
            for r in a:
                n,k,hit=r['record']; assert 0<=k<=n-hit<=v.H
        rng=Random(19)
        for _ in range(100):
            x=[rng.random() for _ in range(6)]; q=v.simplex_quantize(tuple(y/sum(x) for y in x))
            assert sum(q)==v.EXP_GRID and min(q)>=0


def test_symbolic_receipt():
    # Small, frozen independent replay (no torch dependency).
    rows=[]
    for i,s in enumerate(v.SCENARIOS):
        worlds=v.family_stream(844100+i,s,24)
        for m in v.METHODS:
            rs=v.simulate(worlds,m)
            rows.append([s,m,sum(r['net'] for r in rs),sum(r['record'][0] for r in rs)])
    assert hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()==EXPECTED

EXPECTED='4bb9354a914e2a9105a76fb71b2657f98a0ae2f918343a4d1eaa0a97e91ae6a5'
