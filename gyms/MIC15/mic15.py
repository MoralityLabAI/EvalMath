"""MIC-15: public finite reusable-lemma acquisition, exact realized policy utility."""
from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations
from random import Random
from fractions import Fraction as F
from statistics import mean
from pathlib import Path
import json, hashlib, time

FAMILIES=('partition','hub','overlap','alternatives')
BUDGETS=(80,116,152)
SEEDS=range(12000,12016)

@dataclass(frozen=True)
class Rule:
    premises: tuple
    cost: int

@dataclass(frozen=True)
class Lemma:
    atoms: int
    bound: int
    importance: int
    reward: int
    rules: tuple

@dataclass(frozen=True)
class Problem:
    values: tuple  # eight disjoint groups of exact nonnegative entries
    ceilings: tuple
    lemmas: tuple


def bits(m):
    while m:
        low=m&-m; yield low.bit_length()-1; m^=low


def make(f,seed):
    r=Random(seed+100003*FAMILIES.index(f));n=8
    vals=tuple(tuple(r.randint(0,9) for _ in range(r.randint(3,5))) for _ in range(n))
    ceilings=tuple(tuple(10 for _ in row) for row in vals)
    if f=='partition':
        pairs=[3,12,48,192,5,80];targets=[7,15,28,60,112,240]
    elif f=='hub':
        pairs=[1|(1<<j) for j in range(1,7)];targets=[1|(1<<j)|(1<<(1+j%7))|(1<<(1+(j+2)%7)) for j in range(1,7)]
    elif f=='overlap':
        pairs=r.sample([sum(1<<i for i in a) for a in combinations(range(n),2)],6)
        targets=r.sample([sum(1<<i for i in a) for a in combinations(range(n),4)],6)
    elif f=='alternatives':
        pairs=[3,12,5,10,48,192];targets=[15,51,60,195,204,240]
    else:raise ValueError(f)
    # Randomly relabel the eight groups; indices alone do not identify the hub.
    perm=list(range(n));r.shuffle(perm)
    remap=lambda a:sum(1<<perm[i] for i in bits(a))
    pairs=list(map(remap,pairs));targets=list(map(remap,targets));r.shuffle(pairs);r.shuffle(targets)
    ls=[]
    for k,a in enumerate([1<<i for i in range(n)]+pairs+targets):
        value=sum(sum(vals[i]) for i in bits(a));baseline=sum(sum(ceilings[i]) for i in bits(a))
        rules=[Rule((),1+3*sum(len(vals[i]) for i in bits(a)))]
        # All decompositions using earlier atomic groups and reusable pair sums.
        # Target lemmas themselves are never premises in this proxy.
        candidates=[j for j,l in enumerate(ls[:14]) if l.atoms&a==l.atoms]
        def partitions(rem,start=0,chosen=()):
            if not rem:
                if len(chosen)>=2:yield chosen
                return
            first=rem&-rem
            for j in candidates:
                b=ls[j].atoms
                if b&first and b&rem==b:yield from partitions(rem^b,0,chosen+(j,))
        for p in partitions(a):rules.append(Rule(tuple(sorted(p)),2+len(p)))
        rules=tuple(sorted(set(rules),key=lambda x:(x.cost,x.premises)))
        importance=r.randint(1,4) if k>=14 else 0
        reward=(baseline-value)*importance
        ls.append(Lemma(a,value,importance,reward,rules))
    return Problem(vals,ceilings,tuple(ls))


