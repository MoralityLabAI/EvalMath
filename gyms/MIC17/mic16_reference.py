"""MIC-16: finite Bayesian proof acquisition with hidden reusable certificates."""
from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations
from random import Random
from fractions import Fraction as F
from pathlib import Path
import hashlib, json, time

FAMILIES=('local','shared','parity','mixed')
BUDGETS=(8,12,16)
SEEDS=range(16000,16012)
WORLD=8
FULL=255
MODES=('direct_only_exact','greedy_1','lookahead_2','lookahead_3','lookahead_4','bayes_no_probe','bayes','clairvoyant')

@dataclass(frozen=True)
class Problem:
    entries: tuple
    supports: tuple
    reward: tuple
    weights: tuple
    catalog: tuple # per lemma/world: (success, cost)


def bits(m):
    while m:
        low=m&-m;yield low.bit_length()-1;m^=low


def make(f,seed):
    r=Random(seed+100003*FAMILIES.index(f))
    entries=tuple(tuple(r.randint(0,9) for _ in range(r.randint(3,5))) for _ in range(3))
    supports=(1,2,4,3,5,6,7)
    reward=tuple(0 if i<3 else r.randint(1,4)*sum(10-v for j in bits(s) for v in entries[j]) for i,s in enumerate(supports))
    weights=tuple(r.randint(1,4) for _ in range(WORLD))
    catalog=[]
    for i in range(len(supports)):
        bit=1<<(i%3);pol=r.randrange(2)
        if f=='local':m=bit
        elif f=='shared':m=1 if i!=6 else 3
        elif f=='parity':m=r.choice((3,5,6,7))
        else:m=r.randrange(1,8)
        # A hidden catalog has a correlated availability bit and an independently
        # determined cost bit. Failed checks still consume verification work.
        cost_bit=r.choice((1,2,4));row=[]
        for w in range(WORLD):
            ok=((w&m).bit_count()%2)==pol
            cost=1+int(bool(w&cost_bit)) if ok else 1+r.randrange(2)
            row.append((ok,cost))
        catalog.append(tuple(row))
    return Problem(entries,supports,reward,weights,tuple(catalog))


class Planner:
    def __init__(self,d):
        self.d=d;self.n=len(d.supports)
        self.actions=tuple((k,i) for k in ('direct','cached') for i in range(self.n))+tuple(('compose',i) for i in range(3,self.n))+tuple(('probe',i) for i in range(3))
        self.mass=[sum(d.weights[i] for i in bits(m)) for m in range(256)]
        self.parts={};self.calls=0
        for a,(k,i) in enumerate(self.actions):
            groups={}
            for w in range(WORLD):
                o=self.observation(k,i,w);groups[o]=groups.get(o,0)|1<<w
            self.parts[a]=tuple(sorted(groups.items()))
    def observation(self,k,i,w):
        if k=='direct':return True,sum(len(self.d.entries[j]) for j in bits(self.d.supports[i])), -1
        if k=='compose':return True,1+ self.d.supports[i].bit_count()//2,-1
        if k=='cached':
            ok,cost=self.d.catalog[i][w];return ok,cost,-1
        if k=='probe':return False,1,(w>>i)&1
        raise ValueError(k)
    def transitions(self,s,m,b,a):
        k,i=self.actions[a]
        if k!='probe' and s>>i&1:return ()
        if k=='compose' and s&self.d.supports[i]!=self.d.supports[i]:return ()
        out=[]
        for (ok,cost,signal),worlds in self.parts[a]:
            p=m&worlds
            if not p:continue
            if cost>b:return () # safe ex ante admission, no budget overdraft
            q=s|(1<<i) if ok and k!='probe' else s
            reward=self.d.reward[i] if q!=s else 0
            out.append((q,p,b-cost,reward))
        # A deterministic no-progress action burns budget without new information.
        if all(q==s and p==m for q,p,_,_ in out):return ()
        return tuple(out)
    @lru_cache(None)
    def choice(self,s,m,b,h,restriction='all'):
        # Integer weighted reward sum: posterior conditioning is handled by
        # disjoint world masks; division by mass occurs only at reporting.
        self.calls+=1
        if b<=0 or h==0:return 0,-1
        best=(0,-1)
        for a,(k,i) in enumerate(self.actions):
            if restriction=='direct' and k not in ('direct','compose'):continue
            if restriction=='no_probe' and k=='probe':continue
            ts=self.transitions(s,m,b,a)
            if not ts:continue
            v=sum(self.mass[p]*r+self.choice(q,p,c,h-1,restriction)[0] for q,p,c,r in ts)
            if v>best[0]:best=v,a
        return best
    def policy(self,mode,s,m,b):
        if mode=='direct_only_exact':return self.choice(s,m,b,b,'direct')[1]
        if mode=='bayes_no_probe':return self.choice(s,m,b,b,'no_probe')[1]
        if mode in ('bayes','clairvoyant'):return self.choice(s,m,b,b)[1]
        h=1 if mode=='greedy_1' else int(mode[-1]);return self.choice(s,m,b,min(h,b))[1]
    def rollout(self,w,b,mode):
        s=0;m=1<<w if mode=='clairvoyant' else FULL;reward=0;path=[]
        while b:
            a=self.policy(mode,s,m,b)
            if a<0:break
            k,i=self.actions[a];o=self.observation(k,i,w);ts=self.transitions(s,m,b,a)
            q,p,c,r=next(x for x in ts if x[1]>>w&1)
            path.append([k,i,list(o),m,p]);s,m,b=q,p,c;reward+=r
        return dict(reward=reward,remaining=b,acquired=s,posterior=m,path=path)


