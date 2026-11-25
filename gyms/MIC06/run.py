"""MIC-06: finite weighted atomic revisions with support and exclusion."""
from dataclasses import dataclass
from functools import lru_cache
from fractions import Fraction as F
from pathlib import Path
from random import Random
import hashlib, json, time
import numpy as np
import torch
from torch import nn

FAMILIES = ('conflict', 'implication', 'disjunction', 'mixed')
SEEDS = (17, 29, 43)

@dataclass(frozen=True)
class Root:
    weights: tuple
    conflicts: tuple
    support: tuple  # (i, bitmask of alternative supports), one clause per row


def root(f, seed, n):
    rng = Random(seed + 100003 * FAMILIES.index(f))
    w = tuple(rng.randint(1, 12) for _ in range(n))
    edges = tuple((i,j) for i in range(n) for j in range(i+1,n) if rng.random() < (0.30 if f != 'mixed' else 0.23))
    # Ensure at least one conflict, so full-set closure is never a solution.
    if not edges: edges = ((0,1),)
    supports = []
    if f != 'conflict':
        for i in range(n):
            if rng.random() < .65:
                k = 1 if f == 'implication' else 2 if f == 'disjunction' else rng.choice((1,2,3))
                js = rng.sample([j for j in range(n) if i!=j], k)
                supports.append((i, sum(1<<j for j in js)))
            if f == 'mixed' and rng.random() < .25:
                js = rng.sample([j for j in range(n) if i!=j], 2)
                supports.append((i, sum(1<<j for j in js)))
    return Root(w, edges, tuple(supports))


def valid(d, s):
    return type(s) is int and 0 <= s < 1<<len(d.weights) and all(not (s>>i&1 and s>>j&1) for i,j in d.conflicts) and all(not(s>>i&1) or bool(s&js) for i,js in d.support)


def objective(d,s):
    return sum(w for i,w in enumerate(d.weights) if s>>i&1)


def closure(d,s):
    """Largest support-feasible subset; ignores exclusions by design."""
    checks = 0
    while True:
        prev = s
        for i,js in d.support:
            checks += 1
            if s>>i&1 and not (s&js): s &= ~(1<<i)
        if prev == s: return s, checks


def repair(d, priorities=None, lookahead=False):
    """Start at support closure; resolve conflicts and reclose, verifying final mask."""
    s, checks = closure(d,(1<<len(d.weights))-1)
    conflicts_checked = 0
    decisions = 0
    while True:
        edge = None
        for i,j in d.conflicts:
            conflicts_checked += 1
            if s>>i&1 and s>>j&1:
                edge=(i,j);break
        if edge is None: break
        i,j=edge;decisions+=1
        if lookahead:
            a,c = closure(d,s&~(1<<i));b,e = closure(d,s&~(1<<j));checks+=c+e
            s = max((a,b),key=lambda x:(objective(d,x),-x))
        else:
            k = min((i,j),key=lambda x:(priorities[x],-x))
            s,c = closure(d,s&~(1<<k));checks+=c
    assert valid(d,s)
    return dict(mask=s, value=objective(d,s), support_checks=checks, conflict_checks=conflicts_checked, decisions=decisions)


@lru_cache(None)
def masks(n):
    values=np.arange(1<<n,dtype=np.int64)
    bits=((values[:,None]>>np.arange(n))&1)
    return values,bits


def exact(d):
    values,bits=masks(len(d.weights));ok=np.ones(len(values),dtype=bool)
    for i,j in d.conflicts: ok &= ~((bits[:,i]==1)&(bits[:,j]==1))
    for i,js in d.support: ok &= (bits[:,i]==0)|((values&js)!=0)
    scores=bits@np.array(d.weights);best=int(scores[ok].max());winners=bits[ok&(scores==best)]
    return best,winners.mean(axis=0).astype(np.float32)


def features(d):
    n=len(d.weights);conf=np.zeros((n,n),np.float32);sup=conf.copy();rev=conf.copy();alt=np.zeros(n)
    for i,j in d.conflicts: conf[i,j]=conf[j,i]=1
    for i,js in d.support:
        k=js.bit_count();alt[i]+=k
        for j in range(n):
            if js>>j&1: sup[i,j]+=1/k;rev[j,i]+=1/k
    x=np.array([[d.weights[i]/12,conf[i].sum()/n,sup[i].sum()/n,rev[i].sum()/n,alt[i]/n,1.] for i in range(n)],np.float32)
    a=np.stack([conf,sup,rev]);a/=np.maximum(1,a.sum(axis=-1,keepdims=True))
    return torch.from_numpy(x),torch.from_numpy(a)


class Ranker(nn.Module):
    def __init__(self,graph):
        super().__init__();self.graph=graph;self.embed=nn.Linear(6,16);self.cell=nn.GRUCell(48,16);self.out=nn.Linear(16,1)
    def forward(self,x,a):
        h=torch.tanh(self.embed(x))
        for _ in range(3):
            m=torch.cat([a[:,i]@h if self.graph else h for i in range(3)],dim=-1)
            h=self.cell(m.reshape(-1,48),h.reshape(-1,16)).reshape_as(h)
        return self.out(h).squeeze(-1)


def fit(train,seed,graph):
    torch.manual_seed(seed);net=Ranker(graph);opt=torch.optim.Adam(net.parameters(),lr=.008)
    x,a,y=[torch.stack(z) for z in zip(*train)]
    for _ in range(120):
        loss=nn.functional.binary_cross_entropy_with_logits(net(x,a),y);opt.zero_grad();loss.backward();opt.step()
    return net


def run():
    torch.set_num_threads(1);t=time.perf_counter();train=[]
    for f in ('conflict','mixed'):
        for seed in range(96):
            d=root(f,seed,10);_,y=exact(d);x,a=features(d);train.append((x,a,torch.from_numpy(y)))
    models={(name,s):fit(train,s,graph) for s in SEEDS for name,graph in [('self',False),('graph',True)]};rows=[]
    for f in FAMILIES:
        for n in (10,12):
            for seed in range(1000,1016):
                d=root(f,seed,n);gold,_=exact(d);x,a=features(d);rng=Random(seed+5000*n+100*FAMILIES.index(f))
                degree=[sum(i in e for e in d.conflicts) for i in range(n)]
                arms={'weight':repair(d,d.weights),'degree':repair(d,[F(w,1+k) for w,k in zip(d.weights,degree)]),'random':repair(d,[rng.random() for _ in range(n)]),'lookahead':repair(d,lookahead=True)}
                for (name,s),model in models.items():
                    with torch.no_grad(): p=model(x[None],a[None])[0].tolist()
                    arms[f'{name}_{s}']=repair(d,p)
                assert all(valid(d,r['mask']) and r['value']<=gold for r in arms.values())
                rows.append(dict(family=f,n=n,seed=seed,oracle=gold,full_support_mask=closure(d,(1<<n)-1)[0],arms=arms))
    return dict(schema='MIC-06/public-cpu/v1',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),training_roots=len(train),parameter_count=sum(p.numel() for p in next(iter(models.values())).parameters()),model_seeds=SEEDS,rows=rows,elapsed_seconds=time.perf_counter()-t,torch_version=torch.__version__)

if __name__=='__main__': print(json.dumps(run(),sort_keys=True,indent=2))