def verify_problem(d):
    n=len(d.values);assert n==len(d.ceilings)>0
    assert all(len(a)==len(b)>0 and all(0<=x<=y for x,y in zip(a,b)) for a,b in zip(d.values,d.ceilings))
    for i,l in enumerate(d.lemmas):
        assert 0<l.atoms<1<<n and l.reward>=0
        assert l.bound==sum(sum(d.values[j]) for j in bits(l.atoms))
        assert 0<=l.importance<=4 and l.reward==l.importance*(sum(sum(d.ceilings[j]) for j in bits(l.atoms))-l.bound)
        for r in l.rules:
            assert r.cost>0
            if not r.premises:
                assert r.cost==1+3*sum(len(d.values[j]) for j in bits(l.atoms));continue
            assert len(set(r.premises))==len(r.premises)>=2 and all(0<=j<i for j in r.premises)
            cover=0;v=0
            for j in r.premises:
                p=d.lemmas[j];assert not cover&p.atoms;cover|=p.atoms;v+=p.bound
            assert cover==l.atoms and v==l.bound and r.cost==2+len(r.premises)
    return True


class Planner:
    def __init__(self,d):
        self.d=d;self.n=len(d.lemmas);self.rewards=tuple(l.reward for l in d.lemmas)
        self.rules=[tuple((sum(1<<j for j in r.premises),r.cost,k) for k,r in enumerate(l.rules)) for l in d.lemmas]
        self.targets=[i for i,w in enumerate(self.rewards) if w];self.expansions=0
        self.plans=[]
        # All recursively constructed proof packages for each individual lemma; retain
        # alternatives with different prerequisites, even if more expensive alone.
        for i,rs in enumerate(self.rules):
            # Each package is an acquired-lemma mask for a recursive derivation.
            packages=set()
            for p,c,k in rs:
                masks={0}
                for j in bits(p):masks={a|b for a in masks for b in self.plans[j]}
                packages.update(a|1<<i for a in masks)
            self.plans.append(tuple(sorted(packages)))
    def rule(self,i,s):return min((c,k) for p,c,k in self.rules[i] if p&s==p)
    @lru_cache(maxsize=None)
    def cost(self,s):
        if not s:return 0
        i=s.bit_length()-1;a=s^(1<<i)
        return self.cost(a)+self.rule(i,a)[0]
    @lru_cache(maxsize=None)
    def reward(self,s):
        if not s:return 0
        i=s.bit_length()-1;return self.rewards[i]+self.reward(s^(1<<i))
    def materialize(self,s,initial=0):
        # Given previously acquired lemmas, new rules may reuse them.
        cur=initial;actions=[];spent=0
        for i in bits(s&~initial):
            c,k=self.rule(i,cur);actions.append((i,k));spent+=c;cur|=1<<i
        return actions,spent
    def marginal(self,s,package):
        return self.materialize(s|package,s)[1]
    def exact(self,budgets):
        best={b:(0,0,0) for b in budgets};count=0;cap=max(budgets)
        # Canonical topological acquisition: choose each lemma or skip it.
        def dfs(i,s,c,v):
            nonlocal count
            if i==self.n:
                count+=1
                for b in budgets:
                    if c<=b and (v,-c,-s)>best[b]:best[b]=(v,-c,-s)
                return
            dfs(i+1,s,c,v)
            cc,_=self.rule(i,s)
            if c+cc<=cap:dfs(i+1,s|1<<i,c+cc,v+self.rewards[i])
        dfs(0,0,0,0)
        return {b:-best[b][2] for b in budgets},count
    def bundles(self,s,remaining):
        options={}
        for i in self.targets:
            if s>>i&1:continue
            for p in self.plans[i]:
                q=s|p;c=self.marginal(s,p);self.expansions+=1
                if c<=remaining:
                    v=self.reward(q)-self.reward(s)
                    options[q]=(c,v)
        return options
    def immediate(self,b):
        s=0;actions=[];spent=0
        while True:
            opts=[]
            for i in range(self.n):
                if s>>i&1:continue
                c,k=self.rule(i,s);self.expansions+=1
                if self.rewards[i] and c<=b-spent:opts.append((F(self.rewards[i],c),self.rewards[i],-c,-i,k))
            if not opts:break
            _,_,negc,negi,k=max(opts);i=-negi;actions.append((i,k));s|=1<<i;spent-=negc
        return actions
    def bundle(self,b,depth=1):
        s=0;spent=0;actions=[]
        while True:
            opts=self.bundles(s,b-spent)
            if not opts:break
            def key(q):
                c,v=opts[q];future=0
                if depth==2:
                    tail=self.bundles(q,b-spent-c);future=max((x[1] for x in tail.values()),default=0)
                return ((v+future) if depth==2 else F(v,c),F(v,c),v,-c,-q)
            q=max(opts,key=key);steps,c=self.materialize(q,s);actions.extend(steps);spent+=c;s=q
        return actions
    def beam(self,b,width):
        # Target-package macro actions, with distinct state-cost pairs and
        # deterministic optimistic density ordering. Retain feasible incumbents.
        frontier={0:(0,[])};best=(0,0,0,[])
        for _ in self.targets:
            nxt={}
            for s,(c,path) in frontier.items():
                for q,(delta,v) in self.bundles(s,b-c).items():
                    cost=c+delta
                    if q not in nxt or cost<nxt[q][0]:nxt[q]=(cost,path+self.materialize(q,s)[0])
            if not nxt:break
            for q,(c,path) in nxt.items():
                candidate=(self.reward(q),-c,-q,path)
                if candidate[:3]>best[:3]:best=candidate
            order=sorted(nxt,key=lambda s:(self.reward(s),F(self.reward(s),max(1,nxt[s][0])),-nxt[s][0],-s),reverse=True)
            frontier={s:nxt[s] for s in order[:width]}
        return best[3]