def check(d,w,b,mode,receipt):
    """Independent exact execution and posterior reconstruction from catalog."""
    s=set();worlds={w} if mode=='clairvoyant' else set(range(WORLD));total=0
    def observe(k,i,z):
        if k=='probe':return (False,1,(z//(2**i))%2)
        if k=='cached':return (*d.catalog[i][z],-1)
        if k=='direct':return (True,sum(len(row) for j,row in enumerate(d.entries) if d.supports[i]//(2**j)%2),-1)
        if k=='compose':return (True,1+d.supports[i].bit_count()//2,-1)
        raise ValueError('action')
    for k,i,o,prior,post in receipt['path']:
        assert prior==sum(1<<z for z in worlds) and w in worlds
        if k=='probe':assert 0<=i<3
        else:
            assert 0<=i<len(d.supports) and i not in s
            if k=='compose':assert i>=3 and all(j in s for j in range(3) if d.supports[i]>>j&1)
        if mode=='direct_only_exact':assert k in ('direct','compose')
        if mode=='bayes_no_probe':assert k!='probe'
        assert max(observe(k,i,z)[1] for z in worlds)<=b
        actual=observe(k,i,w);assert tuple(o)==actual;ok,cost,_=actual;b-=cost
        worlds={z for z in worlds if observe(k,i,z)==actual};assert post==sum(1<<z for z in worlds) and w in worlds
        if ok:
            # Direct/cached witness is the same exact sum. A composed sum uses
            # the already acquired disjoint group sums; no unverified reward.
            entries=[x for j,row in enumerate(d.entries) if d.supports[i]>>j&1 for x in row]
            v=sum(entries);ceiling=10*len(entries)
            if i>=3:assert ceiling>v and d.reward[i]%(ceiling-v)==0 and 1<=d.reward[i]//(ceiling-v)<=4
            else:assert d.reward[i]==0
            total+=d.reward[i];s.add(i)
    assert receipt['reward']==total and receipt['remaining']==b and receipt['acquired']==sum(1<<i for i in s) and receipt['posterior']==sum(1<<z for z in worlds)
    return total


def run():
    start=time.perf_counter();rows=[]
    for f in FAMILIES:
        for seed in SEEDS:
            d=make(f,seed);p=Planner(d)
            for b in BUDGETS:
                arms={}
                for mode in MODES:
                    t=time.perf_counter();before=p.calls;worlds=[p.rollout(w,b,mode) for w in range(WORLD)]
                    value=sum(d.weights[w]*check(d,w,b,mode,x) for w,x in enumerate(worlds))
                    if mode=='bayes':assert value==p.choice(0,FULL,b,b)[0]
                    if mode=='bayes_no_probe':assert value==p.choice(0,FULL,b,b,'no_probe')[0]
                    if mode=='direct_only_exact':assert value==p.choice(0,FULL,b,b,'direct')[0]
                    if mode=='clairvoyant':assert value==sum(p.choice(0,1<<w,b,b)[0] for w in range(WORLD))
                    arms[mode]=dict(weighted_reward=value,mass=p.mass[FULL],worlds=worlds,new_dp_states=p.calls-before,ms=(time.perf_counter()-t)*1000)
                assert all(arms[k]['weighted_reward']<=arms['bayes']['weighted_reward'] for k in MODES if k!='clairvoyant')
                assert arms['bayes']['weighted_reward']<=arms['clairvoyant']['weighted_reward']
                rows.append(dict(family=f,seed=seed,budget=b,arms=arms,prior=list(d.weights)))
            p.choice.cache_clear()
        print('done',f,flush=True,file=__import__('sys').stderr)
    return dict(schema='MIC-16/public-belief-planning/v1',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),rows=rows,elapsed_s=time.perf_counter()-start)

if __name__=='__main__':print(json.dumps(run(),sort_keys=True,indent=2))