def check_path(d,path,budget):
    # Independent witness replay: check rule eligibility, charge exact declared
    # cost, and reconstruct each numerical claim from the selected proof rule.
    have={};spent=0;reward=0
    for i,k in path:
        assert type(i) is int and type(k) is int and 0<=i<len(d.lemmas) and i not in have
        l=d.lemmas[i];assert 0<=k<len(l.rules);r=l.rules[k]
        if r.premises:
            assert all(j in have for j in r.premises)
            assert len(set(r.premises))==len(r.premises)
            cover=0;v=0
            for j in r.premises:
                a,x=have[j];assert not cover&a;cover|=a;v+=x
            assert cover==l.atoms and v==l.bound and r.cost==2+len(r.premises)
        else:
            entries=[x for j,row in enumerate(d.values) if l.atoms>>j&1 for x in row]
            assert sum(entries)==l.bound and r.cost==1+3*len(entries)
        gain=l.importance*(sum(sum(d.ceilings[j]) for j in bits(l.atoms))-l.bound)
        assert gain==l.reward
        have[i]=(l.atoms,l.bound);spent+=r.cost;reward+=gain
        assert spent<=budget
    return dict(reward=reward,cost=spent,steps=len(have),mask=hex(sum(1<<i for i in have)))


def run():
    t=time.perf_counter();rows=[]
    for f in FAMILIES:
        for seed in SEEDS:
            d=make(f,seed);verify_problem(d);p=Planner(d);gold,count=p.exact(BUDGETS)
            for b in BUDGETS:
                s=gold[b];path,c=p.materialize(s);g=check_path(d,path,b);assert c==g['cost']==p.cost(s)
                arms={'oracle':{**g,'path':path,'subsets':count}}
                for key,fn in [('immediate',p.immediate),('bundle',p.bundle),('look2',lambda b:p.bundle(b,2)),('beam8',lambda b:p.beam(b,8)),('beam32',lambda b:p.beam(b,32))]:
                    p.expansions=0;start=time.perf_counter();a=fn(b);elapsed=time.perf_counter()-start;v=check_path(d,a,b)
                    assert v['reward']<=g['reward'];arms[key]={**v,'path':a,'candidates_scanned':p.expansions,'ms':elapsed*1000}
                rows.append(dict(family=f,seed=seed,budget=b,arms=arms))
            p.cost.cache_clear();p.reward.cache_clear()
        print('done',f,flush=True,file=__import__('sys').stderr)
    return dict(schema='MIC-15/public-realized-lemma-acquisition/v1',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),rows=rows,elapsed_s=time.perf_counter()-t)

if __name__=='__main__':print(json.dumps(run(),indent=2,sort_keys=True))
